"""The slash commands (/bug ..., /suggestion ...), their private replies and forms.

Most build the equivalent text command and run it through CommandHandler, so permissions,
checks and replies are those of the text commands; replies go only to whoever asked.
"""


import io
import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal, Optional

import discord
from discord import app_commands

from .charts import CHARTS
from .commands import CSTATS_MINIMUM, IncomingMessage, OutFile
from .matching import split_string
from .models import Image
from .service import MAX_DESCRIPTION, PRIV_TEAM, UserError
from .tokens import mint_token
from .vocab import COMPLEXITIES, PRIORITIES

if TYPE_CHECKING:
    from .bot import TaskBot

logger = logging.getLogger(__name__)

FORM_TIMEOUT = 3600         # seconds a form waits to be sent (lost if the bot restarts meanwhile)
MAX_SELECT_OPTIONS = 25     # Discord's limit on a pick-list


def register_slash_commands(bot: "TaskBot") -> None:
    """`/bug ...` (or `/suggestion ...`): the text commands without typing in the feed
    channel. Each subcommand runs the same command handler with the same privileges, and
    replies only to the person who used it. Discord allows 25 subcommands, so searches,
    edits and statistics are groups (`/bug search author`). Text too long for one line
    (report, description, append) is typed into a form."""
    cfg = bot.config
    guild = discord.Object(id=cfg.guild_id)
    single = cfg.descriptor_single
    handler = bot.handler
    store = bot.store

    def incoming(interaction: discord.Interaction, content: str = "",
                 attachments: Sequence[discord.Attachment] = ()) -> IncomingMessage:
        member = bot.resolve_member(interaction.user.id)
        return IncomingMessage(content=content, author_id=interaction.user.id,
                               author_name=interaction.user.display_name,
                               privilege=member.privilege if member is not None else 0,
                               message_id=interaction.id, slash=True,
                               attachments=[a.url for a in attachments if a.url])

    async def run(interaction: discord.Interaction, command: str, args: str = "",
                  attachments: Sequence[discord.Attachment] = ()) -> None:
        """Run a text command, replying privately."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        responder = _EphemeralResponder(bot, interaction)
        msg = incoming(interaction, f"{cfg.prefix} {command} {args}".strip(), attachments)
        await handler.run(command, msg, args, responder)
        await responder.finish()

    async def reply_chunks(interaction: discord.Interaction, produce: Any) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        responder = _EphemeralResponder(bot, interaction)
        try:
            chunks: list[str] = produce()
        except UserError as e:
            chunks = [str(e)]
        for chunk in chunks:
            await responder.send(chunk)
        await responder.finish()

    def choices(options: Sequence[str], current: str) -> list[app_commands.Choice[str]]:
        low = current.lower()
        return [app_commands.Choice(name=o, value=o) for o in options if o.lower().startswith(low)][:25]

    async def complete_labels(_: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        # Comma separated: complete the last one, keeping those already typed
        head, _sep, last = current.rpartition(",")
        prefix = head + "," if head else ""
        return [app_commands.Choice(name=prefix + c.value, value=prefix + c.value)
                for c in choices(store.labels(), last.strip())]

    async def complete_priority(_: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return choices(PRIORITIES, current)

    async def complete_complexity(_: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return choices(list(COMPLEXITIES), current)

    group = app_commands.Group(name=single, description=f"The {single} tracker")
    number_help = f"The {single}'s number"

    async def show_form(interaction: discord.Interaction, form: "_Form") -> None:
        await interaction.response.send_modal(form)

    async def form_failed(responder: "_EphemeralResponder", text: str, error: str) -> None:
        """A refused form loses what was typed, so give it back to copy."""
        await responder.send(error)
        for chunk in split_string(text, 1900):
            await responder.send(f"What you wrote:\n```\n{chunk.replace('```', '`` `')}\n```")

    async def run_form(interaction: discord.Interaction, command: str, args: str, text: str,
                       check: Optional[Any] = None) -> None:
        """Run a text command with what was typed into a form, giving the text back if refused.
        `check()`, run with nothing awaited before the command, returns a refusal or None."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        responder = _EphemeralResponder(bot, interaction)
        msg = incoming(interaction, f"{cfg.prefix} {command} {args}")
        refusal = check() if check is not None else None
        if refusal:
            await responder.send(refusal)
            return
        try:
            await handler.commands[command](msg, args, responder)
        except UserError as e:
            await form_failed(responder, text, str(e))
        await responder.finish()

    @group.command(name="report", description=f"Report a new {single}")
    @app_commands.describe(image="An image to include")
    async def s_report(interaction: discord.Interaction, image: Optional[discord.Attachment] = None) -> None:
        async def submitted(form_interaction: discord.Interaction, text: str, labels: str) -> None:
            await form_interaction.response.defer(ephemeral=True, thinking=True)
            responder = _EphemeralResponder(bot, form_interaction)
            try:
                await handler.report(incoming(form_interaction, attachments=[image] if image else []),
                                     text, labels, responder)
            except UserError as e:
                await form_failed(responder, text, str(e))
            await responder.finish()
        await show_form(interaction, _Form(f"Report a {single}", "Description", submitted,
                                           labels=store.labels()))

    @group.command(name="get", description=f"Show a {single}")
    @app_commands.describe(number=number_help)
    async def s_get(interaction: discord.Interaction, number: int) -> None:
        await run(interaction, "get", str(number))

    @group.command(name="notify", description=f"Whether you are notified of changes to your {single}s")
    async def s_notify(interaction: discord.Interaction, setting: Optional[Literal["on", "off"]] = None) -> None:
        await run(interaction, "notify", setting or "")

    @group.command(name="append", description=f"Add text to a {single}'s description")
    @app_commands.describe(number=number_help)
    async def s_append(interaction: discord.Interaction, number: int) -> None:
        try:
            entry = bot.service.get_entry(number)
            bot.service.check_append(incoming(interaction).actor(), entry)
        except UserError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        room = MAX_DESCRIPTION - len(entry.description) - 1
        if room < 1:
            await interaction.response.send_message(
                f"{cfg.descriptor_proper} #{number}'s description is already as long as it can be",
                ephemeral=True)
            return

        async def submitted(form_interaction: discord.Interaction, text: str, _labels: str) -> None:
            await run_form(form_interaction, "append", f"{number} {text}", text)
        await show_form(interaction, _Form(f"Add to {single} #{number}", "Text to add", submitted,
                                           max_length=room))

    # /bug search ...: the text command searches, privately
    search = app_commands.Group(name="search", description=f"Find {single}s", parent=group)

    @search.command(name="labels", description=f"Open {single}s by labels, priorities, complexities")
    @app_commands.describe(terms="As for the text command, e.g. quest,class,high")
    async def s_search(interaction: discord.Interaction, terms: str) -> None:
        await run(interaction, "search", terms)

    @search.command(name="description", description=f"Open {single}s whose description contains every word")
    @app_commands.describe(terms="Words to search for", limit="Maximum number of matches to show")
    async def s_dsearch(interaction: discord.Interaction, terms: str, limit: int = 99) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        responder = _EphemeralResponder(bot, interaction)
        try:
            entries, limit = handler.dsearch_internal(terms, limit)
        except UserError as e:
            await responder.send(str(e))
            return
        await responder.send(f"{len(entries)} {cfg.descriptor_plural} found matching {terms}")
        await handler.print_search_results(responder, entries, limit=limit, include_link=True)
        await responder.finish()

    @search.command(name="author", description=f"Open {single}s reported by you or someone else")
    @app_commands.describe(user="Who (default: you)")
    async def s_asearch(interaction: discord.Interaction, user: Optional[discord.Member] = None) -> None:
        await run(interaction, "asearch", str(user.id) if user else "")

    @search.command(name="reaction", description=f"Open {single}s, most reacted to first")
    @app_commands.describe(reaction="The reaction, e.g. \U0001f44d")
    async def s_rsearch(interaction: discord.Interaction, reaction: str) -> None:
        await run(interaction, "rsearch", reaction.strip())

    @search.command(name="assigned", description=f"Open {single}s assigned to you, someone else, or anyone (team)")
    @app_commands.describe(user="Who (default: you)", everyone="Everything assigned to anyone")
    async def s_list_assigned(interaction: discord.Interaction, user: Optional[discord.Member] = None,
                              everyone: bool = False) -> None:
        await run(interaction, "list_assigned", "all" if everyone else (str(user.id) if user else ""))

    # /bug edit ...: one field each, as `~bug edit <n> <field>`
    edit = app_commands.Group(name="edit", description=f"Change a {single}", parent=group)

    @edit.command(name="description", description=f"Rewrite a {single}'s description")
    @app_commands.describe(number=number_help)
    async def s_description(interaction: discord.Interaction, number: int) -> None:
        try:
            entry = bot.service.get_entry(number)
            bot.service.check_edit(incoming(interaction).actor(), entry, "description")
        except UserError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return

        def redacted_meanwhile() -> Optional[str]:
            # The form shows the description as it was; sent after a redaction, it
            # would put the hidden text back
            now = bot.store.get(number)
            if now is not None and now.redacted and not entry.redacted:
                return (f"{cfg.descriptor_proper} #{number} was redacted while the form was open, "
                        "so it wasn't changed.")
            return None

        async def submitted(form_interaction: discord.Interaction, text: str, _labels: str) -> None:
            await run_form(form_interaction, "edit", f"{number} description {text}", text,
                           check=redacted_meanwhile)
        await show_form(interaction, _Form(f"Edit {single} #{number}", "Description", submitted,
                                           default=entry.description))

    @edit.command(name="labels", description=f"Set a {single}'s labels")
    @app_commands.describe(number=number_help, labels="Comma separated labels")
    @app_commands.autocomplete(labels=complete_labels)
    async def s_labels(interaction: discord.Interaction, number: int, labels: str) -> None:
        await run(interaction, "edit", f"{number} label {labels}")

    @edit.command(name="image", description=f"Replace a {single}'s image")
    @app_commands.describe(number=number_help, image="The new image")
    async def s_image(interaction: discord.Interaction, number: int, image: discord.Attachment) -> None:
        await run(interaction, "edit", f"{number} image", [image])

    @edit.command(name="priority", description=f"Set a {single}'s priority (team)")
    @app_commands.describe(number=number_help)
    @app_commands.autocomplete(priority=complete_priority)
    async def s_priority(interaction: discord.Interaction, number: int, priority: str) -> None:
        await run(interaction, "edit", f"{number} priority {priority}")

    @edit.command(name="complexity", description=f"Set a {single}'s complexity (team)")
    @app_commands.describe(number=number_help)
    @app_commands.autocomplete(complexity=complete_complexity)
    async def s_complexity(interaction: discord.Interaction, number: int, complexity: str) -> None:
        await run(interaction, "edit", f"{number} complexity {complexity}")

    # /bug stats ...
    stats = app_commands.Group(name="stats", description=f"Statistics about {single}s", parent=group)

    @stats.command(name="open", description=f"Open {single}s by priority, complexity and label")
    async def s_stats(interaction: discord.Interaction) -> None:
        await run(interaction, "stats")

    @stats.command(name="authors", description=f"Who reported the most {single}s")
    async def s_astats(interaction: discord.Interaction) -> None:
        await run(interaction, "astats")

    @stats.command(name="closers", description=f"Who closed the most {single}s (team)")
    @app_commands.describe(days="Only the last few days (default: overall)",
                           minimum=f"Only those with at least this many (overall default {CSTATS_MINIMUM})")
    async def s_cstats(interaction: discord.Interaction, days: Optional[app_commands.Range[int, 0]] = None,
                       minimum: Optional[app_commands.Range[int, 0]] = None) -> None:
        args = "" if days is None and minimum is None else f"{days or 0} {minimum if minimum is not None else ''}"
        await run(interaction, "cstats", args.strip())

    async def complete_chart(_: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return choices(list(CHARTS), current)

    @stats.command(name="chart", description="Draw a chart (team)")
    @app_commands.describe(name="Which chart", options="e.g. 2y priority plugin")
    @app_commands.autocomplete(name=complete_chart)
    async def s_chart(interaction: discord.Interaction, name: str, options: Optional[str] = None) -> None:
        await run(interaction, "chart", f"{name} {options or ''}".strip())

    @group.command(name="fix", description=f"Close a {single} as fixed")
    @app_commands.describe(number=number_help, reason="Optional explanation (default: Fixed)")
    async def s_fix(interaction: discord.Interaction, number: int, reason: Optional[str] = None) -> None:
        await run(interaction, "fix", f"{number} {reason or ''}".strip())

    @group.command(name="reject", description=f"Close a {single} as rejected")
    @app_commands.describe(number=number_help, reason="Why")
    async def s_reject(interaction: discord.Interaction, number: int, reason: str) -> None:
        await run(interaction, "reject", f"{number} {reason}")

    @group.command(name="dupe", description=f"Close a {single} as a duplicate of another")
    @app_commands.describe(number=number_help, original="The original's number", note="Optional note")
    async def s_dupe(interaction: discord.Interaction, number: int, original: int,
                     note: Optional[str] = None) -> None:
        await run(interaction, "dupe", f"{number} {original} {note or ''}".strip())

    @group.command(name="reopen", description=f"Reopen a closed {single}")
    @app_commands.describe(number=number_help)
    async def s_reopen(interaction: discord.Interaction, number: int) -> None:
        await run(interaction, "unfix", str(number))

    @group.command(name="redact", description=f"Hide a {single}'s text from everyone but the team")
    @app_commands.describe(number=number_help)
    async def s_redact(interaction: discord.Interaction, number: int) -> None:
        await run(interaction, "redact", str(number))

    @group.command(name="assign", description=f"Assign a {single} to yourself or someone else (team)")
    @app_commands.describe(number=number_help, user="Who (default: you)")
    async def s_assign(interaction: discord.Interaction, number: int,
                       user: Optional[discord.Member] = None) -> None:
        await run(interaction, "assign", f"{number} {user.id if user else ''}".strip())

    @group.command(name="unassign", description=f"Unassign a {single} (team)")
    @app_commands.describe(number=number_help)
    async def s_unassign(interaction: discord.Interaction, number: int) -> None:
        await run(interaction, "unassign", str(number))

    @group.command(name="history", description=f"Who changed a {single} and when (team)")
    @app_commands.describe(number=number_help)
    async def s_history(interaction: discord.Interaction, number: int) -> None:
        await run(interaction, "history", str(number))

    @group.command(name="context", description=f"Context attached to a {single}, such as where it was reported (team)")
    @app_commands.describe(number=number_help)
    async def s_context(interaction: discord.Interaction, number: int) -> None:
        msg = incoming(interaction)
        await reply_chunks(interaction, lambda: handler.context_text(msg.actor(), str(number)))

    @group.command(name="redacted", description=f"What redaction hid from a {single} (team)")
    @app_commands.describe(number=number_help)
    async def s_redacted(interaction: discord.Interaction, number: int) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        responder = _EphemeralResponder(bot, interaction)
        actor = incoming(interaction).actor()
        try:
            chunks = handler.redacted_text(actor, str(number))
            saved = bot.service.redacted_images(actor, bot.service.get_entry(number))
        except UserError as e:
            chunks, saved = [str(e)], []
        for chunk in chunks:
            await responder.send(chunk)
        for image in saved:
            try:
                await bot.send_saved_image(responder, image)
            except discord.HTTPException as e:
                await responder.send(f"Discord refused to attach an image ({e.status})")
        await responder.finish()

    @group.command(name="reupload", description=f"Post the saved copies of a {single}'s images again (team)")
    @app_commands.describe(number=number_help)
    async def s_reupload(interaction: discord.Interaction, number: int) -> None:
        await run(interaction, "reupload", str(number))

    @group.command(name="send_notifications", description="Notify authors of updates, in the bot channel (team)")
    async def s_send_notifications(interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        responder = _EphemeralResponder(bot, interaction)
        target = bot.channel(cfg.bot_input_channel)
        msg = incoming(interaction)
        if not bot.service.has_privilege(msg.actor(), PRIV_TEAM):
            # Refused privately, not in the bot channel where the run would post
            await responder.send("You do not have permission to use this command")
        elif target is None:
            await responder.send("Can't find the bot channel")
        else:
            await handler.run("send_notifications", msg, "", target[0])
            await responder.send(f"Done; see #{target[1]}")
        await responder.finish()

    @group.command(name="purge", description=f"Permanently delete a {single} and its history (leads)")
    @app_commands.describe(number=number_help, confirm="Really delete it; this can't be undone")
    async def s_purge(interaction: discord.Interaction, number: int, confirm: bool = False) -> None:
        await run(interaction, "purge", f"{number} confirm" if confirm else str(number))

    token_group = app_commands.Group(name="api_token", description=f"Tokens for the {single} tracker's network API (team)",
                                     parent=group)

    @token_group.command(name="create", description="Create a token for taskctl or the HTTP API (shown once)")
    @app_commands.describe(lifetime_days="How long the token lasts",
                           read_only="Only allow reading, not changing anything")
    async def token_create(interaction: discord.Interaction, lifetime_days: Optional[int] = None,
                           read_only: bool = False) -> None:
        member = bot.resolve_member(interaction.user.id)
        if member is None or not member.can_view or member.privilege < PRIV_TEAM:
            await interaction.response.send_message(
                f"API tokens are for team members of the {single} tracker.", ephemeral=True)
            return
        default_hours = cfg.api_token_default_ttl_hours
        hours = default_hours if lifetime_days is None else lifetime_days * 24
        hours = max(1, min(cfg.api_token_max_ttl_hours, hours))
        try:
            token, expires_at = mint_token(bot.service, member.id, hours, "read" if read_only else "write")
        except UserError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        scope = "read-only" if read_only else "read/write"
        await interaction.response.send_message(
            f"Your {scope} API token (shown only once), valid until <t:{expires_at}:f>:\n"
            f"```\n{token}\n```\n"
            "Use it with taskctl:\n```\n"
            + (f"export TASKCTL_URL={cfg.api_public_url}\n" if cfg.api_public_url else "")
            + f"export TASKCTL_TOKEN={token}\n```\n"
            f"It acts with your privileges. If it leaks, run `/{single} api_token revoke`.",
            ephemeral=True)

    @token_group.command(name="revoke", description="Revoke every API token you have created")
    async def token_revoke(interaction: discord.Interaction) -> None:
        count = bot.store.revoke_tokens(interaction.user.id)
        await interaction.response.send_message(f"Revoked {count} token(s).", ephemeral=True)

    bot.tree.add_command(group, guild=guild)

    @bot.tree.error
    async def on_slash_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        """Anything but a refusal (those are replies): say so rather than leave the reply
        "thinking" for ever, which invites trying again."""
        logger.error("/%s failed", interaction.command.qualified_name if interaction.command else "?",
                     exc_info=error)
        text = ("Something went wrong (it has been logged). Check before trying again, "
                "in case it went through.")
        try:
            if interaction.response.is_done():
                await interaction.followup.send(text, ephemeral=True)
            else:
                await interaction.response.send_message(text, ephemeral=True)
        except discord.HTTPException:
            logger.warning("Couldn't tell the user that a slash command failed", exc_info=True)


class _EphemeralResponder:
    """Private replies to a slash command: the interaction's response if it is still
    open, follow-ups after that. `finish` makes sure a deferred one gets an answer."""

    def __init__(self, bot: "TaskBot", interaction: discord.Interaction):
        self._bot = bot
        self._interaction = interaction
        self._sent = False

    async def send(self, text: str, *, images: Sequence[Image] = (),
                   file: Optional[OutFile] = None, mentions: Sequence[int] = ()) -> None:  # pylint: disable=unused-argument
        embeds = await self._bot.image_embeds(images)
        chunks = split_string(text) if len(text) > 2000 else [text]
        for i, chunk in enumerate(chunks):
            kwargs: dict[str, Any] = {"ephemeral": True, "allowed_mentions": discord.AllowedMentions.none()}
            if i == len(chunks) - 1:
                kwargs["embeds"] = embeds
                if file is not None:
                    kwargs["file"] = discord.File(io.BytesIO(file.data), filename=file.filename)
            if not self._interaction.response.is_done():
                await self._interaction.response.send_message(chunk or None, **kwargs)
            else:
                await self._interaction.followup.send(chunk or discord.utils.MISSING, **kwargs)
        self._sent = True

    async def finish(self) -> None:
        if not self._sent:
            await self.send("Done.")


class _Form(discord.ui.Modal):
    """A form with one multi-line text box, for text too long or too many lines for a slash
    command option; for reports, also a pick-list of labels (a text box past Discord's
    limit of 25 options). `submitted(interaction, text, labels)` gets labels comma separated."""

    def __init__(self, title: str, text_label: str, submitted: Any, *, default: Optional[str] = None,
                 max_length: int = MAX_DESCRIPTION, labels: Optional[Sequence[str]] = None):
        super().__init__(title=title[:45], timeout=FORM_TIMEOUT)
        self._submitted = submitted
        # A few old descriptions are longer than the limit; Discord refuses a form whose text
        # starts longer than its maximum, so allow it and let the bot refuse on submit
        limit = max(max_length, len(default or ""))
        self._text: discord.ui.TextInput[Any] = discord.ui.TextInput(
            style=discord.TextStyle.paragraph, default=default, max_length=min(limit, 4000))
        self._select: Optional[discord.ui.Select[Any]] = None
        self._labels_text: Optional[discord.ui.TextInput[Any]] = None
        if labels and len(labels) <= MAX_SELECT_OPTIONS:
            self._select = discord.ui.Select(
                options=[discord.SelectOption(label=name, value=name) for name in labels],
                min_values=0, max_values=len(labels), required=False)
            self.add_item(discord.ui.Label(text="Labels", description="None means misc",
                                           component=self._select))
        elif labels is not None:
            self._labels_text = discord.ui.TextInput(required=False, placeholder="Comma separated")
            self.add_item(discord.ui.Label(text="Labels", description="None means misc",
                                           component=self._labels_text))
        self.add_item(discord.ui.Label(text=text_label, component=self._text))

    async def on_submit(self, interaction: discord.Interaction) -> None:  # pylint: disable=arguments-differ
        if self._select is not None:
            labels = ",".join(self._select.values)
        else:
            labels = self._labels_text.value if self._labels_text is not None else ""
        await self._submitted(interaction, self._text.value, labels)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:  # pylint: disable=arguments-differ
        """Anything but a refusal (those are answered as replies): say so, and give the text
        back. A report may have been filed regardless, so this doesn't invite resending."""
        logger.error("Form %s failed", self.title, exc_info=error)
        messages = ["Something went wrong (it has been logged). Check before sending this again, "
                    "in case it went through. What you wrote:"]
        messages += [f"```\n{chunk.replace('```', '`` `')}\n```" for chunk in split_string(self._text.value, 1900)]
        try:
            for text in messages:
                if interaction.response.is_done():
                    await interaction.followup.send(text, ephemeral=True)
                else:
                    await interaction.response.send_message(text, ephemeral=True)
        except discord.HTTPException:
            logger.warning("Couldn't tell the user that form %s failed", self.title, exc_info=True)
