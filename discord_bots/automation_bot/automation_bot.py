#!/usr/bin/env python3

import os
import re
import sys
import logging
import yaml
import threading
import traceback
import datetime
from pprint import pformat

logging.basicConfig(level=logging.INFO)

import discord
from automation_bot_lib import split_string
from automation_bot_instance import AutomationBotInstance

################################################################################
# Config / Environment

config = {}

if "BOT_CONFIG" in os.environ and os.path.isfile(os.environ["BOT_CONFIG"]):
    config_path = os.environ["BOT_CONFIG"]
else:
    config_dir = os.path.expanduser("~/.monumenta_bot/")
    config_path = os.path.join(config_dir, "config.yml")

# Read the bot's config files
with open(config_path, 'r') as ymlfile:
    config = yaml.load(ymlfile)

logging.info("Config: \n{}".format(pformat(config)))

old_umask = os.umask(0o027)
logging.info("New umask=0o027, old umask={}".format(oct(old_umask)))

try:
    client = discord.Client()

    # Create instances of the shell bot, one per channel
    channels = {}

    ################################################################################
    # Raffle reaction tracking
    # This is passed by reference - so don't assign to it directly!
    rlogger = logging.getLogger("react")
    # Set debug verbosity for this feature here
    rlogger.setLevel(logging.DEBUG)
    rreact = {};
    rreact["message_id"] = None
    rreact["channel_id"] = None
    rreact["msg_contents"] = None
    rreact["count"] = 0
    rreact["timestamp"] = datetime.datetime.now()
    rreact["msg"] = None

    ################################################################################
    # Discord event handlers

    @client.event
    async def on_ready():
        logging.info('Logged in as')
        logging.info(client.user.name)
        logging.info(client.user.id)
        logging.info('------')

        for channel_id in config["channels"]:
            try:
                channel = client.get_channel(channel_id)
                instance = AutomationBotInstance(client, channel, config, rreact)
                channels[channel_id] = instance
                await channel.send(config["name"] + " started and now listening.")
            except:
                logging.error( "Cannot connect to channel: " + config["channels"] )

    @client.event
    async def on_message(message):
        if message.channel.id in channels:
            try:
                await channels[message.channel.id].handle_message(message)
            except Exception as e:
                await message.channel.send(message.author.mention)
                await message.channel.send("**ERROR**: ```" + str(e) + "```")
                for chunk in split_string(traceback.format_exc()):
                    await message.channel.send("```" + chunk + "```")

    @client.event
    async def on_raw_reaction_add(payload):
        try:
            if payload.user_id == client.user.id:
                # Don't handle self changes
                return

            if config["reactions_enabled"]:
                rlogger.debug("Processing added reaction")

                time_cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=1)

                channel = client.get_channel(payload.channel_id)

                try:
                    msg = await channel.fetch_message(payload.message_id)
                except discord.errors.Forbidden:
                    rlogger.warn("Permission denied retrieving reaction message in channel {}".format(channel.name))
                    return

                rlogger.debug("time_cutoff={}      msg.created_at={}".format(time_cutoff, msg.created_at))
                if msg.created_at > time_cutoff:
                    rlogger.debug("Reaction was new enough")

                    # If we want to prevent users from using a particular reaction type, you can
                    # This requires manage message perms though...
                    #if '\U0001f441' in payload.emoji.name:
                    #    user = client.get_user(payload.user_id)
                    #    await msg.remove_reaction(payload.emoji, user)
                    #    return

                    highest_reaction_count = 0
                    rlogger.debug("Reactions: {}".format(msg.reactions))
                    for reaction in msg.reactions:
                        if '\U0001f441' in reaction.emoji:
                            continue

                        if reaction.count > highest_reaction_count:
                            highest_reaction_count = reaction.count

                    if (highest_reaction_count > rreact["count"] or (time_cutoff > rreact["timestamp"])):

                        if rreact["msg"] is not None:
                            await rreact["msg"].remove_reaction('\U0001f441', client.user)

                        rreact["message_id"] = payload.message_id
                        rreact["channel_id"] = payload.channel_id
                        rreact["msg_contents"] = re.sub("''*", "'", msg.clean_content).replace('\\', '')
                        rreact["count"] = highest_reaction_count
                        rreact["timestamp"] = msg.created_at
                        rreact["msg"] = msg
                        rlogger.debug("Current rreact = {}".format(pformat(rreact)))

                        try:
                            await msg.add_reaction('\U0001f441')
                        except Exception as e:
                            rlogger.warn("Permission denied adding reaction in channel '{}'".format(channel.name))
                            return
        except Exception as e:
            rlogger.error("Failed to handle adding reaction")
            rlogger.error(traceback.format_exc())

    @client.event
    async def on_raw_reaction_remove(payload):
        try:
            if payload.user_id == client.user.id:
                # Don't handle self changes
                return

            if config["reactions_enabled"]:
                rlogger.debug("Processing removed reaction")

                if rreact["channel_id"] == payload.channel_id and rreact["message_id"] == payload.message_id:
                    channel = client.get_channel(payload.channel_id)
                    msg = await channel.fetch_message(payload.message_id)

                    # Same message as the current winner - update counts
                    highest_reaction_count = 0
                    for reaction in msg.reactions:
                        rlogger.debug("Reactions: {}".format(msg.reactions))
                        if '\U0001f441' in reaction.emoji:
                            continue
                        if reaction.count > highest_reaction_count:
                            highest_reaction_count = reaction.count

                    rreact["count"] = highest_reaction_count
                    rlogger.debug("Set count to {}".format(highest_reaction_count))

        except Exception as e:
            rlogger.error("Failed to handle removing reaction")
            rlogger.error(traceback.format_exc())

    @client.event
    async def on_raw_reaction_clear(payload):
        try:
            if config["reactions_enabled"]:
                rlogger.debug("Processing cleared reaction")

                if rreact["channel_id"] == payload.channel_id and rreact["message_id"] == payload.message_id:
                    # This is no longer the winner
                    rreact["message_id"] = None
                    rreact["channel_id"] = None
                    rreact["msg_contents"] = None
                    rreact["count"] = 0
                    rreact["timestamp"] = datetime.datetime.now()
                    rlogger.debug("Cleared currently leading raffle reaction")

        except Exception as e:
            rlogger.error("Failed to handle removing reaction")
            rlogger.error(traceback.format_exc())

    ################################################################################
    # Entry point

    client.run(config["login"])
except Exception as e:
    logging.error("The following error was visible from outside the client, and may be used to restart or fix it:")
    logging.error(traceback.format_exc())

logging.info("Terminating")

