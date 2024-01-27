import asyncio
import discord
import logging
import signal
import traceback
import config

from common import split_string
from discord.ext import commands

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
        logging.info("Saving %s...", config.DESCRIPTOR_PLURAL)
        self._bot.db._stopping = True
        self._bot.db.save()
        logging.info("All saved. Handing off to discord client...")
        if self._event_loop is not None:
            asyncio.run_coroutine_threadsafe(self._bot.close(), self._event_loop)

class TaskBot(commands.Bot):
    """Top-level discord bot object"""

    def __init__(self):
        super().__init__(
            command_prefix='.',
            intents=intents,
            application_id=config.APPLICATION_ID)

        self.db = None
        #self.modmail = None


    async def setup_hook(self):
        if self.db is None:
            try:
                await bot.load_extension(f"task_database")
                self.db = bot.get_cog(config.DESCRIPTOR_SHORT)
                if self.db is None:
                    raise Exception("Failed to get main cog")
                print(f"Loaded task bot cogs")
            except Exception as e:
                print(f"Failed to load task bot cogs")
                print(f"[ERROR] {e}")
        else:
            print("Already loaded task bot cogs")

        """ try:
            await bot.load_extension(f"flig_modmail")
            self.modmail = bot.get_cog("modmail")
            if self.modmail is None:
                raise Exception("Failed to get modmail cog")
            print(f"Loaded modmail cogs")
        except Exception as e:
            print(f"Failed to load modmail bot cogs")
            print(f"[ERROR] {e}") """

        await self.tree.sync()
        print("Successfully synced commands")
        print(f"Logged onto {self.user}")

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
        
        if message.channel.id == config.BOT_INPUT_CHANNEL:
            try:
                await self.db.handle_message(message)
            except Exception as e:
                await message.channel.send(message.author.mention)
                await message.channel.send("**ERROR**: ```" + str(e) + "```")
                for chunk in split_string(traceback.format_exc()):
                    await message.channel.send("```" + chunk + "```")
        
        if message.channel.id == config.DISCUSSION_ID:
            try:
                await self.db.handle_discussion_message(message)
            except Exception as e:
                return

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = TaskBot()
killer = GracefulKiller(bot)

async def main():
    """Asyncio entrypoint"""
    await bot.start(config.LOGIN)

asyncio.run(main())
