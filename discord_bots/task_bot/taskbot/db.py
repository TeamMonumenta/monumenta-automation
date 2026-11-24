"""SQLite schema and migrations.

The schema version lives in PRAGMA user_version. Each entry in _MIGRATIONS
moves the database from version i to i+1 and runs in one transaction, so a
crash mid-migration leaves the previous version intact. See SCHEMA.md for
what each table is for.

The bot never creates its database. Make one with the legacy import (at
cutover), or an empty one for a new instance or a test guild:

    python -m taskbot.db init <tasks.db>
"""

import argparse
import os
import sqlite3
import sys
from typing import Callable, Optional

_SCHEMA = """
CREATE TABLE meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Labels differ between instances and change with addlabel/dellabel. Order matters:
-- prefix matching walks them by position. (Priorities and complexities are fixed,
-- in taskbot/vocab.py.)
CREATE TABLE labels (
    name     TEXT PRIMARY KEY,
    position INTEGER NOT NULL,
    -- 0 once removed with `dellabel`, or for labels only found on legacy entries.
    -- Inactive labels are not offered or matched, but old entries keep rendering them.
    active   INTEGER NOT NULL DEFAULT 1
);

-- People are Discord users (integer ids) or Minecraft players (uuids), each in their own
-- columns. Every question of "is this the same person" goes through taskbot/identity.py,
-- so a future Discord <-> Minecraft account link only has to answer that one question.
CREATE TABLE entries (
    id                   INTEGER PRIMARY KEY,   -- the public number, never reused
    description          TEXT NOT NULL,
    author_id            INTEGER NOT NULL DEFAULT 0,   -- 0: unknown, or an in-game reporter
    author_mc_uuid       TEXT,                  -- the Minecraft player who filed it in game
    priority             TEXT NOT NULL,
    complexity           TEXT NOT NULL,
    status               TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed')),
    -- NULL while open
    resolution           TEXT CHECK (resolution IN ('fixed', 'rejected', 'duplicate')),
    close_reason         TEXT,                  -- shown after "Closed:"; NULL while open
    closed_at            INTEGER,               -- NULL while open
    closed_by            INTEGER,
    closed_by_mc_uuid    TEXT,
    duplicate_of         INTEGER,
    assignee_id          INTEGER,
    -- Redaction is separate from the resolution, so redacting a fixed entry
    -- doesn't erase the fix from close statistics.
    -- When and by whom is in the event log.
    redacted             INTEGER NOT NULL DEFAULT 0,
    message_id           INTEGER,               -- tracking channel message; NULL when there is none
    pending_notification INTEGER NOT NULL DEFAULT 0,
    -- The best known time: exact for nearly every entry, estimated for imported ones the
    -- old feed channel doesn't cover (see README). NULL only if nothing could be estimated.
    created_at           INTEGER,
    updated_at           INTEGER,
    -- Non-zero while the tracking channel message needs to be sent or edited. A
    -- counter, so a change made while a publish is in flight isn't lost: the
    -- publisher only resets it if it still holds the value read before rendering.
    channel_dirty        INTEGER NOT NULL DEFAULT 0,
    -- when reaction counts were last read from the tracking message
    reactions_checked_at INTEGER
);

CREATE INDEX idx_entries_status ON entries(status);
CREATE INDEX idx_entries_author ON entries(author_id);
CREATE INDEX idx_entries_author_mc ON entries(author_mc_uuid) WHERE author_mc_uuid IS NOT NULL;
CREATE INDEX idx_entries_assignee ON entries(assignee_id) WHERE assignee_id IS NOT NULL;
CREATE INDEX idx_entries_message ON entries(message_id) WHERE message_id IS NOT NULL;
CREATE INDEX idx_entries_dirty ON entries(channel_dirty) WHERE channel_dirty > 0;
CREATE INDEX idx_entries_closed_at ON entries(closed_at);
CREATE INDEX idx_entries_created_at ON entries(created_at);
CREATE INDEX idx_entries_duplicate_of ON entries(duplicate_of) WHERE duplicate_of IS NOT NULL;

CREATE TABLE entry_labels (
    entry_id INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    label    TEXT NOT NULL,
    position INTEGER NOT NULL,
    PRIMARY KEY (entry_id, label)
);
CREATE INDEX idx_entry_labels_label ON entry_labels(label);

CREATE TABLE entry_images (
    entry_id             INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    position             INTEGER NOT NULL,
    url                  TEXT NOT NULL,    -- as Discord first gave it
    -- Parsed from the URL when it is a Discord attachment, which can be refreshed
    attachment_id        INTEGER,
    refreshed_url        TEXT,
    refreshed_expires_at INTEGER,
    PRIMARY KEY (entry_id, position)
);

-- Copies of entries' images saved under images/ next to the database, since Discord deletes
-- an attachment with its message and expires slash command attachments within a day. Keyed
-- by entry and URL, not by entry_images row, so a copy outlives redaction and image edits.
CREATE TABLE image_files (
    entry_id   INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    url        TEXT NOT NULL,      -- as in entry_images or redacted_content
    path       TEXT,               -- relative to images/; NULL until saved
    size       INTEGER,
    checked_at INTEGER NOT NULL,   -- when it was saved, or last tried
    missing    INTEGER NOT NULL DEFAULT 0,   -- 1: Discord no longer has it, so not tried again
    failures   INTEGER NOT NULL DEFAULT 0,   -- downloads that failed otherwise; retried ever slower
    message_id INTEGER,            -- the bot's own feed channel message holding it, if any
    PRIMARY KEY (entry_id, url)
);

-- The history, in id order. Only redaction (which blanks text) and purge (which deletes the
-- entry) change it. See SCHEMA.md for the kinds and their values.
CREATE TABLE events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id      INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    at            INTEGER,          -- NULL when unknown (old closes)
    actor_id      INTEGER,          -- NULL when unknown, or an in-game actor
    actor_mc_uuid TEXT,
    kind          TEXT NOT NULL,
    old_value     TEXT,
    new_value     TEXT,
    reason        TEXT,
    source        TEXT NOT NULL CHECK (source IN ('discord', 'api', 'legacy', 'backfill', 'system')),
    -- Discord message id of the command, or other provenance
    source_ref    TEXT
);
CREATE INDEX idx_events_entry ON events(entry_id, id);
CREATE INDEX idx_events_at ON events(at);
CREATE INDEX idx_events_kind_at ON events(kind, at);
CREATE INDEX idx_events_actor ON events(actor_id, at);
CREATE INDEX idx_events_actor_mc ON events(actor_mc_uuid, at) WHERE actor_mc_uuid IS NOT NULL;

CREATE TABLE reactions (
    entry_id   INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    emoji      TEXT NOT NULL,
    count      INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    PRIMARY KEY (entry_id, emoji)
);

CREATE TABLE notifications_disabled (
    user_id INTEGER PRIMARY KEY
);

-- Last known name of each Minecraft player seen, for display
CREATE TABLE players (
    uuid       TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    updated_at INTEGER NOT NULL
);

-- Per-player preferences (the in-game counterpart of notifications_disabled)
CREATE TABLE player_settings (
    uuid          TEXT PRIMARY KEY,
    notifications INTEGER NOT NULL DEFAULT 1
);

-- Update notices waiting for a player to join, delivered by the game plugin
CREATE TABLE player_notices (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid         TEXT NOT NULL,
    entry_id     INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    text         TEXT NOT NULL,
    created_at   INTEGER NOT NULL,
    delivered_at INTEGER
);
CREATE INDEX idx_player_notices_pending ON player_notices(uuid) WHERE delivered_at IS NULL;

-- Extra data attached to an entry and kept out of the public channel: where an in-game
-- report was made, later player state and so on. Free-form named sections of JSON, so
-- new kinds of context need no schema change.
CREATE TABLE entry_context (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id   INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    section    TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    source     TEXT NOT NULL,          -- who supplied it, e.g. 'service:shards-play'
    data       TEXT NOT NULL           -- a JSON object
);
CREATE INDEX idx_entry_context_entry ON entry_context(entry_id, section);

-- What `redact` hid: the entry's text, images and the text in its history, as JSON.
-- Readable only by the team (privilege 2), never shown in a channel; `purge` removes
-- it with the entry.
CREATE TABLE redacted_content (
    entry_id    INTEGER PRIMARY KEY REFERENCES entries(id) ON DELETE CASCADE,
    redacted_at INTEGER NOT NULL,
    redacted_by INTEGER,
    data        TEXT NOT NULL
);

-- Only hashes are stored. Service tokens (for other programs, such as the game plugin)
-- have `service` set and discord_id 0, and are long-lived.
CREATE TABLE api_tokens (
    token_hash    TEXT PRIMARY KEY,
    discord_id    INTEGER NOT NULL,
    scope         TEXT NOT NULL DEFAULT 'write' CHECK (scope IN ('read', 'write')),
    created_at    INTEGER NOT NULL,
    expires_at    INTEGER NOT NULL,
    service       TEXT,
    max_privilege INTEGER,          -- service tokens: the most privilege they may grant
    last_used_at  INTEGER
);
CREATE INDEX idx_api_tokens_discord ON api_tokens(discord_id);
"""


def _split_sql(script: str) -> list[str]:
    """Split a schema script into statements. The schema has no semicolons or `--` in strings."""
    lines = [line.split("--", 1)[0] for line in script.splitlines()]
    return [s.strip() for s in "\n".join(lines).split(";") if s.strip()]


def _create(conn: sqlite3.Connection) -> None:
    # Statement by statement: executescript() would commit the migration's transaction.
    for stmt in _split_sql(_SCHEMA):
        conn.execute(stmt)


# Each entry moves the database from version i to i+1; the first creates it.
_MIGRATIONS: list[Callable[[sqlite3.Connection], None]] = [
    _create,
]

SCHEMA_VERSION = len(_MIGRATIONS)


def connect(path: str) -> sqlite3.Connection:
    """Open (creating if needed) and migrate the database at path."""
    # The bot uses it from the event loop's thread only; the taskctl tests serve the API
    # from another thread
    conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    # Redaction must not leave the removed text in free pages
    conn.execute("PRAGMA secure_delete=ON")
    migrate(conn)
    return conn


def migrate(conn: sqlite3.Connection) -> None:
    version = int(conn.execute("PRAGMA user_version").fetchone()[0])
    if version > SCHEMA_VERSION:
        raise RuntimeError(
            f"Database schema version {version} is newer than this code ({SCHEMA_VERSION})")
    while version < SCHEMA_VERSION:
        conn.execute("BEGIN IMMEDIATE")
        try:
            _MIGRATIONS[version](conn)
            version += 1
            conn.execute(f"PRAGMA user_version = {version}")
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise


def init(path: str) -> None:
    """Create an empty tracker: the schema, the `misc` label, numbering from #1."""
    conn = connect(path)
    try:
        conn.execute("INSERT INTO labels(name, position) VALUES ('misc', 0)")
        conn.execute("INSERT INTO meta(key, value) VALUES ('next_index', '1')")
    finally:
        conn.close()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m taskbot.db")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_init = sub.add_parser("init", help="create an empty database")
    p_init.add_argument("db")
    args = parser.parse_args(argv)
    if os.path.exists(args.db):
        print(f"{args.db} already exists", file=sys.stderr)
        return 1
    init(args.db)
    print(f"Created {args.db}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
