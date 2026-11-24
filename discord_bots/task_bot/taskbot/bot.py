"""Discord glue: everything that talks to discord.py lives here.

- routes messages in the bot input and discussion channels to CommandHandler
- implements BotPort (member lookup, channel access) and the API's Directory
- publishes entries to the tracking channel (one lock per entry, always rendered
  from the current database row), and retries anything left unpublished
- refreshes expired Discord CDN image URLs before embedding them
- saves every image to disk, and posts images attached to slash commands in the feed
  channel so they outlast Discord's one day (images.py)
- keeps reaction counts in the database current
- syncs the slash commands (slash.py) with Discord at startup when they have changed
- posts a feed-channel notice for changes made through the API
"""

import asyncio
import datetime
import hashlib
import json
import logging
import os
import sqlite3
from dataclasses import dataclass, replace
from collections.abc import Sequence
from typing import Any, Optional

import aiohttp
import discord
from discord.ext import commands as dcommands
from discord.http import Route

from .charts import ChartRenderer
from .commands import SLASH_REF_PREFIX, CommandHandler, IncomingMessage, OutFile, Responder
from .config import InstanceConfig
from .formatting import format_entry
from .matching import split_string
from .images import is_ephemeral
from .models import Actor, Image, ImageFile, Member, Reaction
from .service import Change, TaskService, UserError, compute_privilege
from .slash import register_slash_commands
from .stats import resolution_name
from .store import TaskStore, url_expiry

logger = logging.getLogger(__name__)

PUBLISH_INTERVAL = 5        # seconds between passes over unpublished entries
PUBLISH_BACKOFF = (30, 900)  # seconds to wait after Discord fails, doubling up to the cap
LOOP_RESTART_DELAY = 60     # seconds before a background loop that crashed starts again
REACTION_SWEEP_INTERVAL = 20  # seconds between reconciling one tracking message
NOTICE_FLUSH_INTERVAL = 60   # slow, so a bulk change through the API is a few lines
URL_REFRESH_MARGIN = 3600   # refresh signed URLs expiring within this many seconds
MAX_EMBEDS = 10
SAVE_BATCH = 50          # images saved per pass (one URL refresh call)
SAVE_PAUSE = 10          # seconds between passes while there is a backlog
SAVE_IDLE = 600          # ... and when there is none, or a pass got nowhere
SLASH_HASH_KEY = "slash_commands_sha256"   # meta: the slash commands as last synced


class ChannelResponder:
    """Responder for one Discord channel."""

    def __init__(self, bot: "TaskBot", channel: discord.abc.Messageable):
        self._bot = bot
        self._channel = channel

    async def send(self, text: str, *, images: Sequence[Image] = (),
                   file: Optional[OutFile] = None, mentions: Sequence[int] = ()) -> None:
        # Only the users meant to be pinged: old entries' text can hold other mentions
        allowed = discord.AllowedMentions(everyone=False, roles=False, replied_user=False,
                                          users=[discord.Object(id=u) for u in mentions])
        embeds = await self._bot.image_embeds(images)
        chunks = split_string(text) if len(text) > 2000 else [text]
        for i, chunk in enumerate(chunks):
            last = i == len(chunks) - 1
            kwargs: dict[str, Any] = {"allowed_mentions": allowed}
            if last and embeds:
                kwargs["embeds"] = embeds
            if last and file is not None:
                kwargs["file"] = discord.File(_bytes_io(file.data), filename=file.filename)
            await self._channel.send(chunk or None, **kwargs)


def _bytes_io(data: bytes) -> Any:
    import io
    return io.BytesIO(data)


class TaskBot(dcommands.Bot):
    def __init__(self, config: InstanceConfig, service: TaskService, charts: ChartRenderer):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix=".", intents=intents, application_id=config.application_id,
                         allowed_mentions=discord.AllowedMentions.none())
        self.config = config
        self.service = service
        self.store = service.store
        self.charts = charts
        charts.name_lookup = self.user_name
        self.handler = CommandHandler(service, self, charts)
        self.stopping = False
        self._entry_locks: dict[int, asyncio.Lock] = {}
        self._publish_wakeup = asyncio.Event()
        self._notices: list[Notice] = []
        # Entries Discord refused to publish, with their dirty value then: left alone
        # until they change again
        self._publish_stuck: dict[int, int] = {}
        self._tasks: list[asyncio.Task[Any]] = []
        self._save_wakeup = asyncio.Event()
        self._http_session: Optional[aiohttp.ClientSession] = None
        service.listeners.append(self._on_change)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def setup_hook(self) -> None:
        register_slash_commands(self)
        self._http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=600))
        self._tasks.append(asyncio.create_task(self._sync_slash_commands()))
        for loop in (self._publish_loop, self._reaction_sweep_loop, self._notice_loop,
                     self._maintenance_loop, self._save_loop):
            self._start_loop(loop)

    def _start_loop(self, loop: Any) -> None:
        """Run a background loop, starting it again (after logging) if it ever crashes."""
        task = asyncio.create_task(loop())
        self._tasks.append(task)

        def done(t: "asyncio.Task[Any]") -> None:
            if t in self._tasks:
                self._tasks.remove(t)
            if t.cancelled() or self.stopping or t.exception() is None:
                return
            logger.error("%s crashed; restarting it in %d s", loop.__name__, LOOP_RESTART_DELAY,
                         exc_info=t.exception())

            async def restart() -> None:
                await asyncio.sleep(LOOP_RESTART_DELAY)
                if not self.stopping:
                    self._start_loop(loop)
            self._tasks.append(asyncio.create_task(restart()))
        task.add_done_callback(done)

    async def on_ready(self) -> None:
        assert self.user is not None
        logger.info("Logged in as %s (%s)", self.user.name, self.user.id)

    async def close(self) -> None:
        self.stopping = True
        self.handler.stopping = True
        for task in list(self._tasks):
            task.cancel()
        # Up to a minute of notices may be waiting; the feed channel should still get them
        await self._flush_notices()
        if self._http_session is not None:
            await self._http_session.close()
        await super().close()

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    def _guild(self) -> Optional[discord.Guild]:
        return self.get_guild(self.config.guild_id)

    def _privilege(self, user: discord.abc.User) -> int:
        roles = [r.id for r in user.roles] if isinstance(user, discord.Member) else []
        return compute_privilege(self.config, user.id, roles)

    async def on_message(self, message: discord.Message) -> None:  # pylint: disable=arguments-differ
        if self.stopping or (self.user is not None and message.author.id == self.user.id):
            return
        if message.channel.id == self.config.bot_input_channel:
            incoming = IncomingMessage(
                content=message.content, author_id=message.author.id,
                author_name=message.author.display_name, privilege=self._privilege(message.author),
                message_id=message.id, attachments=[a.url for a in message.attachments if a.url])
            responder = ChannelResponder(self, message.channel)
            if self.handler.claims(incoming):
                async with message.channel.typing():
                    await self.handler.handle_message(incoming, responder)
            else:
                await self.handler.handle_message(incoming, responder)
        elif message.channel.id == self.config.discussion_id and not message.author.bot:
            try:
                await self.handler.handle_discussion_message(
                    message.content, ChannelResponder(self, message.channel))
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Error handling discussion message")

    # ------------------------------------------------------------------
    # BotPort / Directory
    # ------------------------------------------------------------------

    def user_name(self, user_id: int) -> Optional[str]:
        user = self.get_user(user_id)
        return None if user is None else user.display_name

    def find_user(self, query: str) -> tuple[int, str]:
        try:
            user_id = int(query)
        except ValueError:
            guild = self._guild()
            members: Sequence[discord.Member] = guild.members if guild is not None else []
            lowered = query.lower()
            matches = [m for m in members if m.display_name.lower().startswith(lowered)
                       or m.name.lower().startswith(lowered)]
            if not matches:
                raise UserError(f"User {query!r} not found") from None
            if len(matches) > 1:
                multimatch = [f"{m.name} ({m.display_name})" if m.name != m.display_name else m.name
                              for m in matches]
                raise UserError("Multiple users match {!r}: {}".format(query, "\n".join(multimatch))) from None
            user_id = matches[0].id
        name = self.user_name(user_id)
        if name is None:
            raise UserError(f"User {query!r} not found")
        return user_id, name

    def channel(self, channel_id: int) -> Optional[tuple[Responder, str]]:
        ch = self.get_channel(channel_id)
        if ch is None or not isinstance(ch, discord.abc.Messageable):
            return None
        return ChannelResponder(self, ch), str(getattr(ch, "name", channel_id))

    def resolve_member(self, user_id: int) -> Optional[Member]:
        guild = self._guild()
        if guild is None:
            return None
        member = guild.get_member(user_id)
        if member is None:
            return None
        channel = guild.get_channel(self.config.bot_input_channel)
        can_view = channel is not None and channel.permissions_for(member).view_channel
        return Member(id=member.id, name=member.display_name, privilege=self._privilege(member),
                      can_view=can_view)

    def _tracking_channel(self) -> Optional[discord.TextChannel]:
        ch = self.get_channel(self.config.channel_id)
        return ch if isinstance(ch, discord.TextChannel) else None

    async def _sync_slash_commands(self) -> None:
        """Register the slash commands with Discord when they differ from what was last synced,
        or when Discord is missing any. Most restarts make no sync call at all, which keeps well
        clear of Discord's daily limit on creating commands. Runs in the background: if Discord
        makes it wait, the rest of the bot carries on."""
        guild = discord.Object(id=self.config.guild_id)
        local = [cmd.to_dict(self.tree) for cmd in self.tree.get_commands(guild=guild)]
        digest = hashlib.sha256(json.dumps(local, sort_keys=True, default=str).encode()).hexdigest()
        try:
            remote = {cmd.name for cmd in await self.tree.fetch_commands(guild=guild)}
            missing = {str(c["name"]) for c in local} - remote
            if not missing and self.store.get_meta(SLASH_HASH_KEY) == digest:
                logger.info("Slash commands are up to date (%d)", len(local))
                return
            logger.info("Syncing slash commands (%s)", f"missing: {', '.join(sorted(missing))}"
                        if missing else "they have changed")
            synced = await self.tree.sync(guild=guild)
            self.store.set_meta(SLASH_HASH_KEY, digest)
            logger.info("Synced %d slash commands", len(synced))
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Syncing slash commands failed; the next start tries again")

    async def delete_tracking_message(self, message_id: int) -> bool:
        channel = self._tracking_channel()
        if channel is None:
            return False
        try:
            msg = await channel.fetch_message(message_id)
        except discord.NotFound:
            return False
        await msg.delete()
        return True

    async def repost(self, responder: Responder) -> None:
        channel = self._tracking_channel()
        if channel is None:
            raise UserError("Error getting bot channel!")
        if not self.store.tracked_message_ids():
            # With nothing tracked, every message in the channel would look untracked
            raise UserError("Refusing to repost: no tracked messages in the database")
        await responder.send("Repost started, this will take some time...")
        await responder.send(f"Building a set of all valid {self.config.descriptor_single} message ids...")
        valid = self.store.tracked_message_ids()
        await responder.send("Searching the channel for untracked messages...")
        assert self.user is not None
        my_id = self.user.id

        def predicate(m: discord.Message) -> bool:
            return m.author.bot and (m.author.id != my_id or m.id not in valid)

        deleted = await channel.purge(limit=9999, check=predicate)
        for m in deleted:
            if self.stopping:
                return
            await responder.send("Removing untracked message:")
            await responder.send(m.content or "(no text)")
        await responder.send(f"{len(deleted)} untracked messages removed successfully")
        await responder.send("Reposting missing messages...")
        count = 0
        for entry_id in [e.id for e in self.handler.open_entries()]:
            if self.stopping:
                return
            count += 1
            await self.sync_entry(entry_id)
        await responder.send(f"{count} entries reposted successfully")

    # ------------------------------------------------------------------
    # Publishing to the tracking channel
    # ------------------------------------------------------------------

    def _lock(self, entry_id: int) -> asyncio.Lock:
        lock = self._entry_locks.get(entry_id)
        if lock is None:
            lock = self._entry_locks[entry_id] = asyncio.Lock()
        return lock

    async def sync_entry(self, entry_id: int) -> None:
        """Send or edit an entry's tracking message, rendered from the current row.

        Closed entries without a message (pruned) are not reposted; an open
        entry whose message has disappeared is posted again, as before.
        """
        channel = self._tracking_channel()
        if channel is None:
            return
        async with self._lock(entry_id):
            seen = self.store.dirty_value(entry_id)
            entry = self.store.get(entry_id)
            if entry is None:
                return
            text = format_entry(entry, self.config, self.user_name,
                                duplicates=self.store.duplicates_of(entry_id))
            embeds = await self.image_embeds(entry.images)
            msg: Optional[discord.Message] = None
            if entry.message_id is not None:
                try:
                    msg = await channel.fetch_message(entry.message_id)
                except discord.NotFound:
                    msg = None
            if msg is not None:
                current_images = [e.image.url or "" for e in msg.embeds if e.image]
                wanted_images = [e.image.url or "" for e in embeds if e.image]
                if msg.content != text or len(current_images) != len(wanted_images) or \
                        any(_strip_sig(a) != _strip_sig(b) for a, b in zip(current_images, wanted_images)):
                    msg = await msg.edit(content=text, embeds=embeds,
                                         allowed_mentions=discord.AllowedMentions.none())
                if self.store.get(entry_id) is None:
                    return   # purged meanwhile; purge deletes the message
                self.store.set_reactions(entry_id, [Reaction(str(r.emoji), r.count) for r in msg.reactions])
            elif entry.is_closed:
                if entry.message_id is not None:
                    self.service.set_message_id(entry_id, None)
            else:
                msg = await channel.send(text, embeds=embeds, allowed_mentions=discord.AllowedMentions.none())
                if self.store.get(entry_id) is None:
                    # Purged while it was being sent: nothing would ever delete it
                    await msg.delete()
                    return
                self.service.set_message_id(entry_id, msg.id)
                # A new message has no reactions: drop any counted on one that vanished, and
                # the sweep needn't read it soon. The bot's own arrive as reaction events.
                self.store.set_reactions(entry_id, [])
            if msg is not None:
                mine = {str(r.emoji) for r in msg.reactions if getattr(r, "me", False)}
                for reaction in self.config.reactions:
                    if reaction not in mine:
                        await msg.add_reaction(reaction)
            if not self.store.clear_dirty(entry_id, seen):
                # Changed while we were talking to Discord: publish again soon
                self._publish_wakeup.set()

    async def _publish_loop(self) -> None:
        """Publish every dirty entry. Two kinds of failure: Discord or the network being down
        affects every entry, so the pass stops and the loop waits, longer each time, until
        one succeeds; Discord refusing one entry (a 4xx, or a bug of ours on its data) won't
        change on a retry, so that entry is set aside, with a line in the feed channel,
        until it changes again. Both are only in memory: a restart tries everything once."""
        await self.wait_until_ready()
        backoff = 0.0
        while not self.is_closed():
            if backoff:
                await asyncio.sleep(backoff)   # changes meanwhile wait too
            else:
                try:
                    await asyncio.wait_for(self._publish_wakeup.wait(), timeout=PUBLISH_INTERVAL)
                except asyncio.TimeoutError:
                    pass
            self._publish_wakeup.clear()
            backoff = await self.publish_pass(backoff)

    async def publish_pass(self, backoff: float) -> float:
        """One pass over the dirty entries; returns how long to wait before the next."""
        refused: list[tuple[int, Exception]] = []
        for entry_id in self.store.dirty_entry_ids():
            if self.stopping:
                break
            dirty = self.store.dirty_value(entry_id)
            if self._publish_stuck.get(entry_id) == dirty:
                continue
            self._publish_stuck.pop(entry_id, None)
            try:
                await self.sync_entry(entry_id)
                backoff = 0.0
            except (discord.DiscordServerError, discord.Forbidden, aiohttp.ClientError,
                    asyncio.TimeoutError, OSError) as e:
                # Not about this entry: Discord or the network is down, or the bot has
                # lost its permissions in the tracking channel (the one worth a line)
                if isinstance(e, discord.Forbidden) and not backoff:
                    await self._report_stuck([], e)
                backoff = min(max(backoff * 2, PUBLISH_BACKOFF[0]), PUBLISH_BACKOFF[1])
                logger.warning("Publishing failed; trying again in %d s", backoff, exc_info=True)
                break
            except Exception as e:  # pylint: disable=broad-exception-caught
                if self.store.get(entry_id) is None:
                    continue   # purged meanwhile
                logger.exception("Publishing entry %s failed", entry_id)
                self._publish_stuck[entry_id] = dirty
                refused.append((entry_id, e))
        if refused:
            # One line however many: a systematic refusal mustn't flood the channel
            await self._report_stuck([entry_id for entry_id, _ in refused], refused[0][1])
        return backoff

    async def _report_stuck(self, entry_ids: Sequence[int], error: Exception) -> None:
        """A line in the feed channel, where people will see it, for a failed publish."""
        channel = self.get_channel(self.config.bot_input_channel)
        if not isinstance(channel, discord.abc.Messageable):
            return
        detail = (str(error).strip() or type(error).__name__)[:1500]
        if not entry_ids:
            text = (f"Couldn't update the tracking channel: {detail}\n"
                    "Does the bot still have its permissions there? It keeps trying.")
        else:
            numbers = ", ".join(f"#{i}" for i in entry_ids[:50]) + (", ..." if len(entry_ids) > 50 else "")
            plural = self.config.descriptor_plural if len(entry_ids) > 1 else self.config.descriptor_single
            text = (f"Couldn't update the tracking message for {plural} {numbers}: {detail}\n"
                    "Each is tried again when it next changes.")
        try:
            await channel.send(text, allowed_mentions=discord.AllowedMentions.none())
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Reporting a failed publish failed")

    def _on_change(self, change: Change) -> None:
        self._publish_wakeup.set()
        self._save_wakeup.set()
        if change.action == "redacted":
            # The bot's own copies of its images in the feed channel go too: straight away,
            # rather than after a batch the save loop may be in the middle of
            self._background(self._delete_redacted_image_messages())
        # API and slash command replies aren't seen in the feed channel, so their changes
        # get a line there and the channel stays a complete log of changes
        # (the game plugin's changes come through the API). Where a change came from
        # doesn't matter to readers, so the line doesn't say.
        if change.actor.source == "api" or (change.actor.source_ref or "").startswith(SLASH_REF_PREFIX):
            self._notices.append(Notice(change.actor.name, change.action, change.entry_id,
                                        change.value, change.text))

    async def _notice_loop(self) -> None:
        """Gather notices of API and slash command changes into a few feed-channel messages."""
        await self.wait_until_ready()
        while not self.is_closed():
            await asyncio.sleep(NOTICE_FLUSH_INTERVAL)
            await self._flush_notices()

    async def _flush_notices(self) -> None:
        if not self._notices:
            return
        pending, self._notices = self._notices, []
        channel = self.get_channel(self.config.bot_input_channel)
        if not isinstance(channel, discord.abc.Messageable):
            return
        pending = without_hidden_text(pending, self.store)
        chunks = split_string("Changes made outside this channel:\n" + "\n".join(notice_lines(pending, self.config)))
        try:
            for chunk in chunks:
                await channel.send(chunk, allowed_mentions=discord.AllowedMentions.none())
        except (discord.DiscordServerError, aiohttp.ClientError, asyncio.TimeoutError, OSError):
            # Discord or the network is down: keep them for the next flush (a message already
            # sent from a long list is sent again then, which beats losing the rest)
            logger.warning("Posting change notices failed; trying again later", exc_info=True)
            self._notices = pending + self._notices
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Posting change notices failed")

    # ------------------------------------------------------------------
    # Images
    # ------------------------------------------------------------------

    async def refresh_images(self, images: Sequence[Image]) -> None:
        await self.image_embeds(images)

    async def image_embeds(self, images: Sequence[Image]) -> list[discord.Embed]:
        if not images:
            return []
        now = self.service.now()
        stale = [im.url for im in images[:MAX_EMBEDS] if im.attachment_id is not None
                 and (url_expiry(im.best_url(now)) or 0) < now + URL_REFRESH_MARGIN]
        if stale:
            await self._refresh_urls(stale)
            images = [self.store.get_image_cache(im) for im in images]
        embeds: list[discord.Embed] = []
        for im in images[:MAX_EMBEDS]:
            embed = discord.Embed()
            embed.set_image(url=im.best_url(now))
            embeds.append(embed)
        return embeds

    async def _refresh_urls(self, urls: list[str]) -> dict[str, str]:
        """Ask Discord for freshly signed attachment URLs (at most 50) and cache them.
        Returns original -> refreshed. Discord signs URLs even for deleted attachments,
        so only downloading one tells whether it still exists."""
        refreshed: dict[str, str] = {}
        if not urls:
            return refreshed
        try:
            route = Route("POST", "/attachments/refresh-urls")
            data = await self.http.request(route, json={"attachment_urls": urls[:50]})
            for item in data.get("refreshed_urls", []):
                if item.get("original") and item.get("refreshed"):
                    self.store.set_refreshed_url(item["original"], item["refreshed"])
                    refreshed[item["original"]] = item["refreshed"]
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning("Refreshing %d attachment URLs failed", len(urls), exc_info=True)
        return refreshed

    def _background(self, coro: Any) -> None:
        """Run a coroutine without waiting for it (from synchronous listeners)."""
        try:
            task = asyncio.get_running_loop().create_task(coro)
        except RuntimeError:
            coro.close()   # no event loop: nothing to talk to Discord with anyway
            return
        self._tasks.append(task)
        task.add_done_callback(lambda t: self._tasks.remove(t) if t in self._tasks else None)

    # ------------------------------------------------------------------
    # Saved images (images.py)
    # ------------------------------------------------------------------

    async def _download(self, url: str, relative: str) -> bool:
        """Save url to the image directory. False when Discord no longer has it (404);
        other failures raise, to be tried again later."""
        assert self._http_session is not None
        async with self._http_session.get(url) as resp:
            if resp.status == 404:
                return False
            resp.raise_for_status()
            with self.service.archive.writer(relative) as f:
                async for chunk in resp.content.iter_chunked(1 << 16):
                    f.write(chunk)
        return True

    async def _save_loop(self) -> None:
        """Save every image without a copy on disk: new ones as they arrive, and any others
        (such as those of a database restored without its images) a batch at a time. Each pass also
        deletes any of the bot's image messages that redaction left behind."""
        await self.wait_until_ready()
        while not self.is_closed():
            self._save_wakeup.clear()
            todo: list[tuple[int, str]] = []
            progress = 0
            try:
                await self._delete_redacted_image_messages()
                todo = self.store.images_to_save(SAVE_BATCH, self.service.now())
                progress = await self._save_images(todo) if todo else 0
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Saving images failed")
            if progress == 0 or len(todo) < SAVE_BATCH:
                try:
                    await asyncio.wait_for(self._save_wakeup.wait(), timeout=SAVE_IDLE)
                except asyncio.TimeoutError:
                    pass
            else:
                await asyncio.sleep(SAVE_PAUSE)

    async def _save_images(self, todo: Sequence[tuple[int, str]]) -> int:
        """Save a batch of images. Returns how many were saved or found missing."""
        archive = self.service.archive
        fresh = await self._refresh_urls([url for _, url in todo if not is_ephemeral(url)])
        progress = 0
        for entry_id, url in todo:
            if self.stopping:
                break
            now = self.service.now()
            # An expired or unsigned link gets a 404 even when the image exists, so without
            # a fresh one (the refresh failed) try again later
            download_url = url if is_ephemeral(url) else fresh.get(url)
            relative = archive.relative_path(entry_id, url)
            if download_url is None:
                logger.info("Discord gave no fresh link for image %s of entry %s; trying again later",
                            url, entry_id)
                self.store.image_save_failed(entry_id, url, now)
                continue
            try:
                found = await self._download(download_url, relative)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("Saving image %s of entry %s failed; trying again later", url, entry_id,
                               exc_info=True)
                self.store.image_save_failed(entry_id, url, now)
                continue
            if not found:
                logger.info("Image %s of entry %s is gone from Discord", url, entry_id)
            recorded = self.store.add_image_file(ImageFile(
                entry_id, url, relative if found else None,
                archive.size(relative) if found else None, now, missing=not found))
            if not recorded:
                archive.remove_entry(entry_id)   # purged while it was downloading
            progress += 1
        return progress

    async def keep_images(self, entry_id: int) -> list[str]:
        archive = self.service.archive
        entry = self.store.get(entry_id)
        notes: list[str] = []
        for n, image in enumerate(entry.images if entry is not None else [], 1):
            if not is_ephemeral(image.url):
                continue
            # Attached to a slash command: Discord deletes it within a day, so post a copy
            relative = archive.relative_path(entry_id, image.url)
            try:
                if not await self._download(image.url, relative):
                    notes.append(f"Image {n} could not be fetched from Discord")
                    continue
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("Fetching image %s of entry %s failed", image.url, entry_id, exc_info=True)
                notes.append(f"Image {n} could not be fetched from Discord")
                continue
            try:
                await self.post_image(entry_id, image.url, relative, None)
            except Exception as e:  # pylint: disable=broad-exception-caught
                if not isinstance(e, UserError):
                    logger.exception("Posting image %s of entry %s failed", image.url, entry_id)
                if not self.store.add_image_file(ImageFile(entry_id, image.url, relative,
                                                           archive.size(relative), self.service.now())):
                    archive.remove_entry(entry_id)   # purged meanwhile
                    continue
                notes.append(f"Image {n} can't be kept in Discord ({e}), so it will stop showing within "
                             "a day. The team still has a copy.")
        self._save_wakeup.set()
        return notes

    async def post_image(self, entry_id: int, url: str, path: str, actor: Optional[Actor]) -> None:
        self.service.check_postable(entry_id)
        archive = self.service.archive
        channel = self.get_channel(self.config.bot_input_channel)
        if not isinstance(channel, discord.TextChannel):
            raise UserError("the feed channel can't be found")
        size = archive.size(path)
        limit = channel.guild.filesize_limit
        if size > limit:
            raise UserError(f"it is too large to post here ({size / 1e6:.1f} MB, the limit is "
                            f"{limit / 1e6:.0f} MB)")
        filename = path.rsplit("/", 1)[-1].split("-", 1)[-1]
        try:
            msg = await channel.send(f"Image for {self.config.descriptor_single} #{entry_id}",
                                     file=discord.File(archive.absolute(path), filename=filename),
                                     allowed_mentions=discord.AllowedMentions.none())
        except discord.HTTPException as e:
            raise UserError(f"Discord refused the upload: {e.status} {e.text}".strip()) from e
        if not msg.attachments:
            await self._delete_feed_message(msg.id)
            raise UserError("Discord did not keep the image")
        if not self.service.image_posted(entry_id, url, msg.attachments[0].url, path, msg.id, actor):
            # Redacted (or purged) while it was being posted. If deleting fails, the save
            # loop's sweep tries again (image_posted recorded the message)
            if await self._delete_feed_message(msg.id):
                self.service.image_message_deleted(msg.id)
            raise UserError(f"{self.config.descriptor_proper} #{entry_id} was redacted meanwhile")

    async def _delete_feed_message(self, message_id: int) -> bool:
        """Delete one of the bot's messages in the feed channel. True once it is gone."""
        channel = self.get_channel(self.config.bot_input_channel)
        if not isinstance(channel, discord.TextChannel):
            return False
        try:
            await channel.get_partial_message(message_id).delete()
        except discord.NotFound:
            pass
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning("Deleting image message %s failed", message_id, exc_info=True)
            return False
        return True

    async def delete_feed_messages(self, message_ids: Sequence[int]) -> list[int]:
        return [m for m in message_ids if not await self._delete_feed_message(m)]

    async def _delete_redacted_image_messages(self) -> None:
        """Delete the bot's image messages of redacted entries, forgetting each only once
        Discord confirms, so a failure is retried on the next pass of the save loop."""
        for message_id in self.service.image_messages_to_delete():
            if await self._delete_feed_message(message_id):
                self.service.image_message_deleted(message_id)

    async def send_saved_image(self, responder: Responder, saved: ImageFile) -> None:
        """Attach a saved image to a private reply, or say where to find it if too large."""
        assert saved.path is not None
        guild = self._guild()
        limit = guild.filesize_limit if guild is not None else 10 << 20
        name = saved.path.rsplit("/", 1)[-1]
        if (saved.size or 0) > limit:
            await responder.send(f"`{name}` is too large to attach ({(saved.size or 0) / 1e6:.1f} MB); "
                                 f"`taskctl images {saved.entry_id}` downloads it")
            return
        try:
            data = self.service.archive.read(saved.path)
        except OSError:
            logger.warning("Saved image %s is missing", saved.path, exc_info=True)
            await responder.send(f"`{name}` is missing from the image directory")
            return
        await responder.send("", file=OutFile(name.split("-", 1)[-1], data))

    # ------------------------------------------------------------------
    # Reactions
    # ------------------------------------------------------------------

    def _entry_for_payload(self, channel_id: int, message_id: int) -> Optional[int]:
        if channel_id != self.config.channel_id:
            return None
        return self.store.entry_id_for_message(message_id)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        entry_id = self._entry_for_payload(payload.channel_id, payload.message_id)
        if entry_id is not None:
            self.store.adjust_reaction(entry_id, str(payload.emoji), 1)

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        entry_id = self._entry_for_payload(payload.channel_id, payload.message_id)
        if entry_id is not None:
            self.store.adjust_reaction(entry_id, str(payload.emoji), -1)

    async def on_raw_reaction_clear(self, payload: discord.RawReactionClearEvent) -> None:
        entry_id = self._entry_for_payload(payload.channel_id, payload.message_id)
        if entry_id is not None:
            self.store.set_reactions(entry_id, [])

    async def on_raw_reaction_clear_emoji(self, payload: discord.RawReactionClearEmojiEvent) -> None:
        entry_id = self._entry_for_payload(payload.channel_id, payload.message_id)
        if entry_id is not None:
            self.store.remove_reaction(entry_id, str(payload.emoji))

    async def _reaction_sweep_loop(self) -> None:
        """Slowly re-read every tracking message's reactions, catching events missed while offline."""
        await self.wait_until_ready()
        while not self.is_closed():
            await asyncio.sleep(REACTION_SWEEP_INTERVAL)
            channel = self._tracking_channel()
            if channel is None:
                continue
            for entry_id in self.store.stalest_reaction_entries(1):
                entry = self.store.get(entry_id)
                if entry is None or entry.message_id is None:
                    continue
                try:
                    msg = await channel.fetch_message(entry.message_id)
                    self.store.set_reactions(entry_id, [Reaction(str(r.emoji), r.count) for r in msg.reactions])
                except discord.NotFound:
                    # Decided on the row as it is now: it may have been reopened meanwhile
                    current = self.store.get(entry_id)
                    if current is None or current.message_id != entry.message_id:
                        continue
                    if current.is_closed:
                        self.store.clear_message_id(entry_id, entry.message_id)
                    else:
                        self.store.mark_dirty(entry_id)
                        self.store.set_reactions(entry_id, [])
                except Exception:  # pylint: disable=broad-exception-caught
                    # Move on to the next message rather than retrying this one forever
                    self.store.mark_reactions_checked(entry_id)
                    logger.warning("Reaction sweep failed for entry %s", entry_id, exc_info=True)

    # ------------------------------------------------------------------
    # Maintenance: token expiry, backups
    # ------------------------------------------------------------------

    async def _maintenance_loop(self) -> None:
        last_backup_day: Optional[str] = None
        while not self.is_closed():
            try:
                self.store.expire_tokens(self.service.now())
                today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
                if today != last_backup_day:
                    await asyncio.get_running_loop().run_in_executor(None, self._backup, today)
                    last_backup_day = today
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Maintenance failed")
            await asyncio.sleep(3600)

    def _backup(self, day: str) -> None:
        backup_dir = self.config.resolve("backups")
        os.makedirs(backup_dir, exist_ok=True)
        target = os.path.join(backup_dir, f"tasks-{day}.db")
        dest = sqlite3.connect(target)
        try:
            src = sqlite3.connect(self.config.db_file)
            try:
                src.backup(dest)
            finally:
                src.close()
        finally:
            dest.close()
        backups = sorted(f for f in os.listdir(backup_dir) if f.startswith("tasks-") and f.endswith(".db"))
        for old in backups[:-7]:
            os.remove(os.path.join(backup_dir, old))
        logger.info("Backed up database to %s", target)


@dataclass(frozen=True)
class Notice:
    """A change made where the feed channel doesn't see it (the API, slash commands), with
    what changed (`Change.value` and `Change.text`)."""
    actor: str
    action: str
    entry_id: int
    value: str = ""
    text: str = ""


def without_hidden_text(notices: Sequence[Notice], store: TaskStore) -> list[Notice]:
    """Notices wait up to a minute, so an entry may have been redacted or purged since: what
    people wrote about it (a reason, a description) is then left out of every notice."""
    hidden: dict[int, bool] = {}
    out: list[Notice] = []
    for n in notices:
        if n.text:
            if n.entry_id not in hidden:
                entry = store.get(n.entry_id)
                hidden[n.entry_id] = entry is None or entry.redacted
            if hidden[n.entry_id]:
                n = replace(n, text="")
        out.append(n)
    return out


def _notice_phrase(n: Notice, entries: str, count: int, config: InstanceConfig) -> str:
    """What the actor did, around `entries` ("bug #3", "bugs #3, #5")."""
    action, value = n.action, n.value
    field = action[len("edited "):] if action.startswith("edited ") else ""
    if action == "created":
        phrase = f"created {entries}" + (f" [{value}]" if value else "")
    elif action == "duped":
        what = "a duplicate" if count == 1 else "duplicates"
        phrase = f"marked {entries} as {what} of #{value}" if value else f"closed {entries} as {what}"
    elif action == "reopened":
        phrase = f"reopened {entries}" + (f" (was closed as {resolution_name(config, value)})" if value else "")
    elif action == "appended":
        phrase = f"appended to {entries}" + (", which now reads" if n.text else "")
    elif action in ("assigned", "unassigned"):
        phrase = f"{action} {entries}" + (f" {'to' if action == 'assigned' else 'from'} {value}" if value else "")
    elif action == "removed label":
        phrase = f"removed the label {value} from {entries}"
    elif field == "description":
        phrase = f"edited the description of {entries}"
    elif field == "image":
        phrase = f"changed the images of {entries} (now {f'{value} images' if value not in ('', '0') else 'none'})"
    elif field:
        phrase = f"set the {'labels' if field == 'label' else field} of {entries} to {value}"
    else:
        phrase = f"{action} {entries}"   # fixed, rejected, redacted, purged
    return phrase


def notice_lines(notices: Sequence[Notice], config: InstanceConfig, max_ids: int = 50) -> list[str]:
    """One line per change, saying what changed: `Combustible rejected bug #12: can't
    reproduce`. Runs of the same change to several entries (same actor, action and
    detail, such as a bulk fix with the default reason) share a line, in order, so a fix
    then a reopen still reads that way. At most `max_ids` per line, so a bulk change splits
    at line ends rather than inside a number. Text over several lines (a description) is
    quoted below its line."""
    runs: list[tuple[Notice, list[int]]] = []
    for n in notices:
        key = replace(n, entry_id=0)
        if not runs or runs[-1][0] != key:
            runs.append((key, []))
        if n.entry_id not in runs[-1][1]:
            runs[-1][1].append(n.entry_id)
    lines: list[str] = []
    for n, ids in runs:
        for start in range(0, len(ids), max_ids):
            part = ids[start:start + max_ids]
            entries = (f"{config.descriptor_single if len(part) == 1 else config.descriptor_plural} "
                       f"{', '.join(f'#{i}' for i in part)}")
            head = f"{n.actor} {_notice_phrase(n, entries, len(part), config)}"
            text = n.text.strip()
            if not text:
                lines.append(head)
            elif len(text.splitlines()) > 1:
                lines.append(f"{head}:\n" + "\n".join(f"> {line}" for line in text.splitlines()))
            else:
                lines.append(f"{head}: {text}")
    return lines


def _strip_sig(url: str) -> str:
    return url.split("?", 1)[0]
