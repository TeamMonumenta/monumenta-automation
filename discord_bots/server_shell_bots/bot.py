#!/usr/bin/env python3.6

import os
import sys
import logging
import json
import threading
import traceback

import asyncio
from bot_socket_server import BotSocketServer

logging.basicConfig(level=logging.INFO)

import discord
from shell_actions import allActionsDict, findBestMatchDiscord, listening, native_restart
from shell_common import split_string

################################################################################
# Config / Environment

botConfig = {}

botConfig["main_pid"] = os.getpid()
botConfig["listening"] = listening()
botConfig["config_dir"] = os.path.expanduser("~/.monumeneta_bot/")

# Get bot's login info
loginInfo = None
with open(botConfig["config_dir"]+'login','r') as f:
    loginInfo = f.readline()
    if loginInfo[-1] == '\n':
        loginInfo = loginInfo[:-1]
if loginInfo is None:
    sys.exit('No login info is provided')

# Set this bot's name (used to select specific bots)
botName = None
with open(botConfig["config_dir"]+'bot_name','r') as f:
    botName = f.readline()
    if botName[-1] == '\n':
        botName = botName[:-1]
if botName is None:
    sys.exit('Could not find ' + botConfig["config_dir"] + 'bot_name')
botConfig["name"] = botName

# List of actions this bot handles
botActions = {}
with open(botConfig["config_dir"]+'commands','r') as f:
    for line in f:
        line = line[:-1]
        if line in allActionsDict:
            botActions[line] = allActionsDict[line]
        else:
            print('Config error: No such command "{}"'.format(line))
if len(botActions.keys()) == 0:
    sys.exit('Could not find ' + botConfig["config_dir"]+'commands')
botConfig["actions"] = botActions

# List of shards we're expecting to find
serverShards = {}
with open(botConfig["config_dir"]+'shards','r') as f:
    serverShards = json.load(f)
if len(serverShards.keys()) == 0:
    print('WARNING: No shards found.')
botConfig["shards"] = serverShards

botConfig["extraDebug"] = False
for arg in sys.argv[1:]:
    if arg == "--verbose" or arg == "-v":
        botConfig["extraDebug"] = True

# List of channels this bot will consume messages in

botChannelNames = {
    '420045459177078795':'monumenta-bot (dev discord)',
    '467361088460029954':'moderation-bot (public discord, moderators + TE only)',
    '486019840134610965':'epic-bot (public discord, publicly visible, used for terrain reset)',
}

botChannels = list(botChannelNames.keys())

while native_restart.state:
    print("Starting the client...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Start the bot socket server which also accepts commands
        # TODO: This breaks bot auto restarting
        #bot_srv = BotSocketServer("127.0.0.1", 8765, botConfig)
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
            for channelId in botChannels:
                try:
                    channel = client.get_channel(channelId)
                    await client.send_message(channel, botName + " started and now listening.")
                except:
                    print( "Cannot connect to channel: " + botChannelNames[channelId] )

        @client.event
        async def on_message(message):
            if message.channel.id in botChannels:
                actionClass = findBestMatchDiscord(botConfig, message)
                if actionClass is None:
                    return
                try:
                    action = actionClass(botConfig, message)
                    if not action.hasPermissions(message.author):
                        await client.send_message(message.channel, "Sorry " + message.author.mention + ", you do not have permission to run this command")
                    else:
                        await action.doActions(client, message.channel, message.author)
                except Exception as e:
                    await client.send_message(message.channel, message.author.mention)
                    await client.send_message(message.channel, "**ERROR**: ```" + str(e) + "```")
                    if botConfig["extraDebug"]:
                        for chunk in split_string(traceback.format_exc()):
                            await client.send_message(message.channel, "```" + chunk + "```")


        ################################################################################
        # Ignore these, just noting them to avoid the errors we were getting

        @client.event
        async def on_message_delete():
            pass

        @client.event
        async def on_message_edit():
            pass

        @client.event
        async def on_reaction_add():
            pass

        @client.event
        async def on_reaction_remove():
            pass

        @client.event
        async def on_reaction_clear():
            pass

        ################################################################################
        # Entry point

        client.run(loginInfo)
        print("No error detected from outside the client, restarting.")
    except RuntimeError as e:
        print("Runtime Error detected in loop. Exiting.")
        print(repr(e))
        native_restart.state = False
    except BaseException as e:
        print("The following error was visible from outside the client, and may be used to restart or fix it:")
        print(repr(e))
print("Terminating")

