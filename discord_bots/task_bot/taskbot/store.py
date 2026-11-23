"""All SQL lives here. No permission checks and no Discord.

TaskStore methods are synchronous and fast (the whole database is tens of
thousands of small rows), so the bot and the API call them directly from the
event loop, as the exception logger does.
"""

import contextlib
import json
import re
import sqlite3
import time
from collections.abc import Generator, Sequence
from dataclasses import dataclass, field
from typing import Any, Optional

from . import db
from .models import Entry, Event, Image, ImageFile, Reaction
from .vocab import PRIORITY_RANK, UNKNOWN_RANK

_RANK_SQL = "CASE " + " ".join(
    f"WHEN e.priority = '{p}' AND e.complexity = '{c}' THEN {r}"
    for (p, c), r in PRIORITY_RANK.items()
) + f" ELSE {UNKNOWN_RANK} END"

_ATTACHMENT_RE = re.compile(r"/attachments/(\d+)/(\d+)/")
_EXPIRY_RE = re.compile(r"[?&]ex=([0-9a-fA-F]+)")

ENTRY_SORTS = ("priority", "id", "created", "updated", "closed")


def parse_attachment_id(url: str) -> Optional[int]:
    """The attachment id of a Discord CDN attachment URL, else None."""
    m = _ATTACHMENT_RE.search(url)
    if not m:
        return None
    return int(m.group(2))


def url_expiry(url: str) -> Optional[int]:
    """Expiry (epoch seconds) of a signed Discord CDN URL, None when unsigned."""
    m = _EXPIRY_RE.search(url)
    return int(m.group(1), 16) if m else None


# redacted_at of images the legacy import hid (entries redacted by editing the description)
LEGACY_REDACTION = 0


def make_image(url: str) -> Image:
    return Image(url=url, attachment_id=parse_attachment_id(url))


def _py_lower(value: Optional[str]) -> Optional[str]:
    # SQLite's lower() only folds ASCII; the old bot used str.lower().
    return value.lower() if value is not None else None


@dataclass
class TokenInfo:
    discord_id: int                 # 0 for service tokens
    scope: str                      # 'read' | 'write'
    service: Optional[str]          # set for service tokens
    max_privilege: Optional[int]    # service tokens: the most privilege they may assert
    created_at: int
    expires_at: int
    last_used_at: Optional[int]
    token_hash: str


@dataclass
class EntryQuery:
    status: str = "open"                       # open | closed | all
    labels: list[str] = field(default_factory=list[str])            # all must match
    priorities: list[str] = field(default_factory=list[str])        # any
    complexities: list[str] = field(default_factory=list[str])      # any
    resolutions: list[str] = field(default_factory=list[str])       # any
    assignee: Optional[str] = None             # None: no filter, 'any', 'none', or an id
    author_id: Optional[int] = None
    author_mc_uuid: Optional[str] = None
    closed_by: Optional[int] = None
    terms: list[str] = field(default_factory=list[str])             # all must be substrings
    created_after: Optional[int] = None
    created_before: Optional[int] = None
    closed_after: Optional[int] = None
    closed_before: Optional[int] = None
    reaction: Optional[str] = None             # only entries with this reaction, most first
    sort: str = "id"
    descending: bool = False
    limit: Optional[int] = None
    offset: int = 0


@dataclass
class AuthorCount:
    author_id: int                  # 0 for an in-game author
    author_mc_uuid: Optional[str]
    total: int
    open: int


@dataclass
class StatRow:
    """What the statistics and charts need of one entry."""
    id: int
    created_at: Optional[int]
    status: str
    closed_at: Optional[int]
    resolution: Optional[str]
    priority: str
    complexity: str
    closed_by: Optional[int]
    closed_by_mc_uuid: Optional[str]
    author_id: int
    author_mc_uuid: Optional[str]


@dataclass
class Notice:
    id: int
    uuid: str
    entry_id: int
    text: str
    created_at: int


@dataclass
class ContextSection:
    id: int
    entry_id: int
    section: str
    created_at: int
    source: str
    size: int     # bytes of JSON
    data: Any


class PlayerStore:
    """Minecraft players (names, settings, pending notices) and the tables beside an entry
    that only some views read: context and redacted content. Mixed into TaskStore."""

    conn: sqlite3.Connection

    def remember_player(self, uuid: str, name: str, now: int) -> None:
        self.conn.execute(
            "INSERT INTO players(uuid, name, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(uuid) DO UPDATE SET name = excluded.name, updated_at = excluded.updated_at "
            "WHERE players.name != excluded.name OR players.updated_at < excluded.updated_at - 3600",
            (uuid, name, now))

    def player_name(self, uuid: str) -> Optional[str]:
        row = self.conn.execute("SELECT name FROM players WHERE uuid = ?", (uuid,)).fetchone()
        return None if row is None else str(row[0])

    def find_player(self, name_or_uuid: str) -> Optional[tuple[str, str]]:
        """(uuid, name) by uuid or exact (case-insensitive) name of a player seen before."""
        row = self.conn.execute(
            "SELECT uuid, name FROM players WHERE uuid = ? OR lower(name) = lower(?) "
            "ORDER BY updated_at DESC LIMIT 1", (name_or_uuid, name_or_uuid)).fetchone()
        return None if row is None else (str(row[0]), str(row[1]))

    def player_notifications(self, uuid: str) -> bool:
        row = self.conn.execute(
            "SELECT notifications FROM player_settings WHERE uuid = ?", (uuid,)).fetchone()
        return True if row is None else bool(row[0])

    def set_player_notifications(self, uuid: str, enabled: bool) -> None:
        self.conn.execute(
            "INSERT INTO player_settings(uuid, notifications) VALUES (?, ?) "
            "ON CONFLICT(uuid) DO UPDATE SET notifications = excluded.notifications",
            (uuid, int(enabled)))

    def add_notice(self, uuid: str, entry_id: int, text: str, now: int) -> None:
        # One pending notice per entry is enough: replace an undelivered older one
        self.conn.execute("DELETE FROM player_notices WHERE uuid = ? AND entry_id = ? AND delivered_at IS NULL",
                          (uuid, entry_id))
        self.conn.execute("INSERT INTO player_notices(uuid, entry_id, text, created_at) VALUES (?,?,?,?)",
                          (uuid, entry_id, text, now))

    def clear_notices(self, entry_id: int) -> None:
        """Forget every notice about an entry (they quote its close reason)."""
        self.conn.execute("DELETE FROM player_notices WHERE entry_id = ?", (entry_id,))

    def pending_notices(self, uuid: str) -> list[Notice]:
        return [Notice(int(r[0]), str(r[1]), int(r[2]), str(r[3]), int(r[4])) for r in self.conn.execute(
            "SELECT id, uuid, entry_id, text, created_at FROM player_notices "
            "WHERE uuid = ? AND delivered_at IS NULL ORDER BY id", (uuid,))]

    # Context sections

    def add_context(self, entry_id: int, section: str, data: Any, source: str, now: int) -> int:
        cur = self.conn.execute(
            "INSERT INTO entry_context(entry_id, section, created_at, source, data) VALUES (?, ?, ?, ?, ?)",
            (entry_id, section, now, source, json_text(data)))
        return int(cur.lastrowid or 0)

    def context_for(self, entry_id: int, include_data: bool = True) -> list[ContextSection]:
        out: list[ContextSection] = []
        for r in self.conn.execute(
                "SELECT id, entry_id, section, created_at, source, data, length(CAST(data AS BLOB)) "
                "FROM entry_context WHERE entry_id = ? ORDER BY id", (entry_id,)):
            data: Any = json.loads(r[5]) if include_data else None
            out.append(ContextSection(int(r[0]), int(r[1]), str(r[2]), int(r[3]), str(r[4]),
                                      int(r[6]), data))
        return out

    def context_totals(self, entry_id: int) -> tuple[int, int]:
        """(sections, bytes of JSON) of context an entry already has."""
        row = self.conn.execute("SELECT COUNT(*), COALESCE(SUM(length(CAST(data AS BLOB))), 0) "
                                "FROM entry_context WHERE entry_id = ?",
                                (entry_id,)).fetchone()
        return int(row[0]), int(row[1])

    def save_redacted(self, entry_id: int, data: Any, at: int, by: Optional[int]) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO redacted_content(entry_id, redacted_at, redacted_by, data) "
            "VALUES (?, ?, ?, ?)", (entry_id, at, by, json_text(data)))

    def redacted_content(self, entry_id: int) -> Optional[dict[str, Any]]:
        """What `redact` hid, with `redacted_at` and `redacted_by`; None if nothing."""
        row = self.conn.execute("SELECT redacted_at, redacted_by, data FROM redacted_content "
                                "WHERE entry_id = ?", (entry_id,)).fetchone()
        if row is None:
            return None
        data: dict[str, Any] = json.loads(row[2])
        return {"redacted_at": int(row[0]), "redacted_by": row[1], **data}


class TaskStore(PlayerStore):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        conn.create_function("pylower", 1, _py_lower, deterministic=True)
        self._tx_depth = 0

    @classmethod
    def open(cls, path: str) -> "TaskStore":
        return cls(db.connect(path))

    def close(self) -> None:
        self.conn.close()

    @contextlib.contextmanager
    def transaction(self) -> Generator[None]:
        """Group writes atomically. Nested uses join the outer transaction."""
        if self._tx_depth == 0:
            self.conn.execute("BEGIN IMMEDIATE")
        self._tx_depth += 1
        try:
            yield
        except BaseException:
            self._tx_depth -= 1
            if self._tx_depth == 0:
                self.conn.execute("ROLLBACK")
            raise
        self._tx_depth -= 1
        if self._tx_depth == 0:
            self.conn.execute("COMMIT")

    # ------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------

    def dirty_value(self, entry_id: int) -> int:
        row = self.conn.execute("SELECT channel_dirty FROM entries WHERE id = ?", (entry_id,)).fetchone()
        return 0 if row is None else int(row[0])

    def clear_dirty(self, entry_id: int, seen: Optional[int] = None) -> bool:
        """Mark published. With `seen`, only if nothing changed since that value was read."""
        if seen is None:
            return self.conn.execute("UPDATE entries SET channel_dirty = 0 WHERE id = ?",
                                     (entry_id,)).rowcount > 0
        return self.conn.execute("UPDATE entries SET channel_dirty = 0 WHERE id = ? AND channel_dirty = ?",
                                 (entry_id, seen)).rowcount > 0

    def get_meta(self, key: str) -> Optional[str]:
        row = self.conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return None if row is None else str(row[0])

    def set_meta(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT INTO meta(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value))

    def next_index(self) -> int:
        return int(self.get_meta("next_index") or "1")

    def allocate_index(self) -> int:
        with self.transaction():
            index = self.next_index()
            self.set_meta("next_index", str(index + 1))
        return index

    def delete_entry(self, entry_id: int) -> None:
        """Remove an entry and everything attached to it (events, images, context, ...)."""
        self.conn.execute("UPDATE entries SET duplicate_of = NULL WHERE duplicate_of = ?", (entry_id,))
        self.conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))

    def is_empty(self) -> bool:
        return self.conn.execute("SELECT 1 FROM entries LIMIT 1").fetchone() is None \
            and self.get_meta("next_index") is None

    # ------------------------------------------------------------------
    # Vocabularies
    # ------------------------------------------------------------------

    def labels(self, include_inactive: bool = False) -> list[str]:
        sql = "SELECT name FROM labels"
        if not include_inactive:
            sql += " WHERE active = 1"
        return [str(r[0]) for r in self.conn.execute(sql + " ORDER BY position")]

    def add_label(self, name: str) -> None:
        """Append a label, or re-activate (and move to the end) a previously removed one."""
        with self.transaction():
            pos = int(self.conn.execute(
                "SELECT COALESCE(MAX(position), -1) + 1 FROM labels").fetchone()[0])
            self.conn.execute(
                "INSERT INTO labels(name, position, active) VALUES (?, ?, 1) "
                "ON CONFLICT(name) DO UPDATE SET active = 1, position = excluded.position",
                (name, pos))

    def add_inactive_label(self, name: str) -> None:
        pos = int(self.conn.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM labels").fetchone()[0])
        self.conn.execute(
            "INSERT OR IGNORE INTO labels(name, position, active) VALUES (?, ?, 0)", (name, pos))

    def deactivate_label(self, name: str) -> None:
        self.conn.execute("UPDATE labels SET active = 0 WHERE name = ?", (name,))

    def set_label_list(self, labels: Sequence[str]) -> None:
        """Replace the instance's labels (for a new database or an import)."""
        with self.transaction():
            self.conn.execute("DELETE FROM labels")
            self.conn.executemany("INSERT INTO labels(name, position) VALUES (?, ?)",
                                  [(n, i) for i, n in enumerate(labels)])

    # ------------------------------------------------------------------
    # Entries: reads
    # ------------------------------------------------------------------

    def get(self, entry_id: int) -> Optional[Entry]:
        if not 0 < entry_id < 2 ** 63:
            return None   # SQLite integers are 64 bits: a bigger number is no entry
        entries = self._load("WHERE e.id = ?", [entry_id])
        return entries[0] if entries else None

    def get_many(self, ids: Sequence[int]) -> list[Entry]:
        """Entries for the given ids, in the given order, skipping unknown ones."""
        if not ids:
            return []
        found: dict[int, Entry] = {}
        for chunk_start in range(0, len(ids), 500):
            chunk = list(ids[chunk_start:chunk_start + 500])
            marks = ",".join("?" * len(chunk))
            for entry in self._load(f"WHERE e.id IN ({marks})", chunk):
                found[entry.id] = entry
        return [found[i] for i in ids if i in found]

    def all_entries(self) -> list[Entry]:
        return self._load("", [])

    def _load(self, where: str, params: Sequence[Any], order: str = "ORDER BY e.id") -> list[Entry]:
        rows = self.conn.execute(
            f"SELECT e.*, p.name AS author_mc_name FROM entries e "
            f"LEFT JOIN players p ON p.uuid = e.author_mc_uuid {where} {order}", params).fetchall()
        if not rows:
            return []
        entries = [self._row_to_entry(r) for r in rows]
        by_id = {e.id: e for e in entries}
        total = int(self.conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0])
        if len(entries) * 4 >= total:
            # Most of the table: one pass over the child tables is cheaper than IN lists
            chunks: list[tuple[str, list[Any]]] = [("", [])]
        else:
            ids = list(by_id)
            chunks = [(f"WHERE entry_id IN ({','.join('?' * len(ids[i:i + 900]))})", ids[i:i + 900])
                      for i in range(0, len(ids), 900)]
        for filt, fparams in chunks:
            for r in self.conn.execute(
                    f"SELECT entry_id, label FROM entry_labels {filt} ORDER BY entry_id, position", fparams):
                e = by_id.get(int(r[0]))
                if e is not None:
                    e.labels.append(str(r[1]))
            for r in self.conn.execute(
                    f"SELECT * FROM entry_images {filt} ORDER BY entry_id, position", fparams):
                e = by_id.get(int(r["entry_id"]))
                if e is not None:
                    e.images.append(Image(
                        url=r["url"], attachment_id=r["attachment_id"],
                        refreshed_url=r["refreshed_url"], refreshed_expires_at=r["refreshed_expires_at"]))
        return entries

    @staticmethod
    def _row_to_entry(r: sqlite3.Row) -> Entry:
        return Entry(
            id=int(r["id"]), description=r["description"], author_id=int(r["author_id"]),
            priority=r["priority"], complexity=r["complexity"], labels=[],
            status=r["status"], resolution=r["resolution"],
            close_reason=r["close_reason"],
            closed_at=r["closed_at"], closed_by=r["closed_by"], duplicate_of=r["duplicate_of"],
            assignee_id=r["assignee_id"], redacted=bool(r["redacted"]),
            message_id=r["message_id"],
            pending_notification=bool(r["pending_notification"]), created_at=r["created_at"],
            updated_at=r["updated_at"],
            author_mc_uuid=r["author_mc_uuid"], author_mc_name=r["author_mc_name"],
            closed_by_mc_uuid=r["closed_by_mc_uuid"],
        )

    def _query_sql(self, q: EntryQuery) -> tuple[str, list[Any], str]:
        clauses: list[str] = []
        params: list[Any] = []
        if q.status in ("open", "closed"):
            clauses.append("e.status = ?")
            params.append(q.status)
        elif q.status != "all":
            raise ValueError(f"unknown status {q.status!r}")
        for label in q.labels:
            clauses.append("EXISTS (SELECT 1 FROM entry_labels l WHERE l.entry_id = e.id AND l.label = ?)")
            params.append(label)
        for column, values in (("priority", q.priorities), ("complexity", q.complexities),
                               ("resolution", q.resolutions)):
            if values:
                clauses.append(f"e.{column} IN ({','.join('?' * len(values))})")
                params.extend(values)
        if q.assignee == "any":
            clauses.append("e.assignee_id IS NOT NULL")
        elif q.assignee == "none":
            clauses.append("e.assignee_id IS NULL")
        elif q.assignee is not None:
            clauses.append("e.assignee_id = ?")
            params.append(int(q.assignee))
        if q.author_id is not None:
            clauses.append("e.author_id = ?")
            params.append(q.author_id)
        if q.author_mc_uuid is not None:
            clauses.append("e.author_mc_uuid = ?")
            params.append(q.author_mc_uuid)
        if q.closed_by is not None:
            clauses.append("e.closed_by = ?")
            params.append(q.closed_by)
        for term in q.terms:
            clauses.append("instr(pylower(e.description), ?) > 0")
            params.append(term.lower())
        for column, op, value in (("created_at", ">=", q.created_after),
                                  ("created_at", "<", q.created_before),
                                  ("closed_at", ">=", q.closed_after),
                                  ("closed_at", "<", q.closed_before)):
            if value is not None:
                clauses.append(f"e.{column} {op} ?")
                params.append(value)
        join = ""
        if q.reaction is not None:
            join = "JOIN reactions r ON r.entry_id = e.id AND r.emoji = ? AND r.count > 0"
            params.insert(0, q.reaction)
        where = (join + " WHERE " + " AND ".join(clauses)) if clauses else join

        direction = "DESC" if q.descending else "ASC"
        if q.reaction is not None:
            order = "ORDER BY r.count DESC, e.id"
        elif q.sort == "priority":
            order = f"ORDER BY {_RANK_SQL} {direction}, e.id"
        elif q.sort == "id":
            order = f"ORDER BY e.id {direction}"
        elif q.sort in ("created", "updated", "closed"):
            col = f"e.{q.sort}_at"
            # NULLs (unknown times) last either way
            order = f"ORDER BY {col} IS NULL, {col} {direction}, e.id {direction}"
        else:
            raise ValueError(f"unknown sort {q.sort!r}")
        return where, params, order

    def query(self, q: EntryQuery) -> list[Entry]:
        where, params, order = self._query_sql(q)
        if q.limit is not None:
            order += " LIMIT ? OFFSET ?"
            params = params + [q.limit, q.offset]
        elif q.offset:
            order += " LIMIT -1 OFFSET ?"
            params = params + [q.offset]
        return self._load(where, params, order)

    def count(self, q: EntryQuery) -> int:
        where, params, _ = self._query_sql(q)
        return int(self.conn.execute(f"SELECT COUNT(*) FROM entries e {where}", params).fetchone()[0])

    # ------------------------------------------------------------------
    # Counts (stats, astats)
    # ------------------------------------------------------------------

    def author_counts(self, limit: Optional[int] = None) -> list[AuthorCount]:
        """Entries per author, Discord and in-game together, most first (ties: earliest first)."""
        sql = ("SELECT author_id, author_mc_uuid, COUNT(*) AS n, SUM(status = 'open'), MIN(id) AS first "
               "FROM entries WHERE author_id != 0 OR author_mc_uuid IS NOT NULL "
               "GROUP BY author_id, author_mc_uuid ORDER BY n DESC, first")
        params: list[Any] = []
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
        return [AuthorCount(int(r[0]), r[1], int(r[2]), int(r[3]))
                for r in self.conn.execute(sql, params)]

    def stat_rows(self) -> list[StatRow]:
        """Every entry, for statistics and charts, which group and bucket in Python."""
        return [StatRow(int(r[0]), r[1], str(r[2]), r[3], r[4], str(r[5]), str(r[6]), r[7], r[8],
                        int(r[9]), r[10])
                for r in self.conn.execute(
                    "SELECT id, created_at, status, closed_at, resolution, priority, complexity, "
                    "closed_by, closed_by_mc_uuid, author_id, author_mc_uuid FROM entries")]

    def labels_by_entry(self) -> dict[int, list[str]]:
        """Each entry's labels, in order."""
        out: dict[int, list[str]] = {}
        for r in self.conn.execute("SELECT entry_id, label FROM entry_labels ORDER BY entry_id, position"):
            out.setdefault(int(r[0]), []).append(str(r[1]))
        return out

    def open_counts_by_priority_complexity(self) -> dict[tuple[str, str], int]:
        return {(str(r[0]), str(r[1])): int(r[2]) for r in self.conn.execute(
            "SELECT priority, complexity, COUNT(*) FROM entries WHERE status = 'open' "
            "GROUP BY priority, complexity")}

    def open_counts_by_label(self) -> dict[str, int]:
        """Most first."""
        return {str(r[0]): int(r[1]) for r in self.conn.execute(
            "SELECT l.label, COUNT(*) FROM entry_labels l JOIN entries e ON e.id = l.entry_id "
            "WHERE e.status = 'open' GROUP BY l.label ORDER BY COUNT(*) DESC, l.label")}

    def closed_counts_by_resolution(self) -> dict[str, int]:
        return {str(r[0]): int(r[1]) for r in self.conn.execute(
            "SELECT resolution, COUNT(*) FROM entries WHERE status = 'closed' GROUP BY resolution")}

    def entry_id_for_message(self, message_id: int) -> Optional[int]:
        row = self.conn.execute("SELECT id FROM entries WHERE message_id = ?", (message_id,)).fetchone()
        return None if row is None else int(row[0])

    def tracked_message_ids(self) -> set[int]:
        return {int(r[0]) for r in self.conn.execute(
            "SELECT message_id FROM entries WHERE message_id IS NOT NULL")}

    def duplicates_of(self, entry_id: int) -> list[int]:
        """The entries closed as duplicates of this one, oldest first."""
        return [int(r[0]) for r in self.conn.execute(
            "SELECT id FROM entries WHERE duplicate_of = ? ORDER BY id", (entry_id,))]

    def dirty_entry_ids(self) -> list[int]:
        return [int(r[0]) for r in self.conn.execute(
            "SELECT id FROM entries WHERE channel_dirty > 0 ORDER BY id")]

    # ------------------------------------------------------------------
    # Entries: writes
    # ------------------------------------------------------------------

    def insert_entry(self, entry: Entry) -> None:
        with self.transaction():
            self.conn.execute(
                """INSERT INTO entries(id, description, author_id, priority, complexity, status,
                       resolution, close_reason, closed_at, closed_by,
                       duplicate_of, assignee_id, redacted, message_id,
                       pending_notification, created_at, updated_at,
                       author_mc_uuid, closed_by_mc_uuid)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (entry.id, entry.description, entry.author_id, entry.priority, entry.complexity,
                 entry.status, entry.resolution, entry.close_reason,
                 entry.closed_at, entry.closed_by, entry.duplicate_of, entry.assignee_id,
                 int(entry.redacted), entry.message_id,
                 int(entry.pending_notification), entry.created_at,
                 entry.updated_at, entry.author_mc_uuid, entry.closed_by_mc_uuid))
            self.set_labels(entry.id, entry.labels)
            self.set_images(entry.id, entry.images)

    _UPDATABLE = frozenset((
        "description", "author_id", "priority", "complexity", "status", "resolution",
        "close_reason", "closed_at", "closed_by", "duplicate_of",
        "assignee_id", "redacted", "message_id", "pending_notification",
        "updated_at", "channel_dirty", "created_at",
        "author_mc_uuid", "closed_by_mc_uuid",
    ))

    def update(self, entry_id: int, **fields: Any) -> None:
        bad = set(fields) - self._UPDATABLE
        if bad:
            raise ValueError(f"not updatable: {sorted(bad)}")
        if not fields:
            return
        cols = ", ".join(f"{k} = ?" for k in fields)
        values = [int(v) if isinstance(v, bool) else v for v in fields.values()]
        self.conn.execute(f"UPDATE entries SET {cols} WHERE id = ?", [*values, entry_id])

    def checkpoint(self) -> None:
        """Copy the WAL into the database and empty it, so deleted text doesn't linger
        in the WAL file (secure_delete only covers the main file). Best effort: a busy
        reader (the backup) just leaves it for SQLite's next automatic checkpoint."""
        self.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")

    def clear_message_id(self, entry_id: int, message_id: int) -> None:
        """Forget the tracking message, if it is still this one."""
        self.conn.execute("UPDATE entries SET message_id = NULL WHERE id = ? AND message_id = ?",
                          (entry_id, message_id))

    def mark_dirty(self, entry_id: int) -> None:
        self.conn.execute("UPDATE entries SET channel_dirty = channel_dirty + 1 WHERE id = ?", (entry_id,))

    def set_labels(self, entry_id: int, labels: Sequence[str]) -> None:
        with self.transaction():
            self.conn.execute("DELETE FROM entry_labels WHERE entry_id = ?", (entry_id,))
            seen: list[str] = []
            for label in labels:
                if label not in seen:
                    seen.append(label)
            self.conn.executemany(
                "INSERT INTO entry_labels(entry_id, label, position) VALUES (?, ?, ?)",
                [(entry_id, label, i) for i, label in enumerate(seen)])

    def set_images(self, entry_id: int, images: Sequence[Image]) -> None:
        with self.transaction():
            self.conn.execute("DELETE FROM entry_images WHERE entry_id = ?", (entry_id,))
            self.conn.executemany(
                """INSERT INTO entry_images(entry_id, position, url, attachment_id,
                       refreshed_url, refreshed_expires_at) VALUES (?,?,?,?,?,?)""",
                [(entry_id, i, im.url, im.attachment_id, im.refreshed_url,
                  im.refreshed_expires_at) for i, im in enumerate(images)])

    def set_refreshed_url(self, url: str, refreshed: str) -> None:
        """Cache a refreshed signed URL for every image row that has the original url."""
        self.conn.execute(
            "UPDATE entry_images SET refreshed_url = ?, refreshed_expires_at = ? WHERE url = ?",
            (refreshed, url_expiry(refreshed), url))

    def get_image_cache(self, image: Image) -> Image:
        """The image with its refreshed URL as currently cached in the database."""
        row = self.conn.execute(
            "SELECT refreshed_url, refreshed_expires_at FROM entry_images WHERE url = ? "
            "AND refreshed_url IS NOT NULL LIMIT 1", (image.url,)).fetchone()
        if row is None:
            return image
        return Image(url=image.url, attachment_id=image.attachment_id,
                     refreshed_url=row[0], refreshed_expires_at=row[1])

    def replace_image_url(self, entry_id: int, old_url: str, new: Image) -> None:
        """Point an entry's image at a new copy (one the bot posted), keeping its position."""
        self.conn.execute(
            "UPDATE entry_images SET url = ?, attachment_id = ?, refreshed_url = NULL, "
            "refreshed_expires_at = NULL WHERE entry_id = ? AND url = ?",
            (new.url, new.attachment_id, entry_id, old_url))

    # Saved copies of images (images.py)

    def images_to_save(self, limit: int, now: int) -> list[tuple[int, str]]:
        """(entry, url) of Discord attachments, current or redacted, to save: those never
        tried first, newest entries first, then failed ones whose retry is due (an hour
        later per failure, at most a day). Ones Discord no longer has are not tried again."""
        rows = self.conn.execute(
            """SELECT i.entry_id, i.url FROM (
                   SELECT entry_id, url FROM entry_images
                   UNION
                   SELECT r.entry_id, j.value AS url FROM redacted_content r,
                          json_each(r.data, '$.images') j) i
               LEFT JOIN image_files f ON f.entry_id = i.entry_id AND f.url = i.url
               WHERE (i.url LIKE 'https://cdn.discordapp.com/%'
                      OR i.url LIKE 'https://media.discordapp.net/%')
                 AND i.url LIKE '%attachments/%'
                 AND (f.entry_id IS NULL
                      OR (f.path IS NULL AND f.missing = 0
                          AND f.checked_at + min(86400, 3600 * f.failures) <= ?))
               ORDER BY f.entry_id IS NOT NULL, i.entry_id DESC LIMIT ?""", (now, limit))
        return [(int(r[0]), str(r[1])) for r in rows]

    def add_image_file(self, f: ImageFile) -> bool:
        """Record a saved (or missing) image. False when the entry no longer exists (purged)."""
        cur = self.conn.execute(
            """INSERT OR REPLACE INTO image_files(entry_id, url, path, size, checked_at, missing,
                   message_id)
               SELECT ?, ?, ?, ?, ?, ?, ? WHERE EXISTS (SELECT 1 FROM entries WHERE id = ?)""",
            (f.entry_id, f.url, f.path, f.size, f.checked_at, int(f.missing), f.message_id, f.entry_id))
        return cur.rowcount > 0

    def image_save_failed(self, entry_id: int, url: str, at: int) -> None:
        self.conn.execute(
            """INSERT INTO image_files(entry_id, url, checked_at, failures)
               SELECT ?, ?, ?, 1 WHERE EXISTS (SELECT 1 FROM entries WHERE id = ?)
               ON CONFLICT(entry_id, url) DO UPDATE SET failures = failures + 1,
                   checked_at = excluded.checked_at""", (entry_id, url, at, entry_id))

    def image_files(self, entry_id: int) -> list[ImageFile]:
        return [ImageFile(entry_id=r["entry_id"], url=r["url"], path=r["path"], size=r["size"],
                          checked_at=r["checked_at"], message_id=r["message_id"],
                          missing=bool(r["missing"]))
                for r in self.conn.execute(
                    "SELECT * FROM image_files WHERE entry_id = ? ORDER BY checked_at, url", (entry_id,))]

    def image_messages(self, entry_id: int) -> list[int]:
        """The bot's own feed channel messages holding an entry's images."""
        return [int(r[0]) for r in self.conn.execute(
            "SELECT message_id FROM image_files WHERE entry_id = ? AND message_id IS NOT NULL",
            (entry_id,))]

    def redacted_image_messages(self) -> list[int]:
        """The bot's own feed channel messages holding images of redacted entries."""
        return [int(r[0]) for r in self.conn.execute(
            "SELECT f.message_id FROM image_files f JOIN entries e ON e.id = f.entry_id "
            "WHERE e.redacted AND f.message_id IS NOT NULL")]

    def forget_image_message(self, message_id: int) -> None:
        self.conn.execute("UPDATE image_files SET message_id = NULL WHERE message_id = ?", (message_id,))

    def entries_with_label(self, label: str) -> list[int]:
        return [int(r[0]) for r in self.conn.execute(
            "SELECT entry_id FROM entry_labels WHERE label = ? ORDER BY entry_id", (label,))]

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def add_event(self, entry_id: int, kind: str, *, at: Optional[int], actor_id: Optional[int],
                  source: str, old: Any = None, new: Any = None, reason: Optional[str] = None,
                  source_ref: Optional[str] = None, actor_mc_uuid: Optional[str] = None) -> int:
        cur = self.conn.execute(
            """INSERT INTO events(entry_id, at, actor_id, kind, old_value, new_value, reason,
                   source, source_ref, actor_mc_uuid) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (entry_id, at, actor_id, kind, _encode(old), _encode(new), reason, source, source_ref,
             actor_mc_uuid))
        return int(cur.lastrowid or 0)

    def events_for(self, entry_id: int) -> list[Event]:
        return [self._row_to_event(r) for r in self.conn.execute(
            "SELECT * FROM events WHERE entry_id = ? ORDER BY id", (entry_id,))]

    def events(self, *, since: Optional[int] = None, until: Optional[int] = None,
               kinds: Sequence[str] = (), actor_id: Optional[int] = None,
               limit: int = 100, before_id: Optional[int] = None) -> list[Event]:
        """Most recent first. Events with unknown times are excluded when a time bound is given."""
        clauses: list[str] = []
        params: list[Any] = []
        if since is not None:
            clauses.append("at >= ?")
            params.append(since)
        if until is not None:
            clauses.append("at < ?")
            params.append(until)
        if kinds:
            clauses.append(f"kind IN ({','.join('?' * len(kinds))})")
            params.extend(kinds)
        if actor_id is not None:
            clauses.append("actor_id = ?")
            params.append(actor_id)
        if before_id is not None:
            clauses.append("id < ?")
            params.append(before_id)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        return [self._row_to_event(r) for r in self.conn.execute(
            f"SELECT * FROM events {where} ORDER BY id DESC LIMIT ?", [*params, limit])]

    def scrub_events(self, entry_id: int, kinds: Sequence[str]) -> int:
        """Blank the values of an entry's earlier events (used by redaction)."""
        marks = ",".join("?" * len(kinds))
        cur = self.conn.execute(
            f"UPDATE events SET old_value = NULL, new_value = NULL, reason = NULL "
            f"WHERE entry_id = ? AND kind IN ({marks})", [entry_id, *kinds])
        return cur.rowcount

    def scrub_reasons(self, entry_id: int) -> int:
        """Blank every reason recorded for an entry (close reasons can quote the report)."""
        return self.conn.execute(
            "UPDATE events SET reason = NULL WHERE entry_id = ?", (entry_id,)).rowcount

    @staticmethod
    def _row_to_event(r: sqlite3.Row) -> Event:
        return Event(id=int(r["id"]), entry_id=int(r["entry_id"]), at=r["at"],
                     actor_id=r["actor_id"], kind=r["kind"], old_value=r["old_value"],
                     new_value=r["new_value"], reason=r["reason"], source=r["source"],
                     source_ref=r["source_ref"], actor_mc_uuid=r["actor_mc_uuid"])

    # ------------------------------------------------------------------
    # Reactions
    # ------------------------------------------------------------------

    def reactions(self, entry_id: int) -> list[Reaction]:
        return [Reaction(str(r[0]), int(r[1])) for r in self.conn.execute(
            "SELECT emoji, count FROM reactions WHERE entry_id = ? ORDER BY rowid", (entry_id,))]

    def set_reactions(self, entry_id: int, reactions: Sequence[Reaction]) -> None:
        """Replace with the counts Discord reported, keeping Discord's order."""
        now = int(time.time())
        with self.transaction():
            self.conn.execute("UPDATE entries SET reactions_checked_at = ? WHERE id = ?", (now, entry_id))
            self.conn.execute("DELETE FROM reactions WHERE entry_id = ?", (entry_id,))
            self.conn.executemany(
                "INSERT INTO reactions(entry_id, emoji, count, updated_at) VALUES (?,?,?,?)",
                [(entry_id, r.emoji, r.count, now) for r in reactions if r.count > 0])

    def adjust_reaction(self, entry_id: int, emoji: str, delta: int) -> None:
        now = int(time.time())
        with self.transaction():
            row = self.conn.execute(
                "SELECT count FROM reactions WHERE entry_id = ? AND emoji = ?", (entry_id, emoji)).fetchone()
            if row is None:
                if delta > 0:
                    self.conn.execute(
                        "INSERT INTO reactions(entry_id, emoji, count, updated_at) VALUES (?,?,?,?)",
                        (entry_id, emoji, delta, now))
                return
            count = int(row[0]) + delta
            if count <= 0:
                self.conn.execute("DELETE FROM reactions WHERE entry_id = ? AND emoji = ?", (entry_id, emoji))
            else:
                self.conn.execute(
                    "UPDATE reactions SET count = ?, updated_at = ? WHERE entry_id = ? AND emoji = ?",
                    (count, now, entry_id, emoji))

    def stalest_reaction_entries(self, limit: int) -> list[int]:
        """Entries with tracking messages, least recently reconciled first."""
        return [int(r[0]) for r in self.conn.execute(
            "SELECT id FROM entries WHERE message_id IS NOT NULL "
            "ORDER BY COALESCE(reactions_checked_at, 0), id LIMIT ?", (limit,))]

    def mark_reactions_checked(self, entry_id: int) -> None:
        self.conn.execute("UPDATE entries SET reactions_checked_at = ? WHERE id = ?",
                          (int(time.time()), entry_id))

    def count_unchecked_reactions(self) -> int:
        """Tracked messages whose reactions have never been read (e.g. right after migration)."""
        return int(self.conn.execute(
            "SELECT COUNT(*) FROM entries WHERE message_id IS NOT NULL "
            "AND reactions_checked_at IS NULL").fetchone()[0])

    def remove_reaction(self, entry_id: int, emoji: str) -> None:
        self.conn.execute("DELETE FROM reactions WHERE entry_id = ? AND emoji = ?", (entry_id, emoji))

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    def notifications_disabled(self, user_id: int) -> bool:
        return self.conn.execute(
            "SELECT 1 FROM notifications_disabled WHERE user_id = ?", (user_id,)).fetchone() is not None

    def set_notifications_disabled(self, user_id: int, disabled: bool) -> None:
        if disabled:
            self.conn.execute("INSERT OR IGNORE INTO notifications_disabled(user_id) VALUES (?)", (user_id,))
        else:
            self.conn.execute("DELETE FROM notifications_disabled WHERE user_id = ?", (user_id,))

    def take_notices(self, uuid: str, now: int) -> list[Notice]:
        """A player's undelivered notices, marked delivered as they are handed out. Asked on
        every join to a shard, so the usual case (nothing waiting) only reads."""
        if not self.pending_notices(uuid):
            return []
        with self.transaction():
            notices = self.pending_notices(uuid)
            self.conn.execute("UPDATE player_notices SET delivered_at = ? WHERE uuid = ? "
                              "AND delivered_at IS NULL", (now, uuid))
        return notices

    def pending_notification_ids(self) -> list[int]:
        return [int(r[0]) for r in self.conn.execute(
            "SELECT id FROM entries WHERE pending_notification = 1 ORDER BY id")]

    # ------------------------------------------------------------------
    # API tokens (only hashes are stored)
    # ------------------------------------------------------------------

    def add_token(self, token_hash: str, discord_id: int, scope: str, created_at: int,
                  expires_at: int, service: Optional[str] = None,
                  max_privilege: Optional[int] = None) -> None:
        self.conn.execute(
            "INSERT INTO api_tokens(token_hash, discord_id, scope, created_at, expires_at, service, "
            "max_privilege) VALUES (?,?,?,?,?,?,?)",
            (token_hash, discord_id, scope, created_at, expires_at, service, max_privilege))

    def token_info(self, token_hash: str, now: int) -> Optional[TokenInfo]:
        """The live token with this hash, else None. Records use of service tokens."""
        row = self.conn.execute(
            "SELECT discord_id, scope, service, max_privilege, created_at, expires_at, last_used_at "
            "FROM api_tokens WHERE token_hash = ? AND expires_at > ?", (token_hash, now)).fetchone()
        if row is None:
            return None
        info = TokenInfo(discord_id=int(row[0]), scope=str(row[1]), service=row[2],
                         max_privilege=row[3], created_at=int(row[4]), expires_at=int(row[5]),
                         last_used_at=row[6], token_hash=token_hash)
        if info.service is not None and (info.last_used_at or 0) < now - 60:
            self.conn.execute("UPDATE api_tokens SET last_used_at = ? WHERE token_hash = ?",
                              (now, token_hash))
        return info

    def service_tokens(self) -> list[TokenInfo]:
        return [TokenInfo(discord_id=int(r[0]), scope=str(r[1]), service=r[2], max_privilege=r[3],
                          created_at=int(r[4]), expires_at=int(r[5]), last_used_at=r[6],
                          token_hash=str(r[7]))
                for r in self.conn.execute(
                    "SELECT discord_id, scope, service, max_privilege, created_at, expires_at, "
                    "last_used_at, token_hash FROM api_tokens WHERE service IS NOT NULL "
                    "ORDER BY service, created_at")]

    def revoke_service_tokens(self, service: str, hash_prefix: str = "") -> int:
        return self.conn.execute(
            "DELETE FROM api_tokens WHERE service = ? AND token_hash LIKE ?",
            (service, hash_prefix + "%")).rowcount

    def count_tokens(self, discord_id: int, now: int) -> int:
        return int(self.conn.execute(
            "SELECT COUNT(*) FROM api_tokens WHERE discord_id = ? AND service IS NULL AND expires_at > ?",
            (discord_id, now)).fetchone()[0])

    def revoke_tokens(self, discord_id: int) -> int:
        """Revoke a Discord user's tokens (never service tokens)."""
        return self.conn.execute("DELETE FROM api_tokens WHERE discord_id = ? AND service IS NULL",
                                 (discord_id,)).rowcount

    def expire_tokens(self, now: int) -> int:
        return self.conn.execute("DELETE FROM api_tokens WHERE expires_at <= ?", (now,)).rowcount


def _encode(value: Any) -> Optional[str]:
    """Event values are stored as text: strings as-is, everything else as JSON."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def json_text(value: Any) -> str:
    """Compact JSON, as stored for context and redacted content."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
