#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logging.basicConfig(level=logging.INFO)

import discord
from shell_actions import GenerateInstancesAction, PrepareResetBundleAction, TestAction

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
        for action in actionList:
            if message.content == action.getCommand():
                await action.doActions(client, channel)

# The master list of commands this bot is able to handle
actionList = [TestAction(), GenerateInstancesAction(), PrepareResetBundleAction()]

print("Handling these commands:")
for action in actionList:
    print("  " + action.getCommand())

################################################################################
# Entry point
client.run('NDIwMDQ0ODMxMjg1NDQ0NjI5.DX49qQ.eIkPQMOllPAGKaaN8VInr6RKqHI')

