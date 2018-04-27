#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging

logging.basicConfig(level=logging.INFO)

import discord

# Handy utility for running an SSH agent with a key file for this shell
# https://github.com/haarcuba/ssh-agent-setup
import ssh_agent_setup
ssh_agent_setup.setup()
ssh_agent_setup.addKey('/home/rock/.ssh/id_rsa')

from shell_actions import *

################################################################################
# Config / Environment

client = discord.Client()

extraDebug = False
for arg in sys.argv[1:]:
    if arg == "--verbose" or arg == "-v":
        extraDebug = True

# List of channels this bot will consume messages in
# monumenta-bot and general
botChannels = ['420045459177078795', '186225508562763776']

# List of actions this bot handles
actionDict = {}
#actionDict[DebugAction().command] = DebugAction
#actionDict[TestAction().command] = TestAction
actionDict[ListShardsAction().command] = ListShardsAction
#actionDict[TestPrivilegedAction().command] = TestPrivilegedAction
#actionDict[TestUnprivilegedAction().command] = TestUnprivilegedAction
actionDict[FetchResetBundleAction().command] = FetchResetBundleAction
actionDict[StopIn10MinutesAction().command] = StopIn10MinutesAction
actionDict[StopAndBackupAction().command] = StopAndBackupAction
actionDict[TerrainResetAction().command] = TerrainResetAction

botHelp = '''
This is the monumenta play server bot.
It runs on the play server's console.
It can be used to run actions on the play server.
'''

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

client.run('NDIwMDQ1MTQxNDU0MjI1NDI3.DanMyA.SCxISaPMCyBiQ7lFiEQV0BdAIeY')

