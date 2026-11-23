"""Import the original bot's JSON file into a new database, once, at cutover.

    python -m taskbot.legacy import <legacy.json> <tasks.db> [--report FILE]

The JSON is never modified. Close resolutions are guessed from the close reason
(inference.py) and creation times estimated from Discord ids; `taskbot.feed.apply`
then replaces both wherever the old feed channel has the real history. This
module, inference.py and taskbot/feed only matter until the cutover is done.
"""

import argparse
import collections
import datetime
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Optional

from . import inference
from .models import Entry
from .store import LEGACY_REDACTION, TaskStore, make_image
from .vocab import COMPLEXITIES, DEFAULT_COMPLEXITY, DEFAULT_LABEL, DEFAULT_PRIORITY, PRIORITIES

# The old `import` command (used once, for the first ~500 suggestions) appended this
_CREATED_RE = re.compile(r"\n\nCreated: (\d{4})-(\d{2})-(\d{2})\n")



@dataclass
class ImportReport:
    entries: int = 0
    open: int = 0
    closed: int = 0
    resolutions: collections.Counter[str] = field(default_factory=collections.Counter[str])
    reason_table: dict[str, collections.Counter[str]] = field(default_factory=dict[str, collections.Counter[str]])
    precision: collections.Counter[str] = field(default_factory=collections.Counter[str])
    inactive_labels: list[str] = field(default_factory=list[str])
    duplicate_links: int = 0
    warnings: list[str] = field(default_factory=list[str])

    def summary(self) -> str:
        lines = [
            f"Imported {self.entries} entries ({self.open} open, {self.closed} closed)",
            "Resolutions (inferred from close reasons): "
            + ", ".join(f"{k}={v}" for k, v in sorted(self.resolutions.items())),
            f"Duplicate links recovered: {self.duplicate_links}",
            "Creation times: "
            + ", ".join(f"{k}={v}" for k, v in sorted(self.precision.items())),
        ]
        if self.inactive_labels:
            lines.append("Labels used by entries but not in the label list (added inactive): "
                         + ", ".join(self.inactive_labels))
        lines.extend(f"warning: {w}" for w in self.warnings)
        return "\n".join(lines)

    def classification_report(self) -> str:
        """Every distinct close reason with what it was classified as, most common first."""
        rows: list[tuple[int, str, str]] = []
        for resolution, reasons in self.reason_table.items():
            for reason, count in reasons.items():
                rows.append((count, resolution, reason))
        rows.sort(key=lambda r: (-r[0], r[1], r[2]))
        return "\n".join(f"{count:6d}  {resolution:9s}  {reason!r}" for count, resolution, reason in rows)


def _created_date(description: str) -> Optional[int]:
    m = _CREATED_RE.search(description)
    if not m:
        return None
    d = datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                          tzinfo=datetime.timezone.utc)
    return int(d.timestamp())


def _upper_bound(raw: dict[str, Any]) -> Optional[float]:
    bounds: list[float] = []
    if raw.get("message_id"):
        bounds.append(inference.snowflake_time(int(raw["message_id"])))
    if raw.get("image"):
        attachment_id = make_image(str(raw["image"])).attachment_id
        if attachment_id:
            bounds.append(inference.snowflake_time(attachment_id))
    return min(bounds) if bounds else None


def import_legacy(store: TaskStore, data: dict[str, Any]) -> ImportReport:
    """Load a legacy JSON document into an empty store."""
    if not store.is_empty():
        raise RuntimeError("Refusing to import into a database that already has entries")

    report = ImportReport()
    raw_entries: dict[str, dict[str, Any]] = data["entries"]
    ids = sorted(int(k) for k in raw_entries)
    by_id = {i: raw_entries[str(i)] for i in ids}

    labels = [str(x) for x in list(data.get("labels") or [])]
    if DEFAULT_LABEL not in labels:
        labels.insert(0, DEFAULT_LABEL)

    # Creation times. Dates written by the old import command are exact to the day and
    # are also an upper bound (end of that day) for the snowflake estimate.
    dated = {i: _created_date(str(by_id[i].get("description", ""))) for i in ids}
    bounds: list[Optional[float]] = []
    for i in ids:
        b = _upper_bound(by_id[i])
        d = dated[i]
        if d is not None:
            b = min(b, d + 86400) if b is not None else d + 86400
        bounds.append(b)
    estimates = inference.estimate_creation_times(ids, bounds)
    first_anchor = next((k for k, b in enumerate(bounds) if b is not None and b == estimates[k]), None)

    with store.transaction():
        store.set_label_list(labels)
        used: set[str] = set()
        for raw in raw_entries.values():
            used.update(str(lbl) for lbl in list(raw.get("labels") or []))
        for extra in sorted(used - set(labels)):
            store.add_inactive_label(extra)
            report.inactive_labels.append(extra)

        for pos, i in enumerate(ids):
            raw = by_id[i]
            description = str(raw.get("description", ""))
            entry_labels = [str(x) for x in list(raw.get("labels") or [])] or [DEFAULT_LABEL]
            closed = "close_reason" in raw
            close_reason = str(raw["close_reason"]) if closed else None
            redacted = description.strip().lower() in ("redacted", "[redacted]")

            # How the time was found, for the report
            if dated[i] is not None:
                created_at: Optional[int] = dated[i]
                report.precision["date written by the old import command"] += 1
            else:
                est = estimates[pos]
                created_at = int(est) if est is not None else None
                report.precision["no earlier anchor (an upper bound)" if first_anchor is None
                                 or pos < first_anchor else "estimated from Discord ids"] += 1

            resolution: Optional[str] = None
            duplicate_of: Optional[int] = None
            if closed:
                assert close_reason is not None
                resolution, duplicate_of = inference.classify_close_reason(close_reason)
                if duplicate_of is not None and (duplicate_of == i or duplicate_of not in by_id):
                    duplicate_of = None
                if duplicate_of is not None:
                    report.duplicate_links += 1
                report.resolutions[resolution] += 1
                report.reason_table.setdefault(resolution, collections.Counter())[close_reason] += 1
                report.closed += 1
            else:
                report.open += 1

            images = [make_image(str(raw["image"]))] if raw.get("image") else []
            # Redacted by editing the description: hide the image as `redact` does
            hidden_images = [im.url for im in images] if redacted else []
            if redacted:
                images = []
            assignee = raw.get("assignee")
            priority = str(raw.get("priority", DEFAULT_PRIORITY))
            complexity = str(raw.get("complexity", DEFAULT_COMPLEXITY))
            if priority not in PRIORITIES or complexity not in COMPLEXITIES:
                report.warnings.append(f"#{i} has priority {priority!r} / complexity {complexity!r}, "
                                       "outside the standard lists")
            entry = Entry(
                id=i, description=description, author_id=int(raw.get("author") or 0),
                priority=priority, complexity=complexity, labels=entry_labels,
                status="closed" if closed else "open", resolution=resolution,
                close_reason=close_reason,
                duplicate_of=duplicate_of,
                assignee_id=int(assignee) if assignee else None, redacted=redacted,
                message_id=int(raw["message_id"]) if raw.get("message_id") else None,
                pending_notification=bool(raw.get("pending_notification", True)),
                created_at=created_at, updated_at=None,
                images=images)
            store.insert_entry(entry)
            if hidden_images:
                store.save_redacted(i, {"images": hidden_images}, LEGACY_REDACTION, None)

            author = entry.author_id or None
            store.add_event(i, "created", at=created_at, actor_id=author, source="legacy")
            if entry.assignee_id is not None:
                store.add_event(i, "assigned", at=None, actor_id=None, source="legacy",
                                new=entry.assignee_id)
            if closed:
                store.add_event(i, "closed", at=None, actor_id=None, source="legacy",
                                new=resolution, reason=close_reason)
            if redacted:
                store.add_event(i, "redacted", at=None, actor_id=None, source="legacy")
            report.entries += 1

        for user in list(data.get("notifications_disabled") or []):
            store.set_notifications_disabled(int(user), True)

        next_index = int(data.get("next_index", (ids[-1] + 1) if ids else 1))
        if ids and next_index <= ids[-1]:
            report.warnings.append(f"next_index {next_index} <= highest id {ids[-1]}; using {ids[-1] + 1}")
            next_index = ids[-1] + 1
        store.set_meta("next_index", str(next_index))

    for key in data:
        if key not in ("entries", "next_index", "labels", "priorities", "complexities",
                       "notifications_disabled", "kanboard"):
            report.warnings.append(f"ignored unknown top-level key {key!r}")
    return report


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m taskbot.legacy")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_imp = sub.add_parser("import", help="import a legacy JSON file into a new database")
    p_imp.add_argument("json")
    p_imp.add_argument("db")
    p_imp.add_argument("--report", help="write the close-reason classification table here "
                                        "(default: <db>.classification.txt)")
    args = parser.parse_args(argv)

    if os.path.exists(args.db):
        print(f"{args.db} already exists", file=sys.stderr)
        return 1
    # Read the JSON before creating the database, so a wrong path or bad file leaves nothing behind
    with open(args.json, "r", encoding="utf-8") as f:
        data = json.load(f)
    store = TaskStore.open(args.db)
    try:
        report = import_legacy(store, data)
    finally:
        store.close()
    print(report.summary())
    report_path = args.report or args.db + ".classification.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report.classification_report() + "\n")
    print(f"Classification table written to {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
