"""The tracking-channel publishing rules and reaction bookkeeping in bot.py.

Discord itself is replaced by small fakes for a channel and its messages; this
checks what gets sent, edited or left alone, not how Discord displays it.
"""

import os
import sqlite3
import types
from typing import Any, Optional

import aiohttp
import discord
import pytest

from conftest import ALICE, HELPER, TEAM, Harness
from taskbot.bot import ChannelResponder, Notice, TaskBot, notice_lines
from taskbot.slash import _Form, register_slash_commands
from taskbot.models import Actor


def _not_found() -> discord.NotFound:
    return discord.NotFound(types.SimpleNamespace(status=404, reason="Not Found"), "Unknown Message")  # type: ignore[arg-type]


class FakeMessage:
    def __init__(self, mid: int, content: str):
        self.id = mid
        self.content = content
        self.embeds: list[Any] = []
        self.reactions: list[Any] = []
        self.edits = 0
        self.added: list[str] = []

    async def edit(self, content: str, embeds: list[Any], **_: Any) -> "FakeMessage":
        self.content = content
        self.embeds = embeds
        self.edits += 1
        return self

    async def add_reaction(self, emoji: str) -> None:
        self.added.append(emoji)


class FakeChannel:
    def __init__(self) -> None:
        self.messages: dict[int, FakeMessage] = {}
        self.next_id = 900
        self.sends = 0

    async def fetch_message(self, mid: int) -> FakeMessage:
        if mid not in self.messages:
            raise _not_found()
        return self.messages[mid]

    async def send(self, content: str, **_: Any) -> FakeMessage:
        self.next_id += 1
        self.sends += 1
        msg = FakeMessage(self.next_id, content)
        self.messages[msg.id] = msg
        return msg


@pytest.fixture
def bot(h: Harness, monkeypatch: pytest.MonkeyPatch) -> tuple[TaskBot, FakeChannel]:
    b = TaskBot(h.config, h.service, h.charts)
    channel = FakeChannel()
    monkeypatch.setattr(b, "_tracking_channel", lambda: channel)
    monkeypatch.setattr(b, "user_name", {ALICE: "Alice"}.get)
    return b, channel


def _actor(uid: int, priv: int, source: str = "discord") -> Actor:
    return Actor(id=uid, name=f"user{uid}", privilege=priv, source=source)


async def test_send_then_edit_only_when_changed(h: Harness, bot: tuple[TaskBot, FakeChannel]) -> None:
    b, channel = bot
    e = h.service.add(_actor(ALICE, 0), "a report with enough words", ["quest"])
    await b.sync_entry(e.id)
    entry = h.store.get(e.id)
    assert entry is not None and entry.message_id is not None and channel.sends == 1
    msg = channel.messages[entry.message_id]
    assert msg.content.startswith("`#1 [quest - N/A] Alice`") and msg.added == ["\U0001f44d"]
    assert h.store.dirty_entry_ids() == []
    await b.sync_entry(e.id)
    assert msg.edits == 0
    h.service.edit(_actor(TEAM, 2), entry, "priority", "High")
    assert h.store.dirty_entry_ids() == [1]
    await b.sync_entry(e.id)
    assert msg.edits == 1 and "High" in msg.content and channel.sends == 1


async def test_deleted_message_of_open_entry_is_reposted(h: Harness, bot: tuple[TaskBot, FakeChannel]) -> None:
    b, channel = bot
    e = h.service.add(_actor(ALICE, 0), "a report with enough words", ["quest"])
    await b.sync_entry(e.id)
    channel.messages.clear()
    await b.sync_entry(e.id)
    entry = h.store.get(e.id)
    assert channel.sends == 2 and entry is not None and entry.message_id in channel.messages


async def test_closed_entries_are_not_reposted(h: Harness, bot: tuple[TaskBot, FakeChannel]) -> None:
    b, channel = bot
    e = h.service.add(_actor(ALICE, 0), "a report with enough words", ["quest"])
    await b.sync_entry(e.id)
    entry = h.store.get(e.id)
    assert entry is not None
    h.service.fix(_actor(TEAM, 2), entry)
    await b.sync_entry(e.id)  # still in the channel: edited to the closed rendering
    assert entry.message_id is not None
    assert channel.messages[entry.message_id].content.startswith("~~")
    # Message gone (pruned by hand): forget it, don't post a closed entry again
    channel.messages.clear()
    await b.sync_entry(e.id)
    entry = h.store.get(e.id)
    assert entry is not None and entry.message_id is None and channel.sends == 1
    await b.sync_entry(e.id)
    assert channel.sends == 1


async def test_reaction_events_adjust_counts(h: Harness, bot: tuple[TaskBot, FakeChannel]) -> None:
    b, _ = bot
    e = h.service.add(_actor(ALICE, 0), "a report with enough words", ["quest"])
    await b.sync_entry(e.id)
    entry = h.store.get(e.id)
    assert entry is not None and entry.message_id is not None

    def payload(emoji: str, channel_id: Optional[int] = None) -> Any:
        return types.SimpleNamespace(channel_id=channel_id or h.config.channel_id,
                                     message_id=entry.message_id, emoji=emoji)
    await b.on_raw_reaction_add(payload("👍"))
    await b.on_raw_reaction_add(payload("👍"))
    await b.on_raw_reaction_add(payload("🎉"))
    await b.on_raw_reaction_add(payload("👍", channel_id=12345))  # another channel: ignored
    await b.on_raw_reaction_remove(payload("🎉"))
    assert [(r.emoji, r.count) for r in h.store.reactions(e.id)] == [("👍", 2)]
    await b.on_raw_reaction_clear(payload("👍"))
    assert h.store.reactions(e.id) == []


async def test_api_changes_are_published_and_noted_in_the_feed(h: Harness,
                                                               bot: tuple[TaskBot, FakeChannel]) -> None:
    b, channel = bot
    e = h.service.add(_actor(ALICE, 0, source="api"), "a report with enough words", ["quest"])
    h.service.add(_actor(ALICE, 0), "another report with enough words", ["quest"])
    entry = h.store.get(e.id)
    assert entry is not None
    h.service.fix(_actor(TEAM, 2, source="api"), entry)
    # The game plugin uses a service token
    game = Actor(id=0, name="Alex", privilege=2, source="api", source_ref="r1 service:shards-play",
                 mc_uuid="00000000-0000-0000-0000-000000000001")
    h.service.append(game, entry, "more detail from the game")
    # Only API changes get a feed line; Discord commands already show in the feed
    assert notice_lines(b._notices, h.config) == [  # pylint: disable=protected-access
        "user2001 created bug #1 (API)", "user1002 fixed bug #1 (API)", "Alex appended bug #1 (in game)"]
    # ... and the API's change is published like any other
    assert 1 in h.store.dirty_entry_ids()
    await b.sync_entry(1)
    assert h.store.dirty_entry_ids() == [2] and channel.sends == 0  # closed before ever posted


async def test_change_during_publish_is_not_lost(h: Harness, bot: tuple[TaskBot, FakeChannel],
                                                 monkeypatch: pytest.MonkeyPatch) -> None:
    b, channel = bot
    e = h.service.add(_actor(ALICE, 0), "a report with enough words", ["quest"])
    await b.sync_entry(e.id)
    entry = h.store.get(e.id)
    assert entry is not None
    h.service.edit(_actor(TEAM, 2), entry, "priority", "High")

    real_fetch = channel.fetch_message

    async def fetch_and_meanwhile_edit(mid: int) -> FakeMessage:
        # Someone changes the entry while the publisher is waiting on Discord
        current = h.store.get(e.id)
        assert current is not None
        h.service.edit(_actor(TEAM, 2), current, "priority", "Low")
        monkeypatch.setattr(channel, "fetch_message", real_fetch)
        return await real_fetch(mid)
    monkeypatch.setattr(channel, "fetch_message", fetch_and_meanwhile_edit)
    await b.sync_entry(e.id)
    # The publish rendered the pre-change row, so the entry must still be marked unpublished
    assert h.store.dirty_entry_ids() == [e.id]
    await b.sync_entry(e.id)
    assert h.store.dirty_entry_ids() == []
    assert entry.message_id is not None and "Low" in channel.messages[entry.message_id].content


class FakeInteraction:
    """Just enough of discord.Interaction for the slash commands."""

    def __init__(self, user_id: int, name: str):
        self.id = 777000 + user_id
        self.user = types.SimpleNamespace(id=user_id, display_name=name)
        self.sent: list[str] = []
        self.done = False
        self.form: Any = None
        outer = self

        class Response:
            def is_done(self) -> bool:
                return outer.done

            async def defer(self, **_: Any) -> None:
                outer.done = True

            async def send_message(self, text: str, **kwargs: Any) -> None:
                assert kwargs.get("ephemeral")
                outer.done = True
                outer.sent.append(text)

            async def send_modal(self, form: Any) -> None:
                outer.done = True
                outer.form = form

        class Followup:
            async def send(self, text: str, **kwargs: Any) -> None:
                assert kwargs.get("ephemeral")
                outer.sent.append(text)

        self.response = Response()
        self.followup = Followup()


def _slash(b: TaskBot, *path: str) -> Any:
    cmd: Any = b.tree.get_command(path[0], guild=discord.Object(id=b.config.guild_id))
    for name in path[1:]:
        cmd = cmd.get_command(name)
    return cmd


@pytest.fixture
def slash(h: Harness, bot: tuple[TaskBot, FakeChannel], monkeypatch: pytest.MonkeyPatch) -> TaskBot:
    b, _ = bot
    monkeypatch.setattr(b, "resolve_member", h.port.resolve_member)
    register_slash_commands(b)  # normally at login
    return b


async def test_slash_command_shape(slash: TaskBot) -> None:
    assert len(_slash(slash, "bug").commands) <= 25   # Discord's limit
    assert _slash(slash, "bug_description_search") is None and _slash(slash, "bug", "search", "description")


async def test_slash_forms(h: Harness, slash: TaskBot) -> None:
    b = slash
    # Reports are typed into a form. A refused one gives the text back to copy
    alice = FakeInteraction(ALICE, "Alice")
    await _slash(b, "bug", "report").callback(alice, image=None)
    submit = FakeInteraction(ALICE, "Alice")
    await alice.form._submitted(submit, "too short", "")  # pylint: disable=protected-access
    assert submit.sent == ["Description must contain at least 5 words", "What you wrote:\n```\ntoo short\n```"]
    # A description starting with a label's name stays whole when labels come separately
    submit = FakeInteraction(ALICE, "Alice")
    await alice.form._submitted(submit, "quest givers vanish after the reset today\nand stay gone",  # pylint: disable=protected-access
                                "boss")
    assert submit.sent == ["#1 created successfully"]
    e = h.store.get(1)
    assert e is not None and e.labels == ["boss"] and e.description == \
        "quest givers vanish after the reset today\nand stay gone"

    # Forms are only offered to those who may use them
    bob = FakeInteraction(2002, "Bob")
    await _slash(b, "bug", "edit", "description").callback(bob, number=1)
    assert bob.sent == ["You do not have permission to edit description for entry #1"] and bob.form is None
    await _slash(b, "bug", "append").callback(alice, number=1)
    submit = FakeInteraction(ALICE, "Alice")
    await alice.form._submitted(submit, "ask <@1234567890123456789>", "")  # pylint: disable=protected-access
    assert submit.sent[0] == "Please do not include pings in your bug" and "ask <@" in submit.sent[1]
    submit = FakeInteraction(ALICE, "Alice")
    await alice.form._submitted(submit, "second line\nthird line", "")  # pylint: disable=protected-access
    e = h.store.get(1)
    assert e is not None and e.description.endswith("and stay gone\nsecond line\nthird line")

    # A description form opened before a redaction can't put the hidden text back
    await _slash(b, "bug", "edit", "description").callback(alice, number=1)
    h.service.redact(_actor(HELPER, 1), h.service.get_entry(1))
    submit = FakeInteraction(ALICE, "Alice")
    await alice.form._submitted(submit, alice.form._text.default, "")  # pylint: disable=protected-access
    assert "was redacted while the form was open" in submit.sent[0]
    e = h.store.get(1)
    assert e is not None and e.description == "redacted"


async def test_slash_commands_are_the_text_commands(h: Harness, slash: TaskBot) -> None:
    b = slash
    h.service.add(_actor(ALICE, 0), "quest givers vanish after the reset today", ["quest"])
    # Same rules and replies as the text commands, sent privately
    bob = FakeInteraction(2002, "Bob")
    await _slash(b, "bug", "fix").callback(bob, number=1, reason=None)
    assert bob.sent == ["You do not have permission to fix #1"]
    await _slash(b, "bug", "send_notifications").callback(bob)
    assert bob.sent[-1] == "You do not have permission to use this command"
    team = FakeInteraction(TEAM, "Team")
    await _slash(b, "bug", "edit", "priority").callback(team, number=1, priority="high")
    await _slash(b, "bug", "fix").callback(team, number=1, reason="all better")
    assert team.sent[-1] == "Bug #1 marked as fixed"
    e = h.store.get(1)
    assert e is not None and e.priority == "High" and e.closed_by == TEAM and e.close_reason == "all better"

    await _slash(b, "bug", "redact").callback(team, number=1)
    await _slash(b, "bug", "redacted").callback(team, number=1)
    assert "quest givers vanish" in team.sent[-1]
    alice = FakeInteraction(ALICE, "Alice")
    await _slash(b, "bug", "redacted").callback(alice, number=1)
    assert alice.sent[-1] == "You do not have permission to use this command"

    # Their replies are private, so their changes get a line in the feed, as API changes do
    assert notice_lines(b._notices, h.config) == [  # pylint: disable=protected-access
        "Team edited priority bug #1 (/bug)", "Team fixed bug #1 (/bug)", "Team redacted bug #1 (/bug)"]

    # Commands that reply with nothing still answer the deferred interaction
    await _slash(b, "bug", "notify").callback(alice, setting="off")
    assert "__not__" in alice.sent[-1]


def test_notices_are_grouped(h: Harness) -> None:
    notices = [Notice("Ann", "fixed", "API", 3), Notice("Ann", "edited priority", "API", 3),
               Notice("Ann", "fixed", "API", 5), Notice("Bo", "fixed", "/bug", 4),
               Notice("Ann", "fixed", "API", 5)]
    assert notice_lines(notices, h.config) == [
        "Ann fixed bug #3 (API)", "Ann edited priority bug #3 (API)", "Ann fixed bug #5 (API)",
        "Bo fixed bug #4 (/bug)", "Ann fixed bug #5 (API)"]
    # Runs group, and order is kept: fixed, reopened, fixed again reads that way
    run = [Notice("Ann", "fixed", "API", i) for i in range(1, 4)]
    assert notice_lines(run + [Notice("Ann", "reopened", "API", 1), Notice("Ann", "fixed", "API", 1)],
                        h.config) == ["Ann fixed bugs #1, #2, #3 (API)", "Ann reopened bug #1 (API)",
                                      "Ann fixed bug #1 (API)"]
    bulk = notice_lines([Notice("Ann", "fixed", "API", i) for i in range(120)], h.config)
    assert len(bulk) == 3 and all(len(line) < 1000 for line in bulk)


async def test_notices_wait_out_an_outage(bot: tuple[TaskBot, FakeChannel],
                                          monkeypatch: pytest.MonkeyPatch) -> None:
    b, _ = bot
    sent: list[str] = []

    class Feed(discord.abc.Messageable):
        async def _get_channel(self) -> Any:
            return self

    async def down(content: str, **_: Any) -> None:
        raise aiohttp.ClientConnectionError("no network")

    async def up(content: str, **_: Any) -> None:
        sent.append(content)
    channel = Feed()
    monkeypatch.setattr(b, "get_channel", lambda _id: channel)
    b._notices = [Notice("Ann", "fixed", "API", 3)]  # pylint: disable=protected-access
    monkeypatch.setattr(channel, "send", down)
    await b._flush_notices()  # pylint: disable=protected-access
    b._notices.append(Notice("Ann", "fixed", "API", 4))  # pylint: disable=protected-access
    monkeypatch.setattr(channel, "send", up)
    await b._flush_notices()  # pylint: disable=protected-access
    assert sent == ["Changes made outside this channel:\nAnn fixed bugs #3, #4 (API)"]


async def test_slash_commands_sync_only_when_needed(bot: tuple[TaskBot, FakeChannel],
                                                    monkeypatch: pytest.MonkeyPatch) -> None:
    b, _ = bot
    register_slash_commands(b)  # normally at login
    on_discord: list[str] = []
    syncs: list[int] = []

    async def fetch_commands(**_: Any) -> list[Any]:
        return [types.SimpleNamespace(name=n) for n in on_discord]

    async def sync(**_: Any) -> list[Any]:
        syncs.append(1)
        on_discord[:] = [c.name for c in b.tree.get_commands(guild=discord.Object(id=b.config.guild_id))]
        return list(on_discord)

    monkeypatch.setattr(b.tree, "fetch_commands", fetch_commands)
    monkeypatch.setattr(b.tree, "sync", sync)
    sync_now = b._sync_slash_commands  # pylint: disable=protected-access

    await sync_now()          # first start: Discord has none
    assert len(syncs) == 1 and on_discord == ["bug"]
    await sync_now()          # restart, nothing changed
    assert len(syncs) == 1
    on_discord.remove("bug")  # someone removed one on Discord's side
    await sync_now()
    assert len(syncs) == 2
    b.store.set_meta("slash_commands_sha256", "older code")  # the commands changed
    await sync_now()
    assert len(syncs) == 3

    async def refuse(**_: Any) -> list[Any]:
        raise discord.HTTPException(types.SimpleNamespace(status=429, reason="Too Many"), "slow down")  # type: ignore[arg-type]
    monkeypatch.setattr(b.tree, "sync", refuse)
    b.store.set_meta("slash_commands_sha256", "older code")
    await sync_now()          # logged, not raised; the next start tries again
    assert b.store.get_meta("slash_commands_sha256") == "older code"


async def test_forms_take_what_discord_accepts() -> None:
    async def submitted(*_: Any) -> None:
        return None
    # A few old descriptions are longer than the limit; Discord refuses a form prefilled past it
    long_form = _Form("Edit bug #5", "Description", submitted, default="x" * 1800)
    assert long_form._text.max_length == 1800  # pylint: disable=protected-access
    # The label pick-list holds 25, and an empty one isn't allowed
    assert _Form("Report", "Description", submitted, labels=["a"] * 25)._select is not None  # pylint: disable=protected-access
    for labels in (["a"] * 26, []):
        form = _Form("Report", "Description", submitted, labels=labels)
        assert form._select is None and form._labels_text is not None  # pylint: disable=protected-access


def _http_error(cls: Any, status: int) -> Any:
    return cls(types.SimpleNamespace(status=status, reason="x"), "refused")


async def test_failed_publishes_back_off_or_wait_for_a_change(h: Harness, bot: tuple[TaskBot, FakeChannel],
                                                              monkeypatch: pytest.MonkeyPatch) -> None:
    b, tracking = bot
    feed = FakeChannel()
    monkeypatch.setattr(b, "get_channel", lambda _id: feed)
    monkeypatch.setattr(discord.abc, "Messageable", FakeChannel)
    for _ in range(2):
        h.service.add(_actor(ALICE, 0), "a report with enough words", ["quest"])
    real_sync = b.sync_entry
    failure: list[Exception] = []

    async def sync(entry_id: int) -> None:
        if failure:
            raise failure[0]
        await real_sync(entry_id)
    monkeypatch.setattr(b, "sync_entry", sync)

    # Discord down: the pass stops at the first entry, and the wait doubles up to the cap
    failure.append(_http_error(discord.DiscordServerError, 503))
    assert await b.publish_pass(0) == 30
    assert await b.publish_pass(30) == 60
    assert await b.publish_pass(600) == 900
    assert feed.sends == 0 and tracking.sends == 0

    # Discord refusing one entry: set aside with one line in the feed channel, the rest go on
    failure[0] = _http_error(discord.HTTPException, 400)
    assert await b.publish_pass(900) == 900
    assert feed.sends == 1 and "bugs #1, #2:" in feed.messages[901].content
    failure.clear()
    assert await b.publish_pass(900) == 900   # both set aside, nothing tried
    assert tracking.sends == 0 and feed.sends == 1
    # ... until it changes
    entry = h.store.get(1)
    assert entry is not None
    h.service.edit(_actor(TEAM, 2), entry, "priority", "High")
    assert await b.publish_pass(900) == 0
    assert tracking.sends == 1 and h.store.dirty_entry_ids() == [2]


async def test_only_the_intended_user_is_pinged(bot: tuple[TaskBot, FakeChannel]) -> None:
    b, _ = bot
    allowed: list[discord.AllowedMentions] = []

    class Channel:
        async def send(self, _content: str, **kwargs: Any) -> None:
            allowed.append(kwargs["allowed_mentions"])
    responder = ChannelResponder(b, Channel())  # type: ignore[arg-type]
    # Old entries' text can mention others: only the user meant is pinged
    await responder.send("<@1> Your bug was updated: thanks <@2> @everyone", mentions=(1,))
    await responder.send("<@3> mentioned in a search result")
    to_author, to_nobody = (a.to_dict() for a in allowed)
    assert to_author == {"parse": [], "users": [1]}
    assert to_nobody == {"parse": [], "users": []}


def test_daily_backups_keep_a_week(h: Harness, bot: tuple[TaskBot, FakeChannel]) -> None:
    b, _ = bot
    h.service.add(_actor(ALICE, 0), "a report with enough words", ["quest"])
    for day in range(1, 10):
        b._backup(f"2026-01-{day:02d}")  # pylint: disable=protected-access
    backups = sorted(os.listdir(h.config.resolve("backups")))
    assert backups == [f"tasks-2026-01-{day:02d}.db" for day in range(3, 10)]
    copy = sqlite3.connect(os.path.join(h.config.resolve("backups"), backups[-1]))
    assert copy.execute("SELECT description FROM entries").fetchall() == [("a report with enough words",)]
    copy.close()
