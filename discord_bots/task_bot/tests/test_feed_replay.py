"""Feed replay on small hand-written conversations shaped like the real channel."""

import datetime
from typing import Optional

from taskbot.feed import parse
from taskbot.feed.parse import FeedMessage
from taskbot.feed.replay import DELETED_USER, Event, Replay
from taskbot.inference import time_to_snowflake

BOT = 568967694452260864
STAFF = 1001
PLAYER = 2002
OTHER = 3003
START = datetime.datetime(2021, 3, 1, tzinfo=datetime.timezone.utc).timestamp()


class Feed:
    def __init__(self, start: float = START) -> None:
        self.t = start
        self.msgs: list[FeedMessage] = []
        self._seq = 0

    def say(self, author: int, content: str, dt: float = 1.0, *, edited: bool = False,
            attachments: Optional[list[str]] = None, mentions: Optional[list[int]] = None) -> FeedMessage:
        self.t += dt
        self._seq += 1
        name = {STAFF: "Staffer", PLAYER: "Player", OTHER: "Other"}.get(author, "Bot")
        msg = FeedMessage(id=time_to_snowflake(self.t) + self._seq, at=self.t, author_id=author,
                          author_name=name, is_bot=author == BOT, content=content,
                          attachments=attachments or [], mentions=mentions or [], edited=edited,
                          names={author: [name]})
        self.msgs.append(msg)
        return msg

    def bot(self, content: str, dt: float = 0.3) -> FeedMessage:
        return self.say(BOT, content, dt)

    def run(self, known_authors: Optional[dict[int, int]] = None) -> Replay:
        replay = Replay("~bug", ["quest", "item", "misc"], {"unknown": ":white_circle:", "easy": ":green_circle:"},
                        known_authors)
        replay.run(sorted(self.msgs, key=lambda m: m.id))
        return replay


def render(index: int, *, priority: str = "N/A", labels: str = "quest", text: str = "Some bug text",
           closed: Optional[str] = None, assignee: Optional[str] = None) -> str:
    body = f"`#{index} [{labels} - {priority}] Player` :white_circle:\n"
    if assignee:
        body += f"`Assigned: {assignee}`\n"
    body += text + "\n👍 3    👎 1    "
    if closed is not None:
        return f"~~{body}~~\nClosed: {closed}"
    return body


def kinds(events: list[Event]) -> list[tuple[str, int, Optional[int]]]:
    return [(e.kind, e.entry_id, e.actor_id) for e in events]


def test_parse_render_variants() -> None:
    r = parse.parse_render(render(12, priority="High", labels="quest,item", closed="Fixed in 1.2\nfor real",
                                  assignee="Staffer"))
    assert r is not None
    assert (r.index, r.labels, r.priority, r.author_name) == (12, ["quest", "item"], "High", "Player")
    assert r.assignee_name == "Staffer"
    assert r.description == "Some bug text"
    assert r.closed and r.close_reason == "Fixed in 1.2\nfor real"
    early = parse.parse_render("`\n#220 [misc - Low] Athena`\nfor some reason\nsecond line")
    assert early is not None and early.description == "for some reason\nsecond line"
    assert parse.parse_render("just chatting about #12") is None


def test_command_sets_follow_history() -> None:
    early = FeedMessage(1, datetime.datetime(2019, 5, 7, tzinfo=datetime.timezone.utc).timestamp(),
                        STAFF, "", False, "~b fix 770 done")
    later = FeedMessage(2, START, STAFF, "", False, "~b fix 770 done")
    cmd = parse.parse_main(early, "~bug")
    assert cmd is not None and (cmd.name, cmd.index) == ("fix", 770)
    cmd = parse.parse_main(later, "~bug")
    assert cmd is not None and cmd.name == "usage"
    # Ambiguous abbreviations match nothing; adding a command can make an old one ambiguous.
    assert [parse.get_list_match(x, parse.main_commands(START)) for x in ("a", "ass", "g", "e", "i")] == \
        [None, "assign", "get", "edit", None]
    assert parse.get_list_match("a", parse.interactive_commands(early.at)) == "append"
    assert parse.get_list_match("a", parse.interactive_commands(START)) is None


def test_fix_and_create_are_attributed() -> None:
    f = Feed()
    f.say(PLAYER, "~bug report quest")              # fails: no description
    f.bot("Must contain both a label and a description")
    f.say(PLAYER, "~bug report quest The quest giver is stuck in a wall", attachments=["https://cdn/x.png"])
    f.bot("#10 created successfully")
    cmd = f.say(STAFF, "~bug fix 10 Moved him out", dt=60)
    f.bot(render(10, closed="Moved him out"))
    f.bot("Bug #10 marked as fixed")
    replay = f.run()
    assert kinds(replay.events) == [("created", 10, PLAYER), ("closed", 10, STAFF)]
    created, closed = replay.events[0], replay.events[1]
    assert created.new == "The quest giver is stuck in a wall"
    assert created.source_ref == f.msgs[2].id
    assert (closed.new, closed.reason, closed.source_ref) == ("fixed", "Moved him out", cmd.id)
    assert not replay.issues


def test_interactive_session() -> None:
    f = Feed()
    f.say(STAFF, "~bug isearch n/a")
    f.bot("Started interactive session with 3 entries")
    f.bot(render(5))
    f.say(PLAYER, "f")                                 # not the session owner: ignored
    f.say(STAFF, "e p h")
    f.bot(render(5, priority="High"))
    f.bot("Bug #5 updated successfully")
    f.say(STAFF, "n")
    f.bot(render(6))
    f.say(STAFF, "rej Not a bug, working as intended")
    f.bot(render(6, closed="Not a bug, working as intended"))
    f.bot("Bug #6 rejected")
    f.say(STAFF, "s")
    f.bot("Iteration aborted")
    f.say(STAFF, "f")                                  # session over: plain chat now
    replay = f.run()
    assert kinds(replay.events) == [("priority", 5, STAFF), ("closed", 6, STAFF)]
    assert (replay.events[0].old, replay.events[0].new) == ("N/A", "High")
    assert replay.events[1].new == "rejected"
    assert all(e.attribution == "matched" for e in replay.events)
    assert not replay.sessions


def test_quick_edits_take_values_from_their_commands() -> None:
    # The old bot handled both commands at once: the first render already shows both
    # changes, and the second shows nothing new.
    f = Feed()
    f.say(STAFF, "~bug isearch n/a")
    f.bot("Started interactive session with 3 entries")
    f.bot(render(5))
    f.say(STAFF, "e l item")
    f.say(STAFF, "e p h", dt=0.2)
    f.bot(render(5, labels="item", priority="High"))
    f.bot("Bug #5 updated successfully")
    f.bot(render(5, labels="item", priority="High"))
    f.bot("Bug #5 updated successfully")
    replay = f.run()
    changes = sorted((e.kind, e.old, e.new) for e in replay.events)
    assert changes == [("labels", ["quest"], ["item"]), ("priority", "N/A", "High")]


def test_typed_labels_match_the_list_of_the_time() -> None:
    # A label seen only later (or in a stray reply) must not win over what the old bot matched
    f = Feed()
    f.bot("Labels must be one of: [quest,item,misc]")
    f.say(STAFF, "~bug edit 5 l que")
    f.bot(render(5, labels="quest"))
    f.bot("Bug #5 updated successfully")
    f.bot("Label que added successfully")
    replay = f.run()
    assert [(e.kind, e.new) for e in replay.events] == [("labels", ["quest"])]


def test_a_quiet_render_corrects_a_lost_edit() -> None:
    # The old bot could lose an edit (two commands overwriting each other); a render with
    # nothing else under way shows the real state, which the next edit starts from
    f = Feed()
    f.bot(render(5))
    f.say(STAFF, "~bug edit 5 p h")
    f.bot(render(5, priority="N/A"))
    f.bot("Bug #5 updated successfully")
    f.say(STAFF, "~bug edit 5 p h")
    f.bot(render(5, priority="High"))
    f.bot("Bug #5 updated successfully")
    replay = f.run()
    assert [(e.old, e.new) for e in replay.events] == [("N/A", "High"), ("N/A", "High")]


def test_reply_ordered_before_its_command() -> None:
    f = Feed()
    f.bot("Bug #7 marked as fixed", dt=1)
    f.say(STAFF, "~bug fix 7", dt=0.2)
    replay = f.run()
    assert kinds(replay.events) == [("closed", 7, STAFF)]
    assert replay.events[0].reason == "Fixed"


def test_edited_command_and_deleted_account() -> None:
    f = Feed()
    f.say(STAFF, "~bug fix 1446", edited=True)          # originally said 1445
    f.bot("Bug #1445 marked as fixed")
    f.say(DELETED_USER, "~bug report item The sword does nothing at all now")
    f.bot("#20 created successfully")
    f.say(DELETED_USER, "~bug fix 20")
    f.bot("Bug #20 marked as fixed")
    replay = f.run(known_authors={20: OTHER})
    assert kinds(replay.events) == [("closed", 1445, STAFF), ("created", 20, OTHER), ("closed", 20, None)]
    assert [e.attribution for e in replay.events] == ["matched_loose", "deleted_account", "deleted_account"]


def test_assign_unassign_on_close() -> None:
    f = Feed()
    f.say(STAFF, "~bug assign 3 <@3003>", mentions=[OTHER])
    f.bot("Bug #3 assigned to Other")
    f.say(OTHER, "~bug fix 3")
    f.bot(render(3, closed="Fixed"))
    f.bot("Bug #3 marked as fixed")
    f.say(OTHER, "~bug unfix 3")
    f.bot("Bug #3 unmarked as fixed")
    replay = f.run()
    assert kinds(replay.events) == [("assigned", 3, STAFF), ("unassigned", 3, OTHER), ("closed", 3, OTHER),
                                    ("reopened", 3, OTHER)]
    assert replay.events[0].new == OTHER
    assert replay.events[1].reason == "closed"
    assert replay.events[3].old == "fixed"


def test_unmatched_reply_is_reported() -> None:
    f = Feed()
    f.say(STAFF, "~bug fix 1")
    f.bot("Bug #2 marked as fixed", dt=30)
    replay = f.run()
    assert kinds(replay.events) == [("closed", 2, None)]
    assert replay.events[0].attribution == "unmatched"
    assert len(replay.issues) == 1


def test_self_assign_and_name_lookup() -> None:
    f = Feed()
    f.say(STAFF, "~bug assign 4")
    f.bot("Bug #4 assigned to [TAG] Staff Nickname")
    f.say(OTHER, "hello")                              # teaches the replay the name "Other"
    f.say(STAFF, "~bug assign 5 oth")
    f.bot("Bug #5 assigned to Other")
    replay = f.run()
    assert [(e.entry_id, e.new) for e in replay.events] == [(4, STAFF), (5, OTHER)]


def test_custom_emoji_reason_comes_from_command() -> None:
    f = Feed()
    f.say(STAFF, "~bug reject 8 political? <:soylitical:1113980127999692951>")
    f.bot(render(8, closed="political? :soylitical:"))
    f.bot("Bug #8 rejected")
    replay = f.run()
    assert replay.events[0].reason == "political? <:soylitical:1113980127999692951>"


def test_deleted_command_uses_json_author() -> None:
    f = Feed()
    f.bot("#30 created successfully")
    replay = f.run(known_authors={30: PLAYER})
    assert kinds(replay.events) == [("created", 30, PLAYER)]
    assert replay.events[0].attribution == "author_from_json"
