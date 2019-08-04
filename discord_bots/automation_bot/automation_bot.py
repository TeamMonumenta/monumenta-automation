#!/usr/bin/env python3

import os
import sys
import logging
import yaml
import threading
import traceback
from pprint import pformat

logging.basicConfig(level=logging.INFO)

import discord
from automation_bot_lib import split_string
from automation_bot_instance import AutomationBotInstance

################################################################################
# Config / Environment

config = {}

config_dir = os.path.expanduser("~/.monumenta_bot/")
config_path = os.path.join(config_dir, "config.yml")

# Read the bot's config files
with open(config_path, 'r') as ymlfile:
    config = yaml.load(ymlfile)

logging.info("Config: \n{}".format(pformat(config)))

try:
    client = discord.Client()

    # Create instances of the shell bot, one per channel
    channels = {}

    ################################################################################
    # Discord event handlers

    @client.event
    async def on_ready():
        logging.info('Logged in as')
        logging.info(client.user.name)
        logging.info(client.user.id)
        logging.info('------')

        for channel_id in config["channels"]:
            try:
                channel = client.get_channel(channel_id)
                instance = AutomationBotInstance(client, channel, config)
                channels[channel_id] = instance
                await channel.send(config["name"] + " started and now listening.")
            except:
                logging.error( "Cannot connect to channel: " + config["channels"] )

    @client.event
    async def on_message(message):
        if message.channel.id in channels:
            try:
                await channels[message.channel.id].handle_message(message)
            except Exception as e:
                await message.channel.send(message.author.mention)
                await message.channel.send("**ERROR**: ```" + str(e) + "```")
                for chunk in split_string(traceback.format_exc()):
                    await message.channel.send("```" + chunk + "```")

    ################################################################################
    # Entry point

    client.run(config["login"])
except Exception as e:
    logging.error("The following error was visible from outside the client, and may be used to restart or fix it:")
    logging.error(traceback.format_exc())

logging.info("Terminating")

