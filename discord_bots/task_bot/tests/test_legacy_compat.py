"""Differential tests: the original bot's code vs the new code, on production data.

The original task_database.py is loaded from git (LEGACY_COMMIT) with Discord
and config stubbed out, fed the production JSON, and asked to render every
entry, run searches and print stats. The new code, fed the same data through
the legacy importer, must produce identical text. Priorities and complexities are now
the same fixed lists for every instance (taskbot/vocab.py), so the old bot is given
those lists too; that change (the suggestion bot's row order) is deliberate, as is
the line listing an entry's duplicates.

Needs the production snapshot: set TASKBOT_LEGACY_SNAPSHOT to a directory with
bugs/bug_reports.json and suggestions/suggestions.json (default
~/NO_SNAPSHOT/taskbot-cutover-2026-11-22, the final JSON at launch). Skipped when it or git is unavailable.
"""

import asyncio
import importlib.util
import json
import os
import re
import subprocess
import sys
import types
from typing import Any, Optional

import pytest

from conftest import FakeResponder, Sent, make_config
from taskbot.commands import CommandHandler
from taskbot.formatting import format_entry, format_stats
from taskbot.legacy import import_legacy
from taskbot.service import TaskService
from taskbot.store import EntryQuery, TaskStore
from taskbot.vocab import COMPLEXITIES, PRIORITIES

LEGACY_COMMIT = "ea622b8b"
LEGACY_DIR = "discord_bots/task_bot"
SNAPSHOT = os.environ.get("TASKBOT_LEGACY_SNAPSHOT", os.path.expanduser("~/NO_SNAPSHOT/taskbot-cutover-2026-11-22"))
INSTANCES = [
    ("bug", "bugs/bug_reports.json", "~bug"),
    ("suggestion", "suggestions/suggestions.json", "~suggestion"),
]

SEARCHES = {
    "bug": ["quest", "plugin high", "boss,mob", "hard", "moderate easy", "critical", "zero",
            "assigned", "item medium 5", "class hi", "build low hard", "misc n/a", "cmd unknown"],
    "suggestion": ["item", "plugin high", "class", "easy", "zero", "assigned", "misc low",
                   "boss medium hard"],
}
DSEARCHES = ["arrow", "the boss", "Fix", "crash, server", "ä"]


def _repo_root() -> Optional[str]:
    try:
        return subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                              check=True, cwd=os.path.dirname(__file__)).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _load_legacy_module(tmp_dir: str, single: str, prefix: str) -> Any:
    root = _repo_root()
    if root is None:
        pytest.skip("git not available")
    for name in ("task_database.py", "interactive_search.py", "common.py", "task_kanboard.py"):
        try:
            src = subprocess.run(["git", "show", f"{LEGACY_COMMIT}:{LEGACY_DIR}/{name}"], cwd=root,
                                 capture_output=True, check=True).stdout
        except subprocess.CalledProcessError:
            pytest.skip(f"legacy source {name} not in git")
        with open(os.path.join(tmp_dir, name), "wb") as f:
            f.write(src)

    cfg = types.ModuleType("config")
    cfg.CONFIG_DIR = tmp_dir  # type: ignore[attr-defined]
    cfg.DATABASE_PATH = "x.json"  # type: ignore[attr-defined]
    cfg.CHANNEL_ID = 30  # type: ignore[attr-defined]
    cfg.GUILD_ID = 10  # type: ignore[attr-defined]
    cfg.PREFIX = prefix  # type: ignore[attr-defined]
    cfg.DESCRIPTOR_SHORT = single[:3]  # type: ignore[attr-defined]
    cfg.DESCRIPTOR_SINGLE = single  # type: ignore[attr-defined]
    cfg.DESCRIPTOR_PROPER = single.capitalize()  # type: ignore[attr-defined]
    cfg.DESCRIPTOR_PLURAL = single + "s"  # type: ignore[attr-defined]
    cfg.USER_PRIVILEGES = {}  # type: ignore[attr-defined]
    cfg.GROUP_PRIVILEGES = {}  # type: ignore[attr-defined]
    cfg.REACTIONS = []  # type: ignore[attr-defined]
    saved = {k: sys.modules.get(k) for k in ("config", "kanboard", "common", "interactive_search",
                                             "task_kanboard")}
    sys.modules["config"] = cfg
    kanboard = types.ModuleType("kanboard")
    kanboard.Client = object  # type: ignore[attr-defined]
    sys.modules["kanboard"] = kanboard
    sys.path.insert(0, tmp_dir)
    try:
        spec = importlib.util.spec_from_file_location(f"legacy_task_database_{single}",
                                                      os.path.join(tmp_dir, "task_database.py"))
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(tmp_dir)
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return module


class _User:
    def __init__(self, uid: int, name: str):
        self.id = uid
        self.display_name = name
        self.mention = f"<@{uid}>"


def _names(data: dict[str, Any]) -> dict[int, str]:
    """Deterministic fake names for most users; every 7th user is 'unknown' to Discord."""
    ids = sorted({int(e["author"]) for e in data["entries"].values()}
                 | {int(e["assignee"]) for e in data["entries"].values() if e.get("assignee")})
    return {uid: f"User{i}" for i, uid in enumerate(ids) if i % 7 != 3 and uid != 0}


class _Capture:
    def __init__(self) -> None:
        self.sent: list[str] = []

    async def send(self, text: str, embed: Any = None, ephemeral: bool = False) -> None:  # pylint: disable=unused-argument
        self.sent.append(text)


def _legacy_db(module: Any, data: dict[str, Any], names: dict[int, str]) -> Any:
    db = object.__new__(module.TaskDatabase)
    db._entries = data["entries"]  # pylint: disable=protected-access
    db._labels = data["labels"]  # pylint: disable=protected-access
    db._priorities = list(PRIORITIES)  # pylint: disable=protected-access
    db._complexities = dict(COMPLEXITIES)  # pylint: disable=protected-access
    db._stopping = False  # pylint: disable=protected-access
    db._bot = types.SimpleNamespace(  # pylint: disable=protected-access
        get_user=lambda uid: _User(uid, names[uid]) if uid in names else None)
    db._channel = None  # pylint: disable=protected-access
    return db


@pytest.fixture(scope="module", params=INSTANCES, ids=[i[0] for i in INSTANCES])
def pair(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory) -> Any:
    single, rel, prefix = request.param
    path = os.path.join(SNAPSHOT, rel)
    if not os.path.exists(path):
        pytest.skip(f"production snapshot not found at {path}")
    tmp = str(tmp_path_factory.mktemp(single))
    module = _load_legacy_module(tmp, single, prefix)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    names = _names(data)

    store = TaskStore.open(os.path.join(tmp, "tasks.db"))
    with open(path, encoding="utf-8") as f:
        import_legacy(store, json.load(f))
    config = make_config()
    config.prefix = prefix
    config.descriptor_short = single[:3]
    config.descriptor_single = single
    config.descriptor_proper = single.capitalize()
    config.descriptor_plural = single + "s"
    service = TaskService(store, config)

    class Port:
        def user_name(self, uid: int) -> Optional[str]:
            return names.get(uid)

        async def refresh_images(self, images: Any) -> None:
            pass

    handler = CommandHandler(service, Port())  # type: ignore[arg-type]
    return single, _legacy_db(module, data, names), data, store, handler, names


def test_every_entry_renders_identically(pair: Any) -> None:
    single, old, data, store, handler, names = pair
    entries = {e.id: e for e in store.all_entries()}
    mismatches: list[str] = []
    for key, raw in data["entries"].items():
        for kwargs in ({}, {"mention_assigned": True}, {"include_link": True}):
            if kwargs.get("include_link") and "message_id" not in raw:
                continue
            expected, _ = asyncio.run(old.format_entry(key, raw, include_reactions=False, **kwargs))
            got = format_entry(entries[int(key)], handler.config, names.get, **kwargs)
            if len(expected) <= 2000 and got != expected:
                mismatches.append(f"#{key} {kwargs}:\n{expected!r}\n{got!r}")
    assert not mismatches, f"{len(mismatches)} {single} renderings differ, first:\n" + mismatches[0]


def test_searches_match(pair: Any) -> None:
    single, old, _, _, handler, _ = pair
    for query in SEARCHES[single]:
        exp_entries, exp_labels, exp_prios, exp_comps, exp_max = asyncio.run(old.search_helper(query, 10))
        spec = handler.search_helper(query, 10)
        assert [int(k) for k, _ in old.sort_entries_by_priority(exp_entries)] == \
            [e.id for e in handler_sort(spec.entries)], query
        assert (spec.labels, spec.priorities, spec.complexities, spec.max_count) == \
            (exp_labels, exp_prios, exp_comps, exp_max), query


def handler_sort(entries: list[Any]) -> list[Any]:
    from taskbot.formatting import sort_by_priority
    return sort_by_priority(entries)


def test_description_searches_match(pair: Any) -> None:
    _, old, _, _, handler, _ = pair
    for query in DSEARCHES:
        exp, exp_limit = asyncio.run(old.dsearch_internal(query, 15))
        got, limit = handler.dsearch_internal(query, 15)
        assert [int(k) for k, _ in exp] == [e.id for e in got], query
        assert limit == exp_limit


def test_search_result_printing_matches(pair: Any) -> None:
    """print_search_results: limit message, priority sort, links, order."""
    single, old, _, _, handler, _ = pair
    query = SEARCHES[single][0]
    exp_entries, *_ = asyncio.run(old.search_helper(query, 10))
    capture = _Capture()
    asyncio.run(old.print_search_results(capture, exp_entries, limit=10, include_reactions=False,
                                         include_link=True))
    log: list[Sent] = []
    spec = handler.search_helper(query, 10)
    asyncio.run(handler.print_search_results(FakeResponder(log), spec.entries, limit=10,
                                             include_reactions=False, include_link=True))
    # The one deliberate addition: originals list their duplicates on a line of their own
    got = [re.sub(r"\n`Duplicates: [#0-9, ]+`", "", s.text) for s in log]
    assert got == capture.sent


def test_stats_match(pair: Any) -> None:
    single, old, _, store, _, _ = pair
    capture = _Capture()

    async def reply(_message: Any, text: str) -> None:
        capture.sent.append(text)
    old.reply = reply
    asyncio.run(old.cmd_stats(None, ""))
    open_entries = store.query(EntryQuery(status="open"))
    got = format_stats(single, open_entries, store.count(EntryQuery(status="closed")))
    assert got == capture.sent[0]
