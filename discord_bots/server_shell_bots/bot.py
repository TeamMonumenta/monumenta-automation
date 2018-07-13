#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import os
import sys
import logging
import json

logging.basicConfig(level=logging.INFO)

import discord
from shell_actions import allActionsDict, findBestMatch

################################################################################
# Config / Environment

botConfig = {}

botConfig["main_pid"] = os.getpid()
botConfig["listening"] = True
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

botChannels = [
    '420045459177078795', # monumenta-bot
    #'186225508562763776', # general
    '467361088460029954', # moderation-bot (public discord)
]

client = discord.Client()

################################################################################
# Discord event handlers

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.channel.id in botChannels:
        actionClass = findBestMatch(botConfig,message.content)
        if actionClass is None:
            return
        action = actionClass(botConfig,message)
        if not action.hasPermissions(message.author):
            await client.send_message(message.channel, "Sorry " + message.author.mention + ", you do not have permission to run this command")
        else:
            await action.doActions(client, message.channel, message.author)
        return

################################################################################
# Entry point

client.run(loginInfo)

