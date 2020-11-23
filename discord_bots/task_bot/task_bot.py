#!/usr/bin/env python3

import os
import sys
import logging
import traceback
import yaml
import asyncio
import signal
import kanboard
from pprint import pformat

logging.basicConfig(level=logging.INFO)

import discord

from task_database import TaskDatabase
from common import split_string
from kanboard_webhooks import start_webhook_server

################################################################################
# Config / Environment

bot_config = {}

config_dir = os.path.expanduser("~/.task_bot/")
config_path = os.path.join(config_dir, "config.yml")

# Read the bot's config file
with open(config_path, 'r') as ymlfile:
    bot_config = yaml.load(ymlfile)

logging.info("\nBot Configuration: {}\n".format(pformat(bot_config)))

if "login" not in bot_config is None:
    sys.exit('No login info is provided')

kanboard_client = None
kanboard_webhook_queue = None
kanboard_webhook_process = None
if 'kanboard' in bot_config:
    kanboard_client = kanboard.Client(bot_config['kanboard']['url'], 'jsonrpc', bot_config['kanboard']['token'])
    if kanboard_client is None:
        sys.exit("Kanboard specified but failed to connect")

    kanboard_webhook_process, kanboard_webhook_queue = start_webhook_server()


class GracefulKiller:

    def __init__(self, client, facet_channels):
        self.stopping = False
        self._client = client
        self._facet_channels = facet_channels

    def register(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.stopping = True
        logging.info("Received signal; shutting down...")
        for facet_channel, db in facet_channels:
            logging.info(f"Saving {db._descriptor_plural}...")
            db._stopping = True
            db.save()
        logging.info("All saved. Handing off to discord client...")

intents = discord.Intents.default()
intents.members = True

try:
    client = discord.Client(intents=intents)
    facet_channels = []

    killer = GracefulKiller(client, facet_channels)

    ################################################################################
    # Discord event handlers

    @client.event
    async def on_ready():
        logging.info('Logged in as')
        logging.info(client.user.name)
        logging.info(client.user.id)

        killer.register()

        # On ready can happen multiple times when the bot automatically reconnects
        # Don't re-create the per-channel listeners when this happens
        if len(facet_channels) == 0:
            for facet in bot_config["facets"]:
                db = TaskDatabase(client, kanboard_client, facet, config_dir)
                for input_channel in facet["bot_input_channels"]:
                    facet_channels.append((input_channel, db))

    @client.event
    async def on_message(message):
        # Don't process messages while stopping
        if killer.stopping:
            logging.info('Ignoring message during shutdown')
            return

        if kanboard_webhook_queue is not None:
            while not kanboard_webhook_queue.empty():
                json_msg = kanboard_webhook_queue.get()
                for _, db in facet_channels:
                    await db.on_webhook_post(json_msg)


        for facet_channel, db in facet_channels:
            if message.channel.id == facet_channel:
                try:
                    await db.handle_message(message)
                except Exception as e:
                    await message.channel.send(message.author.mention)
                    await message.channel.send("**ERROR**: ```" + str(e) + "```")
                    for chunk in split_string(traceback.format_exc()):
                        await message.channel.send("```" + chunk + "```")

    ################################################################################
    # Entry point

    client.run(bot_config["login"])

except Exception as e:
    logging.error("The following error was visible from outside the client, and may be used to restart or fix it:")
    logging.error(traceback.format_exc())
