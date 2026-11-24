"""The `~bug <command> <args>` text interface.

This module reproduces the old bot's command parsing and replies. It reaches
Discord only through the BotPort and Responder protocols below, which bot.py
implements for real and the tests implement with fakes.
"""

# Every command handler takes (msg, args, responder) whether it uses them or not
# pylint: disable=unused-argument

import json
import random
import re
import traceback
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol

from .charts import ChartError, ChartRenderer
from .config import InstanceConfig
from .formatting import describe_event, format_entry, format_stats, sort_by_priority
from .interactive import InteractiveSession
from .matching import get_list_match, split_string
from .models import Actor, Entry, Image
from .service import (
    EDIT_FIELDS, PRIV_LEAD, PRIV_OWNER, PRIV_TEAM, TaskService, UserError,
)
from .stats import closer_stats, format_closer_stats, resolution_name
from .store import LEGACY_REDACTION, EntryQuery, make_image
from .vocab import COMPLEXITIES, DUPLICATE, PRIORITIES


@dataclass
class OutFile:
    filename: str
    data: bytes


class Responder(Protocol):
    """Sends messages to one channel."""

    async def send(self, text: str, *, images: Sequence[Image] = (),
                   file: Optional[OutFile] = None, mentions: Sequence[int] = ()) -> None:
        """mentions: the users this message may ping; nobody else is, whatever the text."""
        ...


class BotPort(Protocol):
    """Everything the command layer needs from Discord."""

    def user_name(self, user_id: int) -> Optional[str]:
        """The user's global display name (what the old bot showed), None if unknown."""
        ...

    def find_user(self, query: str) -> tuple[int, str]:
        """(user id, display name) for a user id or a guild member name prefix.
        Raises UserError with the old messages when not found or ambiguous."""
        ...

    def channel(self, channel_id: int) -> Optional[tuple[Responder, str]]:
        """(responder, channel name) for another channel, None if unknown."""
        ...

    async def sync_entry(self, entry_id: int) -> None:
        """Send or edit the entry's tracking channel message."""
        ...

    async def refresh_images(self, images: Sequence[Image]) -> None:
        """Get fresh links for images about to be shown, so that sending them right after
        doesn't wait on Discord."""
        ...

    async def delete_tracking_message(self, message_id: int) -> bool:
        """Delete a tracking channel message. False if it no longer exists."""
        ...

    async def repost(self, responder: Responder) -> None:
        """The owner-only `repost`: purge untracked bot messages, resend open entries."""
        ...

    async def keep_images(self, entry_id: int) -> list[str]:
        """Make sure a new or edited entry's images last: save them to disk, and post images
        attached to slash commands (which Discord deletes within a day) in the feed channel.
        Returns notes for whoever added them."""
        ...

    async def post_image(self, entry_id: int, url: str, path: str, actor: Optional[Actor]) -> None:
        """Post a saved image in the feed channel and show that copy from now on (`reupload`).
        Raises UserError when it can't be posted."""
        ...

    async def delete_feed_messages(self, message_ids: Sequence[int]) -> list[int]:
        """Delete the bot's own messages in the feed channel (images of a purged entry).
        Returns those it couldn't delete."""
        ...


# Events from slash commands have source_ref "interaction:<id>"
SLASH_REF_PREFIX = "interaction:"


@dataclass
class IncomingMessage:
    content: str
    author_id: int
    author_name: str          # display name in the guild
    privilege: int
    message_id: int = 0
    attachments: list[str] = field(default_factory=list[str])
    slash: bool = False       # a slash command: message_id is the interaction's id

    def actor(self) -> Actor:
        ref = None
        if self.message_id:
            ref = f"{SLASH_REF_PREFIX}{self.message_id}" if self.slash else str(self.message_id)
        return Actor(id=self.author_id, name=self.author_name, privilege=self.privilege,
                     source="discord", source_ref=ref)


Handler = Callable[[IncomingMessage, str, Responder], Awaitable[None]]

# Order matters to prefix matching; new commands only ever go at the end.
LEGACY_COMMAND_ORDER = (
    "add", "report", "get", "roulette", "iroulette", "search", "dsearch", "isearch", "asearch",
    "rsearch", "delete", "reject", "edit", "append", "fix", "unfix", "prune", "notify",
    "send_notifications", "sync", "import", "repost", "stats", "astats", "addlabel", "dellabel",
    "test", "assign", "unassign", "list_assigned", "ping_assigned", "kanboard_create",
    "kanboard_update_all", "busty_debug",
)
RETIRED_COMMANDS = ("import", "kanboard_create", "kanboard_update_all", "busty_debug")
CSTATS_MINIMUM = 20
NEW_COMMANDS = ("dupe", "history", "cstats", "chart", "context", "redact", "purge", "reupload")
COMMAND_ORDER = tuple(c for c in LEGACY_COMMAND_ORDER if c not in RETIRED_COMMANDS) + NEW_COMMANDS

PRIORITY_HELP = '''
__Available Priorities:__
**Critical**
- Portions of the game are unplayable
- At least a few people are expected to be affected.

**High**
- Significantly impacts the game
- Affects many players but moderator help not required to work around OR affects very few players

**Medium**
- Would be really nice to have
- Either it's not important enough to be high or it is sort of is but requires a ton of work to fix

**Low**
- Worth doing someday when there's time

**Zero**
- Even if this is a good idea, not worth the effort required to make happen.

**N/A**
- No priority assigned'''


@dataclass
class SearchSpec:
    entries: list[Entry]
    labels: list[str]
    priorities: list[str]
    complexities: list[str]
    max_count: int


class CommandHandler:
    def __init__(self, service: TaskService, port: BotPort,
                 charts: Optional[ChartRenderer] = None, rng: Optional[random.Random] = None):
        self.service = service
        self.store = service.store
        self.config: InstanceConfig = service.config
        self.port = port
        self.charts = charts
        self.rng = rng or random.Random()
        self.sessions: list[InteractiveSession] = []
        self.stopping = False
        self.commands: dict[str, Handler] = {name: getattr(self, f"cmd_{name}") for name in COMMAND_ORDER}

    # ------------------------------------------------------------------
    # Shorthands
    # ------------------------------------------------------------------

    @property
    def prefix(self) -> str:
        return self.config.prefix

    @property
    def single(self) -> str:
        return self.config.descriptor_single

    @property
    def plural(self) -> str:
        return self.config.descriptor_plural

    @property
    def proper(self) -> str:
        return self.config.descriptor_proper

    def name_of(self, user_id: int) -> Optional[str]:
        return self.port.user_name(user_id)

    def render(self, entry: Entry, *, include_reactions: bool = False,
               mention_assigned: bool = False, include_link: bool = False) -> str:
        reactions = self.store.reactions(entry.id) if include_reactions else None
        return format_entry(entry, self.config, self.name_of,
                            reactions=reactions, mention_assigned=mention_assigned,
                            include_link=include_link, duplicates=self.store.duplicates_of(entry.id))

    async def show(self, responder: Responder, entry: Entry, **kwargs: bool) -> None:
        """Post an entry as it is now. Callers often hold a copy read before earlier sends,
        and a redaction meanwhile must not be posted, so it is read again, with nothing
        awaited between that and the send (the image links are refreshed first)."""
        await self.port.refresh_images(entry.images)
        current = self.store.get(entry.id)
        if current is None:
            return
        mention = (current.assignee_id,) if kwargs.get("mention_assigned") and current.assignee_id else ()
        await responder.send(self.render(current, **kwargs), images=current.images, mentions=mention)

    async def reply_chunks(self, responder: Responder, text: str) -> None:
        for chunk in split_string(text):
            await responder.send(chunk)

    def open_entries(self) -> list[Entry]:
        return self.store.query(EntryQuery(status="open"))

    async def print_search_results(self, responder: Responder, entries: Sequence[Entry],
                                   limit: int = 15, sort_entries: bool = True,
                                   mention_assigned: bool = False, include_reactions: bool = True,
                                   include_link: bool = False) -> None:
        print_entries = sort_by_priority(entries) if sort_entries else list(entries)
        if len(print_entries) > limit:
            await responder.send(f"Limiting to top {limit} results")
            print_entries = print_entries[:limit]
        for entry in print_entries:
            await self.show(responder, entry, include_reactions=include_reactions,
                            mention_assigned=mention_assigned, include_link=include_link)

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def claims(self, msg: IncomingMessage) -> bool:
        """Whether a message is (probably) for the bot, to decide on a typing indicator."""
        if any(s.author_id == msg.author_id for s in self.sessions):
            return True
        part = msg.content.split(maxsplit=1)
        return bool(part) and get_list_match(part[0].strip(), [self.prefix]) is not None

    async def handle_message(self, msg: IncomingMessage, responder: Responder) -> None:
        """Handle a message in the bot input channel. Never raises."""
        try:
            await self._handle_message(msg, responder)
        except Exception as e:  # pylint: disable=broad-exception-caught
            # As before: ping the author and post the traceback
            await responder.send(f"<@{msg.author_id}>", mentions=(msg.author_id,))
            await responder.send("**ERROR**: ```" + str(e) + "```")
            for chunk in split_string(traceback.format_exc()):
                await responder.send("```" + chunk + "```")

    async def _handle_message(self, msg: IncomingMessage, responder: Responder) -> None:
        # Ongoing interactive sessions get the first look at every message
        for session in self.sessions[:]:
            try:
                if await session.handle_message(msg, responder):
                    return
            except EOFError:
                self.sessions.remove(session)

        part = msg.content.split(maxsplit=2)
        if not msg.content or len(part) < 1:
            return

        if get_list_match(part[0].strip(), [self.prefix]) is None:
            return

        # The length check lets several bots share a channel: the prefix needs 4+ characters
        if len(part) < 2 or len(part[0].strip()) < 4:
            await self.usage(msg, responder)
            return

        # Not a command, so it takes no abbreviation from those people use: `~bug help team`
        if part[1].strip().lower() == "help":
            team = len(part) > 2 and part[2].strip().lower() == "team"
            await self.usage(msg, responder, team=team)
            return

        match = get_list_match(part[1].strip(), self.commands.keys())
        if match is None:
            await self.usage(msg, responder)
            return

        args = part[2].strip() if len(part) > 2 else ""
        await self.run(match, msg, args, responder)

    async def run(self, command: str, msg: IncomingMessage, args: str, responder: Responder) -> None:
        """Run one command, replying with the text of any UserError."""
        try:
            await self.commands[command](msg, args, responder)
        except UserError as e:
            await self.reply_chunks(responder, str(e))

    # ------------------------------------------------------------------
    # Usage
    # ------------------------------------------------------------------

    def usage_text(self, actor: Actor) -> str:
        fmt = {"cstats_minimum": CSTATS_MINIMUM, "prefix": self.prefix, "single": self.single, "plural": self.plural,
               "labels": " ".join(self.store.labels())}
        usage = '''
**Commands everyone can use:**
`{prefix} add [label1,label2,...] <description>`
    Adds a new {single} with the given (optional) label(s)
    Label must be one of: {labels}
    Alias: report

`{prefix} search labels,priorities,limit`
    Searches all {plural} for ones that are tagged with all the specified labels / priorities
    Only show the top #limit results to reduce chatspam
    For example:
        {prefix} search quest,class,high

`{prefix} dsearch <search terms, count>`
    Searches all {single} descriptions for ones that contain all the specified search terms

`{prefix} asearch [author]`
    Finds all {plural} added by self, or author if specified

`{prefix} rsearch <:reaction:>`
    Gets open {plural}, sorted by count of the specified reaction

`{prefix} get <number>`
    Gets the {single} with the specified number

`{prefix} notify [on|off]`
    Toggles whether you get notified of updates to your {plural}

`{prefix} roulette [search terms]`
    Gets a random {single} matching search terms

`{prefix} iroulette [search terms]`
    Starts an interactive search for matching search terms but in random order

`{prefix} stats`
    Gets current {single} statistics

`{prefix} astats`
    Gets current {single} author statistics

**Commands the original {single} author and team members can use:**
`{prefix} reject <number> <reason why>`
    Closes the specified {single} with the given reason

`{prefix} dupe <number> <original number> [note]`
    Closes the specified {single} as a duplicate of the original

`{prefix} edit <number> <description | label | image> [argument]`
    Edits the specified field of the entry

`{prefix} append <number> text`
    Appends text to an existing {single}'s description
'''.format(**fmt)

        if self.service.has_privilege(actor, PRIV_TEAM):
            usage += f"\nTeam members: `{self.prefix} help team` lists the team's commands.\n"
        usage += (f"\nMost commands also work privately as slash commands, `/{self.single} <command>`, "
                  "with replies only you see.")
        return usage

    def team_usage_text(self, actor: Actor) -> str:
        """The team's, leads' and owner's commands, as far as actor may use them."""
        fmt = {"cstats_minimum": CSTATS_MINIMUM, "prefix": self.prefix, "single": self.single, "plural": self.plural}
        if not self.service.has_privilege(actor, PRIV_TEAM):
            return "These commands are for team members"
        usage = '''
**Commands team members can use:**

`{prefix} redact <number>`
    Hides the specified {single}'s text from everyone but the team

`{prefix} history <number>`
    Shows who changed the {single} and when

`{prefix} cstats [days] [minimum]`
    Gets who has closed the most {plural}, overall or in the last few days (0 for overall).
    Overall lists only those with at least {cstats_minimum} closes unless a minimum is given

`{prefix} chart [name]`
    Draws a chart; without a name, lists the available charts

`{prefix} edit <number> [author | priority | complexity ] [argument]`
    Edits the specified field of the entry

`{prefix} fix number [optional explanation]`
    Marks the specified {single} as fixed. Default explanation is simply "Fixed"

`{prefix} unfix <number>`
    Unmarks the specified {single} as fixed

`{prefix} isearch <search terms>`
    Interactive search session

`{prefix} send_notifications`
    Notifies {single} authors about updates to their entries

`{prefix} assign <number> [user]`
    Assigns {single} to self, or user if specified

`{prefix} unassign <number>`
    Unassigns {single}

`{prefix} list_assigned [user | all]`
    Prints out open {plural} that are assigned to you, the specified user, or "all"

`/{single} context <number>`
    Privately shows extra data attached to a {single}, such as where an in-game report was made

`/{single} redacted <number>`
    Privately shows what redaction hid

`{prefix} reupload <number>`
    Posts the saved copies of a {single}'s images again, for when Discord has lost them
'''.format(**fmt)

        if self.service.has_privilege(actor, PRIV_LEAD):
            usage += '''
**Commands only leads can use:**
`{prefix} addlabel <newlabel>`
    Adds a new label

`{prefix} dellabel <label>`
    Removes a label

`{prefix} prune`
    Removes all fixed {plural} from the tracking channel

`{prefix} purge <number>`
    Permanently deletes the specified {single}, its history and anything redacted

`{prefix} ping_assigned channel_id`
    Prints out all open {plural} in specified channel, pinging assigned people
'''.format(**fmt)

        if self.service.has_privilege(actor, PRIV_OWNER):
            usage += '''
**Commands only you can use:**
`{prefix} repost`
    Reposts/edits all known {plural}
'''.format(**fmt)
        return usage

    async def usage(self, msg: IncomingMessage, responder: Responder, team: bool = False) -> None:
        actor = msg.actor()
        await self.reply_chunks(responder, self.team_usage_text(actor) if team else self.usage_text(actor))

    # ------------------------------------------------------------------
    # test
    # ------------------------------------------------------------------

    async def cmd_test(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        actor = msg.actor()
        for level in (4, 3, 2, 1, 0):
            if self.service.has_privilege(actor, level):
                await responder.send(f"Privilege: {level}")
                return
        await responder.send("Privilege: None")

    # ------------------------------------------------------------------
    # Discussion channel: `bug-123` mentions
    # ------------------------------------------------------------------

    async def handle_discussion_message(self, content: str, responder: Responder) -> None:
        pattern = re.compile(r"(" + re.escape(self.config.descriptor_short) + r")-([0-9]+)", re.IGNORECASE)
        found: list[Entry] = []
        for match in pattern.finditer(content):
            entry = self.store.get(int(match.group(2)))
            if entry is not None and entry.message_id is not None and entry not in found:
                found.append(entry)
        links = [f"#{e.id}: {self.config.entry_link(e.message_id or 0)}" for e in found]
        if not links:
            return
        if len(links) > 3:
            await responder.send(
                f"Here are the links to the {self.plural} you mentioned, limited to 3 links:\n"
                + "\n".join(links[:3]))
        elif len(links) == 1:
            await self.show(responder, found[0], include_reactions=True, include_link=True)
        else:
            await responder.send("\n".join(links))

    # ------------------------------------------------------------------
    # add / report
    # ------------------------------------------------------------------

    async def cmd_add(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        if not args:
            raise UserError('''How to submit a {single}:```
{prefix} add [label] <description>
```
Example:```
{prefix} add quest Bihahiahihaaravi refuses to talk to me when I'm wearing a fedora
```
You can also attach an image to your message to include it in the {single}
'''.format(prefix=self.prefix, single=self.single))

        # The first word is labels if it matches any; otherwise the whole text is the description
        part = args.split(maxsplit=1)
        good_labels, failed = self.service.match_labels(part[0])
        if good_labels and failed:
            raise self.service.labels_error()
        description = part[1] if good_labels and len(part) > 1 else args
        await self._create(msg, description, good_labels, responder)

    async def report(self, msg: IncomingMessage, description: str, labels: str,
                     responder: Responder) -> None:
        """The slash command: labels and description come separately, so a description
        that starts with a label's name stays whole."""
        good_labels: list[str] = []
        if labels.strip():
            good_labels, failed = self.service.match_labels(labels)
            if failed or not good_labels:
                raise self.service.labels_error()
        await self._create(msg, description, good_labels, responder)

    async def _create(self, msg: IncomingMessage, description: str, labels: list[str],
                      responder: Responder) -> None:
        images = [make_image(url) for url in msg.attachments]
        entry = self.service.add(msg.actor(), description, labels, images)
        notes = await self.port.keep_images(entry.id) if images else []
        await self.port.sync_entry(entry.id)
        await responder.send(f"#{entry.id} created successfully")
        for note in notes:
            await responder.send(note)

    cmd_report = cmd_add

    # ------------------------------------------------------------------
    # edit / append
    # ------------------------------------------------------------------

    async def cmd_edit(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        part = args.split(maxsplit=2)
        if not args or len(part) < 2:
            raise UserError('''How to edit a {single}:```
{prefix} edit # [description | label | image | author | priority | complexity] edited stuff
```
For example:```
{prefix} edit 5 description Much more detail here
```
'''.format(prefix=self.prefix, single=self.single))

        entry = self.service.get_entry(part[0].strip())
        operation = get_list_match(part[1].strip(), EDIT_FIELDS)
        if operation is None:
            raise UserError("Item to edit must be 'description', 'label', 'image', 'author', "
                            "'priority' or 'complexity'")
        actor = msg.actor()
        self.service.check_edit(actor, entry, operation)

        value: object
        if operation == "description":
            if len(part) < 3:
                raise UserError("You need to actually supply a new description")
            value = part[2].strip()
        elif operation == "label":
            if len(part) < 3:
                raise UserError("You need to actually supply a new label")
            labels, failed = self.service.match_labels(part[2])
            if failed:
                raise self.service.labels_error()
            value = labels
        elif operation == "image":
            if not msg.attachments:
                raise UserError("You need to attach an image")
            value = [make_image(url) for url in msg.attachments]
        elif operation == "author":
            if len(part) < 3:
                raise UserError("You need to actually supply a new author")
            value, _ = self.port.find_user(part[2].strip())
        elif operation == "priority":
            if len(part) < 3:
                raise UserError(PRIORITY_HELP)
            priority = get_list_match(part[2].strip().lower(), PRIORITIES)
            if priority is None:
                raise UserError(f"Priority must be one of: [{','.join(PRIORITIES)}]")
            value = priority
        else:
            complexities = list(COMPLEXITIES)
            complexities_str = ",".join(complexities)
            if len(part) < 3:
                raise UserError(f"Available complexities: [{complexities_str}]")
            complexity = get_list_match(part[2].strip().lower(), complexities)
            if complexity is None:
                raise UserError(f"Complexity must be one of: [{complexities_str}]")
            value = complexity

        entry = self.service.edit(actor, entry, operation, value)
        notes = await self.port.keep_images(entry.id) if operation == "image" else []
        await self.port.sync_entry(entry.id)
        entry = self.service.get_entry(entry.id)
        await self.show(responder, entry, include_reactions=True)
        await responder.send(f"{self.proper} #{entry.id} updated successfully")
        for note in notes:
            await responder.send(note)

    async def cmd_append(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        part = args.split(maxsplit=1)
        if not args or len(part) < 2:
            raise UserError(f"Usage: {self.prefix} append <number> [additional description text]")
        entry = self.service.get_entry(part[0].strip())
        entry = self.service.append(msg.actor(), entry, part[1])
        await self.port.sync_entry(entry.id)
        await self.show(responder, entry, include_reactions=True)
        await responder.send(f"{self.proper} #{entry.id} edited")

    # ------------------------------------------------------------------
    # get / roulette
    # ------------------------------------------------------------------

    async def cmd_get(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        if not args:
            raise UserError(f"Usage: {self.prefix} get <number>")
        await self.print_search_results(responder, [self.service.get_entry(args.strip())])

    def _roulette_pool(self, args: str) -> list[Entry]:
        if args:
            return self.search_helper(args, max_count=10).entries
        return self.open_entries()

    async def cmd_roulette(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        pool = self._roulette_pool(args)
        if not pool:
            await responder.send(f"No {self.plural} found matching those search terms")
        else:
            await self.print_search_results(responder, [self.rng.choice(pool)])

    async def cmd_iroulette(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        pool = self._roulette_pool(args)
        if not pool:
            await responder.send(f"No {self.plural} found matching those search terms")
        else:
            self.rng.shuffle(pool)
            await self._start_session(msg, pool, responder)

    async def _start_session(self, msg: IncomingMessage, entries: list[Entry], responder: Responder) -> None:
        session = InteractiveSession(self, msg.author_id, [e.id for e in entries])
        self.sessions.append(session)
        await session.send_first_message(responder)

    # ------------------------------------------------------------------
    # stats
    # ------------------------------------------------------------------

    async def cmd_stats(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        text = format_stats(self.single, self.open_entries(), self.store.count(EntryQuery(status="closed")))
        await responder.send(text)

    async def cmd_astats(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        # Discord authors and in-game (Minecraft) authors, ranked together
        await responder.send(f"Current {self.single} author stats:")
        stats_text = ""
        for a in self.store.author_counts():
            if a.author_id:
                name = self.name_of(a.author_id)
            else:
                uuid = a.author_mc_uuid or ""
                name = f"{self.store.player_name(uuid) or uuid[:8]} (in-game)"
            if name is not None:
                stats_text += f"{name.ljust(20)} : {a.total}\n"
        for chunk in split_string(stats_text):
            await responder.send("```python\n" + chunk + "```")

    async def cmd_cstats(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        self.service.require_team_view(msg.actor())
        try:
            numbers = [int(a) for a in args.split()]
        except ValueError:
            numbers = []
        if len(numbers) != len(args.split()) or len(numbers) > 2 or any(n < 0 for n in numbers):
            raise UserError(f"Usage: {self.prefix} cstats [days] [minimum]")
        days = numbers[0] if numbers else None
        # Overall, most closers have only a few: list the regulars unless asked otherwise
        minimum = numbers[1] if len(numbers) > 1 else (1 if days else CSTATS_MINIMUM)
        since = self.service.now() - days * 86400 if days else None
        stats = closer_stats(self.store, since=since)
        for message in format_closer_stats(stats, self.config, self.name_of, days,
                                           self.store.player_name, minimum):
            await responder.send(message)

    # ------------------------------------------------------------------
    # Searches
    # ------------------------------------------------------------------

    def search_helper(self, args: str, max_count: int) -> SearchSpec:
        part = args.replace(",", " ").split()
        labels = self.store.labels()
        priorities = PRIORITIES
        complexities = list(COMPLEXITIES)
        if not args or len(part) < 1:
            raise UserError('''Usage: {prefix} search labels,priorities,complexities,assigned,max_count

Search for items by tags. Note this does **not** search by description - use dsearch for that. Search items can be separated by commas or spaces.

Will not show zero priority things by default.

You can combine multiple different tags to search for specific things. For example:
> `{prefix} search plugin cmd moderate hard assigned 5`

This will search for items labeled plugin AND cmd, have complexity=hard OR complexity=moderate, are assigned to someone, and at most return 5 results

Default limit is 10 results
If using multiple labels, all specified labels must match
If using multiple priorities or complexities, at least one must match

Available labels: {labels}
Available priorities: {priorities}
Available complexities: {complexities}'''.format(
                prefix=self.prefix, labels=", ".join(labels), priorities=", ".join(priorities),
                complexities=", ".join(complexities)))

        match_labels: list[str] = []
        match_priorities: list[str] = []
        match_complexities: list[str] = []
        match_assigned = False
        for item in part:
            item = item.strip()
            label_match = get_list_match(item, labels)
            priority_match = get_list_match(item, priorities)
            complexity_match = get_list_match(item, complexities)
            if item.lower() == "assigned":
                match_assigned = True
            elif label_match is not None:
                match_labels.append(label_match)
            elif complexity_match is not None:
                match_complexities.append(complexity_match)
            elif priority_match is not None:
                match_priorities.append(priority_match)
            elif re.search("^[0-9][0-9]*$", item):
                max_count = int(item)
            else:
                raise UserError(f"No priority, label, complexity, or 'assigned' matching {item!r}")

        if not match_labels and not match_priorities and not match_complexities and not match_assigned:
            raise UserError("Must specify something to search for")

        if not match_priorities:
            match_priorities = [p for p in priorities if p != "Zero"]

        entries = self.store.query(EntryQuery(
            status="open", labels=match_labels, priorities=match_priorities,
            complexities=match_complexities, assignee="any" if match_assigned else None))
        return SearchSpec(entries, match_labels, match_priorities, match_complexities, max_count)

    async def cmd_search(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        spec = self.search_helper(args, max_count=10)
        await self.print_search_results(responder, spec.entries, limit=spec.max_count, include_link=True)
        await responder.send(
            f"{len(spec.entries)} {self.plural} found matching labels={','.join(spec.labels)} "
            f"priorities={','.join(spec.priorities)} complexities={','.join(spec.complexities)}")

    def dsearch_internal(self, search_terms: str, limit: int) -> tuple[list[Entry], int]:
        part = search_terms.replace(",", " ").split()
        if not search_terms or len(part) < 1:
            raise UserError(f"Usage: {self.prefix} dsearch <search terms, count>")
        terms: list[str] = []
        for term in part:
            try:
                limit = int(term)
            except ValueError:
                terms.append(term.strip())
        if not terms:
            raise UserError(f"Usage: {self.prefix} dsearch <search terms, count>")
        return self.store.query(EntryQuery(status="open", terms=terms)), max(1, limit)

    async def cmd_dsearch(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        entries, limit = self.dsearch_internal(args, 15)
        await responder.send(f"{len(entries)} {self.plural} found matching {args}")
        await self.print_search_results(responder, entries, limit=limit, include_link=True)

    async def cmd_isearch(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        spec = self.search_helper(args, max_count=100)
        if not spec.entries:
            raise UserError("No results to display")
        await self._start_session(msg, spec.entries, responder)

    async def cmd_asearch(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        author_id, author_name = msg.author_id, msg.author_name
        if args:
            author_id, author_name = self.port.find_user(args)
        total = self.store.count(EntryQuery(status="all", author_id=author_id))
        open_entries = self.store.query(EntryQuery(status="open", author_id=author_id))
        await self.print_search_results(responder, open_entries, include_link=True)
        await responder.send(
            f"{len(open_entries)} open {self.plural} of {total} total from author {author_name}")

    async def cmd_rsearch(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        if not args or " " in args:
            raise UserError(f"Usage: {self.prefix} rsearch <:reaction:>")
        entries = self.store.query(EntryQuery(status="open", reaction=args))
        if not entries:
            raise UserError(f"No entries with reaction {args!r}")
        await self.print_search_results(responder, entries, sort_entries=False)

    # ------------------------------------------------------------------
    # Labels
    # ------------------------------------------------------------------

    async def cmd_addlabel(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        name = self.service.add_label(msg.actor(), args)
        await responder.send(f"Label {name} added successfully")

    async def cmd_dellabel(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        label, changed = self.service.remove_label(msg.actor(), args)
        for entry_id in changed:
            if self.stopping:
                return
            entry = self.store.get(entry_id)
            if entry is not None and (not entry.is_closed or entry.message_id is not None):
                await self.port.sync_entry(entry_id)
        await responder.send(f"Label {label} removed successfully from {len(changed)} {self.plural}")

    # ------------------------------------------------------------------
    # Closing
    # ------------------------------------------------------------------

    async def cmd_delete(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        # Kept only so old habits get pointed at the two commands that replaced it.
        await responder.send(f"`{self.prefix} delete` is now `{self.prefix} redact <number>` (hides "
                             f"a {self.single}'s text from everyone but the team) or "
                             f"`{self.prefix} purge <number>` (leads: deletes it for good)")

    async def cmd_redact(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        part = args.split(maxsplit=1)
        if not args or len(part) < 1:
            raise UserError(f"Usage: {self.prefix} redact <number>")
        entry = self.service.redact(msg.actor(), self.service.get_entry(part[0].strip()))
        await self.port.sync_entry(entry.id)
        await responder.send(f"{self.proper} #{entry.id} redacted; only the team can see its text. "
                             "You still need to manually delete any messages related to this in "
                             "other channels.")

    async def cmd_purge(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        part = args.split()
        if not part or len(part) > 2:
            raise UserError(f"Usage: {self.prefix} purge <number>")
        actor = msg.actor()
        entry = self.service.get_entry(part[0])
        if not self.service.has_privilege(actor, PRIV_LEAD):
            raise UserError("You do not have permission to use this command")
        if len(part) < 2 or part[1].lower() != "confirm":
            await responder.send(f"This permanently deletes {self.single} #{entry.id}, its history "
                                 f"and anything redacted, and can't be undone. To go ahead: "
                                 f"`{self.prefix} purge {entry.id} confirm`")
            return
        # The bot's copies of its images first: once the entry is gone, nothing knows of them
        if await self.port.delete_feed_messages(self.service.image_messages(entry)):
            raise UserError(f"Some of the bot's image messages for {self.single} #{entry.id} in the feed "
                            "channel couldn't be deleted, so nothing was purged. Please try again shortly.")
        message_id = self.service.purge(actor, entry)
        if message_id is not None:
            await self.port.delete_tracking_message(message_id)
        await responder.send(f"{self.proper} #{entry.id} purged. You still need to manually "
                             "delete any messages related to this in other channels.")

    async def cmd_reupload(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        part = args.split()
        if len(part) != 1:
            raise UserError(f"Usage: {self.prefix} reupload <number>")
        actor = msg.actor()
        entry = self.service.get_entry(part[0])
        images = self.service.check_reupload(actor, entry)
        if not images:
            raise UserError(f"{self.proper} #{entry.id} has no images")
        done = 0
        for n, (image, saved) in enumerate(images, 1):
            if saved is None or saved.path is None:
                await responder.send(f"Image {n} of {self.single} #{entry.id} has no saved copy")
                continue
            try:
                await self.port.post_image(entry.id, image.url, saved.path, actor)
                done += 1
            except UserError as e:
                await responder.send(f"Image {n}: {e}")
        if done:
            await self.port.sync_entry(entry.id)
            await responder.send(f"Reuploaded {done} image{'s' if done > 1 else ''} of "
                                 f"{self.single} #{entry.id}")

    async def _after_close(self, entry: Entry, responder: Responder, verb: str) -> None:
        if entry.resolution == DUPLICATE:
            # fix and reject close as a duplicate when the reason says so: say what happened
            verb = "closed as a duplicate" + (f" of #{entry.duplicate_of}" if entry.duplicate_of else "")
        await self.port.sync_entry(entry.id)
        await self.show(responder, entry, include_reactions=True)
        await responder.send(f"{self.proper} #{entry.id} {verb}")

    async def cmd_reject(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        part = args.split(maxsplit=1)
        if not args or len(part) < 2:
            raise UserError(f"Usage: {self.prefix} reject <number> <required explanation>")
        entry = self.service.reject(msg.actor(), self.service.get_entry(part[0].strip()), part[1])
        await self._after_close(entry, responder, "rejected")

    async def cmd_fix(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        part = args.split(maxsplit=1)
        if not args or len(part) < 1:
            raise UserError(f"Usage: {self.prefix} fix <number> [optional explanation]")
        reason = part[1] if len(part) > 1 else ""
        entry = self.service.fix(msg.actor(), self.service.get_entry(part[0].strip()), reason)
        await self._after_close(entry, responder, "marked as fixed")

    async def cmd_dupe(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        part = args.split(maxsplit=2)
        if not args or len(part) < 2:
            raise UserError(f"Usage: {self.prefix} dupe <number> <original number> [note]")
        entry = self.service.get_entry(part[0].strip())
        original = self.service.get_entry(part[1].strip().lstrip("#"))
        entry = self.service.dupe(msg.actor(), entry, original, part[2] if len(part) > 2 else "")
        await self._after_close(entry, responder, "")

    async def cmd_unfix(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        part = args.split(maxsplit=2)
        if not args or len(part) != 1:
            raise UserError(f"Usage: {self.prefix} unfix <number>")
        entry = self.service.reopen(msg.actor(), self.service.get_entry(part[0].strip()))
        await self._after_close(entry, responder, "unmarked as fixed")

    async def cmd_prune(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        actor = msg.actor()
        if not self.service.has_privilege(actor, PRIV_LEAD):
            raise UserError("You do not have permission to use this command")
        await responder.send("Prune started, this will take some time...")
        pruned: list[Entry] = []
        for entry_id in [e.id for e in self.store.query(EntryQuery(status="closed"))]:
            if self.stopping:
                return
            # Read again just before deleting: it may have been reopened meanwhile
            entry = self.store.get(entry_id)
            if entry is None or not entry.is_closed or entry.message_id is None:
                continue
            if await self.port.delete_tracking_message(entry.message_id):
                self.service.pruned(entry, entry.message_id)
                pruned.append(entry)
        await self.print_search_results(responder, pruned, limit=99999)
        await responder.send(f"{len(pruned)} entries pruned successfully")

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    async def cmd_notify(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        actor = msg.actor()
        on_text = f'''You **will** be notified of changes to your {self.plural}.
Notifications are on by default.
To change this, {self.prefix} notify off'''
        off_text = f'''You will __not__ be notified of changes to your {self.plural}.
To change this, {self.prefix} notify on'''
        if not args:
            if self.service.notifications_enabled(actor.id):
                await responder.send(f'''You **will** be notified of changes to your {self.plural}.
Notifications are on by default.
To change this, `{self.prefix} notify off`''')
            else:
                await responder.send(f'''You will __not__ be notified of changes to your {self.plural}.
To change this, `{self.prefix} notify on`''')
            return
        match = get_list_match(args.strip(), ["on", "off"])
        if match is None:
            raise UserError(f"Argument to {self.prefix} notify must be 'on' or 'off'")
        self.service.set_notifications(actor, match == "on")
        await responder.send(on_text if match == "on" else off_text)

    async def cmd_send_notifications(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        actor = msg.actor()
        if not self.service.has_privilege(actor, PRIV_TEAM):
            raise UserError("You do not have permission to use this command")
        await responder.send("Notification process started...")
        count = opt_out = no_user = in_game = 0
        for entry_id in self.store.pending_notification_ids():
            if self.stopping:
                return
            # Each entry is read just before it is used: earlier sends take a while, and one
            # redacted, purged or notified meanwhile must not be sent from an older copy
            entry = self.store.get(entry_id)
            if entry is None or not entry.pending_notification:
                continue
            count += 1
            name = self.name_of(entry.author_id) if entry.author_id else None
            if entry.author_mc_uuid and not entry.author_id:
                # Reported in-game: the game plugin shows it when the player is online
                if self.service.queue_game_notice(entry):
                    in_game += 1
                else:
                    opt_out += 1
            elif name is None:
                no_user += 1
            elif not self.service.notifications_enabled(entry.author_id):
                opt_out += 1
            else:
                await self.port.refresh_images(entry.images)
                entry = self.store.get(entry_id)
                if entry is None or not entry.pending_notification:
                    continue
                text = self.render(entry)
                await responder.send(f"<@{entry.author_id}> Your {self.single} was updated:\n    {text}",
                                     images=entry.images, mentions=(entry.author_id,))
                entry = self.store.get(entry_id)
                if entry is None:
                    continue
            self.service.mark_notified(actor, entry)
        await responder.send(
            f"{count} notifications processed successfully, {opt_out} of which were suppressed by "
            f"user opt-out, {no_user} of which could not find a user to ping"
            + (f", {in_game} of which were queued for in-game delivery" if in_game else ""))

    # ------------------------------------------------------------------
    # Channel maintenance
    # ------------------------------------------------------------------

    async def cmd_repost(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        if not self.service.has_privilege(msg.actor(), PRIV_OWNER):
            raise UserError("You do not have permission to use this command")
        await self.port.repost(responder)

    async def cmd_sync(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        # Kept so the old habit gets an answer
        await responder.send(f"Slash commands now sync by themselves when the bot starts; "
                             f"`{self.prefix} sync` is no longer needed.")

    # ------------------------------------------------------------------
    # Assignment
    # ------------------------------------------------------------------

    async def cmd_assign(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        actor = msg.actor()
        self.service.require_team(actor)
        part = args.split(maxsplit=1)
        if not args or not part:
            raise UserError(f"Usage: {self.prefix} assign <number> [user]")
        entry = self.service.get_entry(part[0].strip())
        assignee_id = msg.author_id
        assignee_name = msg.author_name
        if len(part) > 1:
            assignee_id, assignee_name = self.port.find_user(part[1].strip())
        entry = self.service.assign(actor, entry, assignee_id)
        await self.port.sync_entry(entry.id)
        await self.show(responder, entry, include_reactions=True)
        await responder.send(f"{self.proper} #{entry.id} assigned to {assignee_name}")

    async def cmd_unassign(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        actor = msg.actor()
        self.service.require_team(actor)
        part = args.split(maxsplit=1)
        if not args or not part:
            raise UserError(f"Usage: {self.prefix} unassign <number>")
        entry = self.service.unassign(actor, self.service.get_entry(part[0].strip()))
        await self.port.sync_entry(entry.id)
        await self.show(responder, entry, include_reactions=True)
        await responder.send(f"{self.proper} #{entry.id} unassigned")

    async def cmd_list_assigned(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        self.service.require_team(msg.actor())
        assignee: Optional[tuple[int, str]] = (msg.author_id, msg.author_name)
        if args:
            assignee = None if args.lower() == "all" else self.port.find_user(args)
        q = EntryQuery(status="open", assignee="any" if assignee is None else str(assignee[0]))
        entries = self.store.query(q)
        await self.print_search_results(responder, entries, limit=9999)
        if assignee is None:
            await responder.send(f"{len(entries)} total assigned {self.plural} found")
        else:
            await responder.send(f"{len(entries)} assigned {self.plural} found for user {assignee[1]}")

    async def cmd_ping_assigned(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        if not self.service.has_privilege(msg.actor(), PRIV_LEAD):
            raise UserError("You do not have permission to use this command")
        try:
            channel_id = int(args)
        except ValueError:
            raise UserError(f"{args!r} is not a number") from None
        target = self.port.channel(channel_id)
        if target is None:
            raise UserError(f"Can not find channel {channel_id}")
        await responder.send("Starting notification process...")
        entries = self.store.query(EntryQuery(status="open", assignee="any"))
        await self.print_search_results(target[0], entries, limit=9999, mention_assigned=True)
        await responder.send(f"{len(entries)} total assigned {self.plural} mentioned in channel {target[1]}")

    # ------------------------------------------------------------------
    # New: history, chart
    # ------------------------------------------------------------------

    async def cmd_history(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        self.service.require_team_view(msg.actor())
        if not args.strip():
            raise UserError(f"Usage: {self.prefix} history <number>")
        entry = self.service.get_entry(args.split()[0])
        lines = [f"History of {self.single} #{entry.id}:"]
        for ev in self.store.events_for(entry.id):
            lines.append("- " + describe_event(ev, self.name_of,
                                               lambda r: resolution_name(self.config, r),
                                               self.store.player_name))
        await self.reply_chunks(responder, "\n".join(lines))

    async def cmd_chart(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        self.service.require_team_view(msg.actor())
        if self.charts is None:
            raise UserError("Charts are not available")
        part = args.split()
        if not part:
            await self.reply_chunks(responder, self.charts.describe_all(self.prefix))
            return
        names = self.charts.names()
        name = get_list_match(part[0], names)
        if name is None:
            raise UserError(f"Unknown chart {part[0]!r}. Available: {', '.join(names)}")
        try:
            options = self.charts.parse_options(part[1:])
            png = await self.charts.render_async(name, options)
        except ChartError as e:
            raise UserError(str(e)) from None
        await responder.send(f"`{self.prefix} chart {name}{(' ' + ' '.join(part[1:])) if part[1:] else ''}`",
                             file=OutFile(f"{self.single}-{name}.png", png))

    async def cmd_context(self, msg: IncomingMessage, args: str, responder: Responder) -> None:
        """Context can hold player locations, so it is never posted in the (public) feed
        channel: this points to the ephemeral slash command instead."""
        if not self.service.can_see_context(msg.actor()):
            raise UserError("You do not have permission to use this command")
        number = args.split()[0] if args.split() else "<number>"
        await responder.send(f"Context can include where players were, so it is only shown privately: "
                             f"use `/{self.single} context {number}`")

    def redacted_text(self, actor: Actor, number: str) -> list[str]:
        """What redaction hid, as message chunks (team only, for private replies)."""
        entry = self.service.get_entry(number)
        hidden = self.service.redacted_content(actor, entry)
        by = hidden.get("redacted_by")
        who = (self.name_of(int(str(by))) or str(by)) if by else "unknown"
        when = f"<t:{hidden['redacted_at']}:f>" if hidden["redacted_at"] != LEGACY_REDACTION else "before the new bot"
        lines = [f"Redacted content of {self.single} #{entry.id} (redacted {when} by {who}):"]
        if hidden.get("description"):
            lines.append(f"**Description:**\n{hidden['description']}")
        if hidden.get("close_reason"):
            lines.append(f"**Close reason:** {hidden['close_reason']}")
        images: list[str] = hidden.get("images") or []
        if images:
            lines.append("**Images:** " + " ".join(f"<{url}>" for url in images))
        events: list[dict[str, Any]] = hidden.get("events") or []
        if events:
            lines.append("**History:**")
            for ev in events:
                when = f"<t:{ev['at']}:d>" if ev.get("at") else "unknown time"
                parts = [p for p in (ev.get("old"), ev.get("new")) if p]
                text = " -> ".join(str(p) for p in parts)
                if ev.get("reason"):
                    text += f" ({ev['reason']})"
                lines.append(f"- {when} {ev.get('kind')}: {text}")
        return split_string("\n".join(lines), 1900)

    def context_text(self, actor: Actor, number: str) -> list[str]:
        """The context attached to an entry, as message chunks (team only)."""
        if not self.service.can_see_context(actor):
            raise UserError("You do not have permission to use this command")
        entry = self.service.get_entry(number)
        sections = self.store.context_for(entry.id)
        if not sections:
            return [f"{self.proper} #{entry.id} has no context attached"]
        lines = [f"Context for {self.single} #{entry.id}:"]
        for sec in sections:
            body = json.dumps(sec.data, indent=1, ensure_ascii=False)
            if len(body) > 1500:
                body = body[:1500] + "\n... (truncated; the API has all of it)"
            lines.append(f"**{sec.section}** from {sec.source}, <t:{sec.created_at}:f>\n```json\n{body}\n```")
        return split_string("\n".join(lines), 1900)
