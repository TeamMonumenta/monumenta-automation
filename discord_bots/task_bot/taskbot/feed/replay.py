"""Replay a downloaded feed channel into a history of events.

    python -m taskbot.feed.replay --prefix '~bug' --snapshot bug_reports.json \\
        bugs.jsonl events.jsonl report.txt

The bot's own replies decide what happened: `Bug #12 marked as fixed` means
entry 12 was fixed at that moment, whatever the command looked like. Commands
are only parsed to decide who caused each reply. To do that the replay mirrors
the old bot's message handling, including interactive sessions (`isearch`,
`iroulette`), where the session owner types bare abbreviations like `f` or
`e p l` that act on whichever entry the session is showing.

After each change the bot posted the entry as it then looked; the replay keeps
the latest render of every entry and turns the difference into the event's old
and new values. The result is checked against a copy of the legacy JSON
(`--snapshot`), and every reply it could not attribute is listed in the report.

Output is one JSON event per line, meant for `taskbot.feed.apply`; nothing here
touches a database.
"""

import argparse
import collections
import json
import re
import sys
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field, replace
from typing import Any, Optional

from .. import inference
from ..vocab import PRIORITIES
from . import parse
from .parse import Command, FeedMessage, Render, Reply

# Discord shows every message of a deleted account as coming from this one user.
DELETED_USER = 456226577798135808

# How long after a command its reply may still arrive. Most replies take a second.
REPLY_WINDOW = 600.0
# How far ahead to look for a command whose reply Discord ordered first.
LOOKAHEAD = 3.0
# Identical bot messages this close together, with nothing to answer, are the bot's
# occasional double posting.
DUPLICATE_WINDOW = 10.0
# The old bot dropped interactive sessions after this long without a command.
SESSION_TIMEOUT = 6 * 3600.0

# Reply kind -> command names that produce it.
PRODUCERS: dict[str, set[str]] = {
    "created": {"add", "report"},
    "updated": {"edit"},
    "appended": {"append"},
    "fixed": {"fix"},
    "rejected": {"reject"},
    "unfixed": {"unfix"},
    "assigned": {"assign"},
    "unassigned": {"unassign"},
    "deleted": {"delete"},
}
NAV = {"next", "prev"}
SESSION_STARTERS = {"isearch", "iroulette"}


@dataclass
class Session:
    owner: int
    started: float
    last_active: float
    current: Optional[int] = None


@dataclass
class Pending:
    msg: FeedMessage
    cmd: Command
    session: Optional[Session] = None
    # The entry an interactive command acts on, if the session's position is known.
    target: Optional[int] = None


@dataclass
class Event:
    entry_id: int
    at: float
    actor_id: Optional[int]
    kind: str
    old: Any = None
    new: Any = None
    reason: Optional[str] = None
    source_ref: Optional[int] = None     # the command message
    reply_ref: int = 0                  # the bot reply that confirmed it
    attribution: str = "matched"        # matched | unmatched
    note: str = ""


@dataclass
class EntryState:
    render: Optional[Render] = None
    images: list[str] = field(default_factory=list[str])
    assignee_id: Optional[int] = None
    author_id: Optional[int] = None
    resolution: Optional[str] = None
    # Labels, priority and complexity as of the last event or plain render. Renders can't
    # give an edit's old value: the old bot handled commands concurrently, so the render
    # after `e l item` may already show the `e p l` that came right after it.
    fields: dict[str, Any] = field(default_factory=dict[str, Any])


@dataclass
class Issue:
    kind: str
    message_id: int
    at: float
    text: str


class Replay:
    def __init__(self, prefix: str, labels: Iterable[str], complexities: dict[str, str],
                 known_authors: Optional[dict[int, int]] = None):
        self.prefix = prefix
        # Authors from the legacy JSON (exact), to pick between several pending `add`s.
        self.known_authors = known_authors or {}
        self.labels = list(labels)
        self.emoji_to_complexity = {v: k for k, v in complexities.items()}
        self.complexity_names = list(complexities)
        # The old bot's label list as far as the feed shows it so far, in its order: what an
        # edit's typed labels are matched against. Its "Labels must be one of: [...]" errors
        # give the whole list; renders and addlabel replies add to it in between.
        self._known_labels: list[str] = []
        self.sessions: list[Session] = []
        self.pending: list[Pending] = []
        self.entries: dict[int, EntryState] = collections.defaultdict(EntryState)
        self.events: list[Event] = []
        self.issues: list[Issue] = []
        # Lowercased names -> ids, from authors, mentions and notification renders.
        self.names: dict[str, set[int]] = collections.defaultdict(set)
        self._recent_bot: collections.deque[FeedMessage] = collections.deque(maxlen=20)
        self.bot_ids: set[int] = set()
        self.stats: collections.Counter[str] = collections.Counter()
        # Renders since the last action reply, by entry: the post-change render to use.
        self._fresh_render: dict[int, tuple[Render, FeedMessage]] = {}
        self._msgs: list[FeedMessage] = []
        self._pos = 0
        self._done: set[int] = set()

    def _pull_ahead(self, reply_msg: FeedMessage, names: set[str]) -> None:
        """Discord's ids can put a reply a moment before its command (the two were made on
        different servers). Handle such a command now, before the reply."""
        for msg in self._msgs[self._pos + 1:]:
            if msg.at - reply_msg.at > LOOKAHEAD:
                break
            if msg.is_bot or msg.id in self._done:
                continue
            cmd = parse.parse_main(msg, self.prefix)
            if cmd is not None and cmd.name in names:
                self._done.add(msg.id)
                self.stats["command handled ahead of its reply"] += 1
                self._human_message(msg)
                return

    # --- Driving ------------------------------------------------------------------------

    def run(self, messages: Iterable[FeedMessage]) -> None:
        self._msgs = list(messages)
        # Labels that existed at some point (some were deleted later): every one the bot
        # ever rendered or added. Used to split `add <labels> <description>`.
        vocabulary = set(self.labels)
        for msg in self._msgs:
            if msg.is_bot:
                reply = parse.classify_reply(msg)
                if reply.render is not None:
                    vocabulary.update(reply.render.labels)
                elif reply.kind == "label_added":
                    vocabulary.add(reply.detail.lower())
        self.labels = sorted(vocabulary)
        for pos, msg in enumerate(self._msgs):
            if msg.id in self._done:
                continue
            self._pos = pos
            self._expire(msg.at)
            for user_id, names in msg.names.items():
                if user_id != DELETED_USER:
                    for name in names:
                        self.names[name.lower()].add(user_id)
            if msg.is_bot:
                self.bot_ids.add(msg.author_id)
                self._bot_message(msg)
                self._recent_bot.append(msg)
            else:
                self._human_message(msg)
        self._expire(float("inf"))

    def _expire(self, now: float) -> None:
        keep: list[Pending] = []
        for p in self.pending:
            if now - p.msg.at <= REPLY_WINDOW:
                keep.append(p)
            elif p.cmd.name in _MUTATING:
                self.stats["mutating command without a reply"] += 1
        self.pending = keep

    # --- Human messages: mirror the old bot's handle_message ------------------------------

    def _human_message(self, msg: FeedMessage) -> None:
        for session in list(self.sessions):
            if session.owner != msg.author_id:
                continue
            if msg.at - session.last_active > SESSION_TIMEOUT:
                self.sessions.remove(session)
                continue
            cmd = parse.parse_interactive(msg)
            if cmd is None:
                continue
            session.last_active = msg.at
            if cmd.name == "stop":
                self.sessions.remove(session)
                return
            if cmd.name == "help":
                return
            self.pending.append(Pending(msg, cmd, session, session.current))
            self.stats[f"interactive {cmd.name}"] += 1
            return

        cmd = parse.parse_main(msg, self.prefix)
        if cmd is None or cmd.name == "usage":
            return
        self.stats[f"command {cmd.name}"] += 1
        self.pending.append(Pending(msg, cmd, None, cmd.index))

    # --- Bot messages -----------------------------------------------------------------------

    def _bot_message(self, msg: FeedMessage) -> None:
        reply = parse.classify_reply(msg)
        self.stats[f"reply {reply.kind}"] += 1
        listed = _LABEL_LIST_RE.match(msg.content)
        if listed:
            self._known_labels = [x.strip().lower() for x in listed.group(1).split(",") if x.strip()]
        for label in (reply.render.labels if reply.render is not None else
                      [reply.detail.lower()] if reply.kind == "label_added" else []):
            if label not in self._known_labels:
                self._known_labels.append(label)
        if reply.kind == "label_removed" and reply.detail.lower() in self._known_labels:
            self._known_labels.remove(reply.detail.lower())
        if reply.kind in PRODUCERS:
            self._action(msg, reply)
        elif reply.kind == "render":
            self._render(msg, reply)
        elif reply.kind == "notified":
            assert reply.render is not None
            state = self.entries[reply.render.index]
            state.author_id = int(reply.detail)
            if reply.render.author_name:
                self.names[reply.render.author_name.lower()].add(state.author_id)
            self._observe(reply.render, msg)
        elif reply.kind == "session_started":
            if self._duplicate(msg) and not any(p.cmd.name in SESSION_STARTERS for p in self.pending):
                return
            if not any(p.cmd.name in SESSION_STARTERS for p in self.pending):
                self._pull_ahead(msg, SESSION_STARTERS)
            p = self._take(lambda p: p.cmd.name in SESSION_STARTERS)
            if p is None:
                self._issue("session start without a command", msg)
                return
            session = Session(p.msg.author_id, p.msg.at, p.msg.at)
            self.sessions.append(session)
            # The first entry's render follows; the session waits for it.
            self.pending.insert(0, Pending(p.msg, Command("next", "", None, True), session))
        elif reply.kind == "session_empty":
            self._take(lambda p: p.cmd.name in SESSION_STARTERS)
        elif reply.kind == "session_ended":
            p = self._take(lambda p: p.session is not None and p.cmd.name in NAV | {"stop"})
            session = p.session if p is not None else self._recent_session()
            if session in self.sessions:
                self.sessions.remove(session)
        elif reply.kind in ("nav_noop",):
            self._take(lambda p: p.cmd.name == "prev")
        elif reply.kind == "error_ping":
            # The bot pings the author and then posts the exception text.
            user = int(reply.detail)
            p = self._take(lambda p: p.msg.author_id == user and p.cmd.name in _MUTATING)
            if p is not None:
                self._issue(f"exception after {p.cmd.name!r} command; the change may or may not "
                            f"have been saved: {p.msg.content[:200]!r}", msg)

    def _recent_session(self) -> Optional[Session]:
        return max(self.sessions, key=lambda s: s.last_active) if self.sessions else None

    def _take(self, pred: Callable[["Pending"], bool]) -> Optional[Pending]:
        for i, p in enumerate(self.pending):
            if pred(p):
                return self.pending.pop(i)
        return None

    def _match(self, names: set[str], index: int) -> Optional[Pending]:
        p = self._take_latest(lambda p: p.cmd.name in names and self._targets(p, index))
        if p is None:
            # An edited command (the bot saw the old text), or a session whose position
            # the replay lost track of.
            p = self._take_latest(lambda p: p.cmd.name in names and (p.msg.edited or p.session is not None))
        return p

    def _take_latest(self, pred: Callable[["Pending"], bool]) -> Optional[Pending]:
        """The most recent matching command. Replies come within a second or two, so an
        older match is usually an attempt that failed (and got an error reply)."""
        for i in range(len(self.pending) - 1, -1, -1):
            if pred(self.pending[i]):
                return self.pending.pop(i)
        return None

    def _render(self, msg: FeedMessage, reply: Reply) -> None:
        render = reply.render
        assert render is not None
        index = render.index
        # A render right after a change command for this entry is its new state; otherwise
        # it may be a session moving on (next/prev/first entry), or get/search output.
        changing = any(p.cmd.name in _MUTATING and self._targets(p, index) for p in self.pending)
        got = None if changing else self._take(lambda p: p.cmd.name == "get" and p.target == index)
        if not changing and got is None:
            nav = self._take(lambda p: p.session is not None and p.cmd.name in NAV)
            if nav is not None and nav.session is not None:
                nav.session.current = index
                for p in self.pending:
                    if p.session is nav.session and p.target is None:
                        p.target = index
        self._fresh_render[index] = (render, msg)
        if not changing:
            self._observe(render, msg)

    @staticmethod
    def _targets(p: Pending, index: int) -> bool:
        if p.session is not None:
            return p.target is None or p.target == index
        return p.target == index

    def _observe(self, render: Render, msg: FeedMessage) -> None:
        """A render that isn't the result of a change: just the current state."""
        state = self.entries[render.index]
        state.render = render
        state.fields.update(self._fields(render))
        if msg.embed_images:
            state.images = list(msg.embed_images)

    # --- Action replies ----------------------------------------------------------------------

    def _action(self, msg: FeedMessage, reply: Reply) -> None:
        index = reply.index
        assert index is not None
        names = PRODUCERS[reply.kind]
        if reply.kind == "created":
            author = self.known_authors.get(index)
            p = self._take_latest(lambda p: p.cmd.name in names and p.msg.author_id in (author, DELETED_USER))
            if p is None:
                p = self._take_latest(lambda p: p.cmd.name in names)
        else:
            p = self._match(names, index)
            if p is None:
                self._pull_ahead(msg, names)
                p = self._match(names, index)
        if p is None and self._duplicate(msg):
            # At times the bot posted each reply twice; the copy changed nothing.
            self.stats["duplicate reply ignored"] += 1
            return
        attribution = "matched"
        if p is not None and (p.msg.edited or (p.session is not None and p.target not in (None, index))):
            attribution = "matched_loose"
        if p is None:
            attribution = "unmatched"
            self._issue(f"{reply.kind} #{index} without a matching command", msg)
        state = self.entries[index]
        fresh = self._fresh_render.pop(index, None)
        new_render = fresh[0] if fresh is not None and (p is None or fresh[1].at >= p.msg.at) else None
        new_images = fresh[1].embed_images if fresh is not None and new_render is not None else []
        old_render = state.render

        actor = p.msg.author_id if p is not None else None
        if p is None and reply.kind == "created" and self.known_authors.get(index):
            # The command was deleted, but the JSON's author is exact and the reply's
            # time is within a second of the command.
            actor = self.known_authors[index]
            attribution = "author_from_json"
        deleted_account = actor == DELETED_USER
        if deleted_account:
            actor = self.known_authors.get(index) if reply.kind == "created" else None
        at = p.msg.at if p is not None else msg.at
        base = Event(entry_id=index, at=at, actor_id=actor, kind="",
                     source_ref=p.msg.id if p is not None else None, reply_ref=msg.id,
                     attribution=attribution if not deleted_account else "deleted_account")

        def emit(kind: str, old: Any = None, new: Any = None, reason: Optional[str] = None,
                 note: str = "") -> None:
            self.events.append(replace(base, kind=kind, old=old, new=new, reason=reason, note=note))

        cmd = p.cmd if p is not None else None
        if reply.kind == "created":
            description = self._created_description(p) if p is not None else None
            state.author_id = actor
            state.images = list(p.msg.attachments[-1:]) if p is not None else []
            emit("created", new=description)
        elif reply.kind in ("fixed", "rejected"):
            reason = new_render.close_reason if new_render is not None else None
            typed = _rest_after_index(cmd) if cmd is not None else ""
            if reason is not None and typed and _flatten_emoji(typed) == reason:
                # The bot's copy turns custom emoji it can't use into :name:; the
                # command has them intact.
                reason = typed
            if reason is None and cmd is not None:
                reason = _rest_after_index(cmd)
                # Until 2019-05-11 the bot lowercased close reasons.
                if reason and p is not None and parse.day(p.msg.at) < "2019-05-11":
                    reason = reason.lower()
                reason = reason or ("Fixed" if reply.kind == "fixed" else None)
            resolution = "fixed"
            if reply.kind == "rejected":
                resolution, _ = inference.classify_close_reason(reason or "")
                if resolution == "fixed":
                    resolution = "rejected"
            if state.assignee_id is not None:
                emit("unassigned", old=state.assignee_id, reason="closed")
                state.assignee_id = None
            emit("closed", old=state.resolution, new=resolution, reason=reason)
            state.resolution = resolution
        elif reply.kind == "unfixed":
            emit("reopened", old=state.resolution)
            state.resolution = None
        elif reply.kind == "appended":
            emit("appended", new=_rest_after_index(cmd) if cmd is not None else None)
        elif reply.kind == "updated":
            self._edit(cmd, old_render, new_render, state, new_images, emit)
        elif reply.kind == "assigned":
            assignee = self._assignee(p, reply.detail)
            emit("assigned", old=state.assignee_id, new=assignee,
                 note="" if assignee is not None else f"unresolved assignee {reply.detail!r}")
            state.assignee_id = assignee
        elif reply.kind == "unassigned":
            emit("unassigned", old=state.assignee_id)
            state.assignee_id = None
        elif reply.kind == "deleted":
            emit("deleted")

        if new_render is not None:
            state.render = new_render
            if any(p.cmd.name in _MUTATING and self._targets(p, index) for p in self.pending):
                # Another change to this entry is still under way, and the render may show it
                for name, value in self._fields(new_render).items():
                    state.fields.setdefault(name, value)
            else:
                # Nothing else under way: the render is the state, including any change the
                # old bot lost when two commands overwrote each other
                state.fields.update(self._fields(new_render))
            if new_images:
                state.images = list(new_images)

    def _edit(self, cmd: Optional[Command], old: Optional[Render], new: Optional[Render],
              state: EntryState, new_images: list[str], emit: "Emit") -> None:
        field_name: Optional[str] = None
        value = ""
        if cmd is not None:
            words = (cmd.args if cmd.interactive else _rest_after_index(cmd) or "").split(maxsplit=1)
            if words:
                field_name = parse.get_list_match(words[0], parse.EDIT_FIELDS)
                value = words[1].strip() if len(words) > 1 else ""
        if field_name is None and old is not None and new is not None:
            field_name = _diff_field(old, new)
        if field_name == "description":
            emit("description", old=old.description if old else None,
                 new=new.description if new else value)
        elif field_name in ("label", "priority", "complexity"):
            # The value comes from the command when it parses, as the old bot parsed it;
            # the render only when it doesn't. Labels are matched against the list as the
            # feed showed it at the time, not every label ever seen: a stray "Label que added"
            # reply in 2019 must not turn the `l que` people typed for `quest` into `que`.
            kind = "labels" if field_name == "label" else field_name
            before = state.fields.get(kind, self._fields(old)[kind] if old else None)
            after = self._typed_value(kind, value)
            if after is None and new is not None:
                after = self._fields(new)[kind]
            emit(kind, old=before, new=after)
            if after is not None:
                state.fields[kind] = after
        elif field_name == "image":
            emit("image", old=list(state.images), new=list(new_images))
        else:
            emit("edited", note=f"unknown edit field (command {cmd.args if cmd else None!r})")

    def _fields(self, render: Render) -> dict[str, Any]:
        return {"labels": render.labels, "priority": render.priority,
                "complexity": self._complexity(render)}

    def _typed_value(self, kind: str, value: str) -> Any:
        if not value:
            return None
        if kind == "priority":
            return parse.get_list_match(value, PRIORITIES)
        if kind == "complexity":
            return parse.get_list_match(value, self.complexity_names)
        labels = [parse.get_list_match(w.strip(), self._known_labels) for w in value.lower().split(",")]
        return None if any(label is None for label in labels) else labels

    def _complexity(self, render: Optional[Render]) -> Optional[str]:
        if render is None:
            return None
        return self.emoji_to_complexity.get(render.complexity_emoji, render.complexity_emoji or None)

    def _duplicate(self, msg: FeedMessage) -> bool:
        return any(m.content == msg.content and msg.at - m.at <= DUPLICATE_WINDOW for m in self._recent_bot)

    def _assignee(self, p: Optional[Pending], display_name: str) -> Optional[int]:
        """Who `assign` picked: the author if no user was given, else a mention, an id, or
        (like the old bot's get_user) the one member whose name starts with the text."""
        if p is not None:
            arg = (p.cmd.args if p.cmd.interactive else _rest_after_index(p.cmd) or "").strip()
            if not arg:
                return p.msg.author_id if p.msg.author_id != DELETED_USER else None
            if p.msg.mentions:
                return p.msg.mentions[0]
            if arg.isdigit():
                return int(arg)
            low = arg.lower()
            ids = {i for name, found in self.names.items() if name.startswith(low) for i in found}
            if len(ids) == 1:
                return ids.pop()
        ids = self.names.get(display_name.lower(), set())
        return next(iter(ids)) if len(ids) == 1 else None

    def _created_description(self, p: Pending) -> str:
        """The description cmd_add stored: the args minus a leading label list."""
        args = p.cmd.args
        part = args.split(maxsplit=1)
        if len(part) < 2:
            return args
        wanted = [x.strip() for x in part[0].lower().split(",")]
        # The labels as they were then: abbreviations depend on which existed
        labels = self._known_labels or self.labels
        if all(parse.get_list_match(w, labels) is not None for w in wanted):
            return part[1].strip()
        return args

    def _issue(self, kind: str, msg: FeedMessage) -> None:
        self.issues.append(Issue(kind, msg.id, msg.at, msg.content[:300]))


Emit = Callable[..., None]

_MUTATING = {"add", "report", "edit", "append", "fix", "reject", "unfix", "assign", "unassign", "delete"}


def _rest_after_index(cmd: Command) -> str:
    if cmd.interactive:
        return cmd.args
    part = cmd.args.split(maxsplit=1)
    return part[1].strip() if len(part) > 1 else ""


_LABEL_LIST_RE = re.compile(r"^Labels must be one of: \[([^\]]*)\]$")
_CUSTOM_EMOJI_RE = re.compile(r"<a?(:\w+:)\d+>")


def _flatten_emoji(text: str) -> str:
    return _CUSTOM_EMOJI_RE.sub(r"\1", text)


def _diff_field(old: Render, new: Render) -> Optional[str]:
    if old.labels != new.labels:
        return "label"
    if old.priority != new.priority:
        return "priority"
    if old.complexity_emoji != new.complexity_emoji:
        return "complexity"
    if old.description != new.description:
        return "description"
    return None


# --- Checking against the legacy JSON --------------------------------------------------------


def check_against_snapshot(replay: Replay, snapshot: dict[str, Any]) -> list[str]:
    entries: dict[str, dict[str, Any]] = snapshot["entries"]
    last_close: dict[int, Event] = {}
    creations: dict[int, list[Event]] = collections.defaultdict(list)
    for e in replay.events:
        if e.kind in ("closed", "reopened"):
            last_close[e.entry_id] = e
        elif e.kind == "created":
            creations[e.entry_id].append(e)
    created: dict[int, Event] = {}
    for key, raw in entries.items():
        found = creations.get(int(key))
        if found:
            # The one feed.apply keeps (see real_creation there)
            author = int(raw.get("author") or 0)
            created[int(key)] = next((e for e in found if author and e.actor_id == author), found[-1])
    c: collections.Counter[str] = collections.Counter()
    samples: dict[str, list[str]] = collections.defaultdict(list)

    def note(key: str, text: str) -> None:
        c[key] += 1
        if len(samples[key]) < 15:
            samples[key].append(text)

    for key, raw in entries.items():
        i = int(key)
        closed = "close_reason" in raw
        ev = last_close.get(i)
        if i in created:
            if created[i].actor_id == int(raw.get("author") or 0):
                c["created: author agrees"] += 1
            else:
                note("created: author differs", f"#{i}: replay {created[i].actor_id}, json {raw.get('author')}")
            if created[i].new == raw.get("description"):
                c["created: description agrees"] += 1
            else:
                c["created: description differs (edited later, or parse)"] += 1
        else:
            c["created: no event"] += 1
        if closed:
            if ev is None or ev.kind != "closed":
                note("closed in json, not closed by replay", f"#{i}: {raw['close_reason'][:80]!r}")
            elif (ev.reason or "").strip() == str(raw["close_reason"]).strip():
                c["closed: reason agrees"] += 1
                if ev.attribution == "matched":
                    c["closed: reason agrees, closer known"] += 1
            else:
                note("closed: reason differs", f"#{i}: replay {ev.reason!r:.80} json {raw['close_reason']!r:.80}")
        else:
            if ev is not None and ev.kind == "closed":
                note("open in json, closed by replay", f"#{i}")
            else:
                c["open: agrees"] += 1
        state = replay.entries.get(i)
        assignee = raw.get("assignee")
        if state is not None and (assignee or state.assignee_id):
            if state.assignee_id == (int(assignee) if assignee else None):
                c["assignee agrees"] += 1
            else:
                note("assignee differs", f"#{i}: replay {state.assignee_id}, json {assignee}")
        if state is not None and state.render is not None:
            r = state.render
            c["render: labels agree" if r.labels == raw.get("labels") else "render: labels differ"] += 1
            c["render: priority agrees" if r.priority == raw.get("priority") else "render: priority differs"] += 1
    for i in sorted(set(created) - {int(k) for k in entries}):
        note("created by replay, missing from json", f"#{i}")

    lines = [f"  {k}: {v}" for k, v in sorted(c.items())]
    for k, items in samples.items():
        lines.append(f"  examples of {k}:")
        lines += [f"    {x}" for x in items]
    return lines


def write_report(replay: Replay, path: str, check: list[str]) -> None:
    kinds = collections.Counter(e.kind for e in replay.events)
    attribution = collections.Counter(e.attribution for e in replay.events)
    issue_kinds = collections.Counter(i.kind.split(" #")[0].split(":")[0] for i in replay.issues)
    with open(path, "w", encoding="utf-8") as f:
        f.write("Events by kind:\n")
        f.writelines(f"  {k}: {v}\n" for k, v in kinds.most_common())
        f.write("Attribution:\n")
        f.writelines(f"  {k}: {v}\n" for k, v in attribution.most_common())
        f.write("Counters:\n")
        f.writelines(f"  {k}: {v}\n" for k, v in sorted(replay.stats.items()))
        f.write("Check against the legacy JSON:\n")
        f.writelines(line + "\n" for line in check)
        f.write("Issues by kind:\n")
        f.writelines(f"  {k}: {v}\n" for k, v in issue_kinds.most_common())
        f.write("Issues:\n")
        for i in replay.issues:
            f.write(f"  {i.message_id} {inference_time(i.at)} {i.kind}\n      {i.text[:200]!r}\n")


def inference_time(at: float) -> str:
    import datetime  # pylint: disable=import-outside-toplevel
    return datetime.datetime.fromtimestamp(at, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m taskbot.feed.replay", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prefix", required=True, help="the bot's command prefix, e.g. '~bug'")
    parser.add_argument("--snapshot", required=True, help="a copy of the old bot's JSON, to check against")
    parser.add_argument("feed", help="JSON-lines file from taskbot.feed.download")
    parser.add_argument("events", help="where to write the events (JSON lines)")
    parser.add_argument("report", help="where to write the report")
    args = parser.parse_args(argv)

    with open(args.snapshot, encoding="utf-8") as f:
        snapshot: dict[str, Any] = json.load(f)
    labels = set(snapshot.get("labels") or [])
    for raw in snapshot["entries"].values():
        labels.update(raw.get("labels") or [])
    authors = {int(k): int(v.get("author") or 0) for k, v in snapshot["entries"].items()}
    replay = Replay(args.prefix, sorted(labels), dict(snapshot.get("complexities") or {}), authors)
    replay.run(parse.load(args.feed))
    with open(args.events, "w", encoding="utf-8") as f:
        for e in replay.events:
            f.write(json.dumps(asdict(e), ensure_ascii=False) + "\n")
    write_report(replay, args.report, check_against_snapshot(replay, snapshot))
    print(f"{len(replay.events)} events, {len(replay.issues)} issues; see {args.report}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
