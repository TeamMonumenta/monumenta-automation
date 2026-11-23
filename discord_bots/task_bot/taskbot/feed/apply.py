"""Write a feed replay's events into a freshly imported database.

    python -m taskbot.feed.apply <tasks.db> <events.jsonl>

Run it once, right after `python -m taskbot.legacy import` and before the bot
starts on the database: it refuses a database that holds anything but the
import's own events. To redo it, import again.

For each entry the replay saw, its events replace the import's placeholders of
the same kinds (a `created` at an estimated time, a `closed` and an `assigned`
with no time or actor), and the entry's history is rewritten in time order.
Entries the replay never saw keep what the import wrote.

On the entry itself:
- `created_at` becomes the time of the command, when the replay found the creation.
- `closed_at`, `closed_by` and the resolution come from the last close, if the
  entry is closed and the replay's last close has the same reason (or the entry
  is redacted, whose reason the old bot blanked). The resolution is what the
  closer chose (`fix` or `reject`), with rejects that say they are duplicates
  counted as duplicates, and fixes whose reason names the original by number too.
- Closes still without a time get one, so that every closed entry has a close time and
  statistics never have to carry the gap: the latest time in the entry's history, which
  is its creation time unless the feed shows later events (a close whose reason differs
  from the JSON). Every entry has a creation time from the import, unless the JSON
  holds no Discord ids at all. Who made these closes stays unknown. The import's
  undated `closed` events get the same time.
- Nothing else changes; the import's values for author, assignee, labels and so
  on are the final state and stay.

Redacted entries get their events with the text left out, as `redact` would
leave them.
"""

import argparse
import collections
import json
import os
import sys
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Optional

from .. import inference
from ..models import Entry
from ..store import TaskStore

# Replay kinds that don't exist in the database's vocabulary, renamed or dropped.
_RENAME = {"deleted": "redacted"}   # the old `delete` only redacted
_DROP = {"edited"}                  # an edit whose field the replay couldn't tell
# What redaction blanks (as TaskService.redact does).
_TEXT_KINDS = {"created", "description", "appended", "image"}


@dataclass
class ApplyReport:
    entries: int = 0
    events: int = 0
    skipped_missing: int = 0
    dropped: collections.Counter[str] = field(default_factory=collections.Counter[str])
    created_exact: int = 0
    closes_exact: int = 0
    closes_with_closer: int = 0
    closes_not_matching: int = 0
    resolutions: collections.Counter[str] = field(default_factory=collections.Counter[str])
    resolution_changed: int = 0
    closes_estimated: int = 0
    originals_to_publish: int = 0

    def summary(self) -> str:
        lines = [
            f"Rewrote the history of {self.entries} entries with {self.events} events",
            f"Exact creation times: {self.created_exact}",
            f"Exact close times: {self.closes_exact} ({self.closes_with_closer} with the closer)",
            f"Closes left as imported (the replay's last close differs): {self.closes_not_matching}",
            "Resolutions from the command used: " + ", ".join(
                f"{k} {v}" for k, v in sorted(self.resolutions.items())),
            f"Resolutions that differ from the import's guess: {self.resolution_changed}",
            f"Close times estimated (no matching close in the feed): {self.closes_estimated}",
            f"Tracking messages to update at first start, to list duplicates: {self.originals_to_publish}",
        ]
        if self.skipped_missing:
            lines.append(f"Events for entries not in the database (skipped): {self.skipped_missing}")
        for kind, n in sorted(self.dropped.items()):
            lines.append(f"Dropped {kind} events: {n}")
        return "\n".join(lines)


def load_events(path: str) -> dict[int, list[dict[str, Any]]]:
    by_entry: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    with open(path, encoding="utf-8") as f:
        for line in f:
            ev: dict[str, Any] = json.loads(line)
            by_entry[int(ev["entry_id"])].append(ev)
    return by_entry


def check_fresh_import(store: TaskStore) -> Optional[str]:
    row = store.conn.execute("SELECT source, COUNT(*) FROM events WHERE source != 'legacy' "
                             "GROUP BY source").fetchone()
    if row is not None:
        return (f"the database has {row[1]} events from source {row[0]!r}; apply right after the "
                "legacy import, before the bot runs on it (import again to start over)")
    if store.is_empty():
        return "the database has no entries; import the legacy JSON first"
    return None


def check_matches(store: TaskStore, by_entry: dict[int, list[dict[str, Any]]]) -> list[str]:
    """Reasons to think the events don't belong with this database: the other tracker's
    feed, or a feed and a JSON from different times."""
    problems: list[str] = []
    agree = total = 0
    for entry_id, events in by_entry.items():
        entry = store.get(entry_id)
        if entry is None or not entry.author_id:
            continue
        for ev in events:
            if ev["kind"] == "created" and ev.get("actor_id"):
                total += 1
                agree += ev["actor_id"] == entry.author_id
    if total and agree < total / 2:
        problems.append(f"only {agree} of {total} creations in the feed are by the entry's author: "
                        "is this the other tracker's feed?")
    missing = sorted(i for i in by_entry if store.get(i) is None)
    if missing:
        problems.append(f"the feed has events for {len(missing)} entries the database doesn't have "
                        f"({', '.join(f'#{i}' for i in missing[:10])}): is the JSON older than the feed?")
    newest_created = max((i for i, evs in by_entry.items() if any(e["kind"] == "created" for e in evs)),
                         default=0)
    newest = store.conn.execute("SELECT MAX(id) FROM entries").fetchone()[0] or 0
    if newest > newest_created:
        problems.append(f"the database's newest entry is #{newest} but the feed's is #{newest_created}: "
                        "catch up the download (and replay) first")
    return problems


def apply_events(store: TaskStore, by_entry: dict[int, list[dict[str, Any]]]) -> ApplyReport:
    report = ApplyReport()
    with store.transaction():
        for entry_id in sorted(by_entry):
            entry = store.get(entry_id)
            if entry is None:
                report.skipped_missing += len(by_entry[entry_id])
                continue
            events = real_creation(_prepare(by_entry[entry_id], entry.redacted, report), entry.author_id)
            if not events:
                continue
            replaced = {ev["kind"] for ev in events}
            if _final_close(entry, events) is None:
                # Keep the import's close: it holds the reason the entry really ended with.
                replaced.discard("closed")
            _rewrite_history(store, entry_id, events, replaced)
            report.entries += 1
            report.events += len(events)
            _update_entry(store, entry_id, events, report)
        report.closes_estimated = _fill_unknown_close_times(store)
        # The old bot didn't list duplicates on the original; the first start adds the line
        report.originals_to_publish = store.conn.execute(
            """UPDATE entries SET channel_dirty = channel_dirty + 1
               WHERE message_id IS NOT NULL
                 AND id IN (SELECT duplicate_of FROM entries WHERE duplicate_of IS NOT NULL)""").rowcount
    return report


def real_creation(events: list[dict[str, Any]], author_id: int) -> list[dict[str, Any]]:
    """An entry's events from its real creation. A few numbers were created twice in the
    feed (a test instance or another bot posting in the channel, or a reply posted twice):
    the creation by the entry's author counts, else the last, and what came before it
    belonged to the other entry."""
    created = [i for i, ev in enumerate(events) if ev["kind"] == "created"]
    if len(created) < 2:
        return events
    by_author = [i for i in created if author_id and events[i].get("actor_id") == author_id]
    start = by_author[0] if by_author else created[-1]
    return [ev for i, ev in enumerate(events) if i == start or (i > start and ev["kind"] != "created")]


def _fill_unknown_close_times(store: TaskStore) -> int:
    """The latest known time in the entry's history: its creation, unless the feed shows
    later events, such as a close whose reason differs from the JSON. The import gives
    every entry a creation time when the JSON has any Discord ids at all, so the
    fallbacks (the oldest known close, then now) are for a JSON without them."""
    oldest = store.conn.execute("SELECT MIN(closed_at) FROM entries").fetchone()[0]
    ids = [int(r[0]) for r in store.conn.execute(
        "SELECT id FROM entries WHERE status = 'closed' AND closed_at IS NULL")]
    store.conn.execute(
        "UPDATE entries SET closed_at = COALESCE("
        "(SELECT MAX(at) FROM events WHERE events.entry_id = entries.id), created_at, ?) "
        "WHERE status = 'closed' AND closed_at IS NULL",
        (oldest if oldest is not None else int(time.time()),))
    store.conn.executemany(
        "UPDATE events SET at = (SELECT closed_at FROM entries WHERE id = ?) "
        "WHERE entry_id = ? AND kind = 'closed' AND at IS NULL", [(i, i) for i in ids])
    return len(ids)


def _prepare(raw: Iterable[dict[str, Any]], redacted: bool, report: ApplyReport) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for ev in raw:
        kind = _RENAME.get(ev["kind"], ev["kind"])
        if kind in _DROP:
            report.dropped[kind] += 1
            continue
        ev = dict(ev, kind=kind, at=int(ev["at"]))
        if redacted:
            ev["reason"] = None
            if kind in _TEXT_KINDS:
                ev["old"] = ev["new"] = None
        events.append(ev)
    return events


def _final_close(entry: Entry, events: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """The replay's last close, if it is the close the entry ended with."""
    last = next((ev for ev in reversed(events) if ev["kind"] in ("closed", "reopened")), None)
    if entry.status != "closed" or last is None or last["kind"] != "closed":
        return None
    if not entry.redacted and (last.get("reason") or "").strip() != (entry.close_reason or "").strip():
        return None
    return last


def _rewrite_history(store: TaskStore, entry_id: int, events: list[dict[str, Any]],
                     replaced: set[str]) -> None:
    kept = [r for r in store.conn.execute(
        "SELECT at, actor_id, kind, old_value, new_value, reason, source, source_ref, actor_mc_uuid "
        "FROM events WHERE entry_id = ? ORDER BY id", (entry_id,)) if r["kind"] not in replaced]
    store.conn.execute("DELETE FROM events WHERE entry_id = ?", (entry_id,))

    rows: list[tuple[Optional[int], int, tuple[Any, ...]]] = []
    for r in kept:
        rows.append((r["at"], 0, (r["at"], r["actor_id"], r["kind"], r["old_value"], r["new_value"],
                                  r["reason"], r["source"], r["source_ref"], r["actor_mc_uuid"])))
    for i, ev in enumerate(events):
        ref = ev.get("source_ref") or ev.get("reply_ref")
        rows.append((ev["at"], i + 1, (ev["at"], ev.get("actor_id"), ev["kind"], _encode(ev.get("old")),
                                       _encode(ev.get("new")), ev.get("reason"), "backfill",
                                       str(ref) if ref else None, None)))
    # Known times in order; the import's undated events (a close or redaction the feed
    # doesn't show) last.
    rows.sort(key=lambda r: (r[0] is None, r[0] or 0, r[1]))
    store.conn.executemany(
        "INSERT INTO events(entry_id, at, actor_id, kind, old_value, new_value, reason, source, "
        "source_ref, actor_mc_uuid) VALUES (?,?,?,?,?,?,?,?,?,?)",
        [(entry_id, *r[2]) for r in rows])


def _update_entry(store: TaskStore, entry_id: int, events: list[dict[str, Any]],
                  report: ApplyReport) -> None:
    entry = store.get(entry_id)
    assert entry is not None
    created = next((ev for ev in events if ev["kind"] == "created"), None)
    if created is not None:
        store.update(entry_id, created_at=created["at"])
        report.created_exact += 1
    else:
        # An estimate can't be later than what the feed saw happen to the entry
        earliest = min(ev["at"] for ev in events)
        if entry.created_at is None or earliest < entry.created_at:
            store.update(entry_id, created_at=earliest)

    last = _final_close(entry, events)
    if last is None:
        if entry.status == "closed" and any(ev["kind"] == "closed" for ev in events):
            report.closes_not_matching += 1
        return
    resolution = str(last["new"])
    guess, duplicate_of = inference.classify_close_reason(entry.close_reason or "")
    if duplicate_of is not None and (duplicate_of == entry_id or store.get(duplicate_of) is None):
        duplicate_of = None
    if resolution == inference.FIXED and guess == inference.DUPLICATE and duplicate_of is not None:
        # Fixed with a reason naming the original ("dupe of 2360"): a duplicate too
        resolution = inference.DUPLICATE
    if resolution != inference.DUPLICATE:
        duplicate_of = None
    if resolution != entry.resolution:
        report.resolution_changed += 1
    store.update(entry_id, closed_at=last["at"], closed_by=last.get("actor_id"),
                 resolution=resolution, duplicate_of=duplicate_of)
    report.closes_exact += 1
    report.resolutions[resolution] += 1
    if last.get("actor_id"):
        report.closes_with_closer += 1


def _encode(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m taskbot.feed.apply", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("db", help="a database just made by `python -m taskbot.legacy import`")
    parser.add_argument("events", help="events from `python -m taskbot.feed.replay`")
    parser.add_argument("--force", action="store_true",
                        help="apply even when the events don't seem to match the database")
    args = parser.parse_args(argv)
    if not os.path.exists(args.db):
        print(f"Refusing: {args.db} doesn't exist; make it with `python -m taskbot.legacy import`",
              file=sys.stderr)
        return 1
    store = TaskStore.open(args.db)
    problem = check_fresh_import(store)
    if problem is not None:
        print(f"Refusing: {problem}", file=sys.stderr)
        return 1
    by_entry = load_events(args.events)
    mismatches = check_matches(store, by_entry)
    if mismatches and not args.force:
        for m in mismatches:
            print(f"Refusing: {m}", file=sys.stderr)
        print("(--force applies anyway)", file=sys.stderr)
        return 1
    print(apply_events(store, by_entry).summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
