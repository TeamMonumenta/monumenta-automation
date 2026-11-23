"""Shared fixtures: an in-memory instance with fake Discord pieces."""

import os
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Optional

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pylint: disable=wrong-import-position
from taskbot.charts import ChartRenderer
from taskbot.commands import CommandHandler, IncomingMessage, OutFile, Responder
from taskbot.config import InstanceConfig
from taskbot.models import Image, Member
from taskbot.service import Actor, TaskService, UserError
from taskbot.store import TaskStore

OWNER = 302298391969267712
LEAD = 1001
TEAM = 1002
HELPER = 1003
ALICE = 2001   # a regular player
BOB = 2002     # another regular player
OUTSIDER = 2003  # in the guild but can't see the bot channels

ROLE_LEAD = 9001
ROLE_TEAM = 9002
ROLE_HELPER = 9003

LABELS = ["boss", "class", "item", "mob", "quest", "advancement", "build", "plugin", "misc", "cmd"]


def make_config() -> InstanceConfig:
    return InstanceConfig(
        login="x", application_id=1, guild_id=10, bot_input_channel=20, channel_id=30,
        discussion_id=40, prefix="~bug", descriptor_short="bug", descriptor_single="bug",
        descriptor_proper="Bug", descriptor_plural="bugs",
        user_privileges={OWNER: 4},
        group_privileges={ROLE_LEAD: 3, ROLE_TEAM: 2, ROLE_HELPER: 1},
        reactions=["\U0001f44d"],
    )


class Clock:
    def __init__(self, now: float = 1_800_000_000):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@dataclass
class Sent:
    channel: str
    text: str
    images: list[str] = field(default_factory=list[str])
    file: Optional[OutFile] = None
    mentions: tuple[int, ...] = ()


class FakeResponder:
    def __init__(self, log: list[Sent], channel: str = "feed"):
        self.log = log
        self.channel = channel

    async def send(self, text: str, *, images: Sequence[Image] = (),
                   file: Optional[OutFile] = None, mentions: Sequence[int] = ()) -> None:
        self.log.append(Sent(self.channel, text, [i.url for i in images], file, tuple(mentions)))


@dataclass
class FakeUser:
    id: int
    name: str           # username
    display_name: str   # guild nickname (what members are matched by, besides name)
    global_name: str    # global display name (what the old bot rendered)
    roles: list[int] = field(default_factory=list[int])
    can_view: bool = True


USERS = [
    FakeUser(OWNER, "combustible", "Combustible", "Combustible"),
    FakeUser(LEAD, "leadperson", "Lead Nick", "Lead"),
    FakeUser(TEAM, "teamperson", "Team Nick", "Teammate", [ROLE_TEAM]),
    FakeUser(HELPER, "helper", "Helper", "Helper", [ROLE_HELPER]),
    FakeUser(ALICE, "alice", "Alice in Guild", "Alice"),
    FakeUser(BOB, "bob", "Bobby", "Bob"),
    FakeUser(OUTSIDER, "outsider", "Outsider", "Outsider", can_view=False),
    FakeUser(2004, "bobcat", "Bobcat", "Bobcat"),
]
USERS[1].roles.append(ROLE_LEAD)


class FakePort:
    """BotPort + Directory backed by an in-memory guild and tracking channel."""

    def __init__(self, service: TaskService, log: list[Sent]):
        self.service = service
        self.users = {u.id: u for u in USERS}
        self.log = log
        self.tracking: dict[int, int] = {}   # message id -> entry id
        self.next_message_id = 5000
        self.synced: list[int] = []
        self.deleted: list[int] = []
        self.during_refresh: list[Callable[[], object]] = []

    # BotPort
    def user_name(self, user_id: int) -> Optional[str]:
        u = self.users.get(user_id)
        return None if u is None else u.global_name

    def find_user(self, query: str) -> tuple[int, str]:
        try:
            user_id = int(query)
        except ValueError:
            q = query.lower()
            matches = [u for u in self.users.values()
                       if u.display_name.lower().startswith(q) or u.name.lower().startswith(q)]
            if not matches:
                raise UserError(f"User {query!r} not found") from None
            if len(matches) > 1:
                raise UserError("Multiple users match {!r}: {}".format(
                    query, "\n".join(u.name for u in matches))) from None
            user_id = matches[0].id
        name = self.user_name(user_id)
        if name is None:
            raise UserError(f"User {query!r} not found")
        return user_id, name

    def channel(self, channel_id: int) -> Optional[tuple[Responder, str]]:
        if channel_id == 777:
            return FakeResponder(self.log, "other"), "other-channel"
        return None

    async def sync_entry(self, entry_id: int) -> None:
        self.synced.append(entry_id)
        entry = self.service.store.get(entry_id)
        assert entry is not None
        if entry.message_id is None and not entry.is_closed:
            self.next_message_id += 1
            self.tracking[self.next_message_id] = entry_id
            self.service.set_message_id(entry_id, self.next_message_id)
        self.service.store.clear_dirty(entry_id)

    async def refresh_images(self, images: Sequence[Image]) -> None:  # pylint: disable=unused-argument
        # Where commands await Discord before showing an entry: tests make changes here
        while self.during_refresh:
            self.during_refresh.pop(0)()

    async def delete_tracking_message(self, message_id: int) -> bool:
        if message_id in self.tracking:
            del self.tracking[message_id]
            self.deleted.append(message_id)
            return True
        return False

    async def repost(self, responder: Responder) -> None:
        await responder.send("reposted")

    async def keep_images(self, entry_id: int) -> list[str]:  # pylint: disable=unused-argument
        return []

    async def post_image(self, entry_id: int, url: str, path: str, actor: Optional[Actor]) -> None:
        self.service.check_postable(entry_id)
        self.next_message_id += 1
        new_url = f"https://cdn.discordapp.com/attachments/20/{self.next_message_id}/copy.png"
        assert self.service.image_posted(entry_id, url, new_url, path, self.next_message_id, actor)

    async def delete_feed_messages(self, message_ids: Sequence[int]) -> list[int]:
        self.deleted.extend(message_ids)
        return []

    # Directory (API)
    def is_ready(self) -> bool:
        return True

    def resolve_member(self, user_id: int) -> Optional[Member]:
        u = self.users.get(user_id)
        if u is None:
            return None
        from taskbot.service import compute_privilege
        priv = compute_privilege(self.service.config, u.id, u.roles)
        return Member(id=u.id, name=u.display_name, privilege=priv, can_view=u.can_view)


class Harness:
    """A whole instance with fakes, plus helpers to type commands."""

    def __init__(self, tmp_path: str):
        self.config = make_config()
        self.config.config_dir = tmp_path
        self.clock = Clock()
        self.store = TaskStore.open(os.path.join(tmp_path, "tasks.db"))
        self.store.set_label_list(LABELS)
        self.store.set_meta("next_index", "1")
        self.service = TaskService(self.store, self.config, clock=self.clock)
        self.log: list[Sent] = []
        self.port = FakePort(self.service, self.log)
        self.charts = ChartRenderer(self.store, self.config, self.service.now)
        import random
        self.handler = CommandHandler(self.service, self.port, self.charts, rng=random.Random(4))
        self.responder = FakeResponder(self.log)
        self._msg_id = 100

    def privilege_of(self, user_id: int) -> int:
        from taskbot.service import compute_privilege
        u = self.port.users[user_id]
        return compute_privilege(self.config, u.id, u.roles)

    def actor(self, user_id: int) -> Actor:
        u = self.port.users[user_id]
        return Actor(id=u.id, name=u.global_name, privilege=self.privilege_of(user_id))

    async def say(self, user_id: int, content: str, attachments: Sequence[str] = ()) -> list[str]:
        """Type a message in the bot input channel; returns the texts sent in reply."""
        start = len(self.log)
        self._msg_id += 1
        u = self.port.users[user_id]
        msg = IncomingMessage(content=content, author_id=user_id, author_name=u.display_name,
                              privilege=self.privilege_of(user_id), message_id=self._msg_id,
                              attachments=list(attachments))
        await self.handler.handle_message(msg, self.responder)
        return [s.text for s in self.log[start:]]

    async def add(self, user_id: int, text: str, attachments: Sequence[str] = ()) -> int:
        replies = await self.say(user_id, f"~bug add {text}", attachments)
        assert replies[-1].endswith("created successfully"), replies
        return int(replies[-1].split()[0].lstrip("#"))


@pytest.fixture
def h(tmp_path: object) -> Harness:
    return Harness(str(tmp_path))
