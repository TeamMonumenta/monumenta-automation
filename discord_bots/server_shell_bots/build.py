#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logging.basicConfig(level=logging.INFO)

import discord
from shell_actions import *

################################################################################
# Config / Environment

client = discord.Client()

# List of channels this bot will consume messages in
botChannels = ['420045459177078795']

# List of actions this bot handles
actionDict = {}
actionDict[DebugAction().getCommand()] = DebugAction
actionDict[TestAction().getCommand()] = TestAction
actionDict[ListShardsAction().getCommand()] = ListShardsAction
actionDict[GenerateInstancesAction().getCommand()] = GenerateInstancesAction
actionDict[PrepareResetBundleAction().getCommand()] = PrepareResetBundleAction
actionDict[TestPrivilegedAction().getCommand()] = TestPrivilegedAction
actionDict[TestUnprivilegedAction().getCommand()] = TestUnprivilegedAction

botHelp = '''
This is the monumenta build server bot.
It runs on the build server's console.
It can be used to run actions on the build server.
'''

################################################################################
# Discord event handlers

@client.event
async def on_ready():
    global channel

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    channel = client.get_channel('420045459177078795')

@client.event
async def on_message(message):
    if message.channel.id in botChannels:
        if message.content == "!help":
            helptext = botHelp + '\n__Available Actions__'
            for actionClass in actionDict.values():
                action = actionClass()
                if action.hasPermissions(message.author):
                    helptext += "\n**" + action.getCommand() + "**"
                else:
                    helptext += "\n~~" + action.getCommand() + "~~"
                helptext += "```" + action.help() + "```"

            await client.send_message(message.channel, helptext)
            return

        if message.content in actionDict:
            action = actionDict[message.content]()
            if not action.hasPermissions(message.author):
                await client.send_message(message.channel, "Sorry " + message.author.mention + ", you do not have permission to run this command")
            else:
                await action.doActions(client, channel, message.author)
            return

################################################################################
# Entry point

client.run('NDIwMDQ0ODMxMjg1NDQ0NjI5.DX49qQ.eIkPQMOllPAGKaaN8VInr6RKqHI')

