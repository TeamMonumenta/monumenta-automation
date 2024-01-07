#!/usr/bin/env python3

import re
import logging
import traceback
import datetime
import signal
import asyncio
from pprint import pformat

logging.basicConfig(level=logging.INFO)

import discord
from discord.ext import commands
from discord.ext import tasks

import config
from automation_bot_lib import split_string
from automation_bot_instance import AutomationBotInstance

class GracefulKiller:
    """Class to catch signals (CTRL+C, SIGTERM) and gracefully save databases and stop the bot"""

    def __init__(self, bot):
        self._bot = bot
        self._event_loop = None
        self.stopping = False

    def register(self, event_loop):
        """Register signals that cause shutdown"""
        self._event_loop = event_loop
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, _, __):
        """Exit gracefully on signal"""
        self.stopping = True
        logging.info("Received signal; shutting down...")
        if self._event_loop is not None:
            asyncio.run_coroutine_threadsafe(self._bot.close(), self._event_loop)

class AutomationBot(commands.Bot):
    """Top-level discord bot object"""

    def __init__(self):
        super().__init__(
            command_prefix=config.PREFIX,
            intents=intents,
            application_id=config.APPLICATION_ID)

        # Create instances of the shell bot, one per channel
        self.instance = None
        self.channels = {}

        ################################################################################
        # Raffle reaction tracking
        # This is passed by reference - so don't assign to it directly!
        self.rlogger = logging.getLogger("react")
        self.rlogger.setLevel(config.REACTIONS_LOG_LEVEL)

        self.rreact = {
            "message_id": None,
            "channel_id": None,
            "msg_contents": None,
            "count": 0,
            "timestamp": datetime.datetime.now(),
            "msg": None,
        }

    async def setup_hook(self) -> None:
        # start tasks to run in the background
        # See https://github.com/Rapptz/discord.py/blob/v2.3.2/examples/background_task.py
        # The start method is provided by the decorator
        self.shard_status_background_task.start()

    async def on_ready(self):
        """Bot ready"""

        logging.info('Logged in as')
        logging.info(self.user.name)
        logging.info(self.user.id)

        killer.register(asyncio.get_running_loop())

        # On ready can happen multiple times when the bot automatically reconnects
        # Don't re-create the per-channel listeners when this happens
        if self.instance is None:
            self.instance = AutomationBotInstance(self, self.rreact)
            await bot.add_cog(self.instance, guilds=[discord.Object(id=config.GUILD_ID)])

            for channel_id in config.CHANNELS:
                try:
                    channel = self.get_channel(channel_id)
                    self.channels[channel_id] = self.instance
                    if channel_id != 486019840134610965: # TODO: Config... this is the visible weekly update channel
                        await channel.send(config.NAME + " started and now listening.")
                except Exception:
                    logging.error("Cannot connect to channel: %s", config.CHANNELS)

    @tasks.loop(seconds=5)
    async def shard_status_background_task(self):
        await self.instance.status_tick()

    @shard_status_background_task.before_loop
    async def before_shard_status_background_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

    async def on_message(self, message):
        """Bot received message"""

        # Don't process messages while stopping
        if killer.stopping:
            logging.info('Ignoring message during shutdown')
            return

        if message.channel.id in self.channels:
            try:
                ctx = await self.get_context(message)
                await self.channels[message.channel.id].handle_message(ctx, message)
            except Exception as e:
                await message.channel.send(message.author.mention)
                await message.channel.send("**ERROR**: ```" + str(e) + "```")
                for chunk in split_string(traceback.format_exc()):
                    await message.channel.send("```" + chunk + "```")

    async def on_raw_reaction_add(self, payload):
        """Bot detected reaction add"""
        try:
            if payload.user_id == self.user.id:
                # Don't handle self changes
                return

            if config.REACTIONS_ENABLED:
                self.rlogger.debug("Processing added reaction")

                if payload.channel_id in config.IGNORED_REACTION_CHANNELS:
                    return

                channel = self.get_channel(payload.channel_id)

                try:
                    msg = await channel.fetch_message(payload.message_id)
                except discord.errors.Forbidden:
                    self.rlogger.warning("Permission denied retrieving reaction message in channel %s", channel.name)
                    return

                msg_contents = re.sub("''*", "'", msg.clean_content).replace('\\', '')
                if len(msg_contents) < 1:
                    return

                # Conditionally timezone aware cutoff time
                if msg.created_at.tzinfo is None:
                    time_cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
                else:
                    time_cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)

                self.rlogger.debug("time_cutoff=%s      msg.created_at=%s", time_cutoff, msg.created_at)
                if msg.created_at > time_cutoff:
                    self.rlogger.debug("Reaction was new enough")

                    # If we want to prevent users from using a particular reaction type, you can
                    # This requires manage message perms though...
                    #if '\U0001f441' in payload.emoji.name:
                    #    user = self.get_user(payload.user_id)
                    #    await msg.remove_reaction(payload.emoji, user)
                    #    return

                    highest_reaction_count = 0
                    self.rlogger.debug("Reactions: %s", msg.reactions)
                    for reaction in msg.reactions:
                        if '\U0001f441' in reaction.emoji:
                            continue

                        if reaction.count > highest_reaction_count:
                            highest_reaction_count = reaction.count

                    if (highest_reaction_count > self.rreact["count"] or (time_cutoff > self.rreact["timestamp"])):

                        # If the bot can't react to a message due to permission issues, don't mark it as the winning message
                        try:
                            await msg.add_reaction('\U0001f441')
                        except Exception:
                            self.rlogger.warning("Permission denied adding reaction in channel %s", channel.name)
                            return

                        if self.rreact["msg"] is not None:
                            try:
                                await self.rreact["msg"].remove_reaction('\U0001f441', self.user)
                            except Exception:
                                self.rlogger.warning("Failed to remove previous reaction in %s", channel.name)
                                self.rlogger.warning(traceback.format_exc())

                        self.rreact["message_id"] = payload.message_id
                        self.rreact["channel_id"] = payload.channel_id
                        self.rreact["msg_contents"] = msg_contents
                        self.rreact["count"] = highest_reaction_count
                        self.rreact["timestamp"] = msg.created_at
                        self.rreact["msg"] = msg
                        self.rlogger.debug("Current rreact = %s", pformat(self.rreact))

        except Exception:
            self.rlogger.error("Failed to handle adding reaction")
            self.rlogger.error(traceback.format_exc())

    async def on_raw_reaction_remove(self, payload):
        """Bot detected reaction remove"""
        try:
            if payload.user_id == self.user.id:
                # Don't handle self changes
                return

            if config.REACTIONS_ENABLED:
                self.rlogger.debug("Processing removed reaction")

                if self.rreact["channel_id"] == payload.channel_id and self.rreact["message_id"] == payload.message_id:
                    channel = self.get_channel(payload.channel_id)
                    msg = await channel.fetch_message(payload.message_id)

                    # Same message as the current winner - update counts
                    highest_reaction_count = 0
                    for reaction in msg.reactions:
                        self.rlogger.debug("Reactions: %s", msg.reactions)
                        if '\U0001f441' in reaction.emoji:
                            continue
                        if reaction.count > highest_reaction_count:
                            highest_reaction_count = reaction.count

                    if highest_reaction_count <= 0:
                        # This no longer has any other reactions
                        self.rreact["message_id"] = None
                        self.rreact["channel_id"] = None
                        self.rreact["msg_contents"] = None
                        self.rreact["msg"] = None
                        self.rreact["count"] = 0
                        self.rreact["timestamp"] = datetime.datetime.now()
                        await msg.remove_reaction('\U0001f441', self.user)
                        self.rlogger.debug("Cleared currently leading raffle reaction because it has no more reactions")
                    else:
                        self.rreact["count"] = highest_reaction_count
                        self.rlogger.debug("Set count to %s", highest_reaction_count)

        except Exception:
            self.rlogger.error("Failed to handle removing reaction")
            self.rlogger.error(traceback.format_exc())

    async def on_raw_reaction_clear(self, payload):
        """Bot detected reaction clear"""
        try:
            if config.REACTIONS_ENABLED:
                self.rlogger.debug("Processing cleared reaction")

                if self.rreact["channel_id"] == payload.channel_id and self.rreact["message_id"] == payload.message_id:
                    # This is no longer the winner
                    self.rreact["message_id"] = None
                    self.rreact["channel_id"] = None
                    self.rreact["msg_contents"] = None
                    self.rreact["msg"] = None
                    self.rreact["count"] = 0
                    self.rreact["timestamp"] = datetime.datetime.now()
                    self.rlogger.debug("Cleared currently leading raffle reaction")

        except Exception:
            self.rlogger.error("Failed to handle removing reaction")
            self.rlogger.error(traceback.format_exc())

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = AutomationBot()
killer = GracefulKiller(bot)

async def main():
    """Asyncio entrypoint"""
    await bot.start(config.LOGIN)

asyncio.run(main())

logging.info("Terminating")
