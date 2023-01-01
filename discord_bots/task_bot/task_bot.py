#!/usr/bin/env python3

import sys
import logging
import traceback
import signal
import asyncio
import kanboard

logging.basicConfig(level=logging.INFO)

import discord
from discord.ext import commands

import config
from common import split_string
from kanboard_webhooks import start_webhook_server
from task_database import TaskDatabase

class GracefulKiller:
    """Class to catch signals (CTRL+C, SIGTERM) and gracefully save databases and stop the bot"""

    def __init__(self, bot):
        self._bot = bot
        self.stopping = False

    def register(self):
        """Register signals that cause shutdown"""
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, _, __):
        """Exit gracefully on signal"""
        self.stopping = True
        logging.info("Received signal; shutting down...")
        logging.info("Saving %s...", config.DESCRIPTOR_PLURAL)
        self._bot.db._stopping = True
        self._bot.db.save()
        logging.info("All saved. Handing off to discord client...")
        # TODO: This is not the right way to do this. Kills the process at least... but really jank
        asyncio.run(self._bot.close())

class TaskBot(commands.Bot):
    """Top-level discord bot object"""

    def __init__(self):
        super().__init__(
            command_prefix='.',
            intents=intents,
            application_id=config.APPLICATION_ID)

        self.db = None
        self.kanboard_client = None
        self.kanboard_webhook_queue = None
        self.kanboard_webhook_process = None

    async def on_ready(self):
        """Bot ready"""
        logging.info('Logged in as')
        logging.info(self.user.name)
        logging.info(self.user.id)

        killer.register()

        if config.KANBOARD is not None:
            self.kanboard_client = kanboard.Client(config.KANBOARD['url'], 'jsonrpc', config.KANBOARD['token'])
            if self.kanboard_client is None:
                sys.exit("Kanboard specified but failed to connect")

            self.kanboard_webhook_process, self.kanboard_webhook_queue = start_webhook_server()

        # On ready can happen multiple times when the bot automatically reconnects
        # Don't re-create the per-channel listeners when this happens
        if self.db is None:
            self.db = TaskDatabase(self, self.kanboard_client)
            await bot.add_cog(self.db, guilds=[discord.Object(id=config.GUILD_ID)])

    async def on_message(self, message):
        """Bot received message"""

        logging.debug("Received message in channel %s: %s", message.channel, message.content)

        if self.db is None:
            logging.info('Ignoring message during init')
            return

        # Don't process messages while stopping
        if killer.stopping:
            logging.info('Ignoring message during shutdown')
            return

        if self.kanboard_webhook_queue is not None:
            while not self.kanboard_webhook_queue.empty():
                json_msg = self.kanboard_webhook_queue.get()
                await self.db.on_webhook_post(json_msg)

        if message.channel.id == config.BOT_INPUT_CHANNEL:
            try:
                await self.db.handle_message(message)
            except Exception as e:
                await message.channel.send(message.author.mention)
                await message.channel.send("**ERROR**: ```" + str(e) + "```")
                for chunk in split_string(traceback.format_exc()):
                    await message.channel.send("```" + chunk + "```")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = TaskBot()
killer = GracefulKiller(bot)

async def main():
    """Asyncio entrypoint"""
    await bot.start(config.LOGIN)

asyncio.run(main())
