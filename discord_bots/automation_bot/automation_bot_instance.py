#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import subprocess
import json
import re
import tempfile
import numpy

from collections import OrderedDict
from pprint import pformat

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# TODO: Move this to config file
_file_depth = 3
_file = os.path.abspath(__file__)
_top_level = os.path.abspath( os.path.join( _file, '../'*_file_depth ) )

BYTES_PER_GB = 1<<30

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../utility_code"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from lib_py3.raffle import vote_raffle
from lib_py3.scoreboard import Scoreboard
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.common import parse_name_possibly_json
from lib_py3.lib_k8s import KubernetesManager

from automation_bot_lib import get_list_match, get_available_storage, datestr, split_string
from quarry.types.text_format import unformat_text
from quarry.types import nbt

class Listening():
    def __init__(self):
        self._set = set()

    def isListening(self, key):
        logger.debug("Listening _set: {}".format(pformat(self._set)))
        logger.debug("Listening key: {}".format(pformat(key)))
        if type(key) is not tuple:
            key = (key.channel.id, key.author.id)
        return key not in self._set

    def select(self, key):
        if type(key) is not tuple:
            key = (key.channel.id, key.author.id)
        self._set.remove(key)

    def deselect(self, key):
        if type(key) is not tuple:
            key = (key.channel.id, key.author.id)
        self._set.add(key)

    def set(self, key, value):
        if value:
            self.select(key)
        else:
            self.deselect(key)

    def toggle(self, key):
        if type(key) is not tuple:
            key = (key.channel.id, key.author.id)
        if self.isListening(key):
            self.deselect(key)
        else:
            self.select(key)

class PermissionsError(Exception):
   """Raised when a user does not have permission to run a command"""
   pass

class AutomationBotInstance(object):

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

            "verbose": self.action_verbose,
            "test": self.action_test,
            "testpriv": self.action_test_priv,
            "testunpriv": self.action_test_unpriv,

            "list shards": self.action_list_shards,
            "start": self.action_start,
            "stop": self.action_stop,
            "restart": self.action_restart,

            #"address to english": self.action_address_to_english, # Not working yet
            "plot get": self.action_plot_get,
            "view scores": self.action_view_scores,

            "update item": self.action_update_item,
            "run replacements": self.action_run_replacements,
            "find loot problems": self.action_find_loot_problems,

            "generate instances": self.action_generate_instances,
            "prepare reset bundle": self.action_prepare_reset_bundle,
            "fetch reset bundle": self.action_fetch_reset_bundle,
            "stop and backup": self.action_stop_and_backup,
            "terrain reset": self.action_terrain_reset,
            "get raffle seed": self.action_get_raffle_seed,

            "stage": self.action_stage,
            "generate demo release": self.action_gen_demo_release,
        }

        try:
            self._name = config["name"]
            self._shards = config["shards"]
            self._prefix = config["prefix"]
            self._project_epic_dir = config["project_epic_dir"]

            # Remove any commands that aren't available in the config
            for command in dict(self._commands):
                if command not in config["commands"]:
                    self._commands.pop(command)

            for command in config["commands"]:
                if command not in self._commands:
                    logger.warn("Command '{}' specified in config but does not exist".format(command))

            self._permissions = config["permissions"]
            self._debug = False
            self._listening = Listening()
            self._k8s = KubernetesManager(config["k8s_namespace"])
        except KeyError as e:
            sys.exit('Config missing key: {}'.format(e))

    async def handle_message(self, message):

        msg = message.content

        if msg.strip()[0] != self._prefix:
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
        user_info = self._permissions["users"].get( author.id, {"rights":["@everyone"]} )
        logger.debug("User info = {}".format(pformat(user_info)))
        # This is a copy, not a reference
        user_rights = list(user_info.get("rights",["@everyone"]))
        for role in author.roles:
            permGroupName = self._permissions["groups_by_role"].get(role.id,None)
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
            givenPerm = ( perm[0] == "+" )
            if (
                perm[1:] == command or
                perm[1:] == "*"
            ):
                result = givenPerm

        return result

    async def display_verbatim(self, text):
        for chunk in split_string(text):
            await self._channel.send("```" + chunk + "```")

    async def debug(self, text):
        logger.debug(text)
        if self._debug:
            await self._channel.send(text)

    async def cd(self, path):
        await self.debug("Changing path to `" + path + "`")
        os.chdir(path)

    async def display(self, msg):
        await self._channel.send(msg)

    async def run(self, cmd, ret=0, displayOutput=False):
        if not type(cmd) is list:
            # For simple stuff, splitting on spaces is enough
            splitCmd = cmd.split(' ')
        else:
            # For complicated stuff, the caller must split appropriately
            splitCmd = cmd
        await self.debug("Executing: ```" + str(splitCmd) + "```")
        process = await asyncio.create_subprocess_exec(*splitCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        rc = process.returncode

        await self.debug("Result: {}".format(rc))

        stdout = stdout.decode('utf-8')
        if stdout:
            await self.debug("stdout from command '{}':".format(cmd))
            logger.debug(stdout)

            if self._debug or displayOutput:
                await self.display_verbatim(stdout)

        stderr = stderr.decode('utf-8')
        if stderr:
            await self._channel.send("stderr from command '{}':".format(cmd))
            await self.display_verbatim(stderr)

        if ret != None and rc != ret:
            raise ValueError("Expected result {}, got result {} while processing '{}'".format(ret, rc, cmd))

        return stdout

    async def stop(self, shards):
        if not type(shards) is list:
            shards=[shards,]
        await self.debug("Stopping shards [{}]...".format(",".join(shards)))
        await self._k8s.stop(shards)
        await self.debug("Stopped shards [{}]".format(",".join(shards)))

    async def start(self, shards):
        if not type(shards) is list:
            shards=[shards,]
        await self.debug("Starting shards [{}]...".format(",".join(shards)))
        await self._k8s.start(shards)
        await self.debug("Started shards [{}]".format(",".join(shards)))

    async def restart(self, shards):
        if not type(shards) is list:
            shards=[shards,]
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
                if not (
                    command == target_command or
                    self._prefix + command == target_command
                ):
                    continue

                helptext = '''__Help on:__'''
                if self.check_permissions(command, message.author):
                    helptext += "\n**" + self._prefix + command + "**"
                else:
                    helptext += "\n~~" + self._prefix + command + "~~"
                helptext += "```" + self._commands[command].__doc__.replace('{cmdPrefix}',self._prefix) + "```"

            if helptext is None:
                helptext = '''Command '{}' does not exist!'''.format(target_command)

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

        if (
            (
                '*' in commandArgs or
                self._name in commandArgs
            ) ^
            self._listening.isListening(message)
        ):
            self._listening.toggle(message)
            if self._listening.isListening(message):
                await self.display(self._name + " is now listening for commands.")
            else:
                await self.display(self._name + " is no longer listening for commands.")
        elif self._listening.isListening(message):
            await self.display(self._name + " is still listening for commands.")

    # Always listening actions
    ################################################################################

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

        shards = await self._k8s.list()
        # Format of this is:
        # {'bungee': {'available_replicas': 1, 'replicas': 1}
        #  'dungeon': {'available_replicas': 1, 'replicas': 1}
        #  'test': {'available_replicas': 0, 'replicas': 0}}

        await message.channel.send("Shard list: \n{}".format(pformat(shards)))

    async def _start_stop_restart_common(self, cmd, message, action):
        arg_str = message.content[len(self._prefix + cmd)+1:].strip()
        if arg_str.startswith("shard "):
            arg_str = arg_str[len("shard "):].strip()
        commandArgs = arg_str.split()

        # Kills the bot, causing k8s to restart it
        if arg_str == 'bot' and (action == self.stop or action == self.restart):
            await message.channel.send("Restarting bot. Note: This will not update the bot's image")
            sys.exit(0)

        shards_changed = []
        if '*' in commandArgs:
            for shard in self._shards.keys():
                shards_changed.append(shard)
        else:
            for shard in self._shards.keys():
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
`{cmdPrefix}start shard region_1 region_2 orange'''
        await self._start_stop_restart_common(cmd, message, self.start)

    async def action_stop(self, cmd, message):
        '''Stop specified shards.
Syntax:
`{cmdPrefix}stop shard *`
`{cmdPrefix}stop shard region_1 region_2 orange'''
        await self._start_stop_restart_common(cmd, message, self.stop)

    async def action_restart(self, cmd, message):
        '''Restart specified shards.
Syntax:
`{cmdPrefix}restart shard *`
`{cmdPrefix}restart shard region_1 region_2 orange'''
        await self._start_stop_restart_common(cmd, message, self.restart)


    async def action_view_scores(self, cmd, message):
        '''View player scores on Region 1. Run without arguements for syntax.
Note: the values from this command could be 15 minutes behind the play server.
Do not use for debugging quests or other scores that are likely to change often.'''

        commandArgs = message.content[len(self._prefix + cmd) + 1:].split()

        cmd_str = os.path.join(_top_level, "utility_code/view_scores.py")
        while len(commandArgs) > 0:
            cmd_str = cmd_str + " " + commandArgs.pop(0)

        await self.run(cmd_str, displayOutput=True),
        await self.display("Done"),


    async def action_generate_instances(self, cmd, message):
        '''Dangerous!
Deletes previous terrain reset data
Temporarily brings down the dungeon shard to generate dungeon instances.
Must be run before preparing the build server reset bundle'''

        # TODO Space check
        # estimated_space_left = get_available_storage('/home/epic/4_SHARED')
        # await self.display("Space left: {}".format(estimated_space_left // BYTES_PER_GB))
        #if estimated_space_left < min_free_gb * BYTES_PER_GB:
        #    self._commands = [self.display("Estimated less than {} GB disk space free after operation ({} GB), aborting.".format(min_free_gb, estimated_space_left // BYTES_PER_GB)),]
        #    return

        await self.display("Cleaning up old terrain reset data...")
        await self.run("rm -rf /home/epic/5_SCRATCH/tmpreset", None)
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset")

        await self.display("Stopping the dungeon shard...")
        await self.stop("dungeon")

        await self.display("Copying the dungeon master copies...")
        await self.run("cp -a /home/epic/project_epic/dungeon/Project_Epic-dungeon /home/epic/5_SCRATCH/tmpreset/Project_Epic-dungeon")

        await self.display("Restarting the dungeon shard...")
        await self.cd("/home/epic/project_epic/dungeon")
        await self.start("dungeon")

        await self.display("Generating dungeon instances (this may take a while)...")
        await self.run(os.path.join(_top_level, "utility_code/dungeon_instance_gen.py"))
        await self.run("mv /home/epic/5_SCRATCH/tmpreset/dungeons-out /home/epic/5_SCRATCH/tmpreset/TEMPLATE")

        await self.display("Cleaning up instance generation temp files...")
        await self.run("rm -rf /home/epic/5_SCRATCH/tmpreset/Project_Epic-dungeon")
        await self.display("Dungeon instance generation complete!")
        await self.display(message.author.mention)

    async def action_prepare_reset_bundle(self, cmd, message):
        '''Dangerous!
Temporarily brings down the region_1 and region_2 shards to prepare for terrain reset
Packages up all of the pre-reset server components needed by the play server for reset
Must be run before starting terrain reset on the play server'''

        # TODO Space check

        await self.display("Stopping region_1 and region_2...")
        await self.stop(["region_1", "region_2"])

        await self.display("Copying region_1...")
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset/TEMPLATE/region_1")
        await self.run("cp -a /home/epic/project_epic/region_1/Project_Epic-region_1 /home/epic/5_SCRATCH/tmpreset/TEMPLATE/region_1/")

        await self.display("Restarting the region_1 shard...")
        await self.start("region_1")

        await self.display("Copying region_2...")
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset/TEMPLATE/region_2")
        await self.run("cp -a /home/epic/project_epic/region_2/Project_Epic-region_2 /home/epic/5_SCRATCH/tmpreset/TEMPLATE/region_2/")

        await self.display("Restarting the region_2 shard...")
        await self.start("region_2")

        await self.display("Copying bungee...")
        await self.run("cp -a /home/epic/project_epic/bungee /home/epic/5_SCRATCH/tmpreset/TEMPLATE/")

        await self.display("Copying purgatory...")
        await self.run("cp -a /home/epic/project_epic/purgatory /home/epic/5_SCRATCH/tmpreset/TEMPLATE/")

        await self.display("Copying server_config...")
        await self.run("cp -a /home/epic/project_epic/server_config /home/epic/5_SCRATCH/tmpreset/TEMPLATE/")

        await self.display("Packaging up reset bundle...")
        await self.cd("/home/epic/5_SCRATCH/tmpreset")
        await self.run("tar czf /home/epic/4_SHARED/project_epic_build_template_pre_reset_" + datestr() + ".tgz TEMPLATE")

        await self.display("Reset bundle ready!")
        await self.display(message.author.mention)

    async def action_fetch_reset_bundle(self, cmd, message):
        '''Dangerous!
Deletes in-progress terrain reset info on the play server
Downloads the terrain reset bundle from the build server and unpacks it'''

        # TODO Space check

        await self.display("Unpacking reset bundle...")
        await self.run("rm -rf /home/epic/5_SCRATCH/tmpreset", None)
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset")
        await self.cd("/home/epic/5_SCRATCH/tmpreset")
        await self.run("tar xzf /home/epic/4_SHARED/project_epic_build_template_pre_reset_" + datestr() + ".tgz")
        await self.display("Build server template data retrieved and ready for reset.")
        await self.display(message.author.mention)

    async def action_stop_and_backup(self, cmd, message):
        '''Dangerous!
Brings down all play server shards and backs them up in preparation for terrain reset.
DELETES DUNGEON CORE PROTECT DATA'''

        # TODO Space check

        allShards = self._shards.keys()

        await self.display("Stopping all shards...")

        shards = await self._k8s.list()

        # Stop all shards
        await self.stop([shard for shard in self._shards.keys() if shard.replace('_', '') in shards])

        # Fail if any shards are still running
        await self.display("Checking that all shards are stopped...")
        shards = await self._k8s.list()
        await self.display(pformat(shards))
        for shard in [shard for shard in self._shards.keys() if shard.replace('_', '') in shards]:
            if shards[shard.replace('_', '')]['replicas'] != 0:
                await self.display("ERROR: shard '{}' is still running!".format(shard))
                await self.display(message.author.mention)
                return

        await self.display("Deleting cache and select FAWE and CoreProtect data...")
        for shard in allShards:
            await self.run("rm -rf /home/epic/project_epic/{}/cache".format(shard))

            if shard not in ["build"]:
                await self.run("rm -rf /home/epic/project_epic/{}/plugins/FastAsyncWorldEdit/clipboard".format(shard))
                await self.run("rm -rf /home/epic/project_epic/{}/plugins/FastAsyncWorldEdit/history".format(shard))
                await self.run("rm -rf /home/epic/project_epic/{}/plugins/FastAsyncWorldEdit/sessions".format(shard))

            if shard not in ["build", "region_1", "plots", "betaplots"]:
                await self.run("rm -rf /home/epic/project_epic/{}/plugins/CoreProtect".format(shard))

        await self.display("Saving ops and banned players")
        await self.run("cp -a /home/epic/project_epic/region_1/banned-ips.json /home/epic/4_SHARED/op-ban-sync/region_1/")
        await self.run("cp -a /home/epic/project_epic/region_1/banned-players.json /home/epic/4_SHARED/op-ban-sync/region_1/")
        await self.run("cp -a /home/epic/project_epic/region_1/ops.json /home/epic/4_SHARED/op-ban-sync/region_1/")

        await self.display("Performing backup...")
        await self.cd("/home/epic")
        await self.run("mkdir -p /home/epic/1_ARCHIVE")
        await self.run("tar --exclude=project_epic/0_PREVIOUS -czf /home/epic/1_ARCHIVE/project_epic_pre_reset_" + datestr() + ".tgz project_epic")

        await self.display("Backups complete! Ready for reset.")
        await self.display(message.author.mention)

    async def action_get_raffle_seed(self, cmd, message):
        '''Gets the current raffle seed based on reactions'''

        if self._rreact["msg_contents"] is not None:
            await self.display("Current raffle seed is: ```{}```".format(self._rreact["msg_contents"]))
        else:
            await self.display("No current raffle seed")

    async def action_terrain_reset(self, cmd, message):
        '''Dangerous!
Performs the terrain reset on the play server. Requires StopAndBackupAction.'''

        allShards = self._shards.keys()

        # TODO Space check

        await self.run("mkdir -p /home/epic/1_ARCHIVE")
        await self.run("mkdir -p /home/epic/0_OLD_BACKUPS")

        # Fail if any shards are still running
        await self.display("Checking that all shards are stopped...")
        shards = await self._k8s.list()
        await self.display(pformat(shards))
        for shard in [shard for shard in self._shards.keys() if shard.replace('_', '') in shards]:
            if shards[shard.replace('_', '')]['replicas'] != 0:
                await self.display("ERROR: shard '{}' is still running!".format(shard))
                await self.display(message.author.mention)
                return

        # Sanity check to make sure this script is going to process everything that it needs to
        files = os.listdir("/home/epic/project_epic")
        for f in files:
            if f not in ["server_config", "0_PREVIOUS"] and f not in allShards:
                await self.display("ERROR: project_epic directory contains file '{}' which will not be processed!".format(f))
                await self.display(message.author.mention)
                return

        # Delete previous reset data and move current data to 0_PREVIOUS
        await self.display("Deleting previous reset data...")
        await self.cd("/home/epic/project_epic")
        await self.run("rm -rf 0_PREVIOUS")
        await self.run("mkdir 0_PREVIOUS")

        # Move everything to 0_PREVIOUS except bungee and build
        await self.display("Moving everything except bungee and build to 0_PREVIOUS...")
        for f in files:
            if f not in ["0_PREVIOUS", "bungee", "build"]:
                await self.run("mv {} 0_PREVIOUS/".format(f))

        await self.display("Getting new server config...")
        await self.run("mv /home/epic/5_SCRATCH/tmpreset/TEMPLATE/server_config /home/epic/project_epic/")

        await self.run("rm -rf /home/epic/project_epic/purgatory/")
        await self.run("mv /home/epic/5_SCRATCH/tmpreset/TEMPLATE/purgatory /home/epic/project_epic/")

        await self.run("rm -rf /home/epic/project_epic/tutorial/")
        await self.run("mv /home/epic/5_SCRATCH/tmpreset/TEMPLATE/tutorial /home/epic/project_epic/")

        ########################################
        # Raffle

        await self.display("Raffle results:")
        raffle_seed = "Default raffle seed"
        if self._rreact["msg_contents"] is not None:
            raffle_seed = self._rreact["msg_contents"]

        scoreboard = Scoreboard("/home/epic/project_epic/0_PREVIOUS/region_1/Project_Epic-region_1/data/scoreboard.dat")
        raffle_results = tempfile.mktemp()
        vote_raffle(raffle_seed, scoreboard, raffle_results, 2)
        await self.run("cat {}".format(raffle_results), displayOutput=True)

        # Raffle
        ########################################

        await self.display("Running actual terrain reset (this will take a while!)...")
        await self.run(os.path.join(_top_level, "utility_code/terrain_reset.py " + " ".join(allShards)))

        for shard in ["plots", "betaplots", "region_1"]:
            await self.display("Preserving coreprotect for {0}...".format(shard))
            await self.run("mkdir -p /home/epic/project_epic/{0}/plugins/CoreProtect".format(shard))
            await self.run("mv /home/epic/project_epic/0_PREVIOUS/{0}/{1} /home/epic/project_epic/{0}/{1}".format(shard, "plugins/CoreProtect/database.db"))

        for shard in ["plots", "betaplots", "region_1", "region_2"]:
            await self.display("Preserving warps for {0}...".format(shard))
            await self.run("mkdir -p /home/epic/project_epic/{0}/plugins/EpicWarps".format(shard))
            await self.run("mv /home/epic/project_epic/0_PREVIOUS/{0}/{1} /home/epic/project_epic/{0}/{1}".format(shard, "plugins/EpicWarps/warps.yml"))

        for shard in allShards:
            if shard in ["build","bungee"]:
                continue

            await self.run("cp -af /home/epic/4_SHARED/op-ban-sync/region_1/banned-ips.json /home/epic/project_epic/{}/".format(shard))
            await self.run("cp -af /home/epic/4_SHARED/op-ban-sync/region_1/banned-players.json /home/epic/project_epic/{}/".format(shard))
            await self.run("cp -af /home/epic/4_SHARED/op-ban-sync/region_1/ops.json /home/epic/project_epic/{}/".format(shard))

        await self.display("Generating per-shard config...")
        await self.cd("/home/epic/project_epic")
        await self.run(os.path.join(_top_level, "utility_code/gen_server_config.py --play " + " ".join(allShards)))

        await self.display("Checking for broken symbolic links...")
        await self.run("find /home/epic/project_epic -xtype l", displayOutput=True)

        await self.display("Backing up post-reset artifacts...")
        await self.cd("/home/epic")
        await self.run("tar --exclude=project_epic/0_PREVIOUS -czf /home/epic/1_ARCHIVE/project_epic_post_reset_" + datestr() + ".tgz project_epic")

        await self.display("Done.")
        await self.display(message.author.mention)

    async def action_stage(self, cmd, message):
        ''' Stops all stage server shards
Copies the current play server over to the stage server.
Archives the previous stage server project_epic contents under project_epic/0_PREVIOUS '''

        # Just in case...
        if "stage" not in self._name:
            raise Exception("WARNING: bot name does not contain 'stage', aborting to avoid mangling real data")

        # TODO Space check

        await self.display("Stopping all stage server shards...")

        shards = await self._k8s.list()

        # Stop all shards
        await self.stop([shard for shard in self._shards.keys() if shard.replace('_', '') in shards])

        await self.action_list_shards("~list shards", message)

        await self.cd("/home/epic/project_epic")
        await self.run("rm -rf 0_PREVIOUS")
        await self.run("mkdir 0_PREVIOUS")

        files = os.listdir(".")
        for f in files:
            if "0_PREVIOUS" not in f:
                await self.run("mv {} 0_PREVIOUS/".format(f))

        files = os.listdir("/home/epic/play/project_epic/")
        for f in files:
            if '0_PREVIOUS' not in f:
                await self.run("cp -a /home/epic/play/project_epic/{} /home/epic/project_epic/".format(f))

        await self.display("Stage server loaded with current play server data")
        await self.display(message.author.mention)

    async def action_update_item(self, cmd, message):
        '''
Updates an item in all loot tables

Usage:
    update item minecraft:leather_leggings{Enchantments:[{lvl:3s,id:"minecraft:fire_protection"}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier III"],color:7352328,Name:"{\"text\":\"§fBurnt Leggings\"}"},Damage:0}

Easiest way to get this info is holding an item in your hand and using /nbti tocommand on a command block

For convenience, leading 'give @p' is ignored, along with any data after the last } (usually the quantity of item from /nbti tocommand)
    '''

        # Check for any arguments
        commandArgs = message.content[len(self._prefix):].strip()
        if len(commandArgs) < len(cmd) + 5:
            await self.display("Item argument required")
            return
        if '{' not in commandArgs:
            await self.display("Item must be of the form minecraft:id{nbt}")
            return

        # Parse id / nbt arguments
        commandArgs = message.content[len(self._prefix) + len(cmd) + 1:]

        partitioned = commandArgs.strip().partition("{")
        item_id = partitioned[0].strip()
        item_nbt_str = partitioned[1] + partitioned[2].strip()

        if item_id.startswith("/"):
            item_id = item_id[1:]
        if item_id.startswith("give @p "):
            item_id = item_id[len("give @p "):]

        if item_nbt_str[-1] != '}':
            item_nbt_str = item_nbt_str[:item_nbt_str.rfind("}") + 1]

        mgr = LootTableManager()
        mgr.load_loot_tables_subdirectories(os.path.join(self._project_epic_dir, "server_config/data/datapacks"))
        try:
            locations = mgr.update_item_in_loot_tables(item_id, item_nbt_str=item_nbt_str)
            await self.display("Updated item in loot tables:```" + "\n".join(locations) + "```")
        except Exception as e:
            await message.channel.send(message.author.mention)
            await message.channel.send("**ERROR**: ```" + str(e) + "```")

            item_nbt = nbt.TagCompound.from_mojangson(item_nbt_str)
            if not item_nbt.has_path("display.Name"):
                ValueError("ERROR: Item has no display name")

            item_name = unformat_text(parse_name_possibly_json(item_nbt.at_path("display.Name").value))
            filename = item_name.lower()
            filename = re.sub(" +", "_", filename)
            filename = "".join([i if re.match('[a-z0-9-_]', i) else '' for i in filename])
            filename = filename + ".json"

            entry_json = OrderedDict()
            entry_json["type"] = "item"
            entry_json["weight"] = 10
            entry_json["name"] = item_id
            entry_json["functions"] = []

            func = OrderedDict()
            func["function"] = "set_nbt"
            func["tag"] = item_nbt_str
            entry_json["functions"].append(func)

            pool = OrderedDict()
            pool["rolls"] = 1
            pool["entries"] = [entry_json, ]

            table_dict = OrderedDict()
            table_dict["pools"] = [pool,]

            loot_table_string = json.dumps(table_dict, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': '))

            await self.display("Here is a basic loot table for this item:\n\n" +
                           "You must put this somewhere **sensible** in the loot tables \n\n" +
                           "Use this filename:```{}```\nContents:```{}```".format(filename, loot_table_string))
            await self.display(message.author.mention)

    async def action_run_replacements(self, cmd, message):
        '''Runs item and mob replacements on a given shard
Syntax:
`{cmdPrefix}run replacements shard region_1 region_2 orange`'''

        # TODO Space check

        commandArgs = message.content[len(self._prefix + cmd)+1:].split()

        replace_shards = []
        for shard in self._shards.keys():
            if shard in commandArgs:
                replace_shards.append(shard)

        if not replace_shards:
            await self.display("Nothing to do")
            return

        await self.display("Replacing both mobs AND items on [{}]".format(" ".join(replace_shards)))

        for shard in replace_shards:
            base_backup_name = "/home/epic/0_OLD_BACKUPS/Project_Epic-{}_pre_entity_loot_updates_{}".format(shard, datestr())

            await self.display("Running replacements on shard {}".format(shard))
            await self.stop(shard)
            await self.cd(self._shards[shard])
            await self.run("tar czf {}.tgz Project_Epic-{}".format(base_backup_name, shard))
            await self.run(os.path.join(_top_level, "utility_code/replace_items_in_world.py --world Project_Epic-{} --logfile {}_items.txt".format(shard, base_backup_name)), displayOutput=True)
            await self.run(os.path.join(_top_level, "utility_code/replace_mobs_in_world.py --world Project_Epic-{} --logfile {}_mobs.txt".format(shard, base_backup_name)), displayOutput=True)
            await self.start(shard)

        await self.display(message.author.mention)

    async def action_address_to_english(self, cmd, message):
        '''Translates R1Address scores into a readable street address.'''
        commandArgs = message.content[len(self._prefix + cmd)+1:]
        await self.display("Please wait...")
        await self.run(os.path.join(_top_level, "utility_code/address_to_english.py {}".format(commandArgs)), 0, displayOutput=True)
        await self.display("Done.")

    async def action_plot_get(self, cmd, message):
        '''Gets information on the plots shard. Run without arguements for options.'''
        commandArgs = message.content[len(self._prefix + cmd)+1:]
        await self.display("Please wait...")
        if len(commandArgs) > 0:
            await self.run(os.path.join(_top_level, "utility_code/plot_get.py {}".format(commandArgs)), 0, displayOutput=True)
        else:
            await self.run(os.path.join(_top_level, "utility_code/plot_get.py"), 0, displayOutput=True)
        await self.display("Done.")

    async def action_find_loot_problems(self, cmd, message):
        '''Finds loot table problems
- Lists containers in dungeons that are missing loot tables.
- TODO: Add more!
'''
        await self.display("Checking for loot table problems...")
        await self.display("Checking for missing dungeon loot tables...")
        await self.run(os.path.join(_top_level, "utility_code/dungeon_find_lootless.py"), 0, displayOutput=True)

    async def action_gen_demo_release(self, cmd, message):
        '''Generates a demo release zip with the specified version
Syntax:
`{cmdPrefix}generate demo release <version>`'''

        commandArgs = message.content[len(self._prefix + cmd)+1:]
        version = "".join([i if re.match('[0-9\.]', i) else '' for i in commandArgs])

        if not version:
            await self.display("Version must be specified and can contain only numbers and periods")
            await self.display(message.author.mention)
            return

        # Test if this version already exists
        try:
            await self.run(["test", "!", "-f", "/home/epic/4_SHARED/monumenta_demo/Monumenta Demo - The Halls of Wind and Blood V{}.zip".format(version)])
        except:
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
