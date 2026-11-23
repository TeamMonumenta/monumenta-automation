"""Who is who: Discord users, Minecraft players, and (later) links between them.

Entries and events record either a Discord user id or a Minecraft player uuid.
Permission questions about whether two of those are the same person, such as
whether someone is the author of an entry and may edit it, ask this module.

Today nothing links accounts, so a Discord user and a Minecraft player are
always different people. When an account link system exists, implement
LinkResolver on top of it and pass it to TaskService; ownership and permission
checks then work across both kinds of account. Players who never link keep
working. Author filters, statistics and notification delivery still treat the
two kinds separately; SCHEMA.md ("Identities") lists them.
"""

from typing import Optional, Protocol

from .models import Actor, Entry


class LinkResolver(Protocol):
    def discord_for_player(self, mc_uuid: str) -> Optional[int]:
        """The Discord user linked to a Minecraft player, if any."""
        ...

    def players_for_discord(self, discord_id: int) -> list[str]:
        """Minecraft players linked to a Discord user."""
        ...


class NoLinks:
    """The default: no accounts are linked."""
    # pylint: disable=unused-argument

    def discord_for_player(self, mc_uuid: str) -> Optional[int]:
        return None

    def players_for_discord(self, discord_id: int) -> list[str]:
        return []


def same_person(actor: Actor, discord_id: Optional[int], mc_uuid: Optional[str],
                links: LinkResolver) -> bool:
    """Whether actor is the person identified by discord_id and/or mc_uuid."""
    if discord_id and actor.id and actor.id == discord_id:
        return True
    if mc_uuid and actor.mc_uuid and actor.mc_uuid == mc_uuid:
        return True
    # Across a link, in either direction
    if mc_uuid and actor.id and links.discord_for_player(mc_uuid) == actor.id:
        return True
    if discord_id and actor.mc_uuid and links.discord_for_player(actor.mc_uuid) == discord_id:
        return True
    return False


def is_author(actor: Actor, entry: Entry, links: LinkResolver) -> bool:
    return same_person(actor, entry.author_id or None, entry.author_mc_uuid, links)


def identity_key(discord_id: Optional[int], mc_uuid: Optional[str]) -> Optional[str]:
    """A string naming one identity, for grouping in statistics: 'discord:<id>' or 'mc:<uuid>'."""
    if discord_id:
        return f"discord:{discord_id}"
    if mc_uuid:
        return f"mc:{mc_uuid}"
    return None
