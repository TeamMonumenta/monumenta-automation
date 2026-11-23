"""Reading feed-channel messages: the bot's replies, its entry renders, and commands.

Everything here is about one message at a time; `replay` puts them in order and
decides which command caused which reply.

The old bot (in git from 2019-04-19 to `ea622b8b`) never used Discord replies,
but almost everything it said names the entry: `Bug #12 marked as fixed`,
`#12 created successfully`, and so on. After every change it also posted the
entry as it then looked (the same text as the tracking message), which this
module parses back into fields.
"""

import datetime
import json
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Optional

from ..inference import snowflake_time

# --- Messages ------------------------------------------------------------------------


@dataclass
class FeedMessage:
    id: int
    at: float
    author_id: int
    author_name: str
    is_bot: bool
    content: str
    attachments: list[str] = field(default_factory=list[str])
    embed_images: list[str] = field(default_factory=list[str])
    mentions: list[int] = field(default_factory=list[int])
    # The bot ignored edits, so an edited command's text may not be what it acted on.
    edited: bool = False
    # Names (username, global display name) of the author and anyone mentioned, by id.
    names: dict[int, list[str]] = field(default_factory=dict[int, list[str]])


def from_api(raw: dict[str, Any]) -> FeedMessage:
    author: dict[str, Any] = raw.get("author") or {}
    embeds: list[dict[str, Any]] = raw.get("embeds") or []
    images: list[str] = []
    for e in embeds:
        img: dict[str, Any] = e.get("image") or {}
        if img.get("url"):
            images.append(str(img["url"]))
    attachments: list[dict[str, Any]] = raw.get("attachments") or []
    mentions: list[dict[str, Any]] = raw.get("mentions") or []
    names: dict[int, list[str]] = {}
    for user in [author, *mentions]:
        found = [str(user[k]) for k in ("username", "global_name") if user.get(k)]
        if user.get("id") and found:
            names[int(user["id"])] = found
    return FeedMessage(
        id=int(raw["id"]), at=snowflake_time(int(raw["id"])),
        author_id=int(author.get("id") or 0),
        author_name=str(author.get("global_name") or author.get("username") or ""),
        is_bot=bool(author.get("bot", False)), content=str(raw.get("content") or ""),
        attachments=[str(a["url"]) for a in attachments if a.get("url")],
        embed_images=images,
        mentions=[int(m["id"]) for m in mentions],
        edited=bool(raw.get("edited_timestamp")), names=names)


def load(path: str) -> Iterator[FeedMessage]:
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield from_api(json.loads(line))


# --- Prefix matching, as in the old bot's common.py -------------------------------------


def get_list_match(item: str, options: list[str]) -> Optional[str]:
    low = item.lower()
    match: Optional[str] = None
    for x in options:
        if x.lower().startswith(low):
            if x.lower() == low:
                return x
            if match is None:
                match = x
            else:
                return None
    return match


# --- Command sets over time ------------------------------------------------------------
# From the old bot's git history: (first date in effect, command list in its dict order).
# Dict order matters because get_list_match takes the first prefix match.

_MAIN_BASE = ["add", "report", "get", "roulette", "search", "dsearch", "isearch", "reject", "edit",
              "append", "fix", "unfix", "prune", "import", "repost", "addlabel", "test"]


def _main_after(when: str) -> list[str]:
    cmds = list(_MAIN_BASE)
    if when < "2019-05-06":
        cmds.remove("add")
        cmds.remove("isearch")
        return cmds
    if when < "2019-05-07":
        cmds.remove("isearch")
        return cmds
    if when >= "2019-05-23":
        cmds.insert(cmds.index("addlabel"), "stats")
    if when >= "2019-05-28":
        i = cmds.index("import")
        cmds[i:i] = ["notify", "send_notifications"]
    if when >= "2019-11-08":
        cmds += ["assign", "unassign", "list_assigned", "ping_assigned"]
    if when >= "2019-11-26":
        cmds.insert(cmds.index("reject"), "asearch")
        cmds.insert(cmds.index("addlabel"), "astats")
        cmds.insert(cmds.index("reject"), "rsearch")
    if when >= "2020-04-29":
        cmds.insert(cmds.index("test"), "dellabel")
    if "2020-06-18" <= when < "2020-11-21":
        cmds.append("post_priority_list")
    if when >= "2020-11-21":
        cmds += ["kanboard_create", "kanboard_update_all", "busty_debug"]
    if when >= "2021-09-04":
        cmds.insert(cmds.index("search"), "iroulette")
    if when >= "2022-12-25":
        cmds.insert(cmds.index("import"), "sync")
    if when >= "2024-07-18":
        cmds.insert(cmds.index("reject"), "delete")
    return cmds


def main_commands(at: float) -> list[str]:
    return _main_after(day(at))


def interactive_commands(at: float) -> list[str]:
    today = day(at)
    cmds = ["reject", "edit", "append", "fix", "unfix"]
    if today >= "2019-11-15":
        cmds += ["assign", "unassign"]
    if today >= "2019-05-15":
        cmds.append("help")
    cmds.append("next")
    if today >= "2019-11-26":
        cmds.append("prev")
    cmds.append("stop")
    return cmds


EDIT_FIELDS = ["description", "label", "image", "author", "priority", "complexity"]


def day(at: float) -> str:
    return datetime.datetime.fromtimestamp(at, datetime.timezone.utc).strftime("%Y-%m-%d")


# --- Human commands --------------------------------------------------------------------


@dataclass
class Command:
    """What a human message asks the bot to do, as far as the text alone tells."""
    name: str               # a main or interactive command name
    args: str
    index: Optional[int]    # explicit entry number, if the command takes one
    interactive: bool = False


INDEXED = {"get", "reject", "edit", "append", "fix", "unfix", "delete", "assign", "unassign"}


def parse_main(msg: FeedMessage, prefix: str) -> Optional[Command]:
    """A `~bug <cmd> ...` command, or None if the bot would ignore the message."""
    part = msg.content.split(maxsplit=2)
    if not part or get_list_match(part[0].strip(), [prefix]) is None:
        return None
    # The four-character minimum (to share the channel with other bots) came on 2019-09-26.
    if len(part) < 2 or (len(part[0].strip()) < 4 and day(msg.at) >= "2019-09-26"):
        return Command("usage", "", None)
    name = get_list_match(part[1].strip(), main_commands(msg.at))
    if name is None:
        return Command("usage", "", None)
    args = part[2].strip() if len(part) > 2 else ""
    return Command(name, args, _leading_index(args) if name in INDEXED else None)


def parse_interactive(msg: FeedMessage) -> Optional[Command]:
    """A response inside an interactive session, or None if it isn't one."""
    part = msg.content.split(maxsplit=1)
    if not part:
        return None
    name = get_list_match(part[0].strip(), interactive_commands(msg.at))
    if name is None:
        return None
    return Command(name, part[1].strip() if len(part) > 1 else "", None, interactive=True)


def _leading_index(args: str) -> Optional[int]:
    first = args.split(maxsplit=1)
    if not first:
        return None
    try:
        return int(first[0])
    except ValueError:
        return None


# --- Bot replies ------------------------------------------------------------------------


@dataclass
class Reply:
    kind: str
    index: Optional[int] = None
    detail: str = ""
    count: Optional[int] = None
    render: Optional["Render"] = None


# "Bug #5 rejected", "Bug report #5 rejected", "Suggestion #5 rejected", "#5 created ..."
_ACTION_RE = re.compile(
    r"^(?:[A-Z][a-z]+(?: report)? )?#(\d+) (created successfully|updated successfully|edited|"
    r"marked as fixed|unmarked as fixed|rejected|unassigned|is already unassigned|"
    r"deleted\.|assigned to (.*))", re.DOTALL)
_ACTION_KIND = {
    "created successfully": "created", "updated successfully": "updated", "edited": "appended",
    "marked as fixed": "fixed", "unmarked as fixed": "unfixed", "rejected": "rejected",
    "unassigned": "unassigned", "is already unassigned": "error", "deleted.": "deleted",
}
# Since the 2022 rewrite the entry is indented (an f-string inside a method).
_NOTIFIED_RE = re.compile(r"^<@!?(\d+)> Your \w+ was updated:\n *")
_SIMPLE: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^Started interactive session with (\d+) entries"), "session_started"),
    (re.compile(r"^No results to display"), "session_empty"),
    (re.compile(r"^No more results to display"), "session_ended"),
    (re.compile(r"^Iteration aborted"), "session_ended"),
    (re.compile(r"^Interactive session aborted due to inactivity"), "session_ended"),
    (re.compile(r"^Nothing to go back to"), "nav_noop"),
    (re.compile(r"^Reached beginning of list"), "nav_noop_partial"),
    (re.compile(r"^Valid responses are"), "interactive_help"),
    (re.compile(r"^To see these options again"), "interactive_help"),
    (re.compile(r"^Label (.+) added successfully$"), "label_added"),
    (re.compile(r"^Label (.+) removed successfully from (\d+) "), "label_removed"),
    (re.compile(r"^(\d+) (?:entries|bugs|suggestions) pruned successfully"), "pruned"),
    (re.compile(r"^(\d+) (?:entries|bugs|suggestions) reposted successfully"), "reposted"),
    (re.compile(r"^(\d+) (?:entries|bugs|suggestions) from channel (.*) imported successfully"),
     "imported"),
    (re.compile(r"^(\d+) notifications processed successfully"), "notifications_sent"),
    (re.compile(r"^You \*\*will\*\* be notified"), "notify_on"),
    (re.compile(r"^You will __not__ be notified"), "notify_off"),
    (re.compile(r"^\*\*ERROR\*\*"), "exception"),
    (re.compile(r"^```Traceback"), "traceback"),
    (re.compile(r"^```"), "exception_cont"),
    (re.compile(r"^<@!?(\d+)>$"), "error_ping"),
]


def classify_reply(msg: FeedMessage) -> Reply:
    text = msg.content
    m = _ACTION_RE.match(text)
    if m:
        verb = m.group(2)
        if verb.startswith("assigned to "):
            return Reply("assigned", int(m.group(1)), detail=m.group(3) or "")
        return Reply(_ACTION_KIND[verb], int(m.group(1)))
    n = _NOTIFIED_RE.match(text)
    if n:
        render = parse_render(text[n.end():])
        if render is not None:
            return Reply("notified", render.index, detail=n.group(1), render=render)
    render = parse_render(text)
    if render is not None:
        return Reply("render", render.index, render=render)
    for pattern, kind in _SIMPLE:
        m = pattern.match(text)
        if m:
            groups = m.groups()
            count = int(groups[0]) if groups and groups[0] and groups[0].isdigit() else None
            detail = groups[0] if groups and kind.startswith("label") else ""
            if kind == "error_ping":
                count = None
                detail = groups[0]
            return Reply(kind, None, detail=detail, count=count)
    return Reply("other")


# --- Entry renders -----------------------------------------------------------------------


@dataclass
class Render:
    index: int
    labels: list[str]
    priority: str
    author_name: str
    complexity_emoji: str
    assignee_name: Optional[str]
    description: str
    closed: bool
    close_reason: Optional[str]


_HEADER_RE = re.compile(r"^(~~)?`\n?#(\d+) \[([^\]\n]*) - ([^\]\n]*)\] ?([^`\n]*)`( [^\n]*)?\n")
_ASSIGNED_RE = re.compile(r"^`Assigned: `?(?:<@!?(\d+)>|([^`\n]*))`?\n")
_REACTIONS_RE = re.compile(r"\n(?:\S+ \d+ *)+$")
_CLOSED_SEP = "~~\nClosed: "


def parse_render(text: str) -> Optional[Render]:
    m = _HEADER_RE.match(text)
    if not m:
        return None
    closed = m.group(1) is not None
    rest = text[m.end():]
    close_reason: Optional[str] = None
    if closed:
        cut = rest.rfind(_CLOSED_SEP)
        if cut < 0:
            return None
        close_reason = rest[cut + len(_CLOSED_SEP):]
        rest = rest[:cut]
    assignee: Optional[str] = None
    a = _ASSIGNED_RE.match(rest)
    if a:
        assignee = a.group(1) or a.group(2)
        rest = rest[a.end():]
    # Interactive and fix/reject renders include reaction counts and sometimes a link.
    rest = re.sub(r"\nhttps://discord\.com/channels/\d+/\d+/\d+$", "", rest)
    rest = _REACTIONS_RE.sub("", rest)
    return Render(index=int(m.group(2)), labels=[x for x in m.group(3).split(",") if x],
                  priority=m.group(4), author_name=m.group(5).strip(),
                  complexity_emoji=(m.group(6) or "").strip(), assignee_name=assignee,
                  description=rest, closed=closed, close_reason=close_reason)
