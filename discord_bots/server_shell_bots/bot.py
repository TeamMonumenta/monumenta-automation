#!/usr/bin/env python3

import os
import sys
import logging
import yaml
import threading
import traceback
from pprint import pformat

from bot_socket_server import BotSocketServer

logging.basicConfig(level=logging.INFO)

import discord
from shell_actions import allActionsDict, findBestMatchDiscord, listening
from shell_common import split_string

################################################################################
# Config / Environment

config = {}

config_dir = os.path.expanduser("~/.monumenta_bot/")
config_path = os.path.join(config_dir, "config.yml")

# Read the bot's config files
with open(config_path, 'r') as ymlfile:
    config = yaml.load(ymlfile)

config["main_pid"] = os.getpid()
config["listening"] = listening()

assert "login" in config, "bot's login.yml file must contain 'login' token"
assert "name" in config, "bot's config.yml file must contain 'name' value"
assert "channels" in config, "bot's config.yml file must contain 'channels' map"
assert "commands" in config, "bot's config.yml file must contain 'commands' list"
assert "shards" in config, "bot's config.yml file must contain 'shards' map"

# List of actions this bot handles
actions = {}
for command in config["commands"]:
    if command in allActionsDict:
        actions[command] = allActionsDict[command]
    else:
        logging.error('Config error: No such command {!r}'.format(command))
config["actions"] = actions

config["extraDebug"] = False
for arg in sys.argv[1:]:
    if arg == "--verbose" or arg == "-v":
        config["extraDebug"] = True

config["channel_ids"] = list(config["channels"].keys())

logging.info(pformat(config))

logging.info("Starting the client...")

try:
    # Start the bot socket server which also accepts commands
    #bot_srv = BotSocketServer("127.0.0.1", 8765, config, native_restart)
    #threading.Thread(target = bot_srv.listen).start()

    client = discord.Client()

    ################################################################################
    # Discord event handlers

    @client.event
    async def on_ready():
        logging.info('Logged in as')
        logging.info(client.user.name)
        logging.info(client.user.id)
        logging.info('------')
        for channel_id in config["channel_ids"]:
            try:
                channel = client.get_channel(channel_id)
                if channel_id != 486019840134610965:
                    await channel.send(config["name"] + " started and now listening.")
            except:
                logging.error( "Cannot connect to channel: " + config["channels"][channel_id] )

    @client.event
    async def on_message(message):
        if message.channel.id in config["channel_ids"]:
            actionClass = findBestMatchDiscord(config, message)
            if actionClass is None:
                return
            try:
                action = actionClass(config, message)
                if not action.hasPermissions(message.author):
                    await message.channel.send("Sorry " + message.author.mention + ", you do not have permission to run this command")
                else:
                    await action.doActions(client, message.channel, message.author)
            except Exception as e:
                await message.channel.send(message.author.mention)
                await message.channel.send("**ERROR**: ```" + str(e) + "```")
                if config["extraDebug"]:
                    for chunk in split_string(traceback.format_exc()):
                        await message.channel.send("```" + chunk + "```")


    ################################################################################
    # Ignore these, just noting them to avoid the errors we were getting

    @client.event
    async def on_message_delete(_):
        pass

    @client.event
    async def on_message_edit(_, __):
        pass

    @client.event
    async def on_reaction_add(_, __):
        pass

    @client.event
    async def on_reaction_remove(_, __):
        pass

    @client.event
    async def on_reaction_clear(_, __):
        pass

    ################################################################################
    # Entry point

    client.run(config["login"])
except Exception as e:
    logging.error("The following error was visible from outside the client, and may be used to restart or fix it:")
    logging.error(repr(e))

logging.info("Terminating")

