# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Byron Marohn
"""Discord bot for anonymous voting.

Players create anonymous polls via /anon_vote. Reactions are recorded in YAML
files and immediately removed to preserve anonymity. Poll creators can end
voting with /anon_vote_end.
"""
import logging
import time
from typing import Optional, Union

import discord
from discord import app_commands
from discord.ext import commands

from voting.config import VotingConfig
from voting.store import VoteData, VoteStore

logger = logging.getLogger(__name__)

THUMBSUP = "\U0001f44d"   # 👍
THUMBSDOWN = "\U0001f44e" # 👎


def _format_poll_message(vote: VoteData, force_counts: bool = False) -> str:
    lines = [
        f"Poll started by <@{vote.creator_id}> <t:{vote.created_at}:R>",
        vote.message,
    ]
    if vote.show_counts or force_counts:
        lines.append(f"{THUMBSUP} : {len(vote.thumbsup)}")
        lines.append(f"{THUMBSDOWN} : {len(vote.thumbsdown)}")
    if vote.concluded and vote.concluded_by and vote.concluded_at is not None:
        lines.append(f"Poll concluded by <@{vote.concluded_by}> <t:{vote.concluded_at}:R>")
    return "\n".join(lines)


class VotingBot(commands.Bot):
    """Discord bot that facilitates anonymous polls."""

    def __init__(self, config: VotingConfig, store: VoteStore) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.config = config
        self.store = store
        # In-memory set of active poll message IDs (as int) for fast lookup
        self.active_polls: set[int] = set()

    async def setup_hook(self) -> None:
        self._register_commands()
        await self.tree.sync()

    async def on_ready(self) -> None:
        logger.info("Logged in as %s", self.user)
        await self._catchup_active_polls()

    # --- Helpers ---

    def _check_allowed(self, interaction: discord.Interaction) -> bool:
        if not self.config.discord.allowed_role_ids:
            return True
        if not isinstance(interaction.user, discord.Member):
            return False
        return any(
            role.id in self.config.discord.allowed_role_ids
            for role in interaction.user.roles
        )

    async def _fetch_messageable(
        self, channel_id: int
    ) -> Optional[Union[discord.TextChannel, discord.Thread, discord.VoiceChannel]]:
        channel = self.get_channel(channel_id)
        if channel is None:
            try:
                channel = await self.fetch_channel(channel_id)
            except (discord.NotFound, discord.HTTPException):
                logger.warning("Could not fetch channel %d", channel_id)
                return None
        if not isinstance(channel, (discord.TextChannel, discord.Thread, discord.VoiceChannel)):
            return None
        return channel

    # --- Startup catch-up ---

    async def _catchup_active_polls(self) -> None:
        """Re-register active polls and reconcile any reactions missed while offline."""
        active = self.store.list_active()
        logger.info("Catching up %d active poll(s)", len(active))
        for vote in active:
            self.active_polls.add(int(vote.message_id))
            channel = await self._fetch_messageable(int(vote.channel_id))
            if channel is None:
                continue
            try:
                message = await channel.fetch_message(int(vote.message_id))
            except (discord.NotFound, discord.HTTPException):
                logger.warning("Could not fetch message %s for active poll", vote.message_id)
                continue

            # Collect users who reacted while bot was offline
            up_users: list[discord.User | discord.Member] = []
            down_users: list[discord.User | discord.Member] = []
            for reaction in message.reactions:
                emoji_str = str(reaction.emoji)
                if emoji_str not in (THUMBSUP, THUMBSDOWN):
                    continue
                async for user in reaction.users():
                    if not user.bot:
                        if emoji_str == THUMBSUP:
                            up_users.append(user)
                        else:
                            down_users.append(user)

            # Process thumbsup first, then thumbsdown (thumbsdown wins if both present)
            changed = False
            for user in up_users:
                uid = str(user.id)
                if uid not in vote.thumbsup and uid not in vote.thumbsdown:
                    vote.thumbsup.append(uid)
                    changed = True

            for user in down_users:
                uid = str(user.id)
                if uid in vote.thumbsup:
                    vote.thumbsup.remove(uid)
                if uid not in vote.thumbsdown:
                    vote.thumbsdown.append(uid)
                    changed = True

            if changed:
                self.store.save(vote)

            # Remove accumulated reactions and update message
            for user in up_users:
                try:
                    await message.remove_reaction(THUMBSUP, user)
                except (discord.Forbidden, discord.HTTPException):
                    logger.warning("Could not remove 👍 from user %d on message %s", user.id, vote.message_id)
            for user in down_users:
                try:
                    await message.remove_reaction(THUMBSDOWN, user)
                except (discord.Forbidden, discord.HTTPException):
                    logger.warning("Could not remove 👎 from user %d on message %s", user.id, vote.message_id)

            if changed and vote.show_counts:
                try:
                    await message.edit(content=_format_poll_message(vote))
                except (discord.Forbidden, discord.HTTPException):
                    logger.warning("Could not update message %s", vote.message_id)

    # --- Reaction handler ---

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.message_id not in self.active_polls:
            return
        if self.user and payload.user_id == self.user.id:
            return

        emoji_str = str(payload.emoji)
        if emoji_str not in (THUMBSUP, THUMBSDOWN):
            return

        vote = self.store.load(str(payload.message_id))
        if vote is None or vote.concluded:
            return

        user_id = str(payload.user_id)
        if emoji_str == THUMBSUP:
            if user_id in vote.thumbsdown:
                vote.thumbsdown.remove(user_id)
            if user_id not in vote.thumbsup:
                vote.thumbsup.append(user_id)
        else:
            if user_id in vote.thumbsup:
                vote.thumbsup.remove(user_id)
            if user_id not in vote.thumbsdown:
                vote.thumbsdown.append(user_id)

        self.store.save(vote)

        channel = await self._fetch_messageable(payload.channel_id)
        if channel is None:
            return
        try:
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, discord.Object(id=payload.user_id))
            if vote.show_counts:
                await message.edit(content=_format_poll_message(vote))
        except (discord.Forbidden, discord.HTTPException):
            logger.exception("Failed to update message for poll %s", vote.message_id)

    # --- Slash commands ---

    def _register_commands(self) -> None:
        @self.tree.command(
            name="anon_vote",
            description="Start an anonymous poll in this channel",
        )
        @app_commands.describe(
            show_counts="Whether to show live vote counts during the poll",
            message="The poll question or statement",
        )
        async def cmd_anon_vote(
            interaction: discord.Interaction,
            show_counts: bool,
            message: str,
        ) -> None:
            await interaction.response.defer(ephemeral=True)
            if not self._check_allowed(interaction):
                await interaction.followup.send(
                    "You don't have permission to use this command.", ephemeral=True
                )
                return

            if not isinstance(interaction.channel, (discord.TextChannel, discord.Thread, discord.VoiceChannel)):
                await interaction.followup.send(
                    "This command can only be used in a text channel.", ephemeral=True
                )
                return

            creator_id = str(interaction.user.id)
            created_at = int(time.time())

            vote = VoteData(
                message_id="",  # filled in after posting
                channel_id=str(interaction.channel_id),
                creator_id=creator_id,
                created_at=created_at,
                message=message,
                show_counts=show_counts,
                concluded=False,
                concluded_by=None,
                concluded_at=None,
            )

            poll_message = await interaction.channel.send(_format_poll_message(vote))
            vote.message_id = str(poll_message.id)

            self.store.save(vote)
            self.active_polls.add(poll_message.id)

            await poll_message.add_reaction(THUMBSUP)
            await poll_message.add_reaction(THUMBSDOWN)

            await interaction.followup.send(
                f"Poll created! Message ID: `{poll_message.id}`", ephemeral=True
            )

        @self.tree.command(
            name="anon_vote_end",
            description="End an anonymous poll you created",
        )
        @app_commands.describe(
            message_id="The message ID of the poll to end",
        )
        async def cmd_anon_vote_end(
            interaction: discord.Interaction,
            message_id: str,
        ) -> None:
            await interaction.response.defer(ephemeral=True)

            vote = self.store.load(message_id)
            if vote is None:
                await interaction.followup.send(
                    f"No poll found with message ID `{message_id}`.", ephemeral=True
                )
                return

            if vote.concluded:
                await interaction.followup.send(
                    "That poll has already been concluded.", ephemeral=True
                )
                return

            if str(interaction.user.id) != vote.creator_id:
                await interaction.followup.send(
                    "Only the poll creator can end this poll.", ephemeral=True
                )
                return

            vote.concluded = True
            vote.concluded_by = str(interaction.user.id)
            vote.concluded_at = int(time.time())
            self.store.save(vote)
            self.active_polls.discard(int(message_id))

            channel = await self._fetch_messageable(int(vote.channel_id))
            if channel is not None:
                try:
                    message = await channel.fetch_message(int(vote.message_id))
                    await message.clear_reactions()
                    await message.edit(content=_format_poll_message(vote, force_counts=True))
                except (discord.Forbidden, discord.HTTPException):
                    logger.exception("Failed to finalize poll message %s", message_id)

            await interaction.followup.send("Poll concluded.", ephemeral=True)
