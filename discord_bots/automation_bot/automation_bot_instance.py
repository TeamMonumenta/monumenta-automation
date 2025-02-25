# -*- coding: utf-8 -*-

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pprint import pformat
from urllib.parse import urlparse

import discord
import git
import redis
import yaml
from discord.ext import commands

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# TODO: This is ugly and needs updating if we ever move this file
_file_depth = 3
_file = os.path.abspath(__file__)
_top_level = os.path.abspath(os.path.join(_file, '../'*_file_depth))

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../utility_code"))
from lib_py3.common import decode_escapes, int_to_ordinal
from lib_py3.lockout import LockoutAPI
from lib_py3.raffle import vote_raffle
from lib_py3.lib_k8s import KubernetesManager
from lib_py3.lib_sockets import SocketManager
from lib_py3.redis_scoreboard import RedisRBoard
from minecraft.world import World

import config
from automation_bot_lib import datestr, escape_triple_backtick, split_string

class Listening():
    """Class to keep track of whether a bot is listening to a user or not"""
    def __init__(self):
        self._set = set()

    def isListening(self, key):
        """Checks listening state"""
        logger.debug("Listening _set: %s", pformat(self._set))
        logger.debug("Listening key: %s", pformat(key))
        if not isinstance(key, tuple):
            key = (key.channel.id, key.author.id)
        return key not in self._set

    def select(self, key):
        """Listen on"""
        if not isinstance(key, tuple):
            key = (key.channel.id, key.author.id)
        self._set.remove(key)

    def deselect(self, key):
        """Listen off"""
        if not isinstance(key, tuple):
            key = (key.channel.id, key.author.id)
        self._set.add(key)

    def set(self, key, value):
        """Set listen state"""
        if value:
            self.select(key)
        else:
            self.deselect(key)

    def toggle(self, key):
        """Negate current listen state"""
        if not isinstance(key, tuple):
            key = (key.channel.id, key.author.id)
        if self.isListening(key):
            self.deselect(key)
        else:
            self.select(key)

class AutomationBotInstance(commands.Cog):
    """Instance of an automation bot per channel"""

    ################################################################################
    # Entry points

    def __init__(self, bot: commands.Bot, rreact: dict):
        self._bot = bot

        # For raffle reactions
        self._rreact = rreact

        self._always_listening_commands = [
            "list bots",
            "select",
        ]

        # All actions - these are reduced down by the actions configured for this bot
        self._commands = {
            "help": self.action_help,
            "list bots": self.action_list_bots,
            "select": self.action_select_bot,
            "batch": self.action_batch,
            "update avatar": self.action_update_avatar,

            "verbose": self.action_verbose,
            "test": self.action_test,
            "testpriv": self.action_test_priv,
            "testunpriv": self.action_test_unpriv,

            "lockout": self.action_lockout,
            "lockout check *": self.action_lockout_check_all,
            "lockout check": self.action_lockout_check,
            "lockout clear": self.action_lockout_clear,
            "lockout claim": self.action_lockout_claim,

            "list shards": self.action_list_shards,
            "instances": self.action_list_instances,
            "start": self.action_start,
            "stop": self.action_stop,
            "restart": self.action_restart,

            "view scores": self.action_view_scores,
            "get score": self.action_get_player_scores,
            "set score": self.action_set_player_scores,

            "player find": self.action_player_find,
            "player rollback": self.action_player_rollback,
            "player shard": self.action_player_shard,
            "player transfer": self.action_player_transfer,
            "player wipe": self.action_player_wipe,

            "update item": self.action_update_items,
            "run replacements": self.action_run_replacements,
            "find loot problems": self.action_find_loot_problems,
            "get commands": self.action_get_commands,
            "list world loot": self.action_list_world_loot,

            "generate instances": self.action_generate_instances,
            "prepare update bundle": self.action_prepare_update_bundle,
            "prepare stage bundle": self.action_prepare_stage_bundle,
            "apply stage bundle": self.action_apply_stage_bundle,
            "fetch update bundle": self.action_fetch_update_bundle,
            "stop at": self.action_stop_at_minute,
            "stop and backup": self.action_stop_and_backup,
            "weekly update": self.action_weekly_update,
            "get raffle seed": self.action_get_raffle_seed,
            "run test raffle": self.action_run_test_raffle,

            "stage": self.action_stage,
            "generate demo release": self.action_gen_demo_release,
            "broadcastcommand": self.action_dummy,
            "broadcastbungeecommand": self.action_dummy,
            "broadcastminecraftcommand": self.action_dummy,
            "broadcastproxycommand": self.action_dummy,

            "get timestamp": self.action_get_timestamp,
            "remind": self.action_remind,
            "remind me": self.action_remind,
        }
        self._all_commands = set(self._commands.keys())

        self._dungeons = {
            "labs": "D0Access",
            "white": "D1Access",
            "orange": "D2Access",
            "magenta": "D3Access",
            "lightblue": "D4Access",
            "yellow": "D5Access",
            "lime": "D6Access",
            "pink": "D7Access",
            "gray": "D8Access",
            "lightgray": "D9Access",
            "cyan": "D10Access",
            "purple": "D11Access",
            "blue": "D12Access",
            "brown": "D13Access",
            "willows": "DB1Access",
            "corridors": "DRAccess",
            "reverie": "DCAccess",
            "tutorial": "DTAccess",
            "shiftingcity": "DRL2Access",
            "teal": "DTLAccess",
            "forum": "DFFAccess",
            "rush": "DRDAccess",
            "depths": "DDAccess",
            "gallery": "DGAccess",
            "portal": "DPSAccess",
            "ruin": "DMASAccess",
            "hexfall": "DHFAccess",
            "skt": "DSKTAccess",
            "zenith": "DCZAccess",
        }

        self._status_messages = {
            "Shard Status": self._get_list_shards_str_status,
            "Server Time": self._time_summary,
            #"Public events": self._gameplay_event_summary, # TODO Bot cannot see these messages for reasons unknown
        }
        if config.K8S_NAMESPACE != "play":
            self._status_messages["Developer Lockouts"] = self._get_lockout_message

        self._gameplay_events = {}

        try:
            self._name = config.NAME
            self._shards = config.SHARDS
            self._server_dir = config.SERVER_DIR

            self._persistence_path = Path(f'/home/epic/4_SHARED/bot_persistence/{self._name}')
            self._persistence_path.mkdir(mode=0o775, parents=True, exist_ok=True)

            self._status_channel = None
            if config.STATUS_CHANNEL:
                try:
                    self._status_channel = self._bot.get_channel(config.STATUS_CHANNEL)
                    logging.info("Found audit channel: %s", config.STATUS_CHANNEL)
                except Exception:
                    logging.error("Cannot connect to audit channel: %s", config.STATUS_CHANNEL)

            self._socket = None
            if config.RABBITMQ:
                try:
                    conf = config.RABBITMQ

                    # Get the event loop on the main thread
                    loop = asyncio.get_event_loop()
                    seen_channel_ids = set()

                    def send_message_to_channel(message, channel):
                        # TODO: This is sort of cheating - channel isn't really a context, but it does have a .send()...
                        # Probably hard to fix though
                        logger.debug('Attempting to send %s to %s', message, channel.name)
                        asyncio.run_coroutine_threadsafe(self.display_verbatim(channel, message), loop)

                    def socket_callback(message):
                        message_channel = message.get("channel", None)
                        if not message_channel:
                            return

                        if message_channel not in seen_channel_ids:
                            seen_channel_ids.add(message_channel)
                            logger.warning('First occurance of channel %s: %s', repr(message_channel), message)

                        if message_channel == "monumentanetworkrelay.heartbeat":
                            return

                        #logger.info("Got socket message: %s", pformat(message))
                        if self._audit_channel:
                            if message_channel == "Monumenta.Automation.AuditLog":
                                # Schedule the display coroutine back on the main event loop
                                send_message_to_channel(message["data"]["message"], self._audit_channel)

                        if self._admin_channel:
                            if message_channel == "Monumenta.Automation.AdminNotification":
                                send_message_to_channel(message["data"]["message"], self._admin_channel)

                        if self._audit_severe_channel:
                            if message_channel == "Monumenta.Automation.AuditLogSevere":
                                send_message_to_channel(message["data"]["message"], self._audit_severe_channel)

                        if self._chat_mod_audit_channel:
                            if message_channel == "Monumenta.Automation.ChatModAuditLog":
                                send_message_to_channel(message["data"]["message"], self._chat_mod_audit_channel)

                        if self._death_audit_channel:
                            if message_channel == "Monumenta.Automation.DeathAuditLog":
                                send_message_to_channel(message["data"]["message"], self._death_audit_channel)

                        if self._player_audit_channel:
                            if message_channel == "Monumenta.Automation.PlayerAuditLog":
                                send_message_to_channel(message["data"]["message"], self._player_audit_channel)

                        if self._mail_audit_channel:
                            if message_channel == "Monumenta.Automation.MailAuditLog":
                                send_message_to_channel(message["data"]["message"], self._mail_audit_channel)

                        if self._market_audit_channel:
                            if message_channel == "Monumenta.Automation.MarketAuditLog":
                                send_message_to_channel(message["data"]["message"], self._market_audit_channel)

                        if self._report_audit_channel:
                            if message_channel == "Monumenta.Automation.ReportAuditLog":
                                send_message_to_channel(message["data"]["message"], self._report_audit_channel)

                        if self._stage_notify_channel:
                            if message_channel == "Monumenta.Automation.stage":
                                # Schedule the display coroutine back on the main event loop
                                # TODO: This is sort of cheating - channel isn't really a context, but it does have a .send()...
                                # Probably hard to fix though
                                asyncio.run_coroutine_threadsafe(self.stage_data_request(self._stage_notify_channel, message["data"]), loop)

                        if self._status_channel:
                            if message_channel == "monumenta.eventbroadcast.update":
                                logger.warning("Got Monumenta gameplay event message: %s", pformat(message))
                                event_data = message["data"]

                                event_shard = event_data.get("shard", None)
                                event_name = event_data.get("eventName", None)
                                event_time_left = event_data.get("timeLeft", None)

                                if not all(
                                        isinstance(event_shard, str),
                                        isinstance(event_name, str),
                                        isinstance(event_time_left, int),
                                ):
                                    return

                                event_map = self._gameplay_events.get(event_name, {})
                                self._gameplay_events[event_name] = event_map

                                if event_time_left < 0:
                                    del event_map[event_shard]
                                    if len(event_map) == 0:
                                        del self._gameplay_events[event_name]
                                    return

                                now = datetime.utcnow()
                                gameplay_event = event_map.get("event_shard", {
                                    "shard": event_shard,
                                    "event_name": event_name,
                                })
                                gameplay_event["last_update"] = now
                                if event_time_left > 0:
                                    gameplay_event["ETA"] = now + timedelta(seconds=event_time_left)
                                else:
                                    gameplay_event.pop("ETA", False)

                    log_level = config.RABBITMQ.get("log_level", 20)
                    self._socket = SocketManager(conf["host"], conf["name"], durable=conf["durable"], callback=(socket_callback if conf["process_messages"] else None), log_level=log_level)

                    # Add commands that require the sockets here!
                    self._commands["broadcastcommand"] = self.action_broadcastcommand
                    self._commands["broadcastbungeecommand"] = self.action_broadcastbungeecommand
                    self._commands["broadcastminecraftcommand"] = self.action_broadcastminecraftcommand
                    self._commands["broadcastproxycommand"] = self.action_broadcastproxycommand
                    self._all_commands = set(self._commands.keys())

                    self._audit_channel = None
                    if "audit_channel" in conf:
                        try:
                            self._audit_channel = self._bot.get_channel(conf["audit_channel"])
                            logging.info("Found audit channel: %s", conf["audit_channel"])
                        except Exception:
                            logging.error("Cannot connect to audit channel: %s", conf["audit_channel"])
                    self._audit_severe_channel = None
                    if "audit_severe_channel" in conf:
                        try:
                            self._audit_severe_channel = self._bot.get_channel(conf["audit_severe_channel"])
                            logging.info("Found audit severe channel: %s", conf["audit_severe_channel"])
                        except Exception:
                            logging.error("Cannot connect to audit severe channel: %s", conf["audit_severe_channel"])
                    self._chat_mod_audit_channel = None
                    if "chat_mod_audit_channel" in conf:
                        try:
                            self._chat_mod_audit_channel = self._bot.get_channel(conf["chat_mod_audit_channel"])
                            logging.info("Found mail audit channel: %s", conf["chat_mod_audit_channel"])
                        except Exception:
                            logging.error("Cannot connect to mail audit channel: %s", conf["chat_mod_audit_channel"])
                    self._death_audit_channel = None
                    if "death_audit_channel" in conf:
                        try:
                            self._death_audit_channel = self._bot.get_channel(conf["death_audit_channel"])
                            logging.info("Found death audit channel: %s", conf["death_audit_channel"])
                        except Exception:
                            logging.error("Cannot connect to death audit channel: %s", conf["death_audit_channel"])
                    self._player_audit_channel = None
                    if "player_audit_channel" in conf:
                        try:
                            self._player_audit_channel = self._bot.get_channel(conf["player_audit_channel"])
                            logging.info("Found player audit channel: %s", conf["player_audit_channel"])
                        except Exception:
                            logging.error("Cannot connect to player audit channel: %s", conf["player_audit_channel"])
                    self._mail_audit_channel = None
                    if "mail_audit_channel" in conf:
                        try:
                            self._mail_audit_channel = self._bot.get_channel(conf["mail_audit_channel"])
                            logging.info("Found mail audit channel: %s", conf["mail_audit_channel"])
                        except Exception:
                            logging.error("Cannot connect to mail audit channel: %s", conf["mail_audit_channel"])
                    self._market_audit_channel = None
                    if "market_audit_channel" in conf:
                        try:
                            self._market_audit_channel = self._bot.get_channel(conf["market_audit_channel"])
                            logging.info("Found market audit channel: %s", conf["market_audit_channel"])
                        except Exception:
                            logging.error("Cannot connect to market audit channel: %s", conf["market_audit_channel"])
                    self._report_audit_channel = None
                    if "report_audit_channel" in conf:
                        try:
                            self._report_audit_channel = self._bot.get_channel(conf["report_audit_channel"])
                            logging.info("Found report audit channel: %s", conf["report_audit_channel"])
                        except Exception:
                            logging.error("Cannot connect to report audit channel: %s", conf["report_audit_channel"])
                    self._admin_channel = None
                    if "admin_channel" in conf:
                        try:
                            self._admin_channel = self._bot.get_channel(conf["admin_channel"])
                            logging.info("Found admin channel: %s", conf["admin_channel"])
                        except Exception:
                            logging.error("Cannot connect to admin channel: %s", conf["admin_channel"])

                    self._stage_notify_channel = None
                    if "stage_notify_channel" in conf:
                        try:
                            self._stage_notify_channel = self._bot.get_channel(conf["stage_notify_channel"])
                            logging.info("Found stage notify channel: %s", conf["stage_notify_channel"])
                        except Exception:
                            logging.error("Cannot connect to stage notify channel channel: %s", conf["stage_notify_channel"])
                except Exception as e:
                    logger.warning('Failed to connect to rabbitmq: %s', e)

            # Remove any commands that aren't available in the config
            for command in set(self._commands.keys()):
                if command not in config.COMMANDS:
                    self._commands.pop(command)

            for command in config.COMMANDS:
                if command not in self._commands:
                    logger.warning("Command %s specified in config but does not exist", command)

            self._permissions = config.PERMISSIONS
            self._debug = False
            self._listening = Listening()
            self._k8s = KubernetesManager(config.K8S_NAMESPACE)
        except KeyError as e:
            sys.exit(f'Config missing key: {e}')

    async def handle_message(self, ctx: discord.ext.commands.Context, message):
        """Called by parent bot on receiving a message"""

        msg = message.content

        if not msg.strip().startswith(config.PREFIX):
            return

        match = None
        for command in self._all_commands:
            if msg[1:].startswith(command):
                if match is None or len(match) < len(command):
                    match = command
        if match is None:
            return

        if match not in self._always_listening_commands and not self._listening.isListening(message):
            return

        if match not in self._commands:
            return

        if self.check_permissions(match, message.author):
            await self._commands[match](ctx, match, message)
        else:
            await ctx.send("Sorry " + message.author.mention + ", you do not have permission to run this command")

    async def load_raffle_reaction(self):
        """Loads persistent raffle reaction ID"""
        self.clear_raffle_reaction(save=False)

        raffle_path = self._persistence_path / 'raffle.json'
        if not raffle_path.is_file():
            return

        raffle_data = json.loads(raffle_path.read_text(encoding='utf-8-sig'))
        reaction_data = raffle_data.get("reaction", {})

        channel_id = reaction_data.get("channel_id", None)

        if channel_id is None:
            return
        try:
            channel = self._bot.get_channel(channel_id)
        except Exception:
            return

        message_id = reaction_data.get("message_id", None)
        if message_id is None:
            return
        try:
            msg = await channel.fetch_message(message_id)
        except discord.errors.NotFound:
            return

        await self.update_raffle_reaction(channel, msg, save=False)

    def clear_raffle_reaction(self, save=True):
        """Clears the currently set raffle message"""
        self._rreact.update({
            "timestamp": datetime.now(),
            "channel_id": None,
            "message_id": None,
            "msg_contents": None,
            "count": 0,
            "msg": None,
        })
        if save:
            self.save_raffle_reaction()

    async def update_raffle_reaction(self, channel, msg, save=True):
        """Attempt to update the current raffle message"""
        if msg.id == self._rreact.get("message_id", None):
            return

        msg_contents = re.sub("''*", "'", msg.clean_content).replace('\\', '')
        if len(msg_contents) < 1:
            return

        # Conditionally timezone aware cutoff time
        if msg.created_at.tzinfo is None:
            time_cutoff = datetime.utcnow() - datetime.timedelta(days=7)
        else:
            time_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        self._bot.rlogger.debug("time_cutoff=%s      msg.created_at=%s", time_cutoff, msg.created_at)

        if msg.created_at <= time_cutoff:
            return
        self._bot.rlogger.debug("Reaction was new enough")

        highest_reaction_count = 0
        self._bot.rlogger.debug("Reactions: %s", msg.reactions)
        for reaction in msg.reactions:
            reaction_name = reaction.emoji
            if isinstance(reaction_name, (discord.Emoji, discord.PartialEmoji)):
                reaction_name = reaction_name.name

            if '\U0001f441' in reaction_name:
                continue

            highest_reaction_count = max(highest_reaction_count, reaction.count)

        if not (
                highest_reaction_count > self._rreact["count"]
                or time_cutoff > self._rreact["timestamp"]
        ):
            return

        # If the bot can't react to a message due to permission issues, don't mark it as the winning message
        try:
            await msg.add_reaction('\U0001f441')
        except Exception:
            self._bot.rlogger.warning("Permission denied adding reaction in channel %s", channel.name)
            return

        if self._rreact["msg"] is not None:
            try:
                await self._rreact["msg"].remove_reaction('\U0001f441', self._bot.user)
            except Exception:
                self._bot.rlogger.warning("Failed to remove previous reaction in %s", channel.name)
                self._bot.rlogger.warning(traceback.format_exc())

        self._rreact.update({
            "timestamp": msg.created_at,
            "channel_id": channel.id,
            "message_id": msg.id,
            "msg_contents": msg_contents,
            "count": highest_reaction_count,
            "msg": msg,
        })
        if save:
            self.save_raffle_reaction()

    def save_raffle_reaction(self):
        """Saves the raffle message to persistent storage"""
        raffle_path = self._persistence_path / 'raffle.json'

        raffle_data = {
            "reaction": {
                "channel_id": self._rreact.get("channel_id", None),
                "message_id": self._rreact.get("message_id", None),
            },
        }

        with open(raffle_path, 'w', encoding='utf-8') as fp:
            print(
                json.dumps(
                    raffle_data,
                    ensure_ascii=False,
                    indent=2,
                    separators=(',', ': ')
                ),
                file=fp
            )

    async def status_tick(self):
        """Updates bot status message(s) if required and possible"""

        if self._status_channel is None:
            return

        status_path = self._persistence_path / 'status.json'
        status_data = {
            "messages": {}
        }
        if status_path.is_file():
            status_data = json.loads(status_path.read_text(encoding='utf-8-sig'))
        messages = status_data["messages"]

        for header, callback in self._status_messages.items():
            try:
                new_message = await callback()
            except Exception as ex:
                new_message = f'```\n{ex}\n{traceback.format_exc()}\n```'

            previous_status = messages.get(header, None)
            message_id = None
            previous_timestamp = 0
            previous_message = None
            if previous_status is not None:
                message_id = previous_status["message_id"]
                previous_timestamp = previous_status.get("modify_time", 0)
                previous_message = previous_status["message_data"]

            now = datetime.utcnow()
            now_timestamp = now.timestamp()
            always_update_seconds = 15 * 60
            if (
                    new_message == previous_message
                    and now_timestamp // always_update_seconds == previous_timestamp // always_update_seconds
            ):
                continue

            msg = None
            if message_id is not None:
                try:
                    msg = await self._status_channel.fetch_message(message_id)
                except discord.errors.NotFound:
                    msg = None

            modify_time = "Last updated " + self.get_discord_timestamp(now, ":R")
            formatted_message = f'**{header}** {modify_time}\n{new_message}'
            if msg is None:
                msg = await self._status_channel.send(formatted_message)
                message_id = msg.id
            else:
                await msg.edit(content=formatted_message)

            messages[header] = {
                "message_id": message_id,
                "modify_time": now_timestamp,
                "message_data": new_message,
            }

        with open(status_path, 'w', encoding='utf-8') as fp:
            print(
                json.dumps(
                    status_data,
                    ensure_ascii=False,
                    indent=2,
                    separators=(',', ': ')
                ),
                file=fp
            )

    # Entry points
    ################################################################################

    ################################################################################
    # Infrastructure

    def check_permissions(self, command: str, author):
        """Checks that an author has permission to run a command"""
        logger.debug("author.id = %s", author.id)
        user_info = self._permissions["users"].get(author.id, {"rights":["@everyone"]})
        logger.debug("User info = %s", pformat(user_info))
        # This is a copy, not a reference
        user_rights = list(user_info.get("rights", ["@everyone"]))
        for role in author.roles:
            permGroupName = self._permissions["groups_by_role"].get(role.id, None)
            if permGroupName is not None:
                user_rights = [permGroupName] + user_rights

        return self.check_permissions_explicitly(command, user_rights)

    def check_permissions_explicitly(self, command: str, user_rights):
        """
        Unlike check_permissions, this does not get assigned to an object.
        It checks exactly that the user_rights provided can run the command.
        """
        result = False
        already_checked = set()
        while len(user_rights) > 0:
            perm = user_rights.pop(0)
            if perm[0] == "@":
                # Permission group
                if perm not in already_checked:
                    already_checked.add(perm)
                    user_rights = self._permissions["groups"][perm] + user_rights
                continue
            givenPerm = (perm[0] == "+")
            if (perm[1:] == command or perm[1:] == "*"):
                result = givenPerm

        return result

    async def display_verbatim(self, ctx: discord.ext.commands.Context, text: str):
        """Respond with verbatim text split into chunks that fit the message size"""
        for chunk in split_string(escape_triple_backtick(text)):
            await ctx.send("```\n" + chunk + "\n```")

    async def debug(self, ctx: discord.ext.commands.Context, text: str):
        """Log debug text to the console, and if verbose mode is on, respond with it also"""
        logger.debug(text)
        if self._debug:
            for chunk in split_string(text):
                await ctx.send(chunk)

    async def cd(self, ctx: discord.ext.commands.Context, path: str):
        """Changes the bot's current working directory. This affects all commands!"""
        await self.debug(ctx, "Changing path to `" + path + "`")
        os.chdir(path)

    async def display(self, ctx: discord.ext.commands.Context, msg: str):
        """Respond with text split into chunks that fit the message size"""
        for chunk in split_string(msg):
            await ctx.send(chunk)

    async def run(self, ctx: discord.ext.commands.Context, cmd, ret=0, displayOutput=False, suppressStdErr=False):
        """Run a shell command"""
        if not isinstance(cmd, list):
            # For simple stuff, splitting on spaces is enough
            splitCmd = cmd.split(' ')
        else:
            # For complicated stuff, the caller must split appropriately
            splitCmd = cmd
        await self.debug(ctx, "Executing: ```\n" + escape_triple_backtick(str(splitCmd)) + "\n```")
        process = await asyncio.create_subprocess_exec(*splitCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        rc = process.returncode

        await self.debug(ctx, f"Result: {rc}")

        stdout = stdout.decode('utf-8')
        if stdout:
            await self.debug(ctx, f"stdout from command {cmd}:")
            logger.debug(stdout)

            if self._debug or displayOutput:
                await self.display_verbatim(ctx, stdout)

        stderr = stderr.decode('utf-8')
        if stderr and not suppressStdErr:
            await ctx.send(f"stderr from command {cmd}:")
            await self.display_verbatim(ctx, stderr)

        if isinstance(ret, int) and rc != ret:
            raise ValueError(f"Expected result {ret}, got result {rc} while processing {cmd!r}")

        if isinstance(ret, (list, tuple, set)) and rc not in ret:
            raise ValueError(f"Expected result in {ret}, got result {rc} while processing {cmd!r}")

        return stdout

    async def stop(self, ctx: discord.ext.commands.Context, shards, wait=True, owner=None):
        """Stop shards"""
        if not isinstance(shards, list):
            shards = [shards,]

        lockout_owner = owner if owner is not None else self._name
        for shard in shards:
            opt_lockout = await self.check_lockout(ctx, lockout_owner, shard)
            if opt_lockout:
                raise opt_lockout.as_discord_exception()

        async with ctx.typing():
            await self.debug(ctx, f"Stopping shards [{','.join(shards)}]...")
            await self._k8s.stop(shards, wait=wait)
            await self.debug(ctx, f"Stopped shards [{','.join(shards)}]")

    async def start(self, ctx: discord.ext.commands.Context, shards, wait=True, owner=None):
        """Start shards"""
        if not isinstance(shards, list):
            shards = [shards,]

        lockout_owner = owner if owner is not None else self._name
        for shard in shards:
            opt_lockout = await self.check_lockout(ctx, lockout_owner, shard)
            if opt_lockout:
                raise opt_lockout.as_discord_exception()

        async with ctx.typing():
            await self.debug(ctx, f"Starting shards [{','.join(shards)}]...")
            await self._k8s.start(shards, wait=wait)
            await self.debug(ctx, f"Started shards [{','.join(shards)}]")

    async def restart(self, ctx: discord.ext.commands.Context, shards, wait=True, owner=None):
        """Restart shards"""
        if not isinstance(shards, list):
            shards = [shards,]

        lockout_owner = owner if owner is not None else self._name
        for shard in shards:
            opt_lockout = await self.check_lockout(ctx, lockout_owner, shard)
            if opt_lockout:
                raise opt_lockout.as_discord_exception()

        async with ctx.typing():
            await self.debug(ctx, f"Restarting shards [{','.join(shards)}]...")
            await self._k8s.restart(shards, wait=wait)
            await self.debug(ctx, f"Restarted shards [{','.join(shards)}]")

    def get_raffle_seed(self):
        '''Returns a raffle seed'''

        tz = timezone.utc
        now = datetime.now(tz)
        raffle_seed = "Default raffle seed for " + now.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        if self._rreact["msg_contents"] is not None:
            raffle_seed = self._rreact["msg_contents"]

        return raffle_seed

    async def _gameplay_event_summary(self):
        msg = []

        now = datetime.utcnow()
        expired_threshhold = now - timedelta(minutes=3)

        # Sorting also makes a copy of the collection, allowing entries to be removed
        for event_name, event_map in sorted(self._gameplay_events.items()):
            for shard, gameplay_event in sorted(event_map.items()):
                if gameplay_event["last_update"] < expired_threshhold:
                    event_map.pop(shard, None)
                    continue

                eta = gameplay_event.get("ETA", None)
                if eta:
                    eta_timestamp = self.get_discord_timestamp(eta, ":R")
                    msg.append(f'{event_name} is starting on {shard} {eta_timestamp}')
                else:
                    msg.append(f'{event_name} is in progress on {shard}')

        if not msg:
            msg.append("No events are currently in progress")

        return "\n".join(msg)

    async def _get_lockout_message(self):
        msg = []

        lockout_api = LockoutAPI(config.K8S_NAMESPACE)
        lockouts = await lockout_api.check_all()
        for _, lockout in sorted(lockouts.items()):
            msg.append(f'🔒 {lockout.discord_str()}')

        if not msg:
            msg.append('🔓 No lockouts are currently active')

        return "\n".join(msg)

    # Infrastructure
    ################################################################################

    ################################################################################
    # Always listening actions

    async def action_dummy(self, ctx: discord.ext.commands.Context, _, message: discord.Message):
        '''Placeholder command; the real command did not load correctly.'''

        await self.display(ctx, "This command didn't load correctly!")
        await self.display(ctx, message.author.mention)

    async def action_help(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Lists commands available with this bot'''

        commandArgs = message.content[len(config.PREFIX + cmd) + 1:].split()
        await self.help_internal(ctx, commandArgs, message.author)

    async def help_internal(self, ctx: discord.ext.commands.Context, commandArgs, author):
        '''Provides help for a specific command'''
        # any -v style arguments should go here
        target_command = " ".join(commandArgs)
        if len(commandArgs) == 0:
            helptext = '''__Available Actions__'''
            for command in self._commands:
                if self.check_permissions(command, author):
                    helptext += "\n**" + config.PREFIX + command + "**"
                else:
                    helptext += "\n~~" + config.PREFIX + command + "~~"
            helptext += f"\nRun `{config.PREFIX}help <command>` for more info."
        else:
            helptext = None
            for command in self._commands:
                if target_command not in [command, config.PREFIX + command]:
                    continue

                helptext = '''__Help on:__'''
                if self.check_permissions(command, author):
                    helptext += "\n**" + config.PREFIX + command + "**"
                else:
                    helptext += "\n~~" + config.PREFIX + command + "~~"
                command_help = (
                    self
                    ._commands[command]
                    .__doc__
                    .replace('{cmdPrefix}', config.PREFIX)
                )
                helptext += (
                    "```\n"
                    + escape_triple_backtick(command_help)
                    + "\n```"
                )

            if helptext is None:
                helptext = '''Command {!r} does not exist!'''.format(target_command)

        await ctx.send(helptext)

    async def action_list_bots(self, ctx: discord.ext.commands.Context, _, __: discord.Message):
        '''Lists currently running bots'''
        await ctx.send('`' + self._name + '`')

    async def action_select_bot(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Make specified bots start listening for commands; unlisted bots stop listening.

Syntax:
`{cmdPrefix}select [botName] [botName2] ...`
Examples:
`{cmdPrefix}select` - deselect all bots
`{cmdPrefix}select build` - select only the build bot
`{cmdPrefix}select play play2` - select both the play bots
`{cmdPrefix}select *` - select all bots'''

        commandArgs = message.content[len(config.PREFIX + cmd) + 1:].split()

        if ('*' in commandArgs or self._name in commandArgs) ^ self._listening.isListening(message):
            self._listening.toggle(message)
            if self._listening.isListening(message):
                await self.display(ctx, self._name + " is now listening for commands.")
            else:
                await self.display(ctx, self._name + " is no longer listening for commands.")
        elif self._listening.isListening(message):
            await self.display(ctx, self._name + " is still listening for commands.")

    # Always listening actions
    ################################################################################

    async def action_batch(self, ctx: discord.ext.commands.Context, _, message: discord.Message):
        '''Run multiple commands at once'''
        orig_content = message.content
        commands = message.content.split("\n")
        for command in commands:
            if command.startswith("batch"):
                command = command[5:]
            elif command.startswith(f"{config.PREFIX}batch"):
                command = command[6:]

            if not command:
                continue
            command = command.strip()
            if not command.startswith(config.PREFIX):
                command = config.PREFIX + command
            message.content = command
            await self.handle_message(ctx, message)
        message.content = orig_content

    async def action_verbose(self, ctx: discord.ext.commands.Context, _, __: discord.Message):
        '''Toggle verbosity of discord messages'''

        self._debug = not self._debug

        await ctx.send("Verbose messages setting: {}".format(self._debug))

    async def action_test(self, ctx: discord.ext.commands.Context, _, __: discord.Message):
        '''Simple test action that does nothing'''

        await ctx.send("Testing successful!")

    async def action_test_priv(self, ctx: discord.ext.commands.Context, _, __: discord.Message):
        '''Test if user has permission to use restricted commands'''

        await ctx.send("You've got the power")

    async def action_test_unpriv(self, ctx: discord.ext.commands.Context, _, __: discord.Message):
        '''Test that a restricted command fails for all users'''

        await ctx.send("BUG: You definitely shouldn't have this much power")


    async def action_list_shards(self, ctx: discord.ext.commands.Context, _, inputMsg: discord.Message):
        '''Lists currently running shards on this server'''
        msg = None
        split_input_message = inputMsg.content.split(" ")

        if len(split_input_message) > 2 and split_input_message[2] == "summary":
            msg = await self._get_list_shards_str_summary()
        else:
            msg = await self._get_list_shards_str_long()

        await self.display(ctx, msg)

    async def _list_shards_states_internal(self):
        """Common check for a shard's state for use in the summaries

        Format is
        {
            "valley-2": {
                "status": "starting",
                "reaction": ":arrow_up:",
                "reaction_order": 1,
                "last_change": <integer unix timestamp in seconds>,
            }
        }
        """
        tz = timezone.utc
        shard_states_path = self._persistence_path / 'shard_states'
        shard_states_path.mkdir(mode=0o775, parents=True, exist_ok=True)

        previous_states = {}
        for shard_state_path in shard_states_path.iterdir():
            name = shard_state_path.name
            if not (shard_state_path.is_file() and name.endswith('.json')):
                continue
            name = name[:-5] # Remove .json
            previous_shard_state = None
            try:
                previous_shard_state = json.loads(shard_state_path.read_text(encoding='utf-8-sig'))
            except Exception:
                continue
            previous_states[name] = previous_shard_state

        current_states = {}
        shards = await self._k8s.list()
        for name, state in shards.items():
            prev_status = previous_states.get(name, {}).get('status', None)
            status = 'error'
            reaction = ':exclamation:'
            reaction_order = 99
            if state["replicas"] == 1 and state["available_replicas"] == 1:
                status = 'started'
                reaction = ':white_check_mark:'
                reaction_order = 0
            elif state["replicas"] == 1 and state["available_replicas"] == 0:
                status = 'starting'
                reaction = ':arrow_up:'
                reaction_order = 1
            elif state["replicas"] == 0 and "pod_name" in state:
                status = 'stopping'
                reaction = ':arrow_down:'
                reaction_order = 2
            elif state["replicas"] == 0 and "pod_name" not in state:
                status = 'stopped'
                reaction = ':x:'
                reaction_order = 3

            if status == prev_status:
                current_states[name] = previous_states[name]
            else:
                current_state = {
                    "status": status,
                    "reaction": reaction,
                    "reaction_order": reaction_order,
                    "last_change": int(datetime.now(tz).timestamp()),
                }
                current_states[name] = current_state
                shard_state_path = shard_states_path / f'{name}.json'
                with open(shard_state_path, 'w', encoding='utf-8') as fp:
                    print(
                        json.dumps(
                            current_state,
                            ensure_ascii=False,
                            indent=2,
                            separators=(',', ': ')
                        ),
                        file=fp
                    )

        return current_states

    async def _get_list_shards_str_status(self):
        """Get a status message formatted string"""
        shards = await self._list_shards_states_internal()

        buckets = {}
        for name, state in shards.items():
            reaction = state['reaction']
            reaction_order = state['reaction_order']
            last_change = state['last_change']
            last_change_formatted = self.get_discord_timestamp(last_change, ':R')

            if reaction_order not in buckets:
                buckets[reaction_order] = {
                    "reaction": reaction,
                    "shards": {},
                }
            bucket_shards = buckets[reaction_order]["shards"]
            if last_change not in bucket_shards:
                bucket_shards[last_change] = []
            bucket_shards[last_change].append(f'{name} ({last_change_formatted})')

        msg = []
        if len(shards) <= 0:
            msg.append("No shards to list")
        for _, bucket in sorted(buckets.items()):
            shards = []
            for _, shards_at_timestamp in sorted(bucket["shards"].items()):
                shards += shards_at_timestamp
            msg.append(f'{bucket["reaction"]}: ' + ', '.join(shards))

        return "\n".join(msg)

    async def _get_list_shards_str_summary(self):
        """Get a `~list shard summary` formatted string"""
        shards = await self._list_shards_states_internal()

        buckets = {}
        for name, state in shards.items():
            reaction = state['reaction']
            reaction_order = state['reaction_order']

            if reaction_order not in buckets:
                buckets[reaction_order] = {
                    "reaction": reaction,
                    "shards": [],
                }
            buckets[reaction_order]["shards"].append(name)

        msg = []
        if len(shards) <= 0:
            msg.append("No shards to list")
        for _, bucket in sorted(buckets.items()):
            msg.append(f'{bucket["reaction"]}: ' + ', '.join(bucket["shards"]))

        return "\n".join(msg)

    async def _get_list_shards_str_long(self):
        """Get a `~list shard` formatted string"""
        shards = await self._list_shards_states_internal()

        msg = []

        for name, state in shards.items():
            msg.append(f'{state["reaction"]} {name} since {self.get_discord_timestamp(state["last_change"], ":R")}')
        if not msg:
            msg.append("No shards to list")

        return "\n".join(msg)

    async def get_utc_offset(self):
        utc_offset_path = self._persistence_path / 'utc_offset.json'
        config = {
            "hours": -17
        }
        if utc_offset_path.is_file():
            config = json.loads(utc_offset_path.read_text(encoding='utf-8-sig'))
        try:
            return timedelta(**config)
        except Exception:
            return timedelta(hours=-17)

    async def _time_summary(self):
        """Display common time information"""
        utc_offset = await self.get_utc_offset()
        tz = timezone(utc_offset)
        monumenta_timezone = int(utc_offset / timedelta(hours=1))
        now = datetime.now(tz)
        now_skip_seconds = datetime(now.year, now.month, now.day, now.hour, now.minute, tzinfo=tz)
        today_start = datetime(now.year, now.month, now.day, 0, 0, tzinfo=tz)
        day_of_week_0_indexed = (today_start.weekday() + 3) % 7

        tomorrow_start = today_start + timedelta(days=1)
        new_week = today_start + timedelta(days=7 - day_of_week_0_indexed)

        today_format = now_skip_seconds.strftime(f'%-I:%M %p on %A the {int_to_ordinal(now_skip_seconds.day)} of %B, %Y')

        msg = []
        msg.append(f"Monumenta's local time (UTC{monumenta_timezone:+d})")
        msg.append("The following information is used for daily and weekly events, such as delve bounties, dungeon access, and the season pass. Note that this is not the same as weekly updates, which we use to release new content into the game and provide a fresh copy of the overworlds.")
        msg.append(f'It is currently `{today_format}`')
        msg.append(f'A new day begins {self.get_discord_timestamp(tomorrow_start, ":R")}')
        msg.append(f'A new week begins {self.get_discord_timestamp(new_week, ":R")} (every Friday)')
        return "\n".join(msg)

    async def action_list_instances(self, ctx: discord.ext.commands.Context, _, __: discord.Message):
        """List player dungeon instances"""
        rboard = RedisRBoard("play", redis_host="redis")
        inst_str = '```\n'
        inst_str += f"{'Dungeons' : <15}{'Used' : <15}"
        inst_str += "\n"
        for dungeon in self._dungeons:
            used = rboard.get("$Last", self._dungeons[dungeon])
            if used is not None:
                inst_str += f"{dungeon : <15}{used : <15}"
                inst_str += "\n"
            else:
                await self.display(ctx, f"Warning: Failed to load rboard values for {dungeon}")
        inst_str += "\n```"
        await self.display(ctx, inst_str)

    async def check_lockout(self, ctx: discord.ext.commands.Context, owner, shard):
        """Checks for a lockout on a shard

        owner may be a string for the owner ID, or a message whose author will be checked

        If found for another user, returns the lockout
        Otherwise, returns None
        """
        lockout_api = LockoutAPI(config.K8S_NAMESPACE)
        lockout = await lockout_api.check(shard)

        if lockout is None:
            return None

        if isinstance(owner, str):
            if owner == lockout.owner:
                return None
        else:
            if owner and owner.author.name == lockout.owner:
                return None

        await self.display(ctx, f'🔒 {lockout.discord_str()}')
        return lockout

    # pylint: disable=comparison-with-callable
    async def _start_stop_restart_common(self, ctx: discord.ext.commands.Context, cmd, message, action):
        arg_str = message.content[len(config.PREFIX + cmd)+1:].strip()
        if arg_str.startswith("shard "):
            arg_str = arg_str[len("shard "):].strip()
        commandArgs = arg_str.split()

        # Kills the bot, causing k8s to restart it
        if arg_str == 'bot' and action in (self.stop, self.restart):
            if await self.check_lockout(ctx, message, self._name):
                return
            await ctx.send("Restarting bot. Note: This will not update the bot's image")
            sys.exit(0)

        shards_changed = []
        if '*' in commandArgs:
            for shard in self._shards:
                shards_changed.append(shard)
        else:
            for shard in self._shards:
                if shard in commandArgs:
                    shards_changed.append(shard)

        if not shards_changed:
            await self.display(ctx, "No specified shards on this server.")
        else:
            if action == self.stop:
                await self.display(ctx, "Stopping shards [{}]...".format(",".join(shards_changed)))
            elif action == self.start:
                await self.display(ctx, "Starting shards [{}]...".format(",".join(shards_changed)))
            elif action == self.restart:
                await self.display(ctx, "Restarting shards [{}]...".format(",".join(shards_changed)))

            await action(ctx, shards_changed, owner=message)

            if action == self.stop:
                await self.display(ctx, "Stopped shards [{}]".format(",".join(shards_changed)))
            elif action == self.start:
                await self.display(ctx, "Started shards [{}]".format(",".join(shards_changed)))
            elif action == self.restart:
                await self.display(ctx, "Restarted shards [{}]".format(",".join(shards_changed)))

            await self.display(ctx, message.author.mention)

    async def action_lockout(self, ctx: discord.ext.commands.Context, _, message: discord.Message):
        """Provides help for lockout subcommands"""
        await self.help_internal(ctx, ["lockout check *"], message.author)
        await self.help_internal(ctx, ["lockout check"], message.author)
        await self.help_internal(ctx, ["lockout clear"], message.author)
        await self.help_internal(ctx, ["lockout claim"], message.author)

    async def action_lockout_check_all(self, ctx: discord.ext.commands.Context, _, message: discord.Message, prefix=()):
        """List all active shard lockouts

Syntax:
`{cmdPrefix}lockout check *`
"""

        yours = []
        others = []

        lockout_api = LockoutAPI(config.K8S_NAMESPACE)
        lockouts = await lockout_api.check_all()
        owner = message.author.name

        for _, lockout in sorted(lockouts.items()):
            line = f'🔒 {lockout.discord_str()}'

            if owner == lockout.owner:
                yours.append(line)
            else:
                others.append(line)

        if yours:
            yours.insert(0, 'Your active lockouts:')
        else:
            yours.append('🔓 You have no active lockouts')

        if others:
            others.insert(0, 'Other active lockouts:')
        else:
            others.append('🔓 There are no other active lockouts')

        msg = list(prefix) + yours + [''] + others
        await self.display(ctx, '\n'.join(msg))

    async def action_lockout_check(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        """Check shards for active lockouts

Syntax:
`{cmdPrefix}lockout check bungee valley isles orange'''
"""

        shards = message.content[len(config.PREFIX + cmd) + 1:].split()
        if not shards:
            await self.action_lockout_check_all(ctx, cmd, message)
            return

        yours = []
        others = []
        unlocked = []

        lockout_api = LockoutAPI(config.K8S_NAMESPACE)
        owner = message.author.name

        for shard in shards:
            lockout = await lockout_api.check(shard)

            if lockout is None:
                unlocked.append(f'🔓 {shard} has no active lockout')
                continue

            line = f'🔒 {lockout.discord_str()}'
            if owner == lockout.owner:
                yours.append(line)
            else:
                others.append(line)

        if yours:
            yours.insert(0, 'Your active lockouts:')
        else:
            yours.append('🔓 You have no active lockouts')

        if others:
            others.insert(0, 'Other active lockouts:')
        else:
            others.append('🔓 There are no other active lockouts')

        msg = []
        if unlocked:
            msg.append('\n'.join(unlocked))
        msg.append('\n'.join(yours))
        msg.append('\n'.join(others))

        await self.display(ctx, '\n\n'.join(msg))

    async def action_lockout_clear(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        """Clears lockouts on shards

Syntax:
`{cmdPrefix}lockout clear my valley isles`
`{cmdPrefix}lockout clear my *`
`{cmdPrefix}lockout clear * valley isles`
`{cmdPrefix}lockout clear * *`
"""

        args = message.content[len(config.PREFIX + cmd) + 1:].split()
        if len(args) < 2:
            await self.help_internal(ctx, ["lockout clear"], message.author)
            return

        who, *shards = args

        lockout_api = LockoutAPI(config.K8S_NAMESPACE)
        owner = message.author.name if who in ('me', 'my') else who
        for shard in shards:
            await lockout_api.clear(shard, owner)

        await self.action_lockout_check_all(ctx, cmd, message, prefix=['Remaining lockouts:', ''])

    async def action_lockout_claim(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        """Claim a lockout on a shard

Syntax:
`{cmdPrefix}lockout claim <shard> <minutes> <reason>`
`{cmdPrefix}lockout claim dev3 15 secret mob ability test`
`{cmdPrefix}lockout claim * 240 weekly update test`
`{cmdPrefix}lockout claim * 10080 beta testing all week`
"""

        args = message.content[len(config.PREFIX + cmd) + 1:].split()
        if len(args) < 3:
            await self.help_internal(ctx, ["lockout claim"], message.author)
            return

        shard, minutes, *reason = args
        reason = ' '.join(reason)

        lockout_api = LockoutAPI(config.K8S_NAMESPACE)
        owner = message.author.name
        lockout = await lockout_api.claim(shard, owner, minutes, reason)

        if lockout is None:
            await self.display(ctx, f'Failed to claim lockout; is Redis down?\n{message.author.mention}')
            return

        if lockout.owner != owner:
            await self.display(ctx, f'Failed to claim lockout due to existing claim\n{lockout.discord_str()}\n{message.author.mention}')
            return

        await self.display(ctx, f'Lockout claim successful:\n{lockout.discord_str()}')

    async def action_start(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Start specified shards.
Syntax:
`{cmdPrefix}start shard *`
`{cmdPrefix}start shard valley isles orange'''
        await self._start_stop_restart_common(ctx, cmd, message, self.start)

    async def action_stop(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Stop specified shards.
Syntax:
`{cmdPrefix}stop shard *`
`{cmdPrefix}stop shard valley isles orange'''
        await self._start_stop_restart_common(ctx, cmd, message, self.stop)

    async def action_restart(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Restart specified shards.
Syntax:
`{cmdPrefix}restart shard *`
`{cmdPrefix}restart shard valley isles orange'''
        await self._start_stop_restart_common(ctx, cmd, message, self.restart)


    async def action_view_scores(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''View player scores game-wide, not tied to a specific shard. Run without arguements for syntax.
Note: the values from this command could be at most 5 minutes behind the play server if the player is online.
Do not use for debugging quests or other scores that are likely to change often.'''

        commandArgs = message.content[len(config.PREFIX + cmd) + 1:].split()

        cmd_str = os.path.join(_top_level, "utility_code/view_scores.py")
        while len(commandArgs) > 0:
            cmd_str = cmd_str + " " + commandArgs.pop(0)

        await self.run(ctx, cmd_str, displayOutput=True)
        await self.display(ctx, "Done")


    async def action_get_player_scores(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        """Get score for a player

Note: the values from this command could be at most 5 minutes behind the play server if the player is online.
Do not use for debugging quests or other scores that are likely to change often."""

        commandArgs = message.content[len(config.PREFIX + cmd) + 1:].split()

        cmd_str = os.path.join(_top_level, "utility_code/get_score.py")
        cmd_str = " ".join([cmd_str] + list(commandArgs))

        await self.run(ctx, cmd_str, displayOutput=True, ret=(0, 2))
        await self.display(ctx, "Done")


    async def action_set_player_scores(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Set score for a player. This will work for offline and online players (scores are set in both redis and by broadcastcommand)
        '''

        commandArgs = message.content[len(config.PREFIX + cmd) + 1:]
        lines = commandArgs.split("\n")
        setscores = 0
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                # Skip blank lines
                continue

            commandArgs = line.split()

            if len(commandArgs) != 3:
                await self.display(ctx, f'Usage: {config.PREFIX + cmd} <playername> <objective> <value>')
                return

            name = commandArgs[0]
            objective = commandArgs[1]
            value = commandArgs[2]
            message = f'Set score {objective}={value} via bot'

            await self.run(ctx, [os.path.join(_top_level, "rust/bin/redis_set_offline_player_score"), "redis://redis/", self._k8s.namespace, name, objective, value, message], displayOutput=(len(lines) < 5))
            self._socket.send_packet("*", "monumentanetworkrelay.command", {"command": f"execute if entity {name} run scoreboard players set {name} {objective} {value}"})
            setscores += 1

        await self.display(ctx, f"{setscores} player scores set both in redis (for offline players) and via broadcast (for online players)")

    async def action_player_shard(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''A tool to check what shard a player is on, or transfer one more more offline players.
Usage:
`{cmdPrefix}player shard get NickNackGus` - tells you which shard NickNackGus is on
`{cmdPrefix}player shard histogram` - lists how many players are on each shard
`{cmdPrefix}player shard transfer NickNackGus playerplots` - sends NickNackGus to playerplots shard
`{cmdPrefix}player shard bulk_transfer depths-2,depths-3 depths` - sends everyone on depths-2/3 to the depths shard
`{cmdPrefix}player shard bulk_transfer betaplots,plots valley,valley-2,valley-3` - sends everyone on betaplots and plots to one of three valley shards
'''

        commandArgs = message.content[len(config.PREFIX + cmd) + 1:].split()

        if len(commandArgs) == 0:
            await self.help_internal(ctx, ["player shard"], message.author)
            return

        ns = self._k8s.namespace
        if ns in ('stage', 'volt'):
            ns = 'play'
        await self.run(ctx, [os.path.join(_top_level, "rust/bin/shard_utils"), "redis://redis/", ns, *commandArgs], displayOutput=True)

    async def action_player_transfer(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Transfers player data from one account to another.

Usage: {cmdPrefix}player transfer <sourceplayer> <destplayer>

This will transfer everything from <sourceplayer> to <destplayer> except their guild and plot access. Guild must be done manually by you. Plot access will have to be recreated by the player.

After transferring, source player data is backed up and then deleted. The source player can play again as a new player.

**Both players must be offline for this to work. The bot is not currently able to test for this, so you have to check manually!**
        '''

        commandArgs = message.content[len(config.PREFIX + cmd) + 1:].split()

        if len(commandArgs) != 2:
            await self.help_internal(ctx, ["player transfer"], message.author)
            return

        fromplayer = commandArgs[0]
        toplayer = commandArgs[1]
        backuppath = f"/home/epic/0_OLD_BACKUPS/0_PLAYERDATA_CHANGES/transfer_player_{fromplayer}_to_{toplayer}_{datestr()}"

        await self.run(ctx, [os.path.join(_top_level, "rust/bin/move_redis_data_between_players"), "redis://redis/", "play", fromplayer, toplayer, backuppath], displayOutput=True)
        await self.display(ctx, f"`{fromplayer}` has been wiped and moved to the tutorial. If this was a mistake, you can ask an operator to restore it from the backup in `{backuppath}`.")
        await self.display(ctx, f"`{toplayer}` has had their data overwritten by the data from {fromplayer}. If this was a mistake, you can roll the player back to before the transfer using the in-game /rollback command")
        await self.display(ctx, f"**You still have to fix the player's LuckPerms data.**")
        await self.display(ctx, f"To do this, go in-game and run ```\n/transferpermissions {fromplayer} {toplayer}\n```\nNote that `{fromplayer}` needs to be offline, and `{toplayer}` needs to be online. This will update all LuckPerms data (guilds, roles, etc) in one go.")

    async def action_player_rollback(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Rolls a player back to the most recent weekly update

Usage: {cmdPrefix}player rollback <player>

This will roll a player back to the most recent weekly update data.

**Player must be offline for this to work. The bot is not currently able to test for this, so you have to check manually!**
        '''

        commandArgs = message.content[len(config.PREFIX + cmd) + 1:].split()

        if len(commandArgs) != 1:
            await self.help_internal(ctx, ["player rollback"], message.author)
            return

        playername = commandArgs[0]
        rollbackpath = f"/home/epic/play/m17/server_config/redis_data_initial"
        backuppath = f"/home/epic/0_OLD_BACKUPS/0_PLAYERDATA_CHANGES/rollback_player_{playername}_{datestr()}"

        await self.run(ctx, [os.path.join(_top_level, "rust/bin/player_backup_and_rollback"), "redis://redis/", "play", playername, rollbackpath, backuppath], displayOutput=True)
        await self.display(ctx, f"{playername} has been rolled back to the last weekly update. If this was a mistake, you can either fix it in-game using the `/rollback` command, or ask an operator to restore it from the backup in {backuppath}.")

    async def action_player_wipe(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Wipe's a player's data

Usage: {cmdPrefix}player wipe <player>

This remove player data for this player, but will NOT remove their luckperms groups (guilds, etc.)

**Player must be offline for this to work. The bot is not currently able to test for this, so you have to check manually!**
        '''

        commandArgs = message.content[len(config.PREFIX + cmd) + 1:].split()

        if len(commandArgs) != 1:
            await self.help_internal(ctx, ["player wipe"], message.author)
            return

        playername = commandArgs[0]
        backuppath = f"/home/epic/0_OLD_BACKUPS/0_PLAYERDATA_CHANGES/wipe_player_{playername}_{datestr()}"

        await self.run(ctx, [os.path.join(_top_level, "rust/bin/remove_redis_player"), "redis://redis/", "play", playername, backuppath], displayOutput=True)

        await self.display(ctx, f"{playername} has had their data backed up and then wiped. If this was a mistake, ping an operator to restore it from the backup in `{backuppath}`. Note this only worked if the player is currently logged out.")

        await self.display(ctx, f"**This did not clear their luckperms data** (guilds, patreon, etc.). If the player is just resetting maybe this is fine, but if you're truly removing the account, go in game and run `/lp user {playername} clear`.")

    async def action_player_find(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Finds player names that match the specified string, case insensitive

Usage: {cmdPrefix}player find <search_string>
        '''

        commandArgs = message.content[len(config.PREFIX + cmd) + 1:].split()

        if len(commandArgs) != 1:
            await self.help_internal(ctx, ["player find"], message.author)
            return

        search_string = commandArgs[0].lower()

        r = redis.Redis(host="redis", port=6379)
        name2uuid = r.hgetall('name2uuid')
        uuid2name = r.hgetall('uuid2name')

        # We have two maps, name2uuid (a dict of names to UUID strings) and uuid2name (a dict of UUIDs to most recently seen names). Multiple names may map to the same UUID, indicating the player changed their name at some point. Each name will exist only once in uuid2name (indicating this is the player's current name), or not at all (indicating a past name for that player)
        # We want to find all names that match the search string, and summarize the uuid's of those matching players, along with indicating any prior names for that UUID
        # print the results in the format:
        #   uuid1: most recent name=name1, prior names=(name2, name3, ...
        #   uuid2: most recent name=name1, prior names=(name2, name3,...)
        # Only include the strings "most recent name=" and "prior names=" if more than one name exists for that UUID

        # Initialize an empty dictionary to store the results
        results = {}

        # Iterate over the name2uuid map
        for name, uuid in name2uuid.items():
            namestr = name.decode('utf-8')

            # Check if the name matches the search string
            if search_string in namestr.lower():
                # Retrieve the most recent name and prior names for this UUID
                uuidstr = uuid.decode('utf-8')
                current_namestr = uuid2name.get(uuid, None).decode('utf-8')
                if (current_namestr) is None:
                    await self.display(ctx, f"Found matching name {namestr} with uuid {uuidstr} but somehow this uuid is not in uuid2name, this should not happen. Skipping this name in results.")
                    continue

                result_entry = results.get(uuidstr, {
                    "most recent name":current_namestr,
                    "prior_names":[],
                })
                if namestr != current_namestr and namestr not in result_entry["prior_names"]:
                    result_entry["prior_names"].append(namestr)
                results[uuidstr] = result_entry

                if len(results) > 500:
                    await self.display(ctx, f"More than 500 results, try a more specific search string.")
                    return

        # Scan through again to find names that don't match the search string but were previous names
        for name, uuid in name2uuid.items():
            uuidstr = uuid.decode('utf-8')
            for uuidmatch, result_entry in results.items():
                if uuidstr == uuidmatch:
                    namestr = name.decode('utf-8')
                    if namestr != result_entry["most recent name"] and namestr not in result_entry["prior_names"]:
                        result_entry["prior_names"].append(namestr)
                        results[uuidstr] = result_entry

        # Print the results to a list, then join the list and display it
        await self.display(ctx, f'{len(results)} matching players for search string "{search_string}":')
        resultstrlist = []
        for uuidstr, result_entry in results.items():
            if len(result_entry["prior_names"]) > 0:
                resultstrlist.append(f"{uuidstr}: most recent name= {result_entry['most recent name']}   prior names= {'  '.join(result_entry['prior_names'])}")
            else:
                resultstrlist.append(f"{uuidstr}: {result_entry['most recent name']}")
        await self.display_verbatim(ctx, "\n".join(resultstrlist))

    async def action_generate_instances(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Generates instances from dungeon worlds
Temporarily brings down the dungeon shard to generate dungeon instances.
Must be run before preparing the build server update bundle
If --debug argument is specified, will not stop dungeon shard before copying
'''

        debug = False
        if message.content[len(config.PREFIX + cmd) + 1:].strip() == "--debug":
            debug = True
            await self.display(ctx, "Debug mode enabled! Will only generate 5 of each dungeon, and will not cleanly copy the dungeon shard")

        await self.generate_instances_internal(ctx, mention=message.author.mention, debug=debug, owner=message)

    async def generate_instances_internal(self, ctx: discord.ext.commands.Context, mention=None, debug=False, owner=None):
        '''Internals of {cmdPrefix}generate instances'''

        await self.display(ctx, "Cleaning up old weekly update data...")
        await self.run(ctx, "rm -rf /home/epic/5_SCRATCH/tmpreset", None)
        await self.run(ctx, "mkdir -p /home/epic/5_SCRATCH/tmpreset")

        if not debug:
            await self.display(ctx, "Stopping the dungeon shard...")
            await self.stop(ctx, "dungeon", owner=owner)

        await self.display(ctx, "Copying the dungeon master copies...")
        await self.run(ctx, "cp -a /home/epic/project_epic/dungeon /home/epic/5_SCRATCH/tmpreset/dungeon")

        if not debug:
            await self.display(ctx, "Restarting the dungeon shard...")
            await self.start(ctx, "dungeon", wait=False, owner=owner)

        await self.display(ctx, "Generating dungeon instances (this may take a while)...")
        instance_gen_arg = " --dungeon-path /home/epic/5_SCRATCH/tmpreset/dungeon/ --out-folder /home/epic/5_SCRATCH/tmpreset/dungeons-out/"
        await self.run(ctx, os.path.join(_top_level, "utility_code/dungeon_instance_gen.py") + instance_gen_arg)
        await self.run(ctx, "mv /home/epic/5_SCRATCH/tmpreset/dungeons-out /home/epic/5_SCRATCH/tmpreset/TEMPLATE")

        await self.display(ctx, "Cleaning up instance generation temp files...")
        await self.run(ctx, "rm -rf /home/epic/5_SCRATCH/tmpreset/dungeon")
        await self.display(ctx, "Dungeon instance generation complete!")
        if mention is not None:
            await self.display(ctx, mention)

    async def action_prepare_update_bundle(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''prepare update bundle <version> [--debug] [--skip-commit] [--skip-replacements] [--skip-generation]

Does several things:
- Deletes any existing update bundle
- Commits the data folder, runs autoformat on the data folder, printing errors, commits the autoformat, and tags the commit with <version> (skipped by --skip-commit)
- Runs replacements on valley/isles/dungeon/structures (skipped by --skip-replacements)
- Runs {cmdPrefix}generate instances (skipped by --skip-generation)
- Packages up the update bundle

If specified, --debug implies --skip-format, and --skip-replacements. Shards will not be stopped before copying data.
Generation will still run with the --debug argument, which skips stopping the dungeon shard

Must be run before starting the update on the play server
'''

        debug = False
        skip_commit = False
        skip_replacements = False
        skip_generation = False
        version = None
        args = message.content[len(config.PREFIX + cmd) + 1:].strip().split(" ")

        await self.display(ctx, "Update bundling started")

        if "--debug" in args:
            debug = True
            skip_commit = True
            skip_replacements = True
            await self.display(ctx, "--debug mode enabled! Will not stop shards before copying")

        if "--skip-commit" in args or skip_commit:
            skip_commit = True
            await self.display(ctx, "--skip-commit mode enabled! Will not commit, autoformat, or tag the data folder")

        if "--skip-replacements" in args or skip_replacements:
            skip_replacements = True
            await self.display(ctx, "--skip-replacements mode enabled! Will not run replacements")

        if "--skip-generation" in args or skip_generation:
            skip_generation = True
            await self.display(ctx, "--skip-generation mode enabled! Will not run instance generation. **This probably isn't what you want.**")

        if not skip_commit:
            repo = git.Repo('/home/epic/project_epic/server_config/data')
            tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
            str_tags = [tag.name for tag in tags]
            latest_tag = str_tags[-1]

            if len(args) > 0 and not args[0].startswith("--") and len(args[0]) > 2:
                version = args[0]

            if version is None:
                await self.display(ctx, f"Version must be specified. Latest version is {latest_tag}")
                await self.display(ctx, message.author.mention)
                return

            if version in str_tags:
                await self.display(ctx, f"Version {version} already exists. Latest version is {latest_tag}")
                await self.display(ctx, message.author.mention)
                return

            await self.cd(ctx, '/home/epic/project_epic/server_config/data')
            await self.run(ctx, 'git add .')
            await self.run(ctx, ['git', 'commit', '-m', "Update bundle pre autoformat", '-s'], ret=[0, 1])
            await self.run(ctx, os.path.join(_top_level, "utility_code/autoformat_cleanup_loot_tables_and_quests.py"), displayOutput=True)
            await self.cd(ctx, '/home/epic/project_epic/server_config/data')
            await self.run(ctx, 'git add .')
            await self.run(ctx, ['git', 'commit', '-m', "Update bundle post autoformat", '-s'], ret=[0, 1])

        if not skip_replacements:
            await self.run_replacements_internal(ctx, ["valley", "isles", "ring", "dungeon", "structures"], do_prune=True, owner=message)

        if not skip_commit:
            await self.cd(ctx, '/home/epic/project_epic/server_config/data')
            await self.run(ctx, 'git add .')
            await self.run(ctx, ['git', 'commit', '-m', "Update bundle post replacements", '-s'], ret=[0, 1])
            await self.run(ctx, ['git', 'tag', version])

        if not skip_generation:
            await self.generate_instances_internal(ctx, debug=debug, owner=message)

        if not debug:
            await self.display(ctx, "Stopping valley, isles, ring...")
            await self.stop(ctx, ["valley", "isles", "ring"], owner=message)

        await self.display(ctx, "Copying valley...")
        await self.run(ctx, "mkdir -p /home/epic/5_SCRATCH/tmpreset/TEMPLATE/valley")
        await self.run(ctx, "cp -a /home/epic/project_epic/valley/Project_Epic-valley /home/epic/5_SCRATCH/tmpreset/TEMPLATE/valley/")
        await self.run(ctx, "cp -a /home/epic/project_epic/valley/azacor /home/epic/5_SCRATCH/tmpreset/TEMPLATE/valley/")
        await self.run(ctx, "cp -a /home/epic/project_epic/valley/sanctum /home/epic/5_SCRATCH/tmpreset/TEMPLATE/valley/")
        await self.run(ctx, "cp -a /home/epic/project_epic/valley/verdant /home/epic/5_SCRATCH/tmpreset/TEMPLATE/valley/")
        await self.run(ctx, "cp -a /home/epic/project_epic/valley/quests /home/epic/5_SCRATCH/tmpreset/TEMPLATE/valley/")

        if not debug:
            await self.display(ctx, "Restarting the valley shard...")
            await self.start(ctx, "valley", wait=False, owner=message)

        await self.display(ctx, "Copying isles...")
        await self.run(ctx, "mkdir -p /home/epic/5_SCRATCH/tmpreset/TEMPLATE/isles")
        await self.run(ctx, "cp -a /home/epic/project_epic/isles/Project_Epic-isles /home/epic/5_SCRATCH/tmpreset/TEMPLATE/isles/")
        await self.run(ctx, "cp -a /home/epic/project_epic/isles/mist /home/epic/5_SCRATCH/tmpreset/TEMPLATE/isles/")
        await self.run(ctx, "cp -a /home/epic/project_epic/isles/remorse /home/epic/5_SCRATCH/tmpreset/TEMPLATE/isles/")
        await self.run(ctx, "cp -a /home/epic/project_epic/isles/quests /home/epic/5_SCRATCH/tmpreset/TEMPLATE/isles/")

        if not debug:
            await self.display(ctx, "Restarting the isles shard...")
            await self.start(ctx, "isles", wait=False, owner=message)

        await self.display(ctx, "Copying ring...")
        await self.run(ctx, "mkdir -p /home/epic/5_SCRATCH/tmpreset/TEMPLATE/ring")
        await self.run(ctx, "cp -a /home/epic/project_epic/ring/Project_Epic-ring /home/epic/5_SCRATCH/tmpreset/TEMPLATE/ring/")
        await self.run(ctx, "cp -a /home/epic/project_epic/ring/godspore /home/epic/5_SCRATCH/tmpreset/TEMPLATE/ring/")
        await self.run(ctx, "cp -a /home/epic/project_epic/ring/portal /home/epic/5_SCRATCH/tmpreset/TEMPLATE/ring/")
        await self.run(ctx, "cp -a /home/epic/project_epic/ring/quests /home/epic/5_SCRATCH/tmpreset/TEMPLATE/ring/")
        await self.run(ctx, "cp -a /home/epic/project_epic/ring/ruin /home/epic/5_SCRATCH/tmpreset/TEMPLATE/ring/")
        await self.run(ctx, "cp -a /home/epic/project_epic/ring/land_of_storms /home/epic/5_SCRATCH/tmpreset/TEMPLATE/ring/")

        if not debug:
            await self.display(ctx, "Restarting the ring and ring shards...")
            await self.start(ctx, "ring", wait=False, owner=message)

        await self.display(ctx, "Copying purgatory...")
        await self.run(ctx, "cp -a /home/epic/project_epic/purgatory /home/epic/5_SCRATCH/tmpreset/TEMPLATE/")

        await self.display(ctx, "Copying server_config...")
        await self.run(ctx, "cp -a /home/epic/project_epic/server_config /home/epic/5_SCRATCH/tmpreset/TEMPLATE/")

        await self.display(ctx, "Sanitizing R1's items area...")
        await self.run(ctx, os.path.join(_top_level, "utility_code/sanitize_world.py") + " --world /home/epic/5_SCRATCH/tmpreset/TEMPLATE/valley/Project_Epic-valley --pos1 1140,0,2564 --pos2 1275,123,2811")
        await self.display(ctx, "Sanitizing R2's items area...")
        await self.run(ctx, os.path.join(_top_level, "utility_code/sanitize_world.py") + " --world /home/epic/5_SCRATCH/tmpreset/TEMPLATE/isles/Project_Epic-isles --pos1 1140,0,2564 --pos2 1275,123,2811")
        await self.display(ctx, "Sanitizing R3's items area...")
        await self.run(ctx, os.path.join(_top_level, "utility_code/sanitize_world.py") + " --world /home/epic/5_SCRATCH/tmpreset/TEMPLATE/ring/Project_Epic-ring --pos1 1140,0,2564 --pos2 1275,123,2811")

        await self.display(ctx, "Packaging up update bundle...")
        await self.cd(ctx, "/home/epic/5_SCRATCH/tmpreset")
        await self.run(ctx, "rm -f /home/epic/4_SHARED/project_epic_build_template.tgz")
        await self.run(ctx, ["tar", "-I", "pigz --best", "-cf", "/home/epic/5_SCRATCH/tmpreset/project_epic_build_template.tgz", "TEMPLATE"])
        await self.run(ctx, ["mv", "/home/epic/5_SCRATCH/tmpreset/project_epic_build_template.tgz", "/home/epic/4_SHARED/project_epic_build_template.tgz"])

        await self.display(ctx, "Update bundle ready!")
        await self.display(ctx, message.author.mention)

    async def action_prepare_stage_bundle(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Prepares a bundle of whichever shards you want to update on stage.

`--debug` prepares the bundle without stopping shards.
`--skip-server-config` prepares the bundle without including the server_config folder (no plugins or data folder updates)
`--skip-replacements` prepares the bundle without running replacements on copied worlds (much faster)

Examples:
`{cmdPrefix}prepare stage bundle valley labs`
`{cmdPrefix}prepare stage bundle --debug valley labs`'''

        arg_str = message.content[len(config.PREFIX + cmd)+1:].strip()
        shards = arg_str.split()

        if len(shards) <= 0:
            await self.display(ctx, "No shards specified")
            return

        instance_gen_required = []
        main_shards = []
        debug = False
        copy_server_config = True
        run_replacements = True
        for shard in shards:
            if shard == "--debug":
                debug = True
                await self.display(ctx, "Debug mode enabled! Will not stop shards prior to copying")
            elif shard == "--skip-server-config":
                copy_server_config = False
                await self.display(ctx, "--skip-server-config specified, will not copy server_config folder (no plugins or data folder updates)")
            elif shard == "--skip-replacements":
                run_replacements = False
                await self.display(ctx, "--skip-replacements specified, will not run replacements on copied worlds")
            elif shard in ("valley", "isles", "ring",):
                main_shards.append(shard)
            elif shard in ["white", "orange", "magenta", "lightblue", "yellow", "lime", "pink", "gray", "lightgray", "cyan", "purple", "blue", "brown", "green", "red", "black", "teal", "forum", "tutorial", "reverie", "rush", "willows", "shiftingcity", "labs", "depths", "corridors", "gallery", "portal", "ruin", "hexfall", "skt", "zenith"]:
                instance_gen_required.append(shard)
            else:
                await self.display(ctx, f"Unknown shard specified: {shard}")
                return

        await self.display(ctx, "Starting stage bundle preparation for shards: [{}]".format(" ".join(shards)))

        await self.display(ctx, "Cleaning up old stage data...")
        await self.run(ctx, "rm -rf /home/epic/5_SCRATCH/tmpstage", None)
        await self.run(ctx, "mkdir -p /home/epic/5_SCRATCH/tmpstage")

        if len(main_shards) > 0:
            # Need to copy primary shards

            for shard in main_shards:
                if not debug:
                    await self.display(ctx, f"Stopping {shard}...")
                    await self.stop(ctx, shard, owner=message)

                await self.run(ctx, f"mkdir -p /home/epic/5_SCRATCH/tmpstage/TEMPLATE/{shard}")
                worlds = [Path(path).name for path in World.enumerate_worlds(f"/home/epic/project_epic/{shard}")]
                await self.display(ctx, f"Copying worlds {' '.join(worlds)} from {shard}")
                for worldname in worlds:
                    await self.run(ctx, f"cp -a /home/epic/project_epic/{shard}/{worldname} /home/epic/5_SCRATCH/tmpstage/TEMPLATE/{shard}/")

                # Copy the current warps
                await self.run(ctx, f"cp -a /home/epic/project_epic/{shard}/plugins/MonumentaWarps/warps.yml /home/epic/5_SCRATCH/tmpstage/TEMPLATE/{shard}/")

                if not debug:
                    await self.display(ctx, f"Restarting {shard}...")
                    await self.start(ctx, shard, wait=False, owner=message)

                if run_replacements:
                    await self.display(ctx, f"Running replacements on copied version of {shard}...")
                    args = f" --worlds /home/epic/5_SCRATCH/tmpstage/TEMPLATE/{shard}"
                    await self.run(ctx, os.path.join(_top_level, "utility_code/replace_items.py") + args, displayOutput=True)
                    args = f" --worlds /home/epic/5_SCRATCH/tmpstage/TEMPLATE/{shard} --library-of-souls /home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json"
                    await self.run(ctx, os.path.join(_top_level, "utility_code/replace_mobs.py") + args, displayOutput=True)

        if len(instance_gen_required) > 0:
            # Need to generate instances
            if not debug:
                await self.display(ctx, "Stopping the dungeon shard...")
                await self.stop(ctx, "dungeon", owner=message)

            await self.display(ctx, "Copying the dungeon master copies...")
            await self.run(ctx, "cp -a /home/epic/project_epic/dungeon /home/epic/5_SCRATCH/tmpstage/dungeon")
            await self.run(ctx, "rm -rf /home/epic/5_SCRATCH/tmpstage/dungeon/cache /home/epic/5_SCRATCH/tmpstage/dungeon/plugins")

            if not debug:
                await self.display(ctx, "Restarting the dungeon shard...")
                await self.start(ctx, "dungeon", wait=False, owner=message)

            if run_replacements:
                await self.display(ctx, "Running replacements on copied dungeon masters...")
                args = " --worlds /home/epic/5_SCRATCH/tmpstage/dungeon"
                await self.run(ctx, os.path.join(_top_level, "utility_code/replace_items.py") + args, displayOutput=True)
                args = " --worlds /home/epic/5_SCRATCH/tmpstage/dungeon --library-of-souls /home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json"
                await self.run(ctx, os.path.join(_top_level, "utility_code/replace_mobs.py") + args, displayOutput=True)

            await self.display(ctx, "Generating dungeon instances for [{}]...".format(" ".join(instance_gen_required)))
            instance_gen_arg = (" --dungeon-path /home/epic/5_SCRATCH/tmpstage/dungeon/" +
                                " --out-folder /home/epic/5_SCRATCH/tmpstage/TEMPLATE " +
                                " ".join(instance_gen_required))
            await self.run(ctx, os.path.join(_top_level, "utility_code/dungeon_instance_gen.py") + instance_gen_arg)

            await self.display(ctx, "Dungeon instance generation complete!")

        if copy_server_config:
            await self.display(ctx, "Copying server_config...")
            await self.run(ctx, "cp -a /home/epic/project_epic/server_config /home/epic/5_SCRATCH/tmpstage/TEMPLATE/")

            if run_replacements:
                await self.display(ctx, "Running replacements on copied structures...")
                args = (" --schematics /home/epic/5_SCRATCH/tmpstage/TEMPLATE/server_config/data/structures"
                        + " --structures /home/epic/5_SCRATCH/tmpstage/TEMPLATE/server_config/data/generated"
                        + " --library-of-souls /home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json")
                await self.run(ctx, os.path.join(_top_level, "utility_code/replace_items.py"
                                                 + " --schematics /home/epic/5_SCRATCH/tmpstage/TEMPLATE/server_config/data/structures"
                                                 + " --structures /home/epic/5_SCRATCH/tmpstage/TEMPLATE/server_config/data/generated"), displayOutput=True)
                await self.run(ctx, os.path.join(_top_level, "utility_code/replace_mobs.py") + args, displayOutput=True)

        await self.display(ctx, "Packaging up stage bundle...")
        await self.cd(ctx, "/home/epic/5_SCRATCH/tmpstage")

        await self.run(ctx, "rm -f /home/epic/4_SHARED/stage_bundle.tgz", None)
        await self.run(ctx, ["tar", "-I", "pigz --best", "-cf", "/home/epic/5_SCRATCH/tmpstage/stage_bundle.tgz", "TEMPLATE"])
        await self.run(ctx, ["mv", "/home/epic/5_SCRATCH/tmpstage/stage_bundle.tgz", "/home/epic/4_SHARED/stage_bundle.tgz"])

        await self.display(ctx, "Cleaning up stage temp files...")
        await self.run(ctx, "rm -rf /home/epic/5_SCRATCH/tmpstage")

        await self.display(ctx, "Stage bundle ready!")
        await self.display(ctx, message.author.mention)

    async def action_apply_stage_bundle(self, ctx: discord.ext.commands.Context, _, message: discord.Message):
        '''Applies a bundle of whichever shards you want to update on stage. This takes no arguments.
You can create a bundle with `{cmdPrefix}prepare stage bundle`'''

        await self.display(ctx, "Unpacking stage bundle...")
        await self.run(ctx, "rm -rf /home/epic/5_SCRATCH/tmpreset", None)
        await self.run(ctx, "mkdir -p /home/epic/5_SCRATCH/tmpreset")
        await self.cd(ctx, "/home/epic/5_SCRATCH/tmpreset")
        await self.run(ctx, "cp -a /home/epic/4_SHARED/stage_bundle.tgz /home/epic/5_SCRATCH/tmpreset/stage_bundle.tgz")
        await self.run(ctx, "tar xzf /home/epic/5_SCRATCH/tmpreset/stage_bundle.tgz")
        await self.run(ctx, "rm -f /home/epic/5_SCRATCH/tmpreset/stage_bundle.tgz", None)

        await self.cd(ctx, "/home/epic/5_SCRATCH/tmpreset/TEMPLATE")
        folders_to_update = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d)]
        if len(folders_to_update) < 1:
            await self.display(ctx, "Error: No stage folders to process?")
            await self.display(ctx, message.author.mention)
            return

        await self.display(ctx, "Loading from stage bundle: [{}]".format(" ".join(folders_to_update)))

        # Stop all shards
        await self.display(ctx, "Stopping all shards...")
        shards = await self._k8s.list()
        await self.stop(ctx, [shard for shard in self._shards if shard.replace('_', '') in shards], owner=message)
        for shard in [shard for shard in self._shards if shard.replace('_', '') in shards]:
            if shards[shard.replace('_', '')]['replicas'] != 0:
                await self.display(ctx, f"ERROR: shard {shard} is still running!")
                await self.display(ctx, message.author.mention)
                return

        if 'valley' in self._shards:
            await self.display(ctx, "Saving ops and banned players")
            await self.run(ctx, "mkdir -p /home/epic/4_SHARED/op-ban-sync/stage/")
            await self.run(ctx, f"cp -a {self._shards['valley']}/banned-ips.json /home/epic/4_SHARED/op-ban-sync/stage/")
            await self.run(ctx, f"cp -a {self._shards['valley']}/banned-players.json /home/epic/4_SHARED/op-ban-sync/stage/")
            await self.run(ctx, f"cp -a {self._shards['valley']}/ops.json /home/epic/4_SHARED/op-ban-sync/stage/")

        await self.display(ctx, "Deleting previous update data...")
        await self.cd(ctx, self._server_dir)
        await self.run(ctx, "rm -rf 0_PREVIOUS")
        await self.run(ctx, "mkdir 0_PREVIOUS")

        await self.display(ctx, f"Moving [{' '.join(folders_to_update)}] to 0_PREVIOUS...")
        for folder in folders_to_update:
            await self.run(ctx, f"mv {folder} 0_PREVIOUS/", None)

        if "server_config" in folders_to_update:
            await self.display(ctx, "Getting new server config...")
            await self.run(ctx, f"mv /home/epic/5_SCRATCH/tmpreset/TEMPLATE/server_config {self._server_dir}/")
            folders_to_update.remove("server_config")

        await self.display(ctx, "Running actual weekly update (this will take a while!)...")

        await self.run(ctx, os.path.join(_top_level, f"utility_code/weekly_update.py --last_week_dir {self._server_dir}/0_PREVIOUS/ --output_dir {self._server_dir}/ --build_template_dir /home/epic/5_SCRATCH/tmpreset/TEMPLATE/ -j 6 " + " ".join(folders_to_update)))

        for shard in folders_to_update:
            if shard in ["build",] or shard.startswith("bungee") or shard.startswith("velocity"):
                continue

            await self.run(ctx, f"cp -af /home/epic/4_SHARED/op-ban-sync/stage/banned-ips.json {self._shards[shard]}/")
            await self.run(ctx, f"cp -af /home/epic/4_SHARED/op-ban-sync/stage/banned-players.json {self._shards[shard]}/")
            await self.run(ctx, f"cp -af /home/epic/4_SHARED/op-ban-sync/stage/ops.json {self._shards[shard]}/")

        await self.display(ctx, "Generating per-shard config...")
        await self.cd(ctx, self._server_dir)
        await self.run(ctx, os.path.join(_top_level, "utility_code/gen_server_config.py --play " + " ".join(folders_to_update)))

        # TODO: Revert this once this new content launches!
        if "ring" in folders_to_update:
            await self.cd(ctx, f"{self._server_dir}/ring/plugins/MonumentaStructureManagement")
            await self.run(ctx, "rm -f config.yml")
            await self.run(ctx, "ln -s ../../../server_config/data/plugins/ring/MonumentaStructureManagement/newconfig.yml config.yml")
            await self.cd(ctx, self._server_dir)

        # Apply the warps from the build server
        await self.run(ctx, f"mkdir -p {self._server_dir}/{shard}/plugins/MonumentaWarps")
        await self.run(ctx, f"cp -a /home/epic/5_SCRATCH/tmpreset/TEMPLATE/{shard}/warps.yml {self._server_dir}/{shard}/plugins/MonumentaWarps/warps.yml", None)

        await self.display(ctx, "Checking for broken symbolic links...")
        await self.run(ctx, "find . -xtype l", displayOutput=True)

        await self.display(ctx, "Done.")
        await self.display(ctx, message.author.mention)


    async def action_fetch_update_bundle(self, ctx: discord.ext.commands.Context, _, message: discord.Message):
        '''Dangerous!
Deletes in-progress weekly update info on the play server
Downloads the weekly update bundle from the build server and unpacks it'''

        await self.display(ctx, "Unpacking update bundle...")
        await self.run(ctx, "rm -rf /home/epic/5_SCRATCH/tmpreset", None)
        await self.run(ctx, "mkdir -p /home/epic/5_SCRATCH/tmpreset")
        await self.cd(ctx, "/home/epic/5_SCRATCH/tmpreset")
        await self.run(ctx, "cp -a /home/epic/4_SHARED/project_epic_build_template.tgz /home/epic/5_SCRATCH/tmpreset/project_epic_build_template.tgz")
        await self.run(ctx, "tar xzf /home/epic/5_SCRATCH/tmpreset/project_epic_build_template.tgz")
        await self.run(ctx, "rm -f /home/epic/5_SCRATCH/tmpreset/project_epic_build_template.tgz", None)
        await self.display(ctx, "Build server template data retrieved and ready for update.")
        await self.display(ctx, message.author.mention)

    async def action_stop_at_minute(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Starts a bungee shutdown timer the next HH:MM for the minute specified

Optionally, set a reason. The default reason is "maintenance":
{cmdPrefix}stop at 15
{cmdPrefix}stop at 0 weekly update
If the reason is weekly update, and the timer has at least 5 minutes left,
old coreprotect data will be removed at the 5 minute mark.
'''

        commandArgs = message.content[len(config.PREFIX + cmd) + 1:].strip().split(maxsplit=1)
        reason = "maintenance"
        if len(commandArgs) == 0:
            await self.display(ctx, "Error: Please specify at which minute past the hour to stop.")
            await self.display(ctx, message.author.mention)
            return
        if len(commandArgs) >= 2:
            reason = commandArgs[1]
        try:
            target_minute = int(commandArgs[0])
        except Exception:
            await self.display(ctx, f"Error: Minute must be an integer: {commandArgs[0]!r}")
            await self.display(ctx, message.author.mention)
            return

        if target_minute not in range(60):
            await self.display(ctx, f"Error: Minute must be in 0..59: {target_minute}")
            await self.display(ctx, message.author.mention)
            return

        tz = timezone.utc
        second = timedelta(seconds=1)
        now = datetime.now(tz)
        stop_time = datetime(now.year, now.month, now.day, now.hour, target_minute, tzinfo=tz)
        if stop_time < now:
            stop_time += timedelta(hours=1)

        countdown_targets = sorted([
            60 * 50,
            60 * 40,
            60 * 30,
            60 * 20,
            60 * 10,
            60 * 7,
            60 * 5,
            60 * 3,
            60 * 2,
            60,
            30,
            15,
            5,
            4,
            3,
            2,
            1,
        ], reverse=True)

        self._socket.send_packet("*", "monumentanetworkrelay.command",
                                 {"command": '''tellraw @a[all_worlds=true] ''' + json.dumps([
                                     "",
                                     {"text":"[Alert] ", "color":"red"},
                                     {"text":"Monumenta is going down at ", "color":"white"},
                                     {"text":stop_time.strftime('%I:%M %p UTC'), "color":"red"},
                                     {"text":". " + reason + ". Check our discord for details.", "color":"white"}
                                 ], ensure_ascii=False, separators=(',', ':'))})
        await self.display(ctx, f"Server stopping at <t:{int(stop_time.timestamp())}> (<t:{int(stop_time.timestamp())}:R>)")

        def seconds_to_string(seconds):
            if seconds == 0:
                return "now"
            if seconds == 1:
                return "1 second"
            if seconds < 60:
                return f"{seconds} seconds"

            minutes = seconds // 60
            if minutes == 1:
                return "1 minute"
            return f"{minutes} minutes"

        async def send_broadcast_msg(time_left):
            self._socket.send_packet("*", "monumentanetworkrelay.command",
                                     {"command": '''tellraw @a[all_worlds=true] ''' + json.dumps([
                                         "",
                                         {"text":"[Alert] ", "color":"red"},
                                         {"text":"The Monumenta server is stopping in ", "color":"white"},
                                         {"text":time_left, "color":"red"},
                                         {"text":". " + reason + ". Check our discord for details."}
                                     ], ensure_ascii=False, separators=(',', ':'))})
            await self.display(ctx, f"{time_left} to stop")

        while countdown_targets:
            next_target = countdown_targets.pop(0)
            remaining_seconds = (stop_time - datetime.now(tz)) / second
            if remaining_seconds < next_target:
                continue
            await asyncio.sleep(remaining_seconds - next_target)

            if next_target == 60 * 5 and "weekly update" in reason:
                await self.display(ctx, "Clearing coreprotect data older than 30 days")
                for shard in self._shards:
                    # TODO: add guild worlds to this when added - usb
                    if shard in ["plots", "playerplots"]:
                        self._socket.send_packet(shard, "monumentanetworkrelay.command", {
                            "server_type": "minecraft",
                            "command": 'co purge t:180d'
                        })
                    elif shard not in ["build",]:
                        self._socket.send_packet(shard, "monumentanetworkrelay.command", {
                            "server_type": "minecraft",
                            "command": 'co purge t:30d'
                        })
            if next_target == 15:
                self._socket.send_packet("*", "monumentanetworkrelay.command", {"server_type": "minecraft", "command": 'save-all'})

            await send_broadcast_msg(seconds_to_string(next_target))

        # Stop velocity (I guess you could uh... run maintenance?)
        self._socket.send_packet("*", "monumentanetworkrelay.command", {"server_type": "proxy", "command": 'maintenance on'})
        await asyncio.sleep(5)
        # TODO: don't hardcode velocity instances here
        shards = await self._k8s.list()
        velocityShards = list(filter(lambda x: (x.startswith("velocity")), shards))
        await self.stop(ctx, velocityShards, owner=message)

        await self.display(ctx, message.author.mention)

    async def action_stop_and_backup(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Dangerous!
Brings down all play server shards and backs them up in preparation for weekly update.
DELETES DUNGEON CORE PROTECT DATA'''

        debug = False
        if message.content[len(config.PREFIX + cmd) + 1:].strip() == "--debug":
            debug = True
            await self.display(ctx, "Debug mode enabled! Will not actually make backups")

        await self.display(ctx, "Stopping all shards...")

        shards = await self._k8s.list()

        # Stop all shards
        await self.stop(ctx, [shard for shard in self._shards if shard.replace('_', '') in shards], owner=message)

        # Fail if any shards are still running
        await self.display(ctx, "Checking that all shards are stopped...")
        shards = await self._k8s.list()
        for shard in [shard for shard in self._shards if shard.replace('_', '') in shards]:
            if shards[shard.replace('_', '')]['replicas'] != 0:
                await self.display(ctx, "ERROR: shard {!r} is still running!".format(shard))
                await self.display(ctx, message.author.mention)
                return

        await self.display(ctx, "Deleting cache and select FAWE and CoreProtect data...")
        for shard in self._shards:
            dirs_to_del = []
            dirs_to_del.append(f"{self._shards[shard]}/cache")

            if shard not in ["build",]:
                dirs_to_del.append(f"{self._shards[shard]}/plugins/FastAsyncWorldEdit/clipboard")
                dirs_to_del.append(f"{self._shards[shard]}/plugins/FastAsyncWorldEdit/history")
                dirs_to_del.append(f"{self._shards[shard]}/plugins/FastAsyncWorldEdit/sessions")

            if shard in ["tutorial",]:
                dirs_to_del.append(f"{self._shards[shard]}/plugins/CoreProtect")

            await self.run(ctx, f"rm -rf {' '.join(dirs_to_del)}")

        if "valley" in self._shards:
            await self.display(ctx, "Saving valley warps, ops, and banned players")
            await self.run(ctx, "mkdir -p /home/epic/4_SHARED/op-ban-sync/valley/plugins/")
            await self.run(ctx, "rm -rf /home/epic/4_SHARED/op-ban-sync/valley/plugins/MonumentaWarps")
            await self.run(ctx, f"cp -a {self._shards['valley']}/banned-ips.json /home/epic/4_SHARED/op-ban-sync/valley/")
            await self.run(ctx, f"cp -a {self._shards['valley']}/banned-players.json /home/epic/4_SHARED/op-ban-sync/valley/")
            await self.run(ctx, f"cp -a {self._shards['valley']}/ops.json /home/epic/4_SHARED/op-ban-sync/valley/")
            await self.run(ctx, f"cp -a {self._shards['valley']}/plugins/MonumentaWarps /home/epic/4_SHARED/op-ban-sync/valley/plugins/MonumentaWarps")

        if "isles" in self._shards:
            await self.display(ctx, "Saving isles warps")
            await self.run(ctx, "mkdir -p /home/epic/4_SHARED/op-ban-sync/isles/plugins/")
            await self.run(ctx, "rm -rf /home/epic/4_SHARED/op-ban-sync/isles/plugins/MonumentaWarps")
            await self.run(ctx, f"cp -a {self._shards['isles']}/plugins/MonumentaWarps /home/epic/4_SHARED/op-ban-sync/isles/plugins/MonumentaWarps")

        if "ring" in self._shards:
            await self.display(ctx, "Saving ring warps")
            await self.run(ctx, "mkdir -p /home/epic/4_SHARED/op-ban-sync/ring/plugins/")
            await self.run(ctx, "rm -rf /home/epic/4_SHARED/op-ban-sync/ring/plugins/MonumentaWarps")
            await self.run(ctx, f"cp -a {self._shards['ring']}/plugins/MonumentaWarps /home/epic/4_SHARED/op-ban-sync/ring/plugins/MonumentaWarps", ret=(0, 1,))
            await self.run(ctx, "mkdir -p /home/epic/4_SHARED/op-ban-sync/ring/plugins/MonumentaWarps")

        if config.COMMON_WEEKLY_UPDATE_TASKS:
            await self.display(ctx, "Copying player data from redis")
            await self.run(ctx, os.path.join(_top_level, "rust/bin/redis_playerdata_save_load") + f" redis://redis/ play --output {self._server_dir}/server_config/redis_data_final")

            await self.display(ctx, "Copying market data from redis")
            await self.run(ctx, os.path.join(_top_level, "utility_code/market_itemdb_export.py") + f" redis play {self._server_dir}/server_config/redis_data_final")

        if debug:
            await self.display(ctx, "WARNING! Skipping backup!")
        else:
            await self.display(ctx, "Performing backup...")
            await self.cd(ctx, f"{self._server_dir}/..")
            await self.run(ctx, "mkdir -p /home/epic/1_ARCHIVE")
            folder_name = self._server_dir.strip("/").split("/")[-1]
            await self.run(ctx, ["tar", f"--exclude={folder_name}/0_PREVIOUS", "-I", "pigz --best", "-cf", f"/home/epic/1_ARCHIVE/{folder_name}_pre_reset_{datestr()}.tgz", folder_name])

        await self.display(ctx, "Backups complete! Ready for update.")
        await self.display(ctx, message.author.mention)

    async def action_get_raffle_seed(self, ctx: discord.ext.commands.Context, _, __: discord.Message):
        '''Gets the current raffle seed based on reactions'''

        if self._rreact["msg_contents"] is not None:
            await self.display(ctx, "Current raffle seed is: ```\n{}\n```".format(self._rreact["msg_contents"]))
        else:
            await self.display(ctx, "No current raffle seed")

    async def action_run_test_raffle(self, ctx: discord.ext.commands.Context, _, __: discord.Message):
        '''Runs a test raffle (does not save results)'''

        await self.display(ctx, "Test raffle results:")
        raffle_seed = self.get_raffle_seed()

        raffle_results = tempfile.mktemp()
        vote_raffle(raffle_seed, 'redis', raffle_results, dry_run=True)
        await self.run(ctx, "cat {}".format(raffle_results), displayOutput=True)

    async def action_weekly_update(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Dangerous!
Performs the weekly update on the play server. Requires StopAndBackupAction.'''

        # Check for any arguments
        commandArgs = message.content[len(config.PREFIX):].strip()
        min_phase = 0
        if len(commandArgs) > len(cmd) + 1:
            min_phase = int(commandArgs[len(cmd) + 1:].strip())
        await self.display(ctx, f"Starting from phase {min_phase} at <t:{int(time.time())}:F>")

        await self.run(ctx, "mkdir -p /home/epic/1_ARCHIVE")
        await self.run(ctx, "mkdir -p /home/epic/0_OLD_BACKUPS")

        r = redis.Redis(host="redis", port=6379)
        if min_phase <= 0:
            r.set('monumenta:automation:weekly_update_common_done', 'False')
            common_done = r.get('monumenta:automation:weekly_update_common_done').decode("utf-8")
            await self.display(ctx, "Marked common update tasks as not done")
            if common_done != "False":
                raise Exception(f"Tried to set common_done = False but got {common_done} back!")

        # Fail if any shards are still running
        if min_phase <= 1:
            await self.display(ctx, "Checking that all shards are stopped...")
            shards = await self._k8s.list()
            for shard in [shard for shard in self._shards if shard.replace('_', '') in shards]:
                if shards[shard.replace('_', '')]['replicas'] != 0:
                    await self.display(ctx, "ERROR: shard {!r} is still running!".format(shard))
                    await self.display(ctx, message.author.mention)
                    return

        # Sanity check to make sure this script is going to process everything that it needs to
        if min_phase <= 2:
            files = os.listdir(self._server_dir)
            for f in files:
                if f not in ["server_config", "0_PREVIOUS"] and f not in self._shards:
                    await self.display(ctx, f"ERROR: {self._server_dir} directory contains file {f} which will not be processed!")
                    await self.display(ctx, message.author.mention)
                    return

        # Delete previous update data and move current data to 0_PREVIOUS
        await self.cd(ctx, self._server_dir)
        if min_phase <= 3:
            await self.display(ctx, "Deleting previous update data...")
            await self.run(ctx, "rm -rf 0_PREVIOUS")
            await self.run(ctx, "mkdir 0_PREVIOUS")

        # Move everything to 0_PREVIOUS except bungee and build
        if min_phase <= 4:
            await self.display(ctx, "Moving everything except bungee, and build to 0_PREVIOUS...")
            for f in files:
                if f not in ["0_PREVIOUS", "build",] and not f.startswith("bungee"):
                    await self.run(ctx, "mv {} 0_PREVIOUS/".format(f))

        if min_phase <= 5:
            await self.display(ctx, "Getting new server config...")
            await self.run(ctx, f"mv /home/epic/5_SCRATCH/tmpreset/TEMPLATE/server_config {self._server_dir}/")

        if min_phase <= 6 and config.COMMON_WEEKLY_UPDATE_TASKS:
            await self.display(ctx, "Copying playerdata...")
            await self.run(ctx, f"mv {self._server_dir}/0_PREVIOUS/server_config/redis_data_final {self._server_dir}/server_config/redis_data_initial")

        if min_phase <= 7 and "purgatory" in self._shards:
            await self.display(ctx, "Copying purgatory...")
            await self.run(ctx, f"rm -rf {self._shards['purgatory']}")
            await self.run(ctx, f"mv /home/epic/5_SCRATCH/tmpreset/TEMPLATE/purgatory {self._shards['purgatory']}")

        if min_phase <= 9 and config.COMMON_WEEKLY_UPDATE_TASKS:
            await self.display(ctx, "Removing tutorial data")
            await self.run(ctx, os.path.join(_top_level, "rust/bin/redis_remove_data") + " redis://redis/ tutorial:* --confirm")

        if min_phase <= 10 and config.COMMON_WEEKLY_UPDATE_TASKS:
            await self.display(ctx, "Running score changes for players and moving them to spawn...")
            await self.run(ctx, os.path.join(_top_level, "rust/bin/weekly_update_player_scores") + f" {self._server_dir}/server_config/redis_data_initial")

        if min_phase <= 11 and config.COMMON_WEEKLY_UPDATE_TASKS:
            await self.display(ctx, "Running item replacements for players...")
            await self.run(ctx, os.path.join(_top_level, "utility_code/weekly_update_player_data.py") + f" --world {self._server_dir}/server_config/redis_data_initial --datapacks {self._server_dir}/server_config/data/datapacks -j {config.CPU_COUNT}")

            # TODO REMOVE THIS
            await self.display(ctx, "Stopping for manual player data fixes")
            return

        if min_phase <= 12 and config.COMMON_WEEKLY_UPDATE_TASKS:
            await self.display(ctx, "Loading player data back into redis...")
            await self.run(ctx, os.path.join(_top_level, "rust/bin/redis_playerdata_save_load") + f" redis://redis/ play --input {self._server_dir}/server_config/redis_data_initial 1")

        if min_phase <= 13 and config.COMMON_WEEKLY_UPDATE_TASKS:
            await self.display(ctx, "Loading market data back into redis")
            await self.run(ctx, os.path.join(_top_level, "utility_code/market_itemdb_import.py") + f" redis play {self._server_dir}/server_config/redis_data_initial")

        ########################################
        # Raffle

        if min_phase <= 14 and config.COMMON_WEEKLY_UPDATE_TASKS:
            await self.display(ctx, "Raffle results:")
            raffle_seed = self.get_raffle_seed()
            if self._rreact["msg_contents"] is not None:
                raffle_seed = self._rreact["msg_contents"]

            raffle_results = tempfile.mktemp()
            vote_raffle(raffle_seed, 'redis', raffle_results)
            await self.run(ctx, "cat {}".format(raffle_results), displayOutput=True)

        # Raffle
        ########################################

        if min_phase <= 15 and config.COMMON_WEEKLY_UPDATE_TASKS:
            await self.display(ctx, "Refreshing leaderboards")
            await self.run(ctx, os.path.join(_top_level, "rust/bin/leaderboard_update_redis") + " redis://redis/ play " + os.path.join(_top_level, "leaderboards.yaml"))

        if min_phase <= 16 and config.COMMON_WEEKLY_UPDATE_TASKS:
            await self.display(ctx, "Restarting rabbitmq")
            await self.restart(ctx, "rabbitmq", owner=message)

        if min_phase <= 17 and config.COMMON_WEEKLY_UPDATE_TASKS:
            await self.display(ctx, "Marking common tasks as complete")
            r.set('monumenta:automation:weekly_update_common_done', 'True')

        if min_phase <= 18:
            await self.display(ctx, "Waiting for common tasks to complete...")
            while True:
                common_done = r.get('monumenta:automation:weekly_update_common_done').decode("utf-8")
                if common_done == "True":
                    await self.display(ctx, "Detected common tasks are complete, proceeding with update")
                    break

                # Not done yet, wait a bit before polling
                await asyncio.sleep(5)

        if min_phase <= 19:
            await self.display(ctx, "Running actual weekly update (this will take a while!)...")
            await self.run(ctx, os.path.join(_top_level, f"utility_code/weekly_update.py --last_week_dir {self._server_dir}/0_PREVIOUS/ --output_dir {self._server_dir}/ --build_template_dir /home/epic/5_SCRATCH/tmpreset/TEMPLATE/ -j {config.CPU_COUNT} " + " ".join(self._shards)))

        if min_phase <= 20:
            await self.display(ctx, "Pruning scores from expired instances...")
            for shard in self._shards:
                if shard not in ["build",] and not shard.startswith("bungee") and not shard.startswith("velocity"):
                    await self.run(ctx, os.path.join(_top_level, f"utility_code/prune_scores.py -j {config.CPU_COUNT} {self._shards[shard]}"))

        if min_phase <= 21:
            for shard in self._shards:
                if shard not in ["build",] and not shard.startswith("bungee") and not shard.startswith("velocity"):
                    await self.run(ctx, f"cp -af /home/epic/4_SHARED/op-ban-sync/valley/banned-ips.json {self._shards[shard]}/")
                    await self.run(ctx, f"cp -af /home/epic/4_SHARED/op-ban-sync/valley/banned-players.json {self._shards[shard]}/")
                    await self.run(ctx, f"cp -af /home/epic/4_SHARED/op-ban-sync/valley/ops.json {self._shards[shard]}/")

                if os.path.isdir(f"{self._shards[shard]}/Project_Epic-valley"):
                    await self.run(ctx, f"mkdir -p {self._shards[shard]}/plugins")
                    await self.run(ctx, f"cp -af /home/epic/4_SHARED/op-ban-sync/valley/plugins/MonumentaWarps {self._shards[shard]}/plugins/MonumentaWarps")

                if os.path.isdir(f"{self._shards[shard]}/Project_Epic-isles"):
                    await self.run(ctx, f"mkdir -p {self._shards[shard]}/plugins")
                    await self.run(ctx, f"cp -af /home/epic/4_SHARED/op-ban-sync/isles/plugins/MonumentaWarps {self._shards[shard]}/plugins/MonumentaWarps")

                if os.path.isdir(f"{self._shards[shard]}/Project_Epic-ring"):
                    await self.run(ctx, f"mkdir -p {self._shards[shard]}/plugins")
                    await self.run(ctx, f"cp -af /home/epic/4_SHARED/op-ban-sync/ring/plugins/MonumentaWarps {self._shards[shard]}/plugins/MonumentaWarps")

                # Enable maintenance mode on all bungee shards
                # Maintenance mode should be enabled via ~stop at
                # if shard.startswith("bungee"):
                #   await self.run(ctx, ["perl", "-p", "-i", "-e", "s|enabled: *false|enabled: true|g", f"{self._shards[shard]}/plugins/BungeeDisplay/config.yml"])

        await self.cd(ctx, self._server_dir)
        if min_phase <= 22:
            await self.display(ctx, "Generating per-shard config...")
            await self.run(ctx, os.path.join(_top_level, "utility_code/gen_server_config.py --play " + " ".join(self._shards.keys())))

        if min_phase <= 23:
            await self.display(ctx, "Checking for broken symbolic links...")
            await self.run(ctx, f"find {self._server_dir} -xtype l", displayOutput=True)

        await self.cd(ctx, "/home/epic")
        if min_phase <= 24:
            # XXX NOTE
            # This logic is run the same on play/stage/volt/etc
            # This means that test weekly updates on stage/volt will overwrite real play server backups in 1_ARCHIVE if run on the same day
            # Because of this, 1_ARCHIVE is deliberately not mounted into stage/volt so as not to damage play server backups, while still actually testing that they run correctly
            await self.display(ctx, "Backing up post-update artifacts...")
            await self.cd(ctx, f"{self._server_dir}/..")
            folder_name = self._server_dir.strip("/").split("/")[-1]
            await self.run(ctx, ["tar", f"--exclude={folder_name}/0_PREVIOUS", "-I", "pigz --best", "-cf", f"/home/epic/1_ARCHIVE/{folder_name}_post_reset_{datestr()}.tgz", folder_name])

        if min_phase <= 25:
            await self.display(ctx, "Deleting 0_PREVIOUS...")
            await self.run(ctx, f"rm -rf {self._server_dir}/0_PREVIOUS")

        await self.display(ctx, f"Done at <t:{int(time.time())}:F>.")
        await self.display(ctx, message.author.mention)

    async def action_stage(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        ''' Stops all stage server shards
Copies the current play server over to the stage server.
Archives the previous stage server contents under 0_PREVIOUS '''

        # Just in case...
        if not config.STAGE_SOURCE:
            raise Exception("WARNING: bot doesn't have stage source, aborting")

        log_level = config.RABBITMQ.get("log_level", 20)
        play_broker = SocketManager("rabbitmq.play", "stagebot", callback=None, log_level=log_level)

        # Stop all shards belonging to this bot instance
        # This will fail if there's a lockout in place, so do this at the beginning
        shards = await self._k8s.list()
        await self.display(ctx, f"Stopping shards {', '.join([shard for shard in self._shards if shard in shards])}")
        await self.stop(ctx, [shard for shard in self._shards if shard in shards], owner=message)

        await self.display(ctx, "Removing previous 0_STAGE directories")
        await self.run(ctx, f"rm -rf {self._server_dir}/0_STAGE")
        await self.run(ctx, f"mkdir {self._server_dir}/0_STAGE")

        if config.COMMON_WEEKLY_UPDATE_TASKS:
            # Download the entire redis database from the play server
            # Do this early to give it plenty of time to start
            await self.display(ctx, f"Stopping {self._k8s.namespace} redis...")
            await self.stop(ctx, "redis", owner=message)
            await self.cd(ctx, f"{self._server_dir}/../redis")
            await self.run(ctx, f"mv -f dump.rdb dump.rdb.previous")
            await self.display(ctx, "Downloading current redis database from the play server...")
            await self.run(ctx, f"redis-cli -h redis.play --rdb dump.rdb")
            await self.start(ctx, "redis", owner=message)

        tasks = []
        port = 1111
        for server_name in config.STAGE_SOURCE:
            await self.display(ctx, f"Starting receive task on port {port}")
            task = asyncio.get_event_loop().create_task(self.stage_receive_data_task(ctx, port))
            tasks.append(task)
            port += 1

        await asyncio.sleep(15)

        port = 1111
        for server_name in config.STAGE_SOURCE:
            server_section = config.STAGE_SOURCE[server_name]
            stage_msg = {
                "shards": server_section["shards"],
                "address": f"{config.RABBITMQ['name']}.{config.K8S_NAMESPACE}",
                "port": port,
            }
            await self.display(ctx, f"Sending request to {server_section['queue_name']} with config {pformat(stage_msg)}")
            play_broker.send_packet(server_section["queue_name"], "Monumenta.Automation.stage", stage_msg)
            port += 1

        await self.display(ctx, "Finished launching copy tasks, waiting for them to complete. This will take a while...")
        for task in tasks:
            await task

        # Delete and re-create the 0_PREVIOUS directory
        await self.display(ctx, "Removing previous 0_PREVIOUS directories")
        for shard in self._shards:
            await self.run(ctx, f"rm -rf {self._server_dir}/0_PREVIOUS")
        for shard in self._shards:
            await self.run(ctx, f"mkdir -p {self._server_dir}/0_PREVIOUS")

        # Move the server_config directory to previous
        await self.run(ctx, f"mv {self._server_dir}/server_config {self._server_dir}/0_PREVIOUS/", ret=None, suppressStdErr=True)

        # Move the old shards themselves into previous
        await self.display(ctx, "Moving previous data to 0_PREVIOUS directories")
        tasks = []
        for shard in self._shards:
            tasks.append(asyncio.create_task(self.run(ctx, f"mv {self._shards[shard]} {self._server_dir}/0_PREVIOUS/", ret=None, suppressStdErr=True)))
        for task in tasks:
            await task

        # Move the newly sync'd shard data from 0_STAGE into where it's supposed to be, and remove 0_STAGE
        await self.display(ctx, f"Moving pulled {self._k8s.namespace} data into live folder")
        await self.run(ctx, ["bash", "-c", f"mv {self._server_dir}/0_STAGE/* {self._server_dir}"])
        await self.run(ctx, f"rmdir {self._server_dir}/0_STAGE")

        if config.COMMON_WEEKLY_UPDATE_TASKS:
            # Download the mysql database from the play server
            await self.display(ctx, "Syncing with current mysql database from the play server...")
            # Don't need to be in this directory exactly, but need to be in a stable directory
            await self.cd(ctx, f"{self._server_dir}")
            await self.run(ctx, [os.path.join(_top_level, f"utility_code/sync_mysql.sh"), self._k8s.namespace], displayOutput=True)

            # Note that this needs to be fairly long after starting redis to give it time to load
            await self.display(ctx, f"Truncating playerdata history...")
            await self.run(ctx, [os.path.join(_top_level, f"rust/bin/redis_truncate_playerdata"), 'redis://redis/', 'play', '1'], displayOutput=True)

        await self.display(ctx, "Disabling Plan and PremiumVanish...")
        await self.run(ctx, f"mv -f {self._server_dir}/server_config/plugins/Plan.jar {self._server_dir}/server_config/plugins/Plan.jar.disabled")
        await self.run(ctx, f"mv -f {self._server_dir}/server_config/plugins/PremiumVanish.jar {self._server_dir}/server_config/plugins/PremiumVanish.jar.disabled")

        await self.display(ctx, "Adjusting bungee config...")
        for shard_name, shard_path in self._shards.items():
            if not shard_name.startswith('bungee'):
                continue
            config_path = Path(shard_path) / 'config.yml'
            if not config_path.is_file():
                continue
            with open(config_path, "r") as f:
                bungeeconfig = yaml.load(f, Loader=yaml.FullLoader)
            bungeeconfig["servers"] = {
                "dummy": {
                    "address": "127.0.0.1:65500",
                    "motd": "THIS SERVER DOES NOT EXIST",
                    "restricted": False,
                },
                "isles": {
                    "address": "isles:25566",
                    "motd": "isles",
                    "restricted": False,
                },
                "plots": {
                    "address": "plots:25566",
                    "motd": "plots",
                    "restricted": False,
                },
                "purgatory": {
                    "address": "purgatory:25566",
                    "motd": "purgatory",
                    "restricted": False,
                },
                "ring": {
                    "address": "ring:25566",
                    "motd": "ring",
                    "restricted": False,
                },
                "valley": {
                    "address": "valley:25566",
                    "motd": "valley",
                    "restricted": False,
                },
            }
            bungeeconfig["listeners"][0]["priorities"] = [
                "plots",
                "ring",
                "isles",
                "valley",
                "purgatory",
            ]
            with open(config_path, "w") as f:
                yaml.dump(bungeeconfig, f, width=2147483647, allow_unicode=True)

        await self.display(ctx, f"{self._k8s.namespace} server loaded with current play server data")
        await self.display(ctx, message.author.mention)

    async def stage_receive_data_task(self, ctx: discord.ext.commands.Context, port):
        """Receive stage data over a socket"""
        await self.cd(ctx, f"{self._server_dir}/0_STAGE")
        await self.run(ctx, ["bash", "-c", f"nc -dl {port} | lz4 -d | tar xf -"])
        await self.display(ctx, f"Completed receiving stage data on port {port}")

    async def stage_data_request(self, ctx: discord.ext.commands.Context, message):
        """Send stage data over a socket"""
        shards_str = " ".join(message["shards"])
        await self.display(ctx, f"Got stage request for shards:\n> {shards_str}")
        await self.cd(ctx, f"{self._server_dir}")
        await self.run(ctx, ["bash", "-c", f"tar cf - {shards_str} | lz4 | nc -N {message['address']} {message['port']}"])
        await self.display(ctx, "Completed sending stage data")

    async def action_update_items(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''
Updates one or more items in all loot tables

Usage:
    {cmdPrefix}update item /setblock 1217 3 2720 minecraft:chest{Items:[...]}
    Or if too long for a discord message:
    {cmdPrefix}update item
    <.txt file attachment starting with /setblock ...>

Easiest way to get this is putting an item in a chest, and looking at that chest and pressing f3+i
    '''

        commandArgs = message.content[len(config.PREFIX):].strip()
        temppath = tempfile.mktemp()
        if message.attachments:
            # Save first attachment as text file at the temppath
            attachment = message.attachments[0]
            attachment_url_parsed = urlparse(attachment.url)
            if not attachment_url_parsed.path.endswith(".txt"):
                await self.display(ctx, f"setblock chest argument must be a .txt file, got {attachment_url_parsed.path}")
                return

            await attachment.save(temppath)
        else:
            # Save any text arguments to the text file at the temppath
            if len(commandArgs) < len(cmd) + 5:
                await self.display(ctx, "setblock chest argument required")
                return
            if '{' not in commandArgs:
                await self.display(ctx, "Arguments should be of the form /setblock ~ ~ ~ minecraft:chest{Items:[...]}")
                return
            with open(temppath, "w") as fp:
                fp.write(commandArgs)

        userfoldername = re.sub('[^a-z0-9]', '', message.author.name.lower()) + str(message.id)
        userfolderpath = os.path.join("/tmp", userfoldername)
        await self.run(ctx, ["mkdir", userfolderpath])
        await self.run(ctx, [os.path.join(_top_level, f"utility_code/bulk_update_loottables.py"), "--output-dir", userfolderpath, temppath], displayOutput=True)
        files = [f for f in os.listdir(userfolderpath) if os.path.isfile(os.path.join(userfolderpath, f))]
        if len(files) > 0:
            await self.cd(ctx, "/tmp")
            for fname in files:
                await ctx.send(fname, file=discord.File(os.path.join(userfolderpath, fname)))
            if len(files) > 1:
                await self.run(ctx, f"zip -r {userfoldername}.zip {userfoldername}")
                await ctx.send("Zip file containing all loot tables generated by this run:", file=discord.File(os.path.join("/tmp", f"{userfoldername}.zip")))

        await self.display(ctx, message.author.mention)

    async def action_run_replacements(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Runs item and mob replacements on a given shard
Syntax:
`{cmdPrefix}run replacements shard valley isles orange`'''

        commandArgs = message.content[len(config.PREFIX + cmd)+1:].split()

        replace_shards = []
        for shard in self._shards:
            if shard in commandArgs:
                replace_shards.append(shard)

        do_prune = False
        if "--prune" in commandArgs:
            do_prune = True

        for token in commandArgs:
            if token in ["structures", "schematics"]:
                replace_shards.append("structures")

        if not replace_shards:
            await self.display(ctx, "Nothing to do")
            return

        await self.run_replacements_internal(ctx, replace_shards, mention=message.author.mention, do_prune=do_prune, owner=message)

    async def run_replacements_internal(self, ctx: discord.ext.commands.Context, replace_shards, mention=None, do_prune=False, owner=None):
        """Run replacements on the given shards"""
        await self.display(ctx, f"Replacing both mobs AND items on [{' '.join(replace_shards)}]")

        for shard in replace_shards:
            if shard == "structures":
                base_backup_name = f"/home/epic/0_OLD_BACKUPS/0_AUTOMATED_REPLACEMENTS/structures_pre_entity_loot_updates_{datestr()}"

                await self.display(ctx, "Running replacements on structures")
                await self.cd(ctx, "/home/epic/project_epic/server_config/data")
                await self.run(ctx, ["tar", "-I", "pigz --best", "-cf", f"{base_backup_name}.tgz", "structures"])
                await self.cd(ctx, "/home/epic/project_epic/server_config/data")
                await self.run(ctx, os.path.join(_top_level, f"utility_code/replace_items.py --schematics structures --structures generated"), displayOutput=True)
                await self.cd(ctx, "/home/epic/project_epic/server_config/data")
                await self.run(ctx, os.path.join(_top_level, f"utility_code/replace_mobs.py --schematics structures --structures generated --library-of-souls /home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json --logfile {base_backup_name}_mobs.yml"), displayOutput=True)

            else:
                base_backup_name = f"/home/epic/0_OLD_BACKUPS/0_AUTOMATED_REPLACEMENTS/{shard}_pre_entity_loot_updates_{datestr()}"

                if do_prune:
                    await self.display(ctx, f"Running replacements and pruning world regions on shard {shard}")
                else:
                    await self.display(ctx, f"Running replacements on shard {shard}")
                await self.stop(ctx, shard, owner=owner)
                await self.cd(ctx, os.path.dirname(self._shards[shard].rstrip('/'))) # One level up
                await self.run(ctx, ["tar", f"--exclude={shard}/logs", f"--exclude={shard}/plugins", f"--exclude={shard}/cache", "-I", "pigz --best", "-cf", f"{base_backup_name}.tgz", shard])
                if do_prune:
                    await self.cd(ctx, os.path.dirname(self._shards[shard].rstrip('/'))) # One level up
                    await self.run(ctx, os.path.join(_top_level, f"utility_code/prune_empty_regions.py {shard}"))
                    await self.cd(ctx, os.path.dirname(self._shards[shard].rstrip('/'))) # One level up - change again in case something else changed bot's directory
                    await self.run(ctx, os.path.join(_top_level, f"utility_code/defragment.py {shard}"))
                await self.cd(ctx, os.path.dirname(self._shards[shard].rstrip('/'))) # One level up
                await self.run(ctx, os.path.join(_top_level, f"utility_code/replace_items.py --worlds {shard}"), displayOutput=True)
                await self.cd(ctx, os.path.dirname(self._shards[shard].rstrip('/'))) # One level up
                await self.run(ctx, os.path.join(_top_level, f"utility_code/replace_mobs.py --worlds {shard} --library-of-souls /home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json --logfile {base_backup_name}_mobs.yml"), displayOutput=True)
                await self.start(ctx, shard, owner=owner)

        if mention is not None:
            await self.display(ctx, mention)

    async def action_find_loot_problems(self, ctx: discord.ext.commands.Context, _, __: discord.Message):
        '''Finds loot table problems
- Lists containers in dungeons that are missing loot tables.
- TODO: Add more!
'''
        await self.display(ctx, "Checking for loot table problems...")
        await self.display(ctx, "Checking for missing dungeon loot tables...")
        await self.run(ctx, os.path.join(_top_level, "utility_code/dungeon_find_lootless.py"), 0, displayOutput=True)

    async def action_get_commands(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Scans all command blocks in one or more worlds and returns a JSON file with their information
Syntax:
`{cmdPrefix}get commands valley isles orange ...`'''

        commandArgs = message.content[len(config.PREFIX + cmd)+1:].split()

        scan_shards = []
        for shard in self._shards:
            if shard in commandArgs:
                scan_shards.append(shard)

        if not scan_shards:
            await self.display(ctx, "Nothing to do")
            return

        await self.display(ctx, f"Getting command blocks on [{' '.join(scan_shards)}]")

        for shard in scan_shards:

            await self.display(ctx, "Scanning for command blocks on shard {}".format(shard))
            scan_results = tempfile.mktemp()
            await self.cd(ctx, self._shards[shard])
            await self.run(ctx, os.path.join(_top_level, f"utility_code/command_block_update_tool.py --output {scan_results} Project_Epic-{shard} "), displayOutput=True)
            await self.run(ctx, f"mv -f {scan_results} /tmp/{shard}.json")
            await ctx.send(f"{shard} commands:", file=discord.File(f'/tmp/{shard}.json'))

        await self.display(ctx, message.author.mention)

    async def action_list_world_loot(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Lists all loot tables and items in a world, with optional coordinates
Syntax:
{cmdPrefix}list world loot dungeon
{cmdPrefix}list world loot dungeon 512 0 0 1023 255 511'''

        commandArgs = message.content[len(config.PREFIX + cmd)+1:].split()

        if len(commandArgs) == 0:
            await self.help_internal(ctx, ["list world loot"], message.author)
            return

        shard = commandArgs[0]
        if shard not in commandArgs:
            await self.display(ctx, f"The shard {shard} is not known by this bot.")
            return

        await self.display(ctx, f"Looking for loot...")

        await self.run(ctx, os.path.join(_top_level, f"utility_code/list_world_loot.py {self._shards[shard]}/Project_Epic-{shard}" + "".join([" " + x for x in commandArgs[1:]])), displayOutput=True)

        await self.display(ctx, message.author.mention)

    async def action_gen_demo_release(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Generates a demo release zip with the specified version
Syntax:
`{cmdPrefix}generate demo release <version>`'''

        commandArgs = message.content[len(config.PREFIX + cmd)+1:]
        version = "".join([i if re.match(r'[0-9\.]', i) else '' for i in commandArgs])

        if not version:
            await self.display(ctx, "Version must be specified and can contain only numbers and periods")
            await self.display(ctx, message.author.mention)
            return

        # Test if this version already exists
        try:
            await self.run(ctx, ["test", "!", "-f", "/home/epic/4_SHARED/monumenta_demo/Monumenta Demo - The Halls of Wind and Blood V{}.zip".format(version)])
        except Exception:
            await self.display(ctx, "Demo release V{} already exists!".format(version))
            return

        await self.display(ctx, "Generating demo release version V{}...".format(version))

        await self.stop(ctx, "white-demo", owner=message)

        # Clean up the working directory for testing/etc
        await self.cd(ctx, "/home/epic/project_epic/Monumenta Demo - The Halls of Wind and Blood")
        await self.run(ctx, "rm -rf banned-ips.json banned-players.json command_registration.json whitelist.json usercache.json version_history.json cache logs plugins/ChestSort/playerdata Monumenta-White-Demo/advancements Monumenta-White-Demo/playerdata Monumenta-White-Demo/stats Monumenta-White-Demo/DIM-1 Monumenta-White-Demo/DIM1 Monumenta-White-Demo/data")

        # Make a copy of the demo
        await self.run(ctx, "rm -rf /home/epic/5_SCRATCH/tmpdemo")
        await self.run(ctx, "mkdir -p /home/epic/5_SCRATCH/tmpdemo")
        await self.cd(ctx, "/home/epic/5_SCRATCH/tmpdemo")
        await self.run(ctx, ["cp", "-a", "/home/epic/project_epic/Monumenta Demo - The Halls of Wind and Blood", "."])

        # Turn off the whitelist, set it to normal mode, and delete the ops file
        await self.cd(ctx, "Monumenta Demo - The Halls of Wind and Blood")
        await self.run(ctx, "perl -p -i -e s|^enforce-whitelist.*$|enforce-whitelist=false|g server.properties")
        await self.run(ctx, "perl -p -i -e s|^white-list.*$|white-list=false|g server.properties")
        await self.run(ctx, "perl -p -i -e s|^difficulty.*$|difficulty=2|g server.properties")
        await self.run(ctx, "rm -f ops.json")

        # Package up the release
        await self.cd(ctx, "/home/epic/5_SCRATCH/tmpdemo")
        await self.run(ctx, ["zip", "-rq", "/home/epic/4_SHARED/monumenta_demo/Monumenta Demo - The Halls of Wind and Blood V{}.zip".format(version), "Monumenta Demo - The Halls of Wind and Blood"])
        await self.run(ctx, ["rm", "-rf", "Monumenta Demo - The Halls of Wind and Blood"])

        await self.start(ctx, "white-demo", owner=message)

        await self.display(ctx, "Demo release version V{} generated successfully".format(version))
        await self.display(ctx, message.author.mention)

    async def action_broadcastcommand(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Sends a command to all shards and bungeecord instances
Syntax:
`{cmdPrefix}broadcastcommand <command>`'''
        commandArgs = message.content[len(config.PREFIX + cmd)+1:].strip()
        if commandArgs.startswith("/"):
            commandArgs = commandArgs[1:]

        await self.display(ctx, "Broadcasting command {!r} to all servers".format(commandArgs))
        self._socket.send_packet("*", "monumentanetworkrelay.command", {"command": commandArgs})

    async def action_broadcastbungeecommand(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Sends a command to all bungeecord instances
Syntax:
`{cmdPrefix}broadcastbungeecommand <command>`'''
        commandArgs = message.content[len(config.PREFIX + cmd)+1:].strip()
        if commandArgs.startswith("/"):
            commandArgs = commandArgs[1:]

        await self.display(ctx, "Broadcasting command {!r} to all bungee servers".format(commandArgs))
        self._socket.send_packet("*", "monumentanetworkrelay.command", {"server_type": "bungee", "command": commandArgs})

    async def action_broadcastminecraftcommand(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Sends a command to all minecraft instances
Syntax:
`{cmdPrefix}broadcastminecraftcommand <command>`'''
        commandArgs = message.content[len(config.PREFIX + cmd)+1:].strip()
        if commandArgs.startswith("/"):
            commandArgs = commandArgs[1:]

        await self.display(ctx, "Broadcasting command {!r} to all minecraft servers".format(commandArgs))
        self._socket.send_packet("*", "monumentanetworkrelay.command", {"server_type": "minecraft", "command": commandArgs})

    async def action_broadcastproxycommand(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Sends a command to all proxy instances
Syntax:
`{cmdPrefix}broadcastproxycommand <command>`'''
        commandArgs = message.content[len(config.PREFIX + cmd)+1:].strip()
        if commandArgs.startswith("/"):
            commandArgs = commandArgs[1:]

        await self.display(ctx, "Broadcasting command {!r} to all proxy servers".format(commandArgs))
        self._socket.send_packet("*", "monumentanetworkrelay.command", {"server_type": "proxy", "command": commandArgs})


    async def action_update_avatar(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        """Updates the avatar of the bot.
Usage:
{cmdPrefix}update avatar /home/epic/4_SHARED/bot_avatars/example.png
"""

        avatar_path_str = message.content[len(config.PREFIX + cmd) + 1:]
        avatar_path = Path(avatar_path_str)
        await self.display(ctx, f"Attempting to set avatar `{avatar_path_str}`")
        if not avatar_path.is_file():
            await self.display(ctx, "File not found.")
            test_path = avatar_path.parent
            limit = 5
            while test_path != test_path.parent:
                limit -= 1
                if limit < 0:
                    break
                if not test_path.is_dir():
                    await self.display(ctx, f"- Could not find folder `{test_path!s}`")
                    test_path = test_path.parent
                    continue
                break
            if limit < 0:
                await self.display(ctx, f"Refusing to search any higher up.")
                return
            await self.display(ctx, f"Did find `{test_path}` at least, which contains:")
            await self.display_verbatim(ctx, f'{[item.name for item in test_path.iterdir()]}')

            return
        if not avatar_path_str.endswith('.png') and not avatar_path_str.endswith('.jpg'):
            await self.display(ctx, "Only png and jpg files are supported.")
            return

        try:
            await self._internal_update_avatar(avatar_path)
            await self.display(ctx, "Success")
        except Exception as ex:
            await self.display(ctx, str(ex))
            await self.display_verbatim(ctx, traceback.format_exc())

    async def check_updated_avatar(self):
        """Checks if avatar.png and last_set_avatar.png differ, and if so, use avatar.png"""
        previous_path = self._persistence_path / 'last_set_avatar.png'
        current_path = self._persistence_path / 'avatar.png'

        if not current_path.is_file():
            return

        if (
                not previous_path.is_file()
                or current_path.stat().st_size != previous_path.stat().st_size
        ):
            try:
                await self._internal_update_avatar(current_path)
            except Exception:
                pass
            return

        if current_path.read_bytes() != previous_path.read_bytes():
            try:
                await self._internal_update_avatar(current_path)
            except Exception:
                pass

    async def _internal_update_avatar(self, avatar_path: Path):
        """Internal code to update the bot's avatar, raising an exception on failure"""

        PNG_HEADER = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
        JPG_HEADER = b'\xff\xd8\xff'

        if not avatar_path.is_file():
            raise Exception(f'Could not find {avatar_path}')

        try:
            file_contents = avatar_path.read_bytes()
        except Exception:
            raise Exception(f'Could not read {avatar_path}')

        if not file_contents.startswith(PNG_HEADER) and not file_contents.startswith(JPG_HEADER):
            raise Exception(f'Avatar file must be a real png or jpg file: {avatar_path}')

        user = self._bot.user
        if user is None:
            raise Exception(f'Bot has no user object; is it not signed in?')

        try:
            await user.edit(avatar=file_contents)
        except Exception:
            raise Exception(f'Failed to change avatar; check https://discordpy.readthedocs.io/en/stable/api.html#discord.ClientUser.edit')

        try:
            # Set current and previous bot image files
            previous_path = self._persistence_path / 'last_set_avatar.png'
            previous_path.write_bytes(file_contents)
            current_path = self._persistence_path / 'avatar.png'
            current_path.write_bytes(file_contents)
        except Exception:
            # Any errors in this block are non-critical
            pass

    @staticmethod
    def preprocess_time_description(time_description):
        """Allows for more natuarl date descriptions for the date command"""
        for ignored_prefix in (
                'in ',
                'after ',
                'at ',
        ):
            if time_description.startswith(ignored_prefix):
                time_description = time_description[len(ignored_prefix):]

        for ignored_suffix in (
                ' later',
        ):
            if time_description.endswith(ignored_suffix):
                time_description = time_description[:-len(ignored_suffix)]

        return time_description

    async def time_from_description(self, ctx: discord.ext.commands.Context, time_description):
        '''Gets a DateTime from a time description'''
        time_description = self.preprocess_time_description(time_description)
        unix_timestamp = int(await self.run(ctx, ["date", "-u", "--date", time_description, "+%s"]))
        tz = timezone.utc
        return datetime.fromtimestamp(unix_timestamp, tz)

    @staticmethod
    def get_discord_timestamp(datetime_, fmt=":f"):
        '''Get a Discord timestamp code

Available formats are:
""   - Default              - "June 24, 2021 3:49 AM"
":t" - Short time           - "3:49 AM"
":T" - Long Time            - "3:49:19 AM"
":d" - Short date           - "06/24/2021"
":D" - Long Date            - "June 24, 2021"
":f" - Short full (default) - "June 24, 2021 3:49 AM"
":F" - Long Full            - "Thursday, June 24, 2021 3:49 AM"
":R" - Relative             - "2 years ago", "in 5 seconds"

The argument datetime may be a datetime object or a Unix timestamp in seconds (int or float)
'''
        unix_timestamp = datetime_
        if isinstance(datetime_, datetime):
            unix_timestamp = datetime_.timestamp()
        return f"<t:{int(unix_timestamp)}{fmt}>"

    async def action_get_timestamp(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Converts a human readable time to a Discord timestamp

The input format is very flexible, using the Linux date command set to UTC. For instance:
"5 minutes" - 5 minutes from now
"yesterday" - midnight yesterday, UTC
"10:35 PM EST"
"5:00 PM Friday" - when a new week begins (for dungeons etc, as of March 3rd, 2023)
"8:00 PM Thursday +2 weeks" - 3 weekly updates from now

And the first message on the developer server is:
"5:15 PM May 28 2016 EDT", "May 28 5:15 PM EDT 2016", or a number of variations on this
'''

        time_description = message.content[len(config.PREFIX + cmd) + 1:].strip()
        time_description = self.preprocess_time_description(time_description)

        if len(time_description) == 0:
            await self.help_internal(ctx, ["get timestamp"], message.author)
            return

        selected_time = await self.time_from_description(ctx, time_description)

        def get_output_line(timestamp, fmt):
            '''Internal method to show timestamp code and its result'''
            code = self.get_discord_timestamp(timestamp, fmt)
            return f'\n`{code}`: {code}'

        output_message = f"**{time_description}:**"
        output_message += get_output_line(selected_time, "")
        for fmt_char in 'tTdDfFR':
            output_message += get_output_line(selected_time, f":{fmt_char}")

        await self.display(ctx, output_message)

    RE_REMINDER_ARGS = re.compile(r'(me|@[a-z0-9_.]{2,32}|@.{3,32}#[0-9]{4}|\<@\d{1,32}\>|`@[a-z0-9_.]{2,32}`|`@.{3,32}#[0-9]{4}`|`\<@\d{1,32}\>`)\s\"((?:[^\\\"]+|\\.)+)\"\s(.*)')

    async def action_remind(self, ctx: discord.ext.commands.Context, cmd, message: discord.Message):
        '''Sets a reminder

Examples:
~remind me "in 3 seconds" Do the stuff!
~remind @NickNackGus#2442 "5 PM tomorrow EST" Play the thing!
~remind `@NickNackGus#2442` "8:20 PM EST" Delayed surprise ping!

See `~help get timestamp` for valid time formats
'''

        if cmd.endswith(' me'):
            cmd = cmd[:-3]

        arg_string = message.content[len(config.PREFIX + cmd) + 1:].strip()
        args_match = self.RE_REMINDER_ARGS.fullmatch(arg_string)
        if not args_match:
            await self.help_internal(ctx, ["remind"], message.author)
            return

        mention = args_match[1]
        escaped_time_description = args_match[2]
        reminder = args_match[3]

        if mention.startswith('`') and mention.endswith('`'):
            mention = mention[1:-1]
        if mention == "me":
            mention = message.author.mention

        target_member = None
        if mention.startswith('@'):
            has_discriminator = '#' in mention
            for member in message.channel.members:
                if has_discriminator:
                    member_mention = f"@{member.name}#{member.discriminator}"
                else:
                    member_mention = f"@{member.name}"
                if member_mention == mention:
                    mention = f"<@{member.id}>"
                    target_member = member
                    break
        else:
            for member in message.channel.members:
                if mention == f"<@{member.id}>":
                    target_member = member
                    break

        if target_member is None:
            await self.display(ctx, f"`{mention}` won't ping anyone in this channel.")
            return

        time_description = decode_escapes(escaped_time_description)

        selected_time = await self.time_from_description(ctx, time_description)
        discord_timestamp = self.get_discord_timestamp(selected_time, ":R")

        await self.display(ctx, f"Ok, {discord_timestamp} I'll send `@{target_member.name}#{target_member.discriminator}` this message:")
        await self.display(ctx, f"```md\n{reminder}\n```")

        remaining_seconds = (selected_time - datetime.now(timezone.utc)) / timedelta(seconds=1)
        if remaining_seconds > 0:
            await asyncio.sleep(remaining_seconds)

        await self.display(ctx, f'{reminder}\n{mention}')
