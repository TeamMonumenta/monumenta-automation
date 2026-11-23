"""Applying replayed feed events to a freshly imported database."""

import json
from pathlib import Path
from typing import Any

from taskbot.feed.apply import apply_events, check_fresh_import, check_matches, main
from taskbot.legacy import import_legacy
from taskbot.store import TaskStore

STAFF = 1001
PLAYER = 2002


def entry(description: str, **extra: Any) -> dict[str, Any]:
    return {"description": description, "labels": ["misc"], "author": PLAYER, "priority": "N/A",
            "complexity": "unknown", "pending_notification": False, **extra}


def ev(entry_id: int, at: int, kind: str, actor: Any = STAFF, **extra: Any) -> dict[str, Any]:
    return {"entry_id": entry_id, "at": at, "actor_id": actor, "kind": kind, "old": None, "new": None,
            "reason": None, "source_ref": 900 + at, "reply_ref": 950 + at, "attribution": "matched",
            "note": "", **extra}


def imported(tmp_path: Path) -> TaskStore:
    store = TaskStore.open(str(tmp_path / "t.db"))
    import_legacy(store, {"entries": {
        "1": entry("crash when opening the map in the north", close_reason="seems fixed already"),
        "2": entry("same crash on the map again today", close_reason="dupe of 1"),
        "3": entry("redacted", close_reason=""),
        "4": entry("never seen in the feed at all", close_reason="Fixed"),
        "5": entry("closed again later with a new reason", close_reason="second reason"),
    }, "next_index": 6})
    return store


def test_apply(tmp_path: Path) -> None:
    store = imported(tmp_path)
    assert check_fresh_import(store) is None
    report = apply_events(store, {
        1: [ev(1, 100, "created", PLAYER, new="crash when opening the map in the north"),
            ev(1, 200, "priority", old="N/A", new="High"),
            ev(1, 300, "closed", new="rejected", reason="seems fixed already")],
        2: [ev(2, 110, "created", PLAYER), ev(2, 310, "closed", None, new="duplicate", reason="dupe of 1")],
        3: [ev(3, 120, "created", PLAYER, new="secret exploit text"),
            ev(3, 320, "closed", new="fixed", reason="secret details"), ev(3, 330, "deleted")],
        5: [ev(5, 130, "created", PLAYER), ev(5, 340, "closed", new="fixed", reason="first reason")],
        9: [ev(9, 140, "created", PLAYER)],
    })

    e1 = store.get(1)
    assert e1 is not None
    assert e1.created_at == 100
    # What the closer chose wins over the guess from the text ("fixed" in the reason).
    assert (e1.closed_at, e1.closed_by, e1.resolution) == (300, STAFF, "rejected")
    assert [(x.kind, x.source, x.at) for x in store.events_for(1)] == [
        ("created", "backfill", 100), ("priority", "backfill", 200), ("closed", "backfill", 300)]

    e2 = store.get(2)
    assert e2 is not None and (e2.resolution, e2.duplicate_of, e2.closed_by) == ("duplicate", 1, None)

    e3 = store.get(3)
    assert e3 is not None and e3.closed_at == 320
    history3 = store.events_for(3)
    assert [x.kind for x in history3] == ["created", "closed", "redacted"]
    assert all(x.new_value in (None, "fixed") and x.reason is None for x in history3)

    # Never in the feed, or the feed's last close isn't the one in the JSON: the close
    # time becomes the latest known time in the history (or, with none, the oldest known
    # close), and the closer stays unknown.
    e4, e5 = store.get(4), store.get(5)
    assert e4 is not None and e4.created_at is None and e4.closed_at == 300 and e4.closed_by is None
    assert e5 is not None and e5.closed_at == 340 and e5.created_at == 130
    # The JSON's own close stays, after the replay's earlier one, and gets the same time.
    assert [(x.kind, x.source, x.reason, x.at) for x in store.events_for(5)] == [
        ("created", "backfill", None, 130), ("closed", "backfill", "first reason", 340),
        ("closed", "legacy", "second reason", 340)]
    assert report.closes_not_matching == 1 and report.skipped_missing == 1
    assert report.closes_estimated == 2

    assert check_fresh_import(store) is not None


def test_fix_naming_the_original_is_a_duplicate(tmp_path: Path) -> None:
    store = TaskStore.open(str(tmp_path / "t.db"))
    import_legacy(store, {"entries": {
        "1": entry("crash when opening the map in the north", close_reason="Fixed"),
        "2": entry("same crash on the map again today", close_reason="dupe of 1, fixed there"),
    }, "next_index": 3})
    apply_events(store, {2: [ev(2, 110, "created", PLAYER),
                             ev(2, 310, "closed", new="fixed", reason="dupe of 1, fixed there")]})
    e2 = store.get(2)
    assert e2 is not None and (e2.resolution, e2.duplicate_of) == ("duplicate", 1)


def test_a_number_created_twice_starts_at_the_authors_creation(tmp_path: Path) -> None:
    store = imported(tmp_path)
    apply_events(store, {4: [ev(4, 50, "created", STAFF), ev(4, 60, "labels", old=["misc"], new=["quest"]),
                             ev(4, 100, "created", PLAYER), ev(4, 105, "created", PLAYER)]})
    e4 = store.get(4)
    assert e4 is not None and e4.created_at == 100
    assert [(x.kind, x.at) for x in store.events_for(4)][:1] == [("created", 100)]
    assert [x.kind for x in store.events_for(4)].count("created") == 1


def test_estimates_are_no_later_than_the_feed(tmp_path: Path) -> None:
    store = imported(tmp_path)
    store.update(4, created_at=500)
    apply_events(store, {4: [ev(4, 300, "priority", old="N/A", new="High")]})
    e4 = store.get(4)
    assert e4 is not None and e4.created_at == 300


def test_refuses_events_that_dont_belong(tmp_path: Path) -> None:
    store = imported(tmp_path)
    own = {i: [ev(i, 100 + i, "created", PLAYER)] for i in range(1, 6)}
    assert not check_matches(store, own)
    other_tracker = {i: [ev(i, 100 + i, "created", STAFF)] for i in range(1, 6)}
    assert "other tracker" in check_matches(store, other_tracker)[0]
    newer_feed = {**own, 6: [ev(6, 200, "created", PLAYER)]}
    assert "doesn't have (#6)" in check_matches(store, newer_feed)[0]
    older_feed = {i: own[i] for i in (1, 2)}
    assert "catch up" in check_matches(store, older_feed)[0]
    store.conn.close()

    events = tmp_path / "e.jsonl"
    events.write_text("".join(json.dumps(e) + "\n" for evs in other_tracker.values() for e in evs))
    assert main([str(tmp_path / "t.db"), str(events)]) == 1
    assert main([str(tmp_path / "missing.db"), str(events)]) == 1
    assert not (tmp_path / "missing.db").exists()
