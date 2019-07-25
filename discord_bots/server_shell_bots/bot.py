#!/usr/bin/env python3

import os
import sys
import logging
import yaml
import threading
import traceback
from pprint import pprint

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

# Read the bot's config file
with open(config_path, 'r') as ymlfile:
    config = yaml.load(ymlfile)

config["main_pid"] = os.getpid()
config["listening"] = listening()

assert "login" in config, "bot's config.yml file must contain 'login' token"
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
        print('Config error: No such command "{}"'.format(command))
config["actions"] = actions

config["extraDebug"] = False
for arg in sys.argv[1:]:
    if arg == "--verbose" or arg == "-v":
        config["extraDebug"] = True

config["channel_ids"] = list(config["channels"].keys())

pprint(config)

print("Starting the client...")

try:
    # Start the bot socket server which also accepts commands
    #bot_srv = BotSocketServer("127.0.0.1", 8765, config, native_restart)
    #threading.Thread(target = bot_srv.listen).start()

    client = discord.Client()

    ################################################################################
    # Discord event handlers

    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')
        for channel_id in config["channel_ids"]:
            try:
                channel = client.get_channel(channel_id)
                await client.send_message(channel, config["name"] + " started and now listening.")
            except:
                print( "Cannot connect to channel: " + config["channels"][channel_id] )

    @client.event
    async def on_message(message):
        if message.channel.id in config["channel_ids"]:
            actionClass = findBestMatchDiscord(config, message)
            if actionClass is None:
                return
            try:
                action = actionClass(config, message)
                if not action.hasPermissions(message.author):
                    await client.send_message(message.channel, "Sorry " + message.author.mention + ", you do not have permission to run this command")
                else:
                    await action.doActions(client, message.channel, message.author)
            except Exception as e:
                await client.send_message(message.channel, message.author.mention)
                await client.send_message(message.channel, "**ERROR**: ```" + str(e) + "```")
                if config["extraDebug"]:
                    for chunk in split_string(traceback.format_exc()):
                        await client.send_message(message.channel, "```" + chunk + "```")


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
    print("The following error was visible from outside the client, and may be used to restart or fix it:")
    print(repr(e))

print("Terminating")

