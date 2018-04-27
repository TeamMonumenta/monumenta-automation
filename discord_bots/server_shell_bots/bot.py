#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)

import discord
from shell_actions import allActionsDict

################################################################################
# Config / Environment

configDir = os.path.expanduser("~/.monumeneta_bot/")

botName = None
with open(configDir+'bot_name','r') as f:
    botName = f.readline()
if botName is None:
    sys.exit('Could not find ' + configDir+'bot_name')

# List of actions this bot handles
actionDict = {}
with open(configDir+'commands','r') as f:
    for line in f:
        if line in allActionsDict:
            actionDict[line] = allActionsDict[line]
        else:
            print 'Config error: No such command "{}"'.format(line)

client = discord.Client()

extraDebug = False
for arg in sys.argv[1:]:
    if arg == "--verbose" or arg == "-v":
        extraDebug = True

# List of channels this bot will consume messages in
# monumenta-bot and general
botChannels = ['420045459177078795', '186225508562763776']

botHelp = '''
This is the monumenta {0} server bot.
It runs on the {0} server's console.
It can be used to run actions on the {0} server.
'''.format(botName)

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
        if message.content == "!help":
            helptext = botHelp + '\n__Available Actions__'
            for actionClass in actionDict.values():
                action = actionClass()
                if action.hasPermissions(message.author):
                    helptext += "\n**" + action.command + "**"
                else:
                    helptext += "\n~~" + action.command + "~~"
                helptext += "```" + action.help() + "```"

            await client.send_message(message.channel, helptext)
            return

        if message.content in actionDict:
            action = actionDict[message.content](debug=extraDebug)
            if not action.hasPermissions(message.author):
                await client.send_message(message.channel, "Sorry " + message.author.mention + ", you do not have permission to run this command")
            else:
                await action.doActions(client, message.channel, message.author)
            return

################################################################################
# Entry point

client.run('NDIwMDQ0ODMxMjg1NDQ0NjI5.DX49qQ.eIkPQMOllPAGKaaN8VInr6RKqHI')

