#!/usr/bin/env python3

import os
import sys
import logging
import traceback
import datetime
import signal
import asyncio

logging.basicConfig(level=logging.INFO)

import discord
from discord.ext import commands
from discord.ext import tasks

import pika

from config import Config
from automation_bot_lib import split_string
from automation_bot_instance import AutomationBotInstance

# TODO: This is ugly and needs updating if we ever move this file
_file_depth = 3
_file = os.path.abspath(__file__)
_top_level = os.path.abspath(os.path.join(_file, '../'*_file_depth))

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../utility_code"))
from lib_py3.lockout import LockoutException

config = Config()

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
        self.retry_delays = {
            "heartbeat": 0.0,
            "heartbeat_retry_backoff": 1.0,
            "status": 0.0,
            "reminders": 0.0,
        }

        # start tasks to run in the background
        # See https://github.com/Rapptz/discord.py/blob/v2.3.2/examples/background_task.py
        # The start method is provided by the decorator
        self.update_avatar_task.start()
        self.heartbeat_task.start()
        self.shard_status_task.start()
        self.reminders_task.start()

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

            await self.instance.load_raffle_reaction()

    @tasks.loop(seconds=60)
    async def update_avatar_task(self):
        await self.instance.check_updated_avatar()

    @update_avatar_task.before_loop
    async def before_update_avatar_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

    @tasks.loop(seconds=5)
    async def shard_status_task(self):
        if self.retry_delays["status"] > 0.0:
            self.retry_delays["status"] -= 5.0
            if self.retry_delays["status"] < 0.0:
                self.retry_delays["status"] = 0.0
            return

        try:
            await self.instance.status_tick()
        except discord.errors.DiscordServerError:
            self.rlogger.debug("A 5xx server error occurred on Discord's end, trying again later")
            self.retry_delays["status"] = 60.0
        # Future version?
        #except discord.errors.RateLimited as rate_limited:
        #    retry_after = rate_limited.retry_after
        #    self.rlogger.debug("%s", f"Rate limited (messages might not have sent in the first place); retrying after {retry_after}")
        #    self.retry_delays["status"] = retry_after

    @shard_status_task.before_loop
    async def before_shard_status_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

    @tasks.loop(seconds=1)
    async def heartbeat_task(self):
        if not (self.instance and self.instance._socket):
            return

        if self.retry_delays["heartbeat"] > 0.0:
            self.retry_delays["heartbeat"] -= 1.0
            if self.retry_delays["heartbeat"] < 0.0:
                self.retry_delays["heartbeat"] = 0.0
            return

        try:
            self.instance._socket.send_heartbeat()
            self.retry_delays["heartbeat_retry_backoff"] = 1.0
            return
        except pika.exceptions.StreamLostError as ex:
            self.rlogger.debug("Heartbeat stream lost, will retry shortly: %s", f"{ex}")

        self.retry_delays["heartbeat_retry_backoff"] *= 2.0
        if self.retry_delays["heartbeat_retry_backoff"] > 60.0:
            self.retry_delays["heartbeat_retry_backoff"] = 60.0
        self.retry_delays["heartbeat"] = self.retry_delays["heartbeat_retry_backoff"]

    @heartbeat_task.before_loop
    async def before_heartbeat_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

    @tasks.loop(seconds=1)
    async def reminders_task(self):
        if self.retry_delays["reminders"] > 0.0:
            self.retry_delays["reminders"] -= 1.0
            if self.retry_delays["reminders"] < 0.0:
                self.retry_delays["reminders"] = 0.0
            return

        try:
            await self.instance.reminders_tick()
        except discord.errors.DiscordServerError:
            self.rlogger.debug("A 5xx server error occurred on Discord's end, trying again later")
            self.retry_delays["reminders"] = 60.0
        # Future version?
        #except discord.errors.RateLimited as rate_limited:
        #    retry_after = rate_limited.retry_after
        #    self.rlogger.debug("%s", f"Rate limited (messages might not have sent in the first place); retrying after {retry_after}")
        #    self.retry_delays["reminders"] = retry_after

    @reminders_task.before_loop
    async def before_reminders_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

    async def on_message(self, message):
        """Bot received message"""

        # Don't process messages while stopping
        if killer.stopping:
            logging.info('Ignoring message during shutdown')
            return

        channel_handler = self.channels.get(message.channel.id, None)
        if channel_handler is not None:
            try:
                ctx = await self.get_context(message)
                await channel_handler.handle_message(ctx, message)
            except LockoutException:
                await channel_handler.display(ctx, 'There is a lockout preventing that action')
            except Exception as e:
                await message.channel.send(message.author.mention)
                await message.channel.send("**ERROR**: ```" + str(e) + "```")
                for chunk in split_string(traceback.format_exc()):
                    await message.channel.send("```" + chunk + "```")

    async def on_raw_reaction_add(self, payload):
        """Bot detected reaction add"""
        try:
            reaction_name = payload.emoji.name
            if isinstance(reaction_name, (discord.Emoji, discord.PartialEmoji)):
                reaction_name = reaction_name.name
            if '\U0001f441' in reaction_name:
                # Ignore the raffle indicator reaction
                return

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

                await self.instance.update_raffle_reaction(channel, msg)

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

                channel = self.get_channel(payload.channel_id)
                msg = await channel.fetch_message(payload.message_id)

                await self.instance.update_raffle_reaction(channel, msg)

        except Exception:
            self.rlogger.error("Failed to handle removing reaction")
            self.rlogger.error(traceback.format_exc())

    async def on_raw_reaction_clear(self, payload):
        """Bot detected reaction clear"""
        try:
            if config.REACTIONS_ENABLED:
                self.rlogger.debug("Processing cleared reaction")

                await self.instance.clear_raffle_reaction(channel_id=payload.channel_id, message_id=payload.message_id)

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
