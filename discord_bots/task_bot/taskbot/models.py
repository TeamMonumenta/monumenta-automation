"""Plain data objects shared by the store, service, commands and API."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Image:
    url: str
    attachment_id: Optional[int] = None
    refreshed_url: Optional[str] = None
    refreshed_expires_at: Optional[int] = None

    def best_url(self, now: int) -> str:
        """The refreshed URL while it is still valid, else the original."""
        if self.refreshed_url and (self.refreshed_expires_at or 0) > now:
            return self.refreshed_url
        return self.url


@dataclass
class ImageFile:
    """A copy of one of an entry's images on disk (see images.py)."""
    entry_id: int
    url: str
    path: Optional[str]          # relative to the images directory; None until saved
    size: Optional[int]
    checked_at: int              # when it was saved, or last tried
    message_id: Optional[int] = None   # the bot's feed channel message holding it, if any
    missing: bool = False        # Discord no longer has it


@dataclass
class Entry:
    id: int
    description: str
    author_id: int
    priority: str
    complexity: str
    labels: list[str]
    status: str = "open"
    resolution: Optional[str] = None
    close_reason: Optional[str] = None
    closed_at: Optional[int] = None
    closed_by: Optional[int] = None
    duplicate_of: Optional[int] = None
    assignee_id: Optional[int] = None
    redacted: bool = False
    message_id: Optional[int] = None
    pending_notification: bool = False
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    images: list[Image] = field(default_factory=list[Image])
    # In-game reports: the Minecraft player who filed it (author_id is then 0)
    author_mc_uuid: Optional[str] = None
    author_mc_name: Optional[str] = None   # last known name, from the players table
    closed_by_mc_uuid: Optional[str] = None

    @property
    def is_closed(self) -> bool:
        return self.status == "closed"



@dataclass
class Event:
    id: int
    entry_id: int
    at: Optional[int]
    actor_id: Optional[int]
    kind: str
    old_value: Optional[str]
    new_value: Optional[str]
    reason: Optional[str]
    source: str
    source_ref: Optional[str]
    actor_mc_uuid: Optional[str] = None


@dataclass
class Reaction:
    emoji: str
    count: int


@dataclass
class Actor:
    """Whoever is performing an action, with their privilege already resolved.

    `privilege` is the role/user-based level from config (0-4). Entry ownership
    (which grants level 1 on one's own entries) is applied per action by the
    service, since it depends on the entry.
    """
    id: int
    name: str
    privilege: int
    source: str = "discord"           # 'discord' | 'api' | 'system'
    source_ref: Optional[str] = None  # e.g. the Discord message id of the command
    read_only: bool = False           # API tokens minted with the read scope
    # A Minecraft player acting through a service (the game plugin); id is then 0
    mc_uuid: Optional[str] = None
    # The service token in use, if any (e.g. 'shards-play')
    service: Optional[str] = None

    @property
    def is_service(self) -> bool:
        return self.service is not None


SYSTEM_ACTOR = Actor(id=0, name="system", privilege=4, source="system")


@dataclass
class Member:
    id: int
    name: str
    privilege: int
    can_view: bool   # can see the bot input channel, i.e. could use the bot in Discord
