#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)

import discord
from shell_actions import allActionsDict, findBestMatch, commandPrefix

################################################################################
# Config / Environment

botConfig = {}

botConfig["listening"] = True

botConfig["config_dir"] = os.path.expanduser("~/.monumeneta_bot/")

loginInfo = None
with open(botConfig["config_dir"]+'login','r') as f:
    loginInfo = f.readline()
if loginInfo is None:
    sys.exit('No login info is provided')

botConfig["name"] = None
with open(botConfig["config_dir"]+'bot_name','r') as f:
    botConfig["name"] = f.readline()
if botConfig["name"] is None:
    sys.exit('Could not find ' + botConfig["config_dir"] + 'bot_name')

# List of actions this bot handles
botConfig["actions"] = {}
with open(botConfig["config_dir"]+'commands','r') as f:
    for line in f:
        line = commandPrefix + line[:-1]
        if line in allActionsDict:
            botConfig["actions"][line] = allActionsDict[line]
        else:
            print('Config error: No such command "{}"'.format(line))
if len(botConfig["actions"].keys()) == 0:
    sys.exit('Could not find ' + botConfig["config_dir"]+'commands')

botConfig["extraDebug"] = False
for arg in sys.argv[1:]:
    if arg == "--verbose" or arg == "-v":
        botConfig["extraDebug"] = True

# List of channels this bot will consume messages in
# monumenta-bot and general
botChannels = ['420045459177078795', '186225508562763776']

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

