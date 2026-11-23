"""Text rendering. The entry and stats formats are the old bot's, character for character."""

import datetime
import json
from collections.abc import Callable, Sequence
from typing import Optional

from .config import InstanceConfig
from .models import Entry, Event, Reaction
from .vocab import COMPLEXITIES, PRIORITIES, priority_rank

MAX_MESSAGE = 2000

# Resolves a user id to the name the old bot showed (the global display name), or None
NameLookup = Callable[[int], Optional[str]]


def format_entry(entry: Entry, config: InstanceConfig, names: NameLookup, *,
                 reactions: Optional[Sequence[Reaction]] = None,
                 mention_assigned: bool = False, include_link: bool = False,
                 duplicates: Sequence[int] = (), max_len: int = MAX_MESSAGE) -> str:
    """Render an entry as the old format_entry did.

    reactions=None leaves the reaction line out (the old include_reactions=False);
    an empty list also renders nothing, as a message without reactions did.
    duplicates are the entries closed as duplicates of this one, listed on a line after
    the description (the old bot had no such line). The line is left out if it doesn't
    fit; otherwise the description is shortened if the whole message would exceed
    max_len, which the old bot would have failed to send.
    """
    def render(description: str, duplicates: Sequence[int]) -> str:
        author_name = ""
        if entry.author_id:
            author_name = names(entry.author_id) or ""
        elif entry.author_mc_uuid:
            author_name = f"{entry.author_mc_name or entry.author_mc_uuid[:8]} (in-game)"

        react_text = ""
        if reactions:
            react_text = "\n"
            for react in reactions:
                react_text += f"{react.emoji} {react.count}    "

        assigned_text = ""
        if entry.assignee_id:
            assignee_name = names(entry.assignee_id)
            if assignee_name is not None:
                if mention_assigned:
                    assigned_text = f"`Assigned: `<@{entry.assignee_id}>\n"
                else:
                    assigned_text = f"`Assigned: {assignee_name}`\n"

        dupes_text = ""
        if duplicates:
            dupes_text = "\n`Duplicates: " + ", ".join(f"#{i}" for i in duplicates) + "`"

        link = ""
        if include_link and entry.message_id is not None:
            link = "\n" + config.entry_link(entry.message_id)

        complexity_emoji = COMPLEXITIES.get(entry.complexity, "")
        text = (f"`#{entry.id} [{','.join(entry.labels)} - {entry.priority}] {author_name}` "
                f"{complexity_emoji}\n{assigned_text}{description}{dupes_text}{react_text}{link}")
        if entry.is_closed:
            text = f"~~{text}~~\nClosed: {entry.close_reason or ''}"
        return text

    text = render(entry.description, duplicates)
    if len(text) > max_len and duplicates:
        text = render(entry.description, ())
    if len(text) > max_len:
        overflow = len(text) - max_len + len(" ...")
        text = render(entry.description[:max(0, len(entry.description) - overflow)] + " ...", ())
        text = text[:max_len]
    return text


def sort_by_priority(entries: Sequence[Entry]) -> list[Entry]:
    """Stable sort by the old priority x complexity table."""
    return sorted(entries, key=lambda e: priority_rank(e.priority, e.complexity))


def format_stats(single: str, open_entries: Sequence[Entry], closed_count: int) -> str:
    priorities, complexities = PRIORITIES, list(COMPLEXITIES)
    stats: dict[str, dict[str, int]] = {p: {c: 0 for c in complexities} for p in priorities}
    total: dict[str, int] = {p: 0 for p in priorities}
    for e in open_entries:
        total[e.priority] = total.get(e.priority, 0) + 1
        stats.setdefault(e.priority, {c: 0 for c in complexities})
        stats[e.priority][e.complexity] = stats[e.priority].get(e.complexity, 0) + 1

    text = f"Current {single} stats:```"
    text += f"{'' : <13}"
    for comp in complexities:
        text += f"{comp.capitalize() : <10}"
    text += f"{'Total' : <10}"
    for item in total:
        text += f"\n{item.ljust(10)} | "
        for comp in stats[item]:
            text += f"{stats[item][comp] : <10}"
        text += f"{total[item] : <10}"
    text += f"\n----------------\nTotal Open : {len(open_entries)}\nClosed     : {closed_count}```"
    return text


def fmt_time(ts: Optional[int]) -> str:
    """Discord timestamp markup, which each viewer sees in their own timezone."""
    return "unknown time" if ts is None else f"<t:{ts}:f>"


def fmt_date(ts: Optional[int]) -> str:
    if ts is None:
        return "unknown"
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d")


def describe_event(ev: Event, names: NameLookup,
                   resolution_name: Callable[[str], str],
                   player_name: Callable[[str], Optional[str]] = lambda _uuid: None) -> str:
    """One line of `history` output."""
    def who(uid: Optional[int]) -> str:
        if uid is None:
            return "unknown"
        # Mentions never ping (the bot sends with mentions off) but render as a name
        return names(uid) or f"<@{uid}>"

    if ev.actor_id is None and ev.actor_mc_uuid:
        actor = f"{player_name(ev.actor_mc_uuid) or ev.actor_mc_uuid[:8]} (in-game)"
    else:
        actor = who(ev.actor_id)
    when = fmt_time(ev.at)
    via = {"discord": "", "legacy": " (imported)"}.get(ev.source, f" (via {ev.source})")
    k = ev.kind
    if k == "created":
        what = "created"
        if ev.source == "legacy":
            # The feed didn't see it created, so the time is an estimate: show the day only
            when = fmt_date(ev.at)
    elif k == "closed":
        what = f"closed as **{resolution_name(ev.new_value or '')}**"
        if ev.reason:
            what += f": {_clip(ev.reason, 200)}"
    elif k == "reopened":
        what = "reopened"
    elif k in ("priority", "complexity", "labels"):
        show = _json_list if k == "labels" else str
        if ev.new_value is None:
            # Only from the feed replay, which can't always tell the value
            what = f"changed the {k}"
        elif ev.old_value is None:
            what = f"set {k} to {show(ev.new_value)}"
        else:
            what = f"set {k} {show(ev.old_value)} -> {show(ev.new_value)}"
    elif k == "description":
        what = "edited the description" if ev.new_value is not None else "edited the description (redacted)"
    elif k == "appended":
        what = f"appended: {_clip(ev.new_value or '(redacted)', 200)}"
    elif k == "image":
        what = "changed the image"
    elif k == "author":
        what = f"changed the author {who(_int(ev.old_value))} -> {who(_int(ev.new_value))}"
    elif k == "assigned":
        what = f"assigned to {who(_int(ev.new_value))}"
    elif k == "unassigned":
        what = "unassigned" + (" (closed)" if ev.reason == "closed" else "")
    elif k == "redacted":
        what = "redacted"
    elif k == "notified":
        what = "notified the author"
    else:
        what = k
    if ev.at is None and ev.source == "legacy" and k != "created":
        when = "before the new bot"
    return f"{when} **{actor}** {what}{via}"


def _int(value: Optional[str]) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def _json_list(value: str) -> str:
    try:
        items = json.loads(value)
    except ValueError:
        return value
    if isinstance(items, list):
        return "[" + ",".join(str(x) for x in items) + "]"  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
    return value


def _clip(text: str, n: int) -> str:
    text = text.replace("\n", " ")
    return text if len(text) <= n else text[:n - 3] + "..."
