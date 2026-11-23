"""Legacy JSON import, classification and time estimation, on synthetic data."""

import json
import os
from typing import Any

import pytest

from taskbot import inference
from taskbot.legacy import import_legacy, main
from taskbot.store import TaskStore

T0 = 1_600_000_000


def sf(ts: float) -> int:
    return inference.time_to_snowflake(ts)


def legacy_doc() -> dict[str, Any]:
    return {
        "entries": {
            "1": {"description": "imported one\n\nCreated: 2018-05-04\nOriginal Reactions:", "labels": ["misc"],
                  "author": 11, "priority": "N/A", "complexity": "unknown", "pending_notification": False,
                  "close_reason": "Fixed", "kanboard_id": 3},
            "2": {"description": "two", "labels": ["quest", "suggestion"], "author": 0,
                  "priority": "High", "complexity": "easy", "pending_notification": True,
                  "message_id": sf(T0 + 1000)},
            "3": {"description": "three", "labels": ["boss"], "author": 12,
                  "image": f"https://cdn.discordapp.com/attachments/77/{sf(T0 + 500)}/x.png?ex=6aff&is=1&hm=2&",
                  "priority": "Low", "complexity": "hard", "pending_notification": False,
                  "close_reason": "dupe of 2"},
            "4": {"description": "REDACTED", "labels": ["misc"], "author": 12, "priority": "N/A",
                  "image": "https://cdn.discordapp.com/attachments/77/88/exploit.png",
                  "complexity": "unknown", "pending_notification": False, "close_reason": ""},
            "5": {"description": "five", "labels": ["misc"], "author": 13, "priority": "N/A",
                  "complexity": "unknown", "pending_notification": False, "assignee": 14,
                  "message_id": sf(T0 + 3000)},
        },
        "next_index": 6,
        "labels": ["boss", "quest"],
        "priorities": ["Critical", "High", "Low", "N/A"],
        "complexities": {"easy": ":g:", "hard": ":r:", "unknown": ":w:"},
        "notifications_disabled": [12],
    }


def test_import_maps_everything(tmp_path: Any) -> None:
    store = TaskStore.open(str(tmp_path / "t.db"))
    report = import_legacy(store, legacy_doc())
    assert report.entries == 5 and report.open == 2 and report.closed == 3
    assert store.labels() == ["misc", "boss", "quest"]  # misc is always there
    assert store.labels(include_inactive=True)[-1] == "suggestion"
    assert store.next_index() == 6
    assert store.notifications_disabled(12)

    e1, e2, e3, e4, e5 = store.get_many([1, 2, 3, 4, 5])
    assert e1.resolution == "fixed" and e1.closed_at is None
    assert e1.created_at == 1525392000  # the date the old import command wrote
    assert e2.labels == ["quest", "suggestion"] and e2.pending_notification and e2.author_id == 0
    assert e3.resolution == "duplicate" and e3.duplicate_of == 2
    assert e3.images[0].attachment_id == sf(T0 + 500)
    assert e4.redacted and e4.close_reason == "" and e4.is_closed
    # Redacted by editing the description, image left behind: hidden as `redact` would
    assert not e4.images
    assert store.redacted_content(4) == {"redacted_at": 0, "redacted_by": None,
                                         "images": ["https://cdn.discordapp.com/attachments/77/88/exploit.png"]}
    assert e5.assignee_id == 14
    # #3's image is earlier than #2's message, so #2 is bounded by #3's time
    assert e2.created_at is not None and e3.created_at is not None
    assert e2.created_at <= e3.created_at + 1
    kinds = [ev.kind for ev in store.events_for(5)]
    assert kinds == ["created", "assigned"]
    assert [ev.kind for ev in store.events_for(4)] == ["created", "closed", "redacted"]


def test_refuses_non_empty(tmp_path: Any) -> None:
    store = TaskStore.open(str(tmp_path / "t.db"))
    import_legacy(store, legacy_doc())
    with pytest.raises(RuntimeError):
        import_legacy(store, legacy_doc())


def test_command_line(tmp_path: Any) -> None:
    json_path = str(tmp_path / "legacy.json")
    db_path = str(tmp_path / "t.db")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(legacy_doc(), f)
    assert main(["import", json_path, db_path]) == 0
    assert os.path.exists(db_path + ".classification.txt")
    store = TaskStore.open(db_path)
    assert len(store.all_entries()) == 5
    store.close()
    assert main(["import", json_path, db_path]) == 1  # never over an existing database


@pytest.mark.parametrize("reason,expected", [
    ("Fixed", "fixed"), ("hotfixed", "fixed"), ("Fixed for next update", "fixed"),
    ("Implemented!", "fixed"), ("already fixed", "fixed"), ("no longer an issue", "fixed"),
    ("not a bug", "rejected"), ("intentional", "rejected"), ("Unpopular", "rejected"),
    ("will not be fixed", "rejected"), ("can't be added", "rejected"),
    ("move to bug reports if you want it fixed", "rejected"), ("", "rejected"), (".", "rejected"),
    ("dupe", "duplicate"), ("Dupe of #123", "duplicate"), ("dupe of fixed bug", "duplicate"),
    ("Merged into 10959", "duplicate"), ("tracked by 5119", "duplicate"),
])
def test_classify(reason: str, expected: str) -> None:
    assert inference.classify_close_reason(reason)[0] == expected


def test_classify_duplicate_numbers() -> None:
    assert inference.classify_close_reason("Dupe of #123")[1] == 123
    assert inference.classify_close_reason("merged into 10959, see there")[1] == 10959
    assert inference.classify_close_reason("dupe of bug#6131")[1] is None
    assert inference.classify_close_reason("dupe")[1] is None
    # The number right after the phrase, not the first anywhere, and never a version
    assert inference.classify_close_reason("1. dupe of 14679 2. see there")[1] == 14679
    assert inference.classify_close_reason("Combined 6048 & 6007 into 6114")[1] == 6114
    assert inference.classify_close_reason("Dupe of a known bug since the 1.20 upgrade")[1] is None
    assert inference.classify_close_reason("dupe of 1.20 behaviour")[1] is None
    assert inference.classify_close_reason("Duplicate of #8411.")[1] == 8411
    assert inference.classify_close_reason("dup of 137") == ("duplicate", 137)
    assert inference.classify_close_reason("dub of 137") == ("duplicate", 137)
    # A few words between the phrase and the number
    assert inference.classify_close_reason("Same issue as described in #9092")[1] == 9092
    assert inference.classify_close_reason("dupe/more info in 13976")[1] == 13976
    assert inference.classify_close_reason("Already Reported, see #3443 and #8648.")[1] == 3443
    assert inference.classify_close_reason("dupe of a fixed bug(5262), bows")[1] == 5262


def test_estimate_creation_times() -> None:
    ids = [1, 2, 3, 4, 5, 6]
    bounds = [None, 200.0, None, 150.0, 400.0, None]
    est = inference.estimate_creation_times(ids, bounds)
    # suffix minimum: entries 1-4 bounded by 150, 5 by 400; 6, after the last bound,
    # takes the time of 5
    assert est[3] == 150.0 and est[4] == 400.0 and est[5] == 400.0
    assert est[0] == 150.0 and est[1] == 150.0 and est[2] == 150.0
    ids = [10, 20, 30]
    est = inference.estimate_creation_times(ids, [100.0, None, 300.0])
    assert est == [100.0, 200.0, 300.0]
    assert all(a <= b for a, b in zip(est, est[1:]))
    assert inference.estimate_creation_times([1, 2], [None, None]) == [None, None]


def test_snowflake_round_trip() -> None:
    assert abs(inference.snowflake_time(sf(T0)) - T0) < 0.002
