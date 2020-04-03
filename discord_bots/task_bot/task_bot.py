#!/usr/bin/env python3

import os
import sys
import logging
import traceback
import yaml
import asyncio
from pprint import pformat

logging.basicConfig(level=logging.INFO)

import discord

from task_database import TaskDatabase
from common import split_string

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

try:
    client = discord.Client()

    facet_channels = []

    ################################################################################
    # Discord event handlers

    @client.event
    async def on_ready():
        logging.info('Logged in as')
        logging.info(client.user.name)
        logging.info(client.user.id)

        # On ready can happen multiple times when the bot automatically reconnects
        # Don't re-create the per-channel listeners when this happens
        if len(facet_channels) == 0:
            for facet in bot_config["facets"]:
                db = TaskDatabase(client, facet, config_dir)
                for input_channel in facet["bot_input_channels"]:
                    facet_channels.append((input_channel, db))

    @client.event
    async def on_message(message):
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
