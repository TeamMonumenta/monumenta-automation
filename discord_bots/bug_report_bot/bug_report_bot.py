#!/usr/bin/env python3.6

import os
import sys
import logging
import json
import threading
import traceback

import asyncio

logging.basicConfig(level=logging.INFO)

import discord

from bug_report_manager import BugReportManager, split_string
#from shell_common import split_string

################################################################################
# Config / Environment

botConfig = {}

botConfig["main_pid"] = os.getpid()
botConfig["config_dir"] = os.path.expanduser("~/.bug_report_bot/")
botConfig["database_path"] = os.path.join(botConfig["config_dir"], "database.json")

# Get bot's login info
loginInfo = None
with open(botConfig["config_dir"]+'login','r') as f:
    loginInfo = f.readline()
    if loginInfo[-1] == '\n':
        loginInfo = loginInfo[:-1]
if loginInfo is None:
    sys.exit('No login info is provided')


# List of channels this bot will consume messages in
bot_input_channels = [
    # Sekrit-bot-feed
    '569283901202366524',
]

# Sekrit-bot-feed
bug_reports_channel_id = '569283558741508107'

user_privileges = {
    # Combustible
    "302298391969267712": 4,
    # NickNackGus
    "228226807353180162": 3,
    # Crondis
    "225791510636003329": 3,
}

group_privileges = {
    # Team Epic (Leads)
    "224393252156080128": 3,
    # Team Epic (TE)
    "341032989787947008": 2,
    # Intern (TE)
    "390269554657460226": 2,
    # Moderator (Public)
    "313067199579422722": 2,
    # Team Monumenta (Public)
    "313066719365300264": 2,
}

# TODO: Better automatic restarting
restart = True
while restart:
    restart = False

    print("Starting the bug reaction bot...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        client = discord.Client()
        manager = BugReportManager(client, user_privileges, group_privileges, bug_reports_channel_id, botConfig["database_path"])

        ################################################################################
        # Discord event handlers

        @client.event
        async def on_ready():
            print('Logged in as')
            print(client.user.name)
            print(client.user.id)

        @client.event
        async def on_message(message):
            if message.channel.id in bot_input_channels:
                try:
                    await manager.handle_message(message)
                except Exception as e:
                    await client.send_message(message.channel, message.author.mention)
                    await client.send_message(message.channel, "**ERROR**: ```" + str(e) + "```")
                    for chunk in split_string(traceback.format_exc()):
                        await client.send_message(message.channel, "```" + chunk + "```")


        ################################################################################
        # Ignore these, just noting them to avoid the errors we were getting

        @client.event
        async def on_message_delete():
            pass

        @client.event
        async def on_message_edit(_, __):
            pass

        @client.event
        async def on_reaction_add(_, __):
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
