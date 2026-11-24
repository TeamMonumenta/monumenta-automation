"""taskbot.db: version 1 stays as production has it, and migrations keep existing data."""
# pyright: reportPrivateUsage=false
# pylint: disable=protected-access

import hashlib
import os
import sqlite3
from typing import Any

import pytest

from taskbot import db
from taskbot.store import TaskStore

# The statements of _SCHEMA_V1 (comments and spacing aside) as the production databases
# were created at launch. Comments may change; the statements may not.
V1_SHA256 = "a2ec852faf8ec94e17cfe36cc83d92307fdd5ac518ddbd6c6b504fe71fc2208c"


def _v1_digest() -> str:
    statements = (" ".join(s.split()) for s in db._split_sql(db._SCHEMA_V1))
    return hashlib.sha256("\n".join(statements).encode()).hexdigest()


def test_version_1_is_frozen() -> None:
    assert _v1_digest() == V1_SHA256, (
        "_SCHEMA_V1 changed, but databases at version 1 already exist and won't see it. "
        "Put the change in a new migration at the end of _MIGRATIONS (see taskbot/db.py).")


def _make_v1(path: str) -> None:
    """A version 1 database with one entry and something in each table that points at it,
    written with plain SQL so it stays version 1 whatever the current code is."""
    conn = sqlite3.connect(path, isolation_level=None)
    db._create_v1(conn)
    conn.executescript("""
        INSERT INTO meta(key, value) VALUES ('next_index', '2');
        INSERT INTO labels(name, position) VALUES ('misc', 0);
        INSERT INTO entries(id, description, author_id, priority, complexity, status, resolution,
                            close_reason, closed_at, message_id, created_at)
            VALUES (1, 'The boss falls through the floor', 42, 'High', 'Low', 'closed', 'fixed',
                    'Fixed', 200, 999, 100);
        INSERT INTO entry_labels(entry_id, label, position) VALUES (1, 'misc', 0);
        INSERT INTO entry_images(entry_id, position, url) VALUES (1, 0, 'https://cdn.example/a.png');
        INSERT INTO events(entry_id, at, actor_id, kind, source) VALUES (1, 100, 42, 'created', 'discord');
        INSERT INTO events(entry_id, at, actor_id, kind, new_value, reason, source)
            VALUES (1, 200, 7, 'closed', 'fixed', 'Fixed', 'discord');
        INSERT INTO reactions(entry_id, emoji, count, updated_at) VALUES (1, '👍', 3, 100);
        INSERT INTO image_files(entry_id, url, path, size, checked_at)
            VALUES (1, 'https://cdn.example/a.png', '1/a.png', 10, 100);
        INSERT INTO players(uuid, name, updated_at) VALUES ('0f-uuid', 'Steve', 100);
        INSERT INTO player_notices(uuid, entry_id, text, created_at) VALUES ('0f-uuid', 1, 'fixed', 200);
        INSERT INTO entry_context(entry_id, section, created_at, source, data)
            VALUES (1, 'location', 100, 'service:shards-play', '{"x": 1}');
        INSERT INTO redacted_content(entry_id, redacted_at, redacted_by, data)
            VALUES (1, 0, NULL, '{"images": ["https://cdn.example/old.png"]}');
        PRAGMA user_version = 1;
    """)
    conn.close()


# Every table whose rows point at an entry
CHILD_TABLES = ("entry_labels", "entry_images", "image_files", "events", "reactions",
                "player_notices", "entry_context", "redacted_content")


def _child_rows(conn: sqlite3.Connection) -> dict[str, int]:
    return {t: int(conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
            for t in CHILD_TABLES}


def test_the_fixture_covers_every_table_that_points_at_entries(tmp_path: Any) -> None:
    conn = db.connect(os.path.join(tmp_path, "tasks.db"))
    try:
        tables = [str(r[0]) for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
        pointing = {t for t in tables
                    if any(fk[2] == "entries" for fk in conn.execute(f"PRAGMA foreign_key_list({t})"))}
    finally:
        conn.close()
    assert pointing == set(CHILD_TABLES)


def test_migrations_apply_to_a_populated_version_1_database(tmp_path: Any) -> None:
    path = os.path.join(tmp_path, "tasks.db")
    _make_v1(path)
    store = TaskStore.open(path)
    try:
        assert int(store.conn.execute("PRAGMA user_version").fetchone()[0]) == db.SCHEMA_VERSION
        assert store.conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        entry = store.get(1)
        assert entry is not None and entry.description == "The boss falls through the floor"
        assert entry.labels == ["misc"] and [im.url for im in entry.images] == ["https://cdn.example/a.png"]
        assert [ev.kind for ev in store.events_for(1)] == ["created", "closed"]
        assert store.next_index() == 2
        assert store.redacted_content(1) == {"redacted_at": 0, "redacted_by": None,
                                             "images": ["https://cdn.example/old.png"]}
        assert _child_rows(store.conn) == {**dict.fromkeys(CHILD_TABLES, 1), "events": 2}
    finally:
        store.close()


def _rebuild_entries(conn: sqlite3.Connection) -> None:
    """The usual way to change a table SQLite can't ALTER: copy it and swap it in."""
    sql = str(conn.execute("SELECT sql FROM sqlite_master WHERE name = 'entries'").fetchone()[0])
    conn.execute(sql.replace("CREATE TABLE entries", "CREATE TABLE entries_new", 1))
    conn.execute("INSERT INTO entries_new SELECT * FROM entries")
    indexes = [str(r[0]) for r in conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'index' AND tbl_name = 'entries' AND sql IS NOT NULL")]
    conn.execute("DROP TABLE entries")
    conn.execute("ALTER TABLE entries_new RENAME TO entries")
    for sql in indexes:   # dropping the table dropped them
        conn.execute(sql)


def _indexes(conn: sqlite3.Connection) -> list[str]:
    return sorted(str(r[0]) for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'"))


def test_a_table_rebuild_keeps_the_rows_that_point_at_it(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    path = os.path.join(tmp_path, "tasks.db")
    _make_v1(path)
    before = sqlite3.connect(path)
    indexes = _indexes(before)
    before.close()
    monkeypatch.setattr(db, "_MIGRATIONS", [*db._MIGRATIONS, _rebuild_entries])
    monkeypatch.setattr(db, "SCHEMA_VERSION", db.SCHEMA_VERSION + 1)
    conn = db.connect(path)
    try:
        assert int(conn.execute("PRAGMA user_version").fetchone()[0]) == db.SCHEMA_VERSION
        assert _indexes(conn) == indexes and any(i.startswith("idx_entries_") for i in indexes)
        assert _child_rows(conn) == {**dict.fromkeys(CHILD_TABLES, 1), "events": 2}
        # and the cascades work again afterwards
        conn.execute("DELETE FROM entries WHERE id = 1")
        assert _child_rows(conn) == dict.fromkeys(CHILD_TABLES, 0)
    finally:
        conn.close()


def test_a_migration_that_breaks_foreign_keys_is_rolled_back(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    def drop_entries(conn: sqlite3.Connection) -> None:
        conn.execute("DROP TABLE entries")
        conn.execute("CREATE TABLE entries (id INTEGER PRIMARY KEY)")

    path = os.path.join(tmp_path, "tasks.db")
    _make_v1(path)
    monkeypatch.setattr(db, "_MIGRATIONS", [*db._MIGRATIONS, drop_entries])
    monkeypatch.setattr(db, "SCHEMA_VERSION", db.SCHEMA_VERSION + 1)
    with pytest.raises(RuntimeError, match="broke foreign keys"):
        db.connect(path)
    monkeypatch.undo()
    store = TaskStore.open(path)
    try:
        assert int(store.conn.execute("PRAGMA user_version").fetchone()[0]) == 1
        entry = store.get(1)
        assert entry is not None and entry.description == "The boss falls through the floor"
    finally:
        store.close()


def test_refuses_a_database_newer_than_the_code(tmp_path: Any) -> None:
    path = os.path.join(tmp_path, "tasks.db")
    _make_v1(path)
    conn = sqlite3.connect(path)
    conn.execute(f"PRAGMA user_version = {db.SCHEMA_VERSION + 1}")
    conn.close()
    with pytest.raises(RuntimeError, match="newer than this code"):
        db.connect(path)


def test_a_migration_that_commits_part_way_is_reported(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    def with_executescript(conn: sqlite3.Connection) -> None:
        conn.executescript("CREATE TABLE extra (x INTEGER);")   # commits the transaction

    path = os.path.join(tmp_path, "tasks.db")
    _make_v1(path)
    monkeypatch.setattr(db, "_MIGRATIONS", [*db._MIGRATIONS, with_executescript])
    monkeypatch.setattr(db, "SCHEMA_VERSION", db.SCHEMA_VERSION + 1)
    with pytest.raises(RuntimeError, match="committed part way"):
        db.connect(path)
    conn = sqlite3.connect(path)
    assert int(conn.execute("PRAGMA user_version").fetchone()[0]) == 1
    conn.close()


def test_a_migration_that_commits_part_way_then_fails_is_reported(tmp_path: Any,
                                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    def half(conn: sqlite3.Connection) -> None:
        conn.executescript("CREATE TABLE extra (x INTEGER);")
        conn.execute("SELECT * FROM no_such_table")

    path = os.path.join(tmp_path, "tasks.db")
    _make_v1(path)
    monkeypatch.setattr(db, "_MIGRATIONS", [*db._MIGRATIONS, half])
    monkeypatch.setattr(db, "SCHEMA_VERSION", db.SCHEMA_VERSION + 1)
    with pytest.raises(RuntimeError, match="committed part way") as raised:
        db.connect(path)
    assert isinstance(raised.value.__cause__, sqlite3.OperationalError)


def test_migrate_refuses_foreign_keys_on(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    path = os.path.join(tmp_path, "tasks.db")
    _make_v1(path)
    monkeypatch.setattr(db, "_MIGRATIONS", [*db._MIGRATIONS, _rebuild_entries])
    monkeypatch.setattr(db, "SCHEMA_VERSION", db.SCHEMA_VERSION + 1)
    conn = sqlite3.connect(path, isolation_level=None)
    conn.execute("PRAGMA foreign_keys=ON")
    with pytest.raises(RuntimeError, match="foreign keys off"):
        db.migrate(conn)
    assert _child_rows(conn) == {**dict.fromkeys(CHILD_TABLES, 1), "events": 2}
    conn.close()
