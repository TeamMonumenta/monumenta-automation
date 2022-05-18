# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import subprocess
import re
import tempfile
import time
import datetime
from pprint import pformat
import logging
import redis
import discord
import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# TODO: Move this to config file
_file_depth = 3
_file = os.path.abspath(__file__)
_top_level = os.path.abspath(os.path.join(_file, '../'*_file_depth))

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../utility_code"))
from lib_py3.raffle import vote_raffle
from lib_py3.lib_k8s import KubernetesManager
from lib_py3.lib_sockets import SocketManager
from lib_py3.redis_scoreboard import RedisRBoard

from automation_bot_lib import datestr, split_string

class Listening():
    def __init__(self):
        self._set = set()

    def isListening(self, key):
        logger.debug(f"Listening _set: {pformat(self._set)}")
        logger.debug(f"Listening key: {pformat(key)}")
        if not isinstance(key, tuple):
            key = (key.channel.id, key.author.id)
        return key not in self._set

    def select(self, key):
        if not isinstance(key, tuple):
            key = (key.channel.id, key.author.id)
        self._set.remove(key)

    def deselect(self, key):
        if not isinstance(key, tuple):
            key = (key.channel.id, key.author.id)
        self._set.add(key)

    def set(self, key, value):
        if value:
            self.select(key)
        else:
            self.deselect(key)

    def toggle(self, key):
        if not isinstance(key, tuple):
            key = (key.channel.id, key.author.id)
        if self.isListening(key):
            self.deselect(key)
        else:
            self.select(key)

# pylint: disable=unused-argument
class AutomationBotInstance():

    ################################################################################
    # Entry points

    def __init__(self, client, channel, config, rreact):
        self._client = client
        self._channel = channel
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

            "verbose": self.action_verbose,
            "test": self.action_test,
            "testpriv": self.action_test_priv,
            "testunpriv": self.action_test_unpriv,

            "list shards": self.action_list_shards,
            "instances": self.action_list_instances,
            "start": self.action_start,
            "stop": self.action_stop,
            "restart": self.action_restart,

            "view scores": self.action_view_scores,
            "get score": self.action_get_player_scores,
            "set score": self.action_set_player_scores,

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
            "stop in 10 minutes": self.action_stop_in_10_minutes,
            "stop and backup": self.action_stop_and_backup,
            "weekly update": self.action_weekly_update,
            "get raffle seed": self.action_get_raffle_seed,
            "run test raffle": self.action_run_test_raffle,

            "stage": self.action_stage,
            "generate demo release": self.action_gen_demo_release,
        }

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
            "willows": "DB1Access",
            "corridors": "DRAccess",
            "verdant": "DVAccess",
            "reverie": "DCAccess",
            "tutorial": "DTAccess",
            "sanctum": "DFSAccess",
            "shiftingcity": "DRL2Access",
            "teal": "DTLAccess",
            "forum": "DFFAccess",
            "rush": "DRDAccess",
            "mist": "DBMAccess",
            "depths": "DDAccess",
            "remorse": "DSRAccess",
        }

        try:
            self._name = config["name"]
            self._shards = config["shards"]
            self._stage_source = None
            self._server_dir = config["server_dir"]
            if "stage_source" in config:
                self._stage_source = config["stage_source"]

            self._prefix = config["prefix"]
            self._common_weekly_update_tasks = config.get("common_weekly_update_tasks", True)

            if "rabbitmq" in config:
                # Since each bot can have multiple channel facets (i.e. an object of this class for each channel),
                # want to only connect to rabbitmq if this channel should actually do so, and with what parameters
                if self._channel.id in config["rabbitmq"]:
                    conf = config["rabbitmq"][self._channel.id]

                    try:
                        # Get the event loop on the main thread
                        loop = asyncio.get_event_loop()

                        def socket_callback(message):
                            if "channel" in message:
                                if "Heartbeat" in message["channel"]:
                                    return

                                logger.info("Got socket message: {}".format(pformat(message)))
                                if self._audit_channel:
                                    if message["channel"] == "Monumenta.Automation.AuditLog":
                                        # Schedule the display coroutine back on the main event loop
                                        asyncio.run_coroutine_threadsafe(self.display_verbatim(message["data"]["message"],
                                                                                               channel=self._audit_channel),
                                                                         loop)

                                if self._admin_channel:
                                    if message["channel"] == "Monumenta.Automation.AdminNotification":
                                        asyncio.run_coroutine_threadsafe(self.display_verbatim(message["data"]["message"],
                                                                                               channel=self._admin_channel),
                                                                         loop)
                                if self._audit_severe_channel:
                                    if message["channel"] == "Monumenta.Automation.AuditLogSevere":
                                        # Schedule the display coroutine back on the main event loop
                                        asyncio.run_coroutine_threadsafe(self.display_verbatim(message["data"]["message"],
                                                                                               channel=self._audit_severe_channel),
                                                                         loop)
                                if message["channel"] == "Monumenta.Automation.stage":
                                    # Schedule the display coroutine back on the main event loop
                                    asyncio.run_coroutine_threadsafe(self.stage_data_request(message["data"]), loop)

                        if "log_level" in conf:
                            log_level = conf["log_level"]
                        else:
                            log_level = 20

                        self._socket = SocketManager(conf["host"], conf["name"], durable=conf["durable"], callback=(socket_callback if conf["process_messages"] else None), log_level=log_level)

                        # Add commands that require the sockets here!
                        self._commands["broadcastcommand"] = self.action_broadcastcommand

                        self._audit_channel = None
                        if "audit_channel" in conf:
                            try:
                                self._audit_channel = client.get_channel(conf["audit_channel"])
                            except Exception:
                                logging.error("Cannot connect to audit channel: " + conf["audit_channel"])
                        self._audit_severe_channel = None
                        if "audit_severe_channel" in conf:
                            try:
                                self._audit_severe_channel = client.get_channel(conf["audit_severe_channel"])
                            except Exception:
                                logging.error("Cannot connect to audit severe channel: " + conf["audit_severe_channel"])
                        self._admin_channel = None
                        if "admin_channel" in conf:
                            try:
                                self._admin_channel = client.get_channel(conf["admin_channel"])
                            except Exception:
                                logging.error("Cannot connect to admin channel: " + conf["admin_channel"])
                    except Exception as e:
                        logger.warn('Failed to connect to rabbitmq: {}'.format(e))

            # Remove any commands that aren't available in the config
            for command in dict(self._commands):
                if command not in config["commands"]:
                    self._commands.pop(command)

            for command in config["commands"]:
                if command not in self._commands:
                    logger.warn("Command {!r} specified in config but does not exist".format(command))

            self._permissions = config["permissions"]
            self._debug = False
            self._listening = Listening()
            self._k8s = KubernetesManager(config["k8s_namespace"])
        except KeyError as e:
            sys.exit('Config missing key: {}'.format(e))

    async def handle_message(self, message):

        msg = message.content

        if not msg.strip().startswith(self._prefix):
            return

        match = None
        for command in self._commands:
            if msg[1:].startswith(command):
                match = command
        if match is None:
            return

        if (match not in self._always_listening_commands) and not self._listening.isListening(message):
            return

        if self.check_permissions(match, message.author):
            await self._commands[match](match, message)
        else:
            await message.channel.send("Sorry " + message.author.mention + ", you do not have permission to run this command")

    # Entry points
    ################################################################################

    ################################################################################
    # Infrastructure

    def check_permissions(self, command, author):
        logger.debug("author.id = {}".format(author.id))
        user_info = self._permissions["users"].get(author.id, {"rights":["@everyone"]})
        logger.debug("User info = {}".format(pformat(user_info)))
        # This is a copy, not a reference
        user_rights = list(user_info.get("rights", ["@everyone"]))
        for role in author.roles:
            permGroupName = self._permissions["groups_by_role"].get(role.id, None)
            if permGroupName is not None:
                user_rights = [permGroupName] + user_rights

        return self.check_permissions_explicitly(command, user_rights)

    # Unlike check_permissions, this does not get assigned to an object.
    # It checks exactly that the user_rights provided can run the command.
    def check_permissions_explicitly(self, command, user_rights):
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

    async def display_verbatim(self, text, channel=None):
        if channel is None:
            channel = self._channel

        for chunk in split_string(text):
            await channel.send("```" + chunk + "```")

    async def debug(self, text):
        logger.debug(text)
        if self._debug:
            await self._channel.send(text)

    async def cd(self, path):
        await self.debug("Changing path to `" + path + "`")
        os.chdir(path)

    async def display(self, msg):
        for chunk in split_string(msg):
            await self._channel.send(chunk)

    async def run(self, cmd, ret=0, displayOutput=False):
        if not isinstance(cmd, list):
            # For simple stuff, splitting on spaces is enough
            splitCmd = cmd.split(' ')
        else:
            # For complicated stuff, the caller must split appropriately
            splitCmd = cmd
        await self.debug("Executing: ```" + str(splitCmd) + "```")
        async with self._channel.typing():
            process = await asyncio.create_subprocess_exec(*splitCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await process.communicate()
            rc = process.returncode

            await self.debug("Result: {}".format(rc))

            stdout = stdout.decode('utf-8')
            if stdout:
                await self.debug("stdout from command {!r}:".format(cmd))
                logger.debug(stdout)

                if self._debug or displayOutput:
                    await self.display_verbatim(stdout)

            stderr = stderr.decode('utf-8')
            if stderr:
                await self._channel.send("stderr from command {!r}:".format(cmd))
                await self.display_verbatim(stderr)

            if isinstance(ret, int) and rc != ret:
                raise ValueError(f"Expected result {ret}, got result {rc} while processing {cmd!r}")

            if isinstance(ret, (list, tuple, set)) and rc not in ret:
                raise ValueError(f"Expected result in {ret}, got result {rc} while processing {cmd!r}")

        return stdout

    async def stop(self, shards):
        if not isinstance(shards, list):
            shards = [shards,]
        async with self._channel.typing():
            await self.debug("Stopping shards [{}]...".format(",".join(shards)))
            await self._k8s.stop(shards)
            await self.debug("Stopped shards [{}]".format(",".join(shards)))

    async def start(self, shards):
        if not isinstance(shards, list):
            shards = [shards,]
        async with self._channel.typing():
            await self.debug("Starting shards [{}]...".format(",".join(shards)))
            await self._k8s.start(shards)
            await self.debug("Started shards [{}]".format(",".join(shards)))

    async def restart(self, shards):
        if not isinstance(shards, list):
            shards = [shards,]
        async with self._channel.typing():
            await self.debug("Restarting shards [{}]...".format(",".join(shards)))
            await self._k8s.restart(shards)
            await self.debug("Restarted shards [{}]".format(",".join(shards)))

    # Infrastructure
    ################################################################################

    ################################################################################
    # Always listening actions

    async def action_help(self, cmd, message):
        '''Lists commands available with this bot'''

        commandArgs = message.content[len(self._prefix + cmd) + 1:].split()
        # any -v style arguments should go here
        target_command = " ".join(commandArgs)
        if len(commandArgs) == 0:
            helptext = '''__Available Actions__'''
            for command in self._commands:
                if self.check_permissions(command, message.author):
                    helptext += "\n**" + self._prefix + command + "**"
                else:
                    helptext += "\n~~" + self._prefix + command + "~~"
            helptext += "\nRun `~help <command>` for more info."
        else:
            helptext = None
            for command in self._commands:
                if not (command == target_command or self._prefix + command == target_command):
                    continue

                helptext = '''__Help on:__'''
                if self.check_permissions(command, message.author):
                    helptext += "\n**" + self._prefix + command + "**"
                else:
                    helptext += "\n~~" + self._prefix + command + "~~"
                helptext += "```" + self._commands[command].__doc__.replace('{cmdPrefix}', self._prefix) + "```"

            if helptext is None:
                helptext = '''Command {!r} does not exist!'''.format(target_command)

        await message.channel.send(helptext)

    async def action_list_bots(self, cmd, message):
        '''Lists currently running bots'''
        await message.channel.send('`' + self._name + '`')

    async def action_select_bot(self, cmd, message):
        '''Make specified bots start listening for commands; unlisted bots stop listening.

Syntax:
`{cmdPrefix}select [botName] [botName2] ...`
Examples:
`{cmdPrefix}select` - deselect all bots
`{cmdPrefix}select build` - select only the build bot
`{cmdPrefix}select play play2` - select both the play bots
`{cmdPrefix}select *` - select all bots'''

        commandArgs = message.content[len(self._prefix + cmd) + 1:].split()

        if ('*' in commandArgs or self._name in commandArgs) ^ self._listening.isListening(message):
            self._listening.toggle(message)
            if self._listening.isListening(message):
                await self.display(self._name + " is now listening for commands.")
            else:
                await self.display(self._name + " is no longer listening for commands.")
        elif self._listening.isListening(message):
            await self.display(self._name + " is still listening for commands.")

    # Always listening actions
    ################################################################################

    async def action_batch(self, cmd, message):
        '''Run multiple commands at once'''
        orig_content = message.content
        commands = message.content.split("\n")
        for command in commands:
            if command.startswith("batch"):
                command = command[5:]
            elif command.startswith("~batch"):
                command = command[6:]

            if not command:
                continue
            command = command.strip()
            if not command.startswith("~"):
                command = "~" + command
            message.content = command
            await self.handle_message(message)
        message.content = orig_content

    async def action_verbose(self, cmd, message):
        '''Toggle verbosity of discord messages'''

        self._debug = not self._debug

        await message.channel.send("Verbose messages setting: {}".format(self._debug))

    async def action_test(self, cmd, message):
        '''Simple test action that does nothing'''

        await message.channel.send("Testing successful!")

    async def action_test_priv(self, cmd, message):
        '''Test if user has permission to use restricted commands'''

        await message.channel.send("You've got the power")

    async def action_test_unpriv(self, cmd, message):
        '''Test that a restricted command fails for all users'''

        await message.channel.send("BUG: You definitely shouldn't have this much power")

    async def action_list_shards(self, cmd, message):
        '''Lists currently running shards on this server'''
        await self.list_shards()

    async def list_shards(self):
        shards = await self._k8s.list()
        # Format of this is:
        # {'dungeon': {'available_replicas': 1, 'replicas': 1, 'pod_name': 'dungeon-xyz'}
        #  'test': {'available_replicas': 0, 'replicas': 0}}

        msg = ""
        for name in shards:
            state = shards[name]
            if state["replicas"] == 1 and state["available_replicas"] == 1:
                msg += f"\n:white_check_mark: {name}"
            elif state["replicas"] == 1 and state["available_replicas"] == 0:
                msg += f"\n:arrow_up: {name}"
            elif state["replicas"] == 0 and "pod_name" in state:
                msg += f"\n:arrow_down: {name}"
            elif state["replicas"] == 0 and "pod_name" not in state:
                msg += f"\n:x: {name}"
            else:
                msg += f"\n:exclamation: {name}: {pformat(state)}"
        if not msg:
            msg = "No shards to list"

        await self.display(msg)



    async def action_list_instances(self, cmd, message):
        rboard = RedisRBoard("play", redis_host="redis")
        inst_str = '```'
        inst_str += f"{'Dungeons' : <15}{'Used' : <15}{'Remaining' : <15}{'Total' : <15}"
        inst_str += "\n"
        for dungeon in self._dungeons:
            used = rboard.get("$Last", self._dungeons[dungeon])
            instances = rboard.get("$Instances", self._dungeons[dungeon])
            if used is not None and instances is not None:
                remaining = instances - used
                inst_str += f"{dungeon : <15}{used : <15}{remaining : <15}{instances : <15}"
                inst_str += "\n"
            else:
                self.display(f"Warning: Failed to load rboard values for {dungeon}")
        inst_str += "```"
        await self.display(inst_str)

    # pylint: disable=comparison-with-callable
    async def _start_stop_restart_common(self, cmd, message, action):
        arg_str = message.content[len(self._prefix + cmd)+1:].strip()
        if arg_str.startswith("shard "):
            arg_str = arg_str[len("shard "):].strip()
        commandArgs = arg_str.split()

        # Kills the bot, causing k8s to restart it
        if arg_str == 'bot' and action in (self.stop, self.restart):
            await message.channel.send("Restarting bot. Note: This will not update the bot's image")
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
            await self.display("No specified shards on this server.")
        else:
            if action == self.stop:
                await self.display("Stopping shards [{}]...".format(",".join(shards_changed)))
            elif action == self.start:
                await self.display("Starting shards [{}]...".format(",".join(shards_changed)))
            elif action == self.restart:
                await self.display("Restarting shards [{}]...".format(",".join(shards_changed)))

            await action(shards_changed)

            if action == self.stop:
                await self.display("Stopped shards [{}]".format(",".join(shards_changed)))
            elif action == self.start:
                await self.display("Started shards [{}]".format(",".join(shards_changed)))
            elif action == self.restart:
                await self.display("Restarted shards [{}]".format(",".join(shards_changed)))

            await self.display(message.author.mention)

    async def action_start(self, cmd, message):
        '''Start specified shards.
Syntax:
`{cmdPrefix}start shard *`
`{cmdPrefix}start shard valley isles orange'''
        await self._start_stop_restart_common(cmd, message, self.start)

    async def action_stop(self, cmd, message):
        '''Stop specified shards.
Syntax:
`{cmdPrefix}stop shard *`
`{cmdPrefix}stop shard valley isles orange'''
        await self._start_stop_restart_common(cmd, message, self.stop)

    async def action_restart(self, cmd, message):
        '''Restart specified shards.
Syntax:
`{cmdPrefix}restart shard *`
`{cmdPrefix}restart shard valley isles orange'''
        await self._start_stop_restart_common(cmd, message, self.restart)


    async def action_view_scores(self, cmd, message):
        '''View player scores game-wide, not tied to a specific shard. Run without arguements for syntax.
Note: the values from this command could be at most 5 minutes behind the play server if the player is online.
Do not use for debugging quests or other scores that are likely to change often.'''

        commandArgs = message.content[len(self._prefix + cmd) + 1:].split()

        cmd_str = os.path.join(_top_level, "utility_code/view_scores.py")
        while len(commandArgs) > 0:
            cmd_str = cmd_str + " " + commandArgs.pop(0)

        await self.run(cmd_str, displayOutput=True)
        await self.display("Done")


    async def action_get_player_scores(self, cmd, message):
        """Get score for a player

Note: the values from this command could be at most 5 minutes behind the play server if the player is online.
Do not use for debugging quests or other scores that are likely to change often."""

        commandArgs = message.content[len(self._prefix + cmd) + 1:].split()

        cmd_str = os.path.join(_top_level, "utility_code/get_score.py")
        cmd_str = " ".join([cmd_str] + list(commandArgs))

        await self.run(cmd_str, displayOutput=True, ret=(0, 2))
        await self.display("Done")


    async def action_set_player_scores(self, cmd, message):
        '''Set score for a player. This will work for offline and online players (scores are set in both redis and by broadcastcommand)
        '''

        commandArgs = message.content[len(self._prefix + cmd) + 1:]
        lines = commandArgs.split("\n")
        setscores = 0
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                # Skip blank lines
                continue

            commandArgs = line.split()

            if len(commandArgs) != 3:
                await self.display(f'Usage: {self._prefix + cmd} <playername> <objective> <value>')
                return

            name = commandArgs[0]
            objective = commandArgs[1]
            value = commandArgs[2]
            message = f'Set score {objective}={value} via bot'

            await self.run([os.path.join(_top_level, "rust/bin/redis_set_offline_player_score"), "redis://redis/", self._k8s.namespace, name, objective, value, message], displayOutput=(len(lines) < 5))
            self._socket.send_packet("*", "monumentanetworkrelay.command", {"command": f"execute if entity {name} run scoreboard players set {name} {objective} {value}"})
            setscores += 1

        await self.display(f"{setscores} player scores set both in redis (for offline players) and via broadcast (for online players)")

    async def action_generate_instances(self, cmd, message):
        '''Dangerous!
Deletes previous weekly update data
Temporarily brings down the dungeon shard to generate dungeon instances.
Must be run before preparing the build server update bundle'''

        debug = False
        if message.content[len(self._prefix + cmd) + 1:].strip() == "--debug":
            debug = True
            await self.display("Debug mode enabled! Will only generate 5 of each dungeon, and will not cleanly copy the dungeon shard")

        await self.display("Cleaning up old weekly update data...")
        await self.run("rm -rf /home/epic/5_SCRATCH/tmpreset", None)
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset")

        if not debug:
            await self.display("Stopping the dungeon shard...")
            await self.stop("dungeon")

        await self.display("Copying the dungeon master copies...")
        await self.run("cp -a /home/epic/project_epic/dungeon /home/epic/5_SCRATCH/tmpreset/dungeon")

        if not debug:
            await self.display("Restarting the dungeon shard...")
            await self.start("dungeon")

        await self.display("Generating dungeon instances (this may take a while)...")
        instance_gen_arg = " --dungeon-path /home/epic/5_SCRATCH/tmpreset/dungeon/ --out-folder /home/epic/5_SCRATCH/tmpreset/dungeons-out/"
        if debug:
            instance_gen_arg += " --count 5"
        await self.run(os.path.join(_top_level, "utility_code/dungeon_instance_gen.py") + instance_gen_arg)
        await self.run("mv /home/epic/5_SCRATCH/tmpreset/dungeons-out /home/epic/5_SCRATCH/tmpreset/TEMPLATE")

        await self.display("Cleaning up instance generation temp files...")
        await self.run("rm -rf /home/epic/5_SCRATCH/tmpreset/dungeon")
        await self.display("Dungeon instance generation complete!")
        await self.display(message.author.mention)

    async def action_prepare_update_bundle(self, cmd, message):
        '''Dangerous!
Temporarily brings down the valley and isles shards to prepare for weekly update
Packages up all of the pre-update server components needed by the play server for update
Must be run before starting weekly update on the play server'''

        debug = False
        if message.content[len(self._prefix + cmd) + 1:].strip() == "--debug":
            debug = True
            await self.display("Debug mode enabled! Will not stop shards before copying")

        if not debug:
            await self.display("Stopping valley and isles...")
            await self.stop(["valley", "isles"])

        await self.display("Copying valley...")
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset/TEMPLATE/valley")
        await self.run("cp -a /home/epic/project_epic/valley/Project_Epic-valley /home/epic/5_SCRATCH/tmpreset/TEMPLATE/valley/")

        if not debug:
            await self.display("Restarting the valley shard...")
            await self.start("valley")

        await self.display("Copying isles...")
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset/TEMPLATE/isles")
        await self.run("cp -a /home/epic/project_epic/isles/Project_Epic-isles /home/epic/5_SCRATCH/tmpreset/TEMPLATE/isles/")

        if not debug:
            await self.display("Restarting the isles shard...")
            await self.start("isles")

        await self.display("Copying purgatory...")
        await self.run("cp -a /home/epic/project_epic/purgatory /home/epic/5_SCRATCH/tmpreset/TEMPLATE/")

        await self.display("Copying server_config...")
        await self.run("cp -a /home/epic/project_epic/server_config /home/epic/5_SCRATCH/tmpreset/TEMPLATE/")

        await self.display("Sanitizing R1's items area...")
        await self.run(os.path.join(_top_level, "utility_code/sanitize_world.py") + " --world /home/epic/5_SCRATCH/tmpreset/TEMPLATE/valley/Project_Epic-valley --pos1 1140,0,2564 --pos2 1275,123,2811")
        await self.display("Sanitizing R2's items area...")
        await self.run(os.path.join(_top_level, "utility_code/sanitize_world.py") + " --world /home/epic/5_SCRATCH/tmpreset/TEMPLATE/isles/Project_Epic-isles --pos1 1140,0,2564 --pos2 1275,123,2811")

        await self.display("Packaging up update bundle...")
        await self.cd("/home/epic/5_SCRATCH/tmpreset")
        await self.run(["tar", "-I", "pigz --best", "-cf", f"/home/epic/4_SHARED/project_epic_build_template_pre_reset_{datestr()}.tgz", "TEMPLATE"])

        await self.display("Update bundle ready!")
        await self.display(message.author.mention)

    async def action_prepare_stage_bundle(self, cmd, message):
        '''Prepares a bundle of whichever shards you want to update on stage.

`--debug` prepares the bundle without stopping shards.
`--skip-server-config` prepares the bundle without including the server_config folder (no plugins or data folder updates)

Examples:
`{cmdPrefix}prepare stage bundle valley labs`
`{cmdPrefix}prepare stage bundle --debug valley labs`'''

        arg_str = message.content[len(self._prefix + cmd)+1:].strip()
        shards = arg_str.split()

        if len(shards) <= 0:
            await self.display("No shards specified")
            return

        instance_gen_required = []
        main_shards = []
        debug = False
        copy_server_config = True
        for shard in shards:
            if shard == "--debug":
                debug = True
                await self.display("Debug mode enabled! Will not stop shards prior to copying")
            elif shard == "--skip-server-config":
                copy_server_config = False
                await self.display("--skip-server-config specified, will not copy server_config folder (no plugins or data folder updates) ")
            elif shard in ("valley", "isles",):
                main_shards.append(shard)
            elif shard in ["white", "orange", "magenta", "lightblue", "yellow", "lime", "pink", "gray", "lightgray", "cyan", "purple", "blue", "brown", "green", "red", "black", "teal", "forum", "tutorial", "reverie", "rush", "mist", "willows", "sanctum", "shiftingcity", "labs", "depths", "remorse", "corridors", "verdant"]:
                instance_gen_required.append(shard)
            else:
                await self.display("Unknown shard specified: {}".format(shard))
                return

        await self.display("Starting stage bundle preparation for shards: [{}]".format(" ".join(shards)))

        await self.display("Cleaning up old stage data...")
        await self.run("rm -rf /home/epic/5_SCRATCH/tmpstage", None)
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpstage")

        if len(main_shards) > 0:
            # Need to copy primary shards

            for shard in main_shards:
                if not debug:
                    await self.display("Stopping {shard}...".format(shard=shard))
                    await self.stop(shard)

                await self.display("Copying {shard}...".format(shard=shard))
                await self.run("mkdir -p /home/epic/5_SCRATCH/tmpstage/TEMPLATE/{shard}".format(shard=shard))
                # TODO: This needs to copy all the worlds, not just the base one
                await self.run("cp -a /home/epic/project_epic/{shard}/Project_Epic-{shard} /home/epic/5_SCRATCH/tmpstage/TEMPLATE/{shard}/".format(shard=shard))

                if not debug:
                    await self.display("Restarting {shard}...".format(shard=shard))
                    await self.start(shard)

                await self.display("Running replacements on copied version of {shard}...".format(shard=shard))
                args = " --worlds /home/epic/5_SCRATCH/tmpstage/TEMPLATE/{shard}".format(shard=shard)
                await self.run(os.path.join(_top_level, "utility_code/replace_items.py") + args, displayOutput=True)
                args = " --worlds /home/epic/5_SCRATCH/tmpstage/TEMPLATE/{shard} --library-of-souls /home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json".format(shard=shard)
                await self.run(os.path.join(_top_level, "utility_code/replace_mobs.py") + args, displayOutput=True)

        if len(instance_gen_required) > 0:
            # Need to generate instances
            if not debug:
                await self.display("Stopping the dungeon shard...")
                await self.stop("dungeon")

            await self.display("Copying the dungeon master copies...")
            await self.run("cp -a /home/epic/project_epic/dungeon /home/epic/5_SCRATCH/tmpstage/dungeon")
            await self.run("rm -rf /home/epic/5_SCRATCH/tmpstage/dungeon/cache /home/epic/5_SCRATCH/tmpstage/dungeon/plugins")

            if not debug:
                await self.display("Restarting the dungeon shard...")
                await self.start("dungeon")

            await self.display("Running replacements on copied dungeon masters...")
            args = " --worlds /home/epic/5_SCRATCH/tmpstage/dungeon"
            await self.run(os.path.join(_top_level, "utility_code/replace_items.py") + args, displayOutput=True)
            args = " --worlds /home/epic/5_SCRATCH/tmpstage/dungeon --library-of-souls /home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json"
            await self.run(os.path.join(_top_level, "utility_code/replace_mobs.py") + args, displayOutput=True)

            await self.display("Generating dungeon instances for [{}]...".format(" ".join(instance_gen_required)))
            instance_gen_arg = (" --dungeon-path /home/epic/5_SCRATCH/tmpstage/dungeon/" +
                                " --out-folder /home/epic/5_SCRATCH/tmpstage/TEMPLATE" +
                                " --count 8 " + " ".join(instance_gen_required))
            await self.run(os.path.join(_top_level, "utility_code/dungeon_instance_gen.py") + instance_gen_arg)

            await self.display("Dungeon instance generation complete!")

        if copy_server_config:
            await self.display("Copying server_config...")
            await self.run("cp -a /home/epic/project_epic/server_config /home/epic/5_SCRATCH/tmpstage/TEMPLATE/")

            await self.display("Running replacements on copied structures...")
            args = (" --schematics /home/epic/5_SCRATCH/tmpstage/TEMPLATE/server_config/data/structures"
                    + " --structures /home/epic/5_SCRATCH/tmpstage/TEMPLATE/server_config/data/generated"
                    + " --library-of-souls /home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json")
            await self.run(os.path.join(_top_level, "utility_code/replace_items.py"
                                        + " --schematics /home/epic/5_SCRATCH/tmpstage/TEMPLATE/server_config/data/structures"
                                        + " --structures /home/epic/5_SCRATCH/tmpstage/TEMPLATE/server_config/data/generated"), displayOutput=True)
            await self.run(os.path.join(_top_level, "utility_code/replace_mobs.py") + args, displayOutput=True)

        await self.display("Packaging up stage bundle...")
        await self.cd("/home/epic/5_SCRATCH/tmpstage")

        await self.run("rm -f /home/epic/4_SHARED/stage_bundle.tgz", None)
        await self.run(["tar", "-I", "pigz --best", "-cf", "/home/epic/4_SHARED/stage_bundle.tgz", "TEMPLATE"])

        await self.display("Cleaning up stage temp files...")
        await self.run("rm -rf /home/epic/5_SCRATCH/tmpstage")

        await self.display("Stage bundle ready!")
        await self.display(message.author.mention)

    async def action_apply_stage_bundle(self, cmd, message):
        '''Applies a bundle of whichever shards you want to update on stage. This takes no arguments.
You can create a bundle with `{cmdPrefix}prepare stage bundle`'''

        await self.display("Unpacking stage bundle...")
        await self.run("rm -rf /home/epic/5_SCRATCH/tmpreset", None)
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset")
        await self.cd("/home/epic/5_SCRATCH/tmpreset")
        await self.run("tar xzf /home/epic/4_SHARED/stage_bundle.tgz")

        await self.cd("/home/epic/5_SCRATCH/tmpreset/TEMPLATE")
        folders_to_update = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d)]
        if len(folders_to_update) < 1:
            await self.display("Error: No stage folders to process?")
            await self.display(message.author.mention)
            return

        await self.display("Loading from stage bundle: [{}]".format(" ".join(folders_to_update)))

        # Stop all shards
        await self.display("Stopping all shards...")
        shards = await self._k8s.list()
        await self.stop([shard for shard in self._shards if shard.replace('_', '') in shards])
        for shard in [shard for shard in self._shards if shard.replace('_', '') in shards]:
            if shards[shard.replace('_', '')]['replicas'] != 0:
                await self.display("ERROR: shard {!r} is still running!".format(shard))
                await self.display(message.author.mention)
                return

        await self.display("Saving ops and banned players")
        await self.run("mkdir -p /home/epic/4_SHARED/op-ban-sync/stage/")
        await self.run(f"cp -a {self._shards['valley']}/banned-ips.json /home/epic/4_SHARED/op-ban-sync/stage/")
        await self.run(f"cp -a {self._shards['valley']}/banned-players.json /home/epic/4_SHARED/op-ban-sync/stage/")
        await self.run(f"cp -a {self._shards['valley']}/ops.json /home/epic/4_SHARED/op-ban-sync/stage/")

        await self.display("Deleting previous update data...")
        await self.cd(self._server_dir)
        await self.run("rm -rf 0_PREVIOUS")
        await self.run("mkdir 0_PREVIOUS")

        await self.display(f"Moving [{' '.join(folders_to_update)}] to 0_PREVIOUS...")
        for f in folders_to_update:
            await self.run("mv {} 0_PREVIOUS/".format(f), None)

        if "server_config" in folders_to_update:
            await self.display("Getting new server config...")
            await self.run(f"mv /home/epic/5_SCRATCH/tmpreset/TEMPLATE/server_config {self._server_dir}/")
            folders_to_update.remove("server_config")

        await self.display("Running actual weekly update (this will take a while!)...")

        await self.run(os.path.join(_top_level, f"utility_code/weekly_update.py --last_week_dir {self._server_dir}/0_PREVIOUS/ --output_dir {self._server_dir}/ --build_template_dir /home/epic/5_SCRATCH/tmpreset/TEMPLATE/ -j 6 " + " ".join(folders_to_update)))

        for shard in ["plots", "valley", "isles", "playerplots",]:
            if shard in folders_to_update:
                await self.display("Preserving warps for {0}...".format(shard))
                os.makedirs(f"{self._shards[shard]}/plugins/MonumentaWarps")
                if os.path.exists(f"{self._server_dir}/0_PREVIOUS/{shard}/plugins/MonumentaWarps/warps.yml"):
                    await self.run(f"cp {self._server_dir}/0_PREVIOUS/{shard}/plugins/MonumentaWarps/warps.yml {self._shards[shard]}/plugins/MonumentaWarps/warps.yml")

        for shard in folders_to_update:
            if shard in ["build",] or shard.startswith("bungee"):
                continue

            await self.run(f"cp -af /home/epic/4_SHARED/op-ban-sync/stage/banned-ips.json {self._shards[shard]}/")
            await self.run(f"cp -af /home/epic/4_SHARED/op-ban-sync/stage/banned-players.json {self._shards[shard]}/")
            await self.run(f"cp -af /home/epic/4_SHARED/op-ban-sync/stage/ops.json {self._shards[shard]}/")

        await self.display("Generating per-shard config...")
        await self.cd(self._server_dir)
        await self.run(os.path.join(_top_level, "utility_code/gen_server_config.py --play " + " ".join(folders_to_update)))

        await self.display("Checking for broken symbolic links...")
        await self.run("find . -xtype l", displayOutput=True)

        await self.display("Done.")
        await self.display(message.author.mention)


    async def action_fetch_update_bundle(self, cmd, message):
        '''Dangerous!
Deletes in-progress weekly update info on the play server
Downloads the weekly update bundle from the build server and unpacks it'''

        await self.display("Unpacking update bundle...")
        await self.run("rm -rf /home/epic/5_SCRATCH/tmpreset", None)
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset")
        await self.cd("/home/epic/5_SCRATCH/tmpreset")
        await self.run("tar xzf /home/epic/4_SHARED/project_epic_build_template_pre_reset_" + datestr() + ".tgz")
        await self.display("Build server template data retrieved and ready for update.")
        await self.display(message.author.mention)

    async def action_stop_in_10_minutes(self, cmd, message):
        '''Dangerous!
Starts a bungee shutdown timer for 10 minutes and cleans up old coreprotect data'''

        async def send_broadcast_msg(time_left):
            self._socket.send_packet("*", "monumentanetworkrelay.command",
                                     {"command": '''tellraw @a ["",{"text":"[Alert] ","color":"red"},{"text":"Monumenta's weekly update will begin in","color":"white"},{"text":" ''' + time_left + '''","color":"red"},{"text":". The server will be down for approximately 1 hour while we patch new content into the game."}]'''})
            await self.display("{} to weekly update".format(time_left))

        await send_broadcast_msg("10 minutes")
        await asyncio.sleep(3 * 60)
        await send_broadcast_msg("7 minutes")
        await asyncio.sleep(2 * 60)
        await send_broadcast_msg("5 minutes")
        self._socket.send_packet("playerplots", "monumentanetworkrelay.command", {"command": 'co purge t:30d'})
        self._socket.send_packet("plots", "monumentanetworkrelay.command", {"command": 'co purge t:30d'})
        await asyncio.sleep(2 * 60)
        await send_broadcast_msg("3 minutes")
        await asyncio.sleep(60)
        await send_broadcast_msg("2 minutes")
        await asyncio.sleep(60)
        await send_broadcast_msg("1 minute")
        await asyncio.sleep(30)
        await send_broadcast_msg("30 seconds")
        await asyncio.sleep(15)
        await send_broadcast_msg("15 seconds")
        self._socket.send_packet("*", "monumentanetworkrelay.command", {"command": 'save-all'})
        await asyncio.sleep(10)
        await send_broadcast_msg("5 seconds")
        await asyncio.sleep(5)

        # Stop bungee
        await self.stop("bungee")
        await self.stop("bungee-11")

        await self.display(message.author.mention)

    async def action_stop_and_backup(self, cmd, message):
        '''Dangerous!
Brings down all play server shards and backs them up in preparation for weekly update.
DELETES DUNGEON CORE PROTECT DATA'''

        debug = False
        if message.content[len(self._prefix + cmd) + 1:].strip() == "--debug":
            debug = True
            await self.display("Debug mode enabled! Will not actually make backups")

        await self.display("Stopping all shards...")

        shards = await self._k8s.list()

        # Stop all shards
        await self.stop([shard for shard in self._shards if shard.replace('_', '') in shards])

        # Fail if any shards are still running
        await self.display("Checking that all shards are stopped...")
        shards = await self._k8s.list()
        for shard in [shard for shard in self._shards if shard.replace('_', '') in shards]:
            if shards[shard.replace('_', '')]['replicas'] != 0:
                await self.display("ERROR: shard {!r} is still running!".format(shard))
                await self.display(message.author.mention)
                return

        await self.display("Deleting cache and select FAWE and CoreProtect data...")
        for shard in self._shards:
            dirs_to_del = []
            dirs_to_del.append(f"{self._shards[shard]}/cache")

            if shard not in ["build",]:
                dirs_to_del.append(f"{self._shards[shard]}/plugins/FastAsyncWorldEdit/clipboard")
                dirs_to_del.append(f"{self._shards[shard]}/plugins/FastAsyncWorldEdit/history")
                dirs_to_del.append(f"{self._shards[shard]}/plugins/FastAsyncWorldEdit/sessions")

            if shard not in ["build", "valley", "plots", "playerplots"]:
                dirs_to_del.append(f"{self._shards[shard]}/plugins/CoreProtect")

            await self.run(f"rm -rf {' '.join(dirs_to_del)}")

        if "valley" in self._shards:
            await self.display("Saving ops and banned players")
            await self.run(f"cp -a {self._shards['valley']}/banned-ips.json /home/epic/4_SHARED/op-ban-sync/valley/")
            await self.run(f"cp -a {self._shards['valley']}/banned-players.json /home/epic/4_SHARED/op-ban-sync/valley/")
            await self.run(f"cp -a {self._shards['valley']}/ops.json /home/epic/4_SHARED/op-ban-sync/valley/")

        if self._common_weekly_update_tasks:
            await self.display("Copying player data from redis")
            await self.run(os.path.join(_top_level, "rust/bin/redis_playerdata_save_load") + f" redis://redis/ play --output {self._server_dir}/server_config/redis_data_final")

        if debug:
            await self.display("WARNING! Skipping backup!")
        else:
            await self.display("Performing backup...")
            await self.cd(f"{self._server_dir}/..")
            await self.run("mkdir -p /home/epic/1_ARCHIVE")
            folder_name = self._server_dir.strip("/").split("/")[-1]
            await self.run(["tar", f"--exclude={folder_name}/0_PREVIOUS", "-I", "pigz --best", "-cf", f"/home/epic/1_ARCHIVE/{folder_name}_pre_reset_{datestr()}.tgz", folder_name])

        await self.display("Backups complete! Ready for update.")
        await self.display(message.author.mention)

    async def action_get_raffle_seed(self, cmd, message):
        '''Gets the current raffle seed based on reactions'''

        if self._rreact["msg_contents"] is not None:
            await self.display("Current raffle seed is: ```{}```".format(self._rreact["msg_contents"]))
        else:
            await self.display("No current raffle seed")

    async def action_run_test_raffle(self, cmd, message):
        '''Runs a test raffle (does not save results)'''

        await self.display("Test raffle results:")
        raffle_seed = "Default raffle seed"
        if self._rreact["msg_contents"] is not None:
            raffle_seed = self._rreact["msg_contents"]

        raffle_results = tempfile.mktemp()
        vote_raffle(raffle_seed, 'redis', raffle_results, dry_run=True)
        await self.run("cat {}".format(raffle_results), displayOutput=True)

    async def action_weekly_update(self, cmd, message):
        '''Dangerous!
Performs the weekly update on the play server. Requires StopAndBackupAction.'''

        # Check for any arguments
        commandArgs = message.content[len(self._prefix):].strip()
        min_phase = 0
        if len(commandArgs) > len(cmd) + 1:
            min_phase = int(commandArgs[len(cmd) + 1:].strip())
        await self.display(f"Starting from phase {min_phase} at <t:{int(time.time())}:F>")

        await self.run("mkdir -p /home/epic/1_ARCHIVE")
        await self.run("mkdir -p /home/epic/0_OLD_BACKUPS")

        r = redis.Redis(host="redis", port=6379)
        if min_phase <= 0:
            r.set('monumenta:automation:weekly_update_common_done', 'False')
            common_done = r.get('monumenta:automation:weekly_update_common_done').decode("utf-8")
            await self.display("Marked common update tasks as not done")
            if common_done != "False":
                raise Exception(f"Tried to set common_done = False but got {common_done} back!")

        # Fail if any shards are still running
        if min_phase <= 1:
            await self.display("Checking that all shards are stopped...")
            shards = await self._k8s.list()
            for shard in [shard for shard in self._shards if shard.replace('_', '') in shards]:
                if shards[shard.replace('_', '')]['replicas'] != 0:
                    await self.display("ERROR: shard {!r} is still running!".format(shard))
                    await self.display(message.author.mention)
                    return

        # Sanity check to make sure this script is going to process everything that it needs to
        if min_phase <= 2:
            files = os.listdir(self._server_dir)
            for f in files:
                if f not in ["server_config", "0_PREVIOUS"] and f not in self._shards:
                    await self.display(f"ERROR: {self._server_dir} directory contains file {f} which will not be processed!")
                    await self.display(message.author.mention)
                    return

        # Delete previous update data and move current data to 0_PREVIOUS
        await self.cd(self._server_dir)
        if min_phase <= 3:
            await self.display("Deleting previous update data...")
            await self.run("rm -rf 0_PREVIOUS")
            await self.run("mkdir 0_PREVIOUS")

        # Move everything to 0_PREVIOUS except bungee and build
        if min_phase <= 4:
            await self.display("Moving everything except bungee, and build to 0_PREVIOUS...")
            for f in files:
                if f not in ["0_PREVIOUS", "build",] and not f.startswith("bungee"):
                    await self.run("mv {} 0_PREVIOUS/".format(f))

        if min_phase <= 5:
            await self.display("Getting new server config...")
            await self.run(f"mv /home/epic/5_SCRATCH/tmpreset/TEMPLATE/server_config {self._server_dir}/")

        if min_phase <= 6 and self._common_weekly_update_tasks:
            await self.display("Copying playerdata...")
            await self.run(f"mv {self._server_dir}/0_PREVIOUS/server_config/redis_data_final {self._server_dir}/server_config/redis_data_initial")

        if min_phase <= 7 and "purgatory" in self._shards:
            await self.display("Copying purgatory...")
            await self.run(f"rm -rf {self._shards['purgatory']}")
            await self.run(f"mv /home/epic/5_SCRATCH/tmpreset/TEMPLATE/purgatory {self._shards['purgatory']}")

        if min_phase <= 9 and self._common_weekly_update_tasks:
            await self.display("Removing tutorial data")
            await self.run(os.path.join(_top_level, "rust/bin/redis_remove_data") + " redis://redis/ tutorial:* --confirm")

        if min_phase <= 10 and self._common_weekly_update_tasks:
            await self.display("Running score changes for players and moving them to spawn...")
            await self.run(os.path.join(_top_level, "rust/bin/weekly_update_player_scores") + f" {self._server_dir}/server_config/redis_data_initial")

        if min_phase <= 11 and self._common_weekly_update_tasks:
            await self.display("Running item replacements for players...")
            await self.run(os.path.join(_top_level, "utility_code/weekly_update_player_data.py") + f" --world {self._server_dir}/server_config/redis_data_initial --datapacks {self._server_dir}/server_config/data/datapacks --logfile {self._server_dir}/server_config/redis_data_initial/replacements.yml -j 16")

        if min_phase <= 12 and self._common_weekly_update_tasks:
            await self.display("Loading player data back into redis...")
            await self.run(os.path.join(_top_level, "rust/bin/redis_playerdata_save_load") + f" redis://redis/ play --input {self._server_dir}/server_config/redis_data_initial 1")

        ########################################
        # Raffle

        if min_phase <= 13 and self._common_weekly_update_tasks:
            await self.display("Raffle results:")
            raffle_seed = "Default raffle seed"
            if self._rreact["msg_contents"] is not None:
                raffle_seed = self._rreact["msg_contents"]

            raffle_results = tempfile.mktemp()
            vote_raffle(raffle_seed, 'redis', raffle_results)
            await self.run("cat {}".format(raffle_results), displayOutput=True)

        # Raffle
        ########################################

        if min_phase <= 14 and self._common_weekly_update_tasks:
            await self.display("Refreshing leaderboards")
            await self.run(os.path.join(_top_level, "rust/bin/leaderboard_update_redis") + " redis://redis/ play " + os.path.join(_top_level, "leaderboards.yaml"))

        if min_phase <= 15 and self._common_weekly_update_tasks:
            await self.display("Restarting rabbitmq")
            await self.restart("rabbitmq")

        if min_phase <= 16 and self._common_weekly_update_tasks:
            await self.display("Marking common tasks as complete")
            r.set('monumenta:automation:weekly_update_common_done', 'True')

        if min_phase <= 17:
            await self.display("Waiting for common tasks to complete...")
            while True:
                common_done = r.get('monumenta:automation:weekly_update_common_done').decode("utf-8")
                if common_done == "True":
                    await self.display("Detected common tasks are complete, proceeding with update")
                    break

                # Not done yet, wait a bit before polling
                await asyncio.sleep(5)

        if min_phase <= 18:
            await self.display("Running actual weekly update (this will take a while!)...")
            logfile = f"/home/epic/0_OLD_BACKUPS/terrain_reset_item_replacements_log_{self._name}_{datetime.date.today().strftime('%Y-%m-%d')}.log"
            await self.run(os.path.join(_top_level, f"utility_code/weekly_update.py --last_week_dir {self._server_dir}/0_PREVIOUS/ --output_dir {self._server_dir}/ --build_template_dir /home/epic/5_SCRATCH/tmpreset/TEMPLATE/ --logfile {logfile} -j 16 " + " ".join(self._shards)))

        if min_phase <= 19:
            for shard in self._shards:
                if shard not in ["build",] and not shard.startswith("bungee"):
                    await self.run(f"cp -af /home/epic/4_SHARED/op-ban-sync/valley/banned-ips.json {self._shards[shard]}/")
                    await self.run(f"cp -af /home/epic/4_SHARED/op-ban-sync/valley/banned-players.json {self._shards[shard]}/")
                    await self.run(f"cp -af /home/epic/4_SHARED/op-ban-sync/valley/ops.json {self._shards[shard]}/")

        await self.cd(self._server_dir)
        if min_phase <= 20:
            await self.display("Generating per-shard config...")
            await self.run(os.path.join(_top_level, "utility_code/gen_server_config.py --play " + " ".join(self._shards.keys())))

        if min_phase <= 21:
            await self.display("Checking for broken symbolic links...")
            await self.run(f"find {self._server_dir} -xtype l", displayOutput=True)

        await self.cd("/home/epic")
        if min_phase <= 22:
            await self.display("Backing up post-update artifacts...")
            await self.cd(f"{self._server_dir}/..")
            folder_name = self._server_dir.strip("/").split("/")[-1]
            await self.run(["tar", f"--exclude={folder_name}/0_PREVIOUS", "-I", "pigz --best", "-cf", f"/home/epic/1_ARCHIVE/{folder_name}_post_reset_{datestr()}.tgz", folder_name])

        await self.display(f"Done at <t:{int(time.time())}:F>.")
        await self.display(message.author.mention)

    async def action_stage(self, cmd, message):
        ''' Stops all stage server shards
Copies the current play server over to the stage server.
Archives the previous stage server contents under 0_PREVIOUS '''

        # Just in case...
        if not self._stage_source:
            raise Exception("WARNING: bot doesn't have stage source, aborting")

        play_broker = SocketManager("rabbitmq.play", "stagebot", callback=None)

        await self.display("Removing previous 0_STAGE directories")
        await self.run(f"rm -rf {self._server_dir}/0_STAGE")
        await self.run(f"mkdir {self._server_dir}/0_STAGE")

        tasks = []
        port = 1111
        for server_name in self._stage_source:
            await self.display(f"Starting receive task on port {port}")
            task = asyncio.get_event_loop().create_task(self.stage_receive_data_task(port))
            tasks.append(task)
            port += 1

        await asyncio.sleep(15)

        port = 1111
        for server_name in self._stage_source:
            server_section = self._stage_source[server_name]
            stage_msg = {
                "shards": server_section["shards"],
                "address": "automation-bot.stage",
                "port": port,
            }
            await self.display(f"Sending request to {server_section['queue_name']} with config {pformat(stage_msg)}")
            play_broker.send_packet(server_section["queue_name"], "Monumenta.Automation.stage", stage_msg)
            port += 1

        await self.display("Finished launching copy tasks, waiting for them to complete. This will take a while...")
        for task in tasks:
            await task

        # Stop all shards
        await self.display("Stopping all stage server shards...")
        shards = await self._k8s.list()
        await self.stop([shard for shard in self._shards if shard in shards])

        # Delete and re-create all the 0_PREVIOUS directories, wherever they might be at one level above the shard folders
        await self.display("Removing previous 0_PREVIOUS directories")
        for shard in self._shards:
            await self.run(f"rm -rf {self._server_dir}/0_PREVIOUS")
        for shard in self._shards:
            await self.run(f"mkdir -p {self._server_dir}/0_PREVIOUS")

        # Move the server_config directory
        await self.run(f"mv {self._server_dir}/server_config {self._server_dir}/0_PREVIOUS/", None)

        # Move the shard folders into those folders
        await self.display("Moving previous data to 0_PREVIOUS directories")
        tasks = []
        for shard in self._shards:
            tasks.append(asyncio.create_task(self.run(f"mv {self._shards[shard]} {self._server_dir}/0_PREVIOUS/", None)))
        for task in tasks:
            await task

        await self.display("Moving pulled stage data into live folder")
        await self.run(["bash", "-c", f"mv {self._server_dir}/0_STAGE/* {self._server_dir}"])
        await self.run(f"rmdir {self._server_dir}/0_STAGE")

        # Download the entire redis database from the play server
        await self.display("Stopping stage redis...")
        await self.stop("redis")
        await self.cd(f"{self._server_dir}/../redis")
        await self.run(f"mv dump.rdb dump.rdb.previous")
        await self.display("Downloading current redis database from the play server...")
        await self.run(f"redis-cli -h redis.play --rdb dump.rdb")
        await self.start("redis")

        await self.display("Disabling Plan and PremiumVanish...")
        await self.run(f"mv -f {self._server_dir}/server_config/plugins/Plan.jar {self._server_dir}/server_config/plugins/Plan.jar.disabled")
        await self.run(f"mv -f {self._server_dir}/server_config/plugins/PremiumVanish.jar {self._server_dir}/server_config/plugins/PremiumVanish.jar.disabled")

        await self.display("Adjusting bungee config...")
        with open(f"{self._shards['bungee']}/config.yml", "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        config["listeners"][0]["priorities"] = [
            "purgatory",
            "valley",
            "isles",
            "plots",
        ]
        with open(f"{self._shards['bungee']}/config.yml", "w") as f:
            yaml.dump(config, f, width=2147483647, allow_unicode=True)

        await self.display("Stage server loaded with current play server data")
        await self.display(message.author.mention)

    async def stage_receive_data_task(self, port):
        await self.cd(f"{self._server_dir}/0_STAGE")
        await self.run(["bash", "-c", f"nc -dl {port} | lz4 -d | tar xf -"])
        await self.display(f"Completed receiving stage data on port {port}")

    async def stage_data_request(self, message):
        shards_str = " ".join(message["shards"])
        await self.display(f"Got stage request for shards:\n> {shards_str}")
        await self.cd(f"{self._server_dir}")
        await self.run(["bash", "-c", f"tar cf - {shards_str} | lz4 | nc -N {message['address']} {message['port']}"])
        await self.display("Completed sending stage data")

    async def action_update_items(self, cmd, message):
        '''
Updates one or more items in all loot tables

Usage:
    ~update item /setblock 1217 3 2720 minecraft:chest{Items:[...]}
    Or if too long for a discord message:
    ~update item
    <.txt file attachment starting with /setblock ...>

Easiest way to get this is putting an item in a chest, and looking at that chest and pressing f3+i
    '''

        commandArgs = message.content[len(self._prefix):].strip()
        temppath = tempfile.mktemp()
        if message.attachments:
            # Save first attachment as text file at the temppath
            attachment = message.attachments[0]
            if not attachment.url.endswith(".txt"):
                await self.display("setblock chest argument must be a .txt file")
                return

            await attachment.save(temppath)
        else:
            # Save any text arguments to the text file at the temppath
            if len(commandArgs) < len(cmd) + 5:
                await self.display("setblock chest argument required")
                return
            if '{' not in commandArgs:
                await self.display("Arguments should be of the form /setblock ~ ~ ~ minecraft:chest{Items:[...]}")
                return
            with open(temppath, "w") as fp:
                fp.write(commandArgs)

        userfoldername = re.sub('[^a-z0-9]', '', message.author.name.lower()) + str(message.id)
        userfolderpath = os.path.join("/tmp", userfoldername)
        await self.run(["mkdir", userfolderpath])
        await self.run([os.path.join(_top_level, f"utility_code/bulk_update_loottables.py"), "--output-dir", userfolderpath, temppath], displayOutput=True)
        files = [f for f in os.listdir(userfolderpath) if os.path.isfile(os.path.join(userfolderpath, f))]
        if len(files) > 0:
            await self.cd("/tmp")
            for fname in files:
                await self._channel.send(fname, file=discord.File(os.path.join(userfolderpath, fname)))
            if len(files) > 1:
                await self.run(f"zip -r {userfoldername}.zip {userfoldername}")
                await self._channel.send("Zip file containing all loot tables generated by this run:", file=discord.File(os.path.join("/tmp", f"{userfoldername}.zip")))

        await self.display(message.author.mention)

    async def action_run_replacements(self, cmd, message):
        '''Runs item and mob replacements on a given shard
Syntax:
`{cmdPrefix}run replacements shard valley isles orange`'''

        commandArgs = message.content[len(self._prefix + cmd)+1:].split()

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
            await self.display("Nothing to do")
            return

        await self.display(f"Replacing both mobs AND items on [{' '.join(replace_shards)}]")

        for shard in replace_shards:
            if shard == "structures":
                base_backup_name = f"/home/epic/0_OLD_BACKUPS/structures_pre_entity_loot_updates_{datestr()}"

                await self.display("Running replacements on structures")
                await self.cd("/home/epic/project_epic/server_config/data")
                await self.run(["tar", "-I", "pigz --best", "-cf", f"{base_backup_name}.tgz", "structures"])
                await self.cd("/home/epic/project_epic/server_config/data")
                await self.run(os.path.join(_top_level, f"utility_code/replace_items.py --schematics structures --structures generated --logfile {base_backup_name}_items.yml"), displayOutput=True)
                await self.cd("/home/epic/project_epic/server_config/data")
                await self.run(os.path.join(_top_level, f"utility_code/replace_mobs.py --schematics structures --structures generated --library-of-souls /home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json --logfile {base_backup_name}_mobs.yml"), displayOutput=True)

            else:
                base_backup_name = f"/home/epic/0_OLD_BACKUPS/{shard}_pre_entity_loot_updates_{datestr()}"

                if do_prune:
                    await self.display(f"Running replacements and pruning world regions on shard {shard}")
                else:
                    await self.display(f"Running replacements on shard {shard}")
                await self.stop(shard)
                await self.cd(os.path.dirname(self._shards[shard].rstrip('/'))) # One level up
                await self.run(["tar", f"--exclude={shard}/logs", f"--exclude={shard}/plugins", f"--exclude={shard}/cache", "-I", "pigz --best", "-cf", f"{base_backup_name}.tgz", shard])
                if do_prune:
                    await self.cd(os.path.dirname(self._shards[shard].rstrip('/'))) # One level up
                    await self.run(os.path.join(_top_level, f"utility_code/prune_empty_regions.py {shard}"))
                await self.cd(os.path.dirname(self._shards[shard].rstrip('/'))) # One level up
                await self.run(os.path.join(_top_level, f"utility_code/replace_items.py --worlds {shard} --logfile {base_backup_name}_items.yml"), displayOutput=True)
                await self.cd(os.path.dirname(self._shards[shard].rstrip('/'))) # One level up
                await self.run(os.path.join(_top_level, f"utility_code/replace_mobs.py --worlds {shard} --library-of-souls /home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json --logfile {base_backup_name}_mobs.yml"), displayOutput=True)
                await self.start(shard)

        await self.display(message.author.mention)

    async def action_find_loot_problems(self, cmd, message):
        '''Finds loot table problems
- Lists containers in dungeons that are missing loot tables.
- TODO: Add more!
'''
        await self.display("Checking for loot table problems...")
        await self.display("Checking for missing dungeon loot tables...")
        await self.run(os.path.join(_top_level, "utility_code/dungeon_find_lootless.py"), 0, displayOutput=True)

    async def action_get_commands(self, cmd, message):
        '''Scans all command blocks in one or more worlds and returns a JSON file with their information
Syntax:
`{cmdPrefix}get commands valley isles orange ...`'''

        commandArgs = message.content[len(self._prefix + cmd)+1:].split()

        scan_shards = []
        for shard in self._shards:
            if shard in commandArgs:
                scan_shards.append(shard)

        if not scan_shards:
            await self.display("Nothing to do")
            return

        await self.display(f"Getting command blocks on [{' '.join(scan_shards)}]")

        for shard in scan_shards:

            await self.display("Scanning for command blocks on shard {}".format(shard))
            scan_results = tempfile.mktemp()
            await self.cd(self._shards[shard])
            await self.run(os.path.join(_top_level, f"utility_code/command_block_update_tool.py --world Project_Epic-{shard} --output {scan_results}"), displayOutput=True)
            await self.run(f"mv -f {scan_results} /tmp/{shard}.json")
            await self._channel.send(f"{shard} commands:", file=discord.File(f'/tmp/{shard}.json'))

        await self.display(message.author.mention)

    async def action_list_world_loot(self, cmd, message):
        '''Lists all loot tables and items in a world, with optional coordinates
Syntax:
`{cmdPrefix}list world loot dungeon`
`{cmdPrefix}list world loot dungeon 512 0 0 1023 255 511`'''

        commandArgs = message.content[len(self._prefix + cmd)+1:].split()

        shard = commandArgs[0]
        if shard not in commandArgs:
            await self.display(f"The shard {shard} is not known by this bot.")
            return

        await self.display(f"Looking for loot...")

        await self.run(os.path.join(_top_level, f"utility_code/list_world_loot.py {self._shards[shard]}/Project_Epic-{shard}" + "".join([" " + x for x in commandArgs[1:]])), displayOutput=True)

        await self.display(message.author.mention)

    async def action_gen_demo_release(self, cmd, message):
        '''Generates a demo release zip with the specified version
Syntax:
`{cmdPrefix}generate demo release <version>`'''

        commandArgs = message.content[len(self._prefix + cmd)+1:]
        version = "".join([i if re.match(r'[0-9\.]', i) else '' for i in commandArgs])

        if not version:
            await self.display("Version must be specified and can contain only numbers and periods")
            await self.display(message.author.mention)
            return

        # Test if this version already exists
        try:
            await self.run(["test", "!", "-f", "/home/epic/4_SHARED/monumenta_demo/Monumenta Demo - The Halls of Wind and Blood V{}.zip".format(version)])
        except Exception:
            await self.display("Demo release V{} already exists!".format(version))
            return

        await self.display("Generating demo release version V{}...".format(version))

        await self.stop("white-demo")

        # Clean up the working directory for testing/etc
        await self.cd("/home/epic/project_epic/Monumenta Demo - The Halls of Wind and Blood")
        await self.run("rm -rf banned-ips.json banned-players.json command_registration.json whitelist.json usercache.json version_history.json cache logs plugins/ChestSort/playerdata Monumenta-White-Demo/advancements Monumenta-White-Demo/playerdata Monumenta-White-Demo/stats Monumenta-White-Demo/DIM-1 Monumenta-White-Demo/DIM1 Monumenta-White-Demo/data")

        # Make a copy of the demo
        await self.run("rm -rf /home/epic/5_SCRATCH/tmpdemo")
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpdemo")
        await self.cd("/home/epic/5_SCRATCH/tmpdemo")
        await self.run(["cp", "-a", "/home/epic/project_epic/Monumenta Demo - The Halls of Wind and Blood", "."])

        # Turn off the whitelist, set it to normal mode, and delete the ops file
        await self.cd("Monumenta Demo - The Halls of Wind and Blood")
        await self.run("perl -p -i -e s|^enforce-whitelist.*$|enforce-whitelist=false|g server.properties")
        await self.run("perl -p -i -e s|^white-list.*$|white-list=false|g server.properties")
        await self.run("perl -p -i -e s|^difficulty.*$|difficulty=2|g server.properties")
        await self.run("rm -f ops.json")

        # Package up the release
        await self.cd("/home/epic/5_SCRATCH/tmpdemo")
        await self.run(["zip", "-rq", "/home/epic/4_SHARED/monumenta_demo/Monumenta Demo - The Halls of Wind and Blood V{}.zip".format(version), "Monumenta Demo - The Halls of Wind and Blood"])
        await self.run(["rm", "-rf", "Monumenta Demo - The Halls of Wind and Blood"])

        await self.start("white-demo")

        await self.display("Demo release version V{} generated successfully".format(version))
        await self.display(message.author.mention)

    async def action_broadcastcommand(self, cmd, message):
        '''Sends a command to all shards connected to bungeecord
Syntax:
`{cmdPrefix}broadcastcommand <command>`'''
        commandArgs = message.content[len(self._prefix + cmd)+1:].strip()
        if commandArgs.startswith("/"):
            commandArgs = commandArgs[1:]

        await self.display("Broadcasting command {!r} to all shards".format(commandArgs))
        self._socket.send_packet("*", "monumentanetworkrelay.command", {"command": commandArgs})
