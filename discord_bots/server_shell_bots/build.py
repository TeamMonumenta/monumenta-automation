#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logging.basicConfig(level=logging.INFO)

import discord
from shell_actions import GenerateInstancesAction, PrepareResetBundleAction, TestAction, DebugAction, TestPrivilegedAction

################################################################################
# Config / Environment

client = discord.Client()

channel = ""

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
    if message.channel == channel:
        if message.content in actionDict:
            action = actionDict[message.content]()
            if not action.hasPermissions(message.author):
                await client.send_message(message.channel, "Sorry " + message.author.mention + ", you do not have permission to run this command")
            else:
                await action.doActions(client, channel, message.author)
            return

# The master list of commands this bot is able to handle
actionDict = {}

actionDict[DebugAction().getCommand()] = DebugAction
actionDict[TestAction().getCommand()] = TestAction
actionDict[GenerateInstancesAction().getCommand()] = GenerateInstancesAction
actionDict[PrepareResetBundleAction().getCommand()] = PrepareResetBundleAction
actionDict[TestPrivilegedAction().getCommand()] = TestPrivilegedAction

print("Handling these commands:")
print(actionDict.keys())

################################################################################
# Entry point
client.run('NDIwMDQ0ODMxMjg1NDQ0NjI5.DX49qQ.eIkPQMOllPAGKaaN8VInr6RKqHI')

