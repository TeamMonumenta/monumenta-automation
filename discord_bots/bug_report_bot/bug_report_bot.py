#!/usr/bin/env python3.6

import os
import sys
import logging
import traceback
import yaml

import asyncio

logging.basicConfig(level=logging.INFO)

import discord

from bug_report_manager import BugReportManager, split_string

################################################################################
# Config / Environment

bot_config = {}

config_dir = os.path.expanduser("~/.bug_report_bot/")
config_path = os.path.join(config_dir, "config.yml")

# Get bot's login info
with open(config_path, 'r') as ymlfile:
    bot_config = yaml.load(ymlfile)
bot_config["database_path"] = os.path.join(config_dir, "database.json")
bot_config["main_pid"] = os.getpid()

# TODO: Better automatic restarting
restart = True
while restart:
    restart = False

    print("Starting the bug reaction bot...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        client = discord.Client()
        manager = BugReportManager(client, bot_config)

        ################################################################################
        # Discord event handlers

        @client.event
        async def on_ready():
            print('Logged in as')
            print(client.user.name)
            print(client.user.id)

        @client.event
        async def on_message(message):
            if message.channel.id in bot_config["bot_input_channels"]:
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
        async def on_message_delete(_):
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

        if "login" not in bot_config is None:
            sys.exit('No login info is provided')
        client.run(bot_config["login"])

        print("No error detected from outside the client, restarting.")
    except RuntimeError as e:
        print("Runtime Error detected in loop. Exiting.")
        print(repr(e))
        native_restart.state = False
    except BaseException as e:
        print("The following error was visible from outside the client, and may be used to restart or fix it:")
        print(repr(e))
print("Terminating")
