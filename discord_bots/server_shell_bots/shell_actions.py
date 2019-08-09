#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

"""
This is the list of all shell actions available to the discord bots;
Please keep this list in alphabetical order within each category
"""

import os
import sys
from pprint import pformat

import logging
logger = logging.getLogger(__name__)

_file_depth = 3
_file = os.path.abspath(__file__)
_top_level = os.path.abspath( os.path.join( _file, '../'*_file_depth ) )

from shell_common import ShellAction, datestr
from lib_k8s import KubernetesManager

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../utility_code"))
from lib_py3.loot_table_manager import LootTableManager

commandPrefix = '~'

min_free_gb = 30
bytes_per_gb = 1<<30

allActions = []
allActionsDict = {}

def get_size(start_path='.'):
    if os.path.isfile(start_path):
        return os.lstat(start_path).st_size
    total_size = 0
    if os.path.isdir(start_path):
        for dirpath, dirnames, filenames in os.walk(start_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.lstat(start_path).st_size
    return total_size

def get_available_storage(path = '.'):
    size_data = os.statvfs(path)
    block_size = size_data.f_frsize
    blocks_available = size_data.f_bavail
    return block_size * blocks_available

################################################################################
# Common privilege code

################################################################################
# Simple test functions

class DebugAction(ShellAction):
    '''Prints debugging information about the requestor'''
    command = "debug"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])

    async def doActions(self, client, channel, author):
        self._client = client
        self._channel = channel
        self._author = author

        message = "Your user ID is: " + str(author.id) + "\n\nYour roles are:"
        for role in author.roles:
            message += "\n`" + role.name + "`: " + role.id

        message += "\n\nYour access rights are:\n```\n"
        userInfo = privUsers.get( author.id, {"rights":["@everyone"]} )
        userRights = userInfo.get("rights",["@everyone"])

        for role in author.roles:
            permGroupName = groupByRole.get(role.id,None)
            if permGroupName is not None:
                userRights = [permGroupName] + userRights

        groupStack = [ {"index":0,"rights":userRights} ]
        alreadyChecked = set()
        while len(groupStack) > 0:
            depth = len(groupStack)
            group = groupStack[depth-1]
            if group["index"] == len(group["rights"]):
                groupStack.pop()
                continue
            aRight = group["rights"][ group["index"] ]
            group["index"] += 1
            message += "  "*depth + aRight + "\n"
            if (
                aRight[0] == "@" and
                aRight not in alreadyChecked
            ):
                alreadyChecked.add(aRight)
                groupStack.append({"index":0,"rights":permissionGroups[aRight]})
        message += "```"

        await self.display(message),
allActions.append(DebugAction)

################################################################################
# Useful actions start here

class KaulAction(ShellAction):
    '''Tells the kaul role that kaul is starting'''
    command = "kaul"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._config = botConfig

    async def doActions(self, client, channel, author):
        self._client = client
        self._channel = channel
        self._author = author

        for channelId in self._config["channels"]:
            try:
                channel = client.get_channel(channelId)
                await channel.send("this is a test of an upcoming feature")
            except Exception as ex:
                await self.display(channelId + str(ex))
                pass

allActions.append(KaulAction)

class DumpErrorCommandsAction(ShellAction):
    '''Display command blocks with potential errors to:
data/commands_to_update/*.txt'''
    command = "dump error commands"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.run(_top_level + "/utility_code/dump_error_commands.py", displayOutput=True),
        ]
allActions.append(DumpErrorCommandsAction)

class DungeonLootAction(ShellAction):
    '''List the loot tables and items in chests in the dungeons.'''
    command = "dungeon loot"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.run(_top_level + "/utility_code/dungeon_loot_info.py", displayOutput=True),
            self.display("Done."),
        ]
allActions.append(DungeonLootAction)


class GitAction(ShellAction):
    '''Dangerous!
Doesn't have a good way to tell if changes are in progress.
Check in #server-ops before using.

Currently exposes all valid git syntax, including syntax that *will* softlock this action.'''
    command = "git"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])

        estimated_space_left = get_available_storage('/')

        if estimated_space_left < min_free_gb * bytes_per_gb:
            self._commands = [self.display("Estimated less than {} GB disk space free after operation ({} GB), aborting.".format(min_free_gb, estimated_space_left // bytes_per_gb)),]
            return

        commandArgs = message.content[len(commandPrefix):]
        if len(commandArgs) > 3 and commandArgs[3] != ' ':
            self._commands = [
                self.display("Space expected at 4th character past prefix: " + repr(commandArgs)),
            ]
            return
        self._commands = [
            self.cd(_top_level),
            self.display("Running `" + commandArgs + "`"),
            self.run(commandArgs, displayOutput=True),
        ]
allActions.append(GitAction)

class GetErrorsAction(ShellAction):
    '''Get the last minute of error log data from a given shard.

Syntax:
{cmdPrefix}get errors region_1'''
    command = "get errors"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command)+1:].split()

        if len(commandArgs) != 1:
            self._commands = [
                self.display("You must specify exactly one shard per command."),
            ]

        shard = commandArgs[0]
        allShards = botConfig["shards"]
        if shard in allShards.keys():
            self._commands = [
                self.cd(allShards[shard]),
                self.cd("logs"),
                self.run(_top_level + "/discord_bots/server_shell_bots/bin/get_errors.sh", displayOutput=True),
            ]
        else:
            self._commands = [
                self.display("No specified shards on this server."),
            ]
allActions.append(GetErrorsAction)

class RollLootAction(ShellAction):
    '''Generates 1024 loot table chests, "opens" them, and finds the number of items per chest on average.

Syntax:
`{cmdPrefix}roll loot minecraft:empty` Get item odds for this loot table.
`{cmdPrefix}roll loot epic:r1/kits/city_guide/c0 epic:r1/kits/city_guide/c1 minecraft:empty` Get item odds for multiple loot tables.
'''
    command = "roll loot"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = []

        estimated_space_left = get_available_storage('/')

        if estimated_space_left < min_free_gb * bytes_per_gb:
            self._commands = [self.display("Estimated less than {} GB disk space free after operation ({} GB), aborting.".format(min_free_gb, estimated_space_left // bytes_per_gb)),]
            return

        command_args = message.content[len(commandPrefix + self.command)+1:].split()

        if len(command_args) == 0:
            self._commands += [
                self.display(self.__doc__.replace('{cmdPrefix}', commandPrefix)),
            ]

        for loot_table in command_args:
            self._commands += [
                self.display("**{}**".format(loot_table)),
                self.run(_top_level + "/utility_code/loot_table_test_mobs.sh " + loot_table, displayOutput=True),
            ]

        self._commands += [
            self.display("Done."),
        ]
allActions.append(RollLootAction)

class R1AddressToEnglishAction(ShellAction):
    '''Convert R1Address scores to a human-readable format

Syntax:
`{cmdPrefix}r1address to english address1 [address2] ...`'''
    command = "r1address to english"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command)+1:].split()
        cmdString = _top_level + "/utility_code/r1address_to_english.py"
        self._commands = []
        while len(commandArgs) > 0:
            newVal = commandArgs.pop(0)
            try:
                newVal = int(newVal)
                cmdString = cmdString + " " + str(newVal)
            except:
                self.display(repr(newVal) + " is not a number."),
        self._commands = [
            self.run(cmdString, displayOutput=True),
            self.display("Done."),
        ]
allActions.append(R1AddressToEnglishAction)

class R1PlotGetAction(ShellAction):
    '''Get R1Plot address info in a human-readable format, including TP coordinates.
Accepts existing scores or a player to look up.

For syntax, run:
~r1plot get'''
    command = "r1plot get"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command):]
        cmdString = _top_level + "/utility_code/r1plot_get.py"
        self._commands = []
        cmdString += commandArgs
        self._commands = [
            self.run(cmdString, displayOutput=True),
            self.display("Done."),
        ]
allActions.append(R1PlotGetAction)

class SkillInfoAction(ShellAction):
    '''Print out skill info; used to update the public Google spreadsheet.

This will be updated to use the Google Sheets API at some point so it won't need to be updated manually.'''
    command = "skill info"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.run(_top_level + "/utility_code/skill_info.py", displayOutput=True),
        ]
allActions.append(SkillInfoAction)

class StopIn10MinutesAction(ShellAction):
    '''Dangerous!
Starts a bungee shutdown timer for 10 minutes. Returns immediately.'''
    command = "stop in 10 minutes"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Telling bungee it should stop in 10 minutes..."),
            self.run("mark2 send -n bungee ~stop 10m;5m;3m;2m;1m;30s;10s", None),
            self.run("mark2 send -n region_1 co purge t:30d", None),
            self.run("mark2 send -n r1plots co purge t:30d", None),
            self.run("mark2 send -n betaplots co purge t:30d", None),
            # TODO: Something to wait for bungee to shut down
            self.display("Bungee will shut down in 10 minutes."),
            self.sleep(10*60),
            self.display("Bungee should be shutting down."),
            self.mention(),
        ]
allActions.append(StopIn10MinutesAction)

class ViewScoresAction(ShellAction):
    '''View player scores on Region 1. Run without arguements for syntax.
Note: the values from this command could be 15 minutes behind the play server.
Do not use for debugging quests or other scores that are likely to change often.'''
    command = "view scores"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command)+1:].split()
        cmdString = _top_level + "/utility_code/view_scores.py"
        while len(commandArgs) > 0:
            cmdString = cmdString + " " + commandArgs.pop(0)
        self._commands = [
            self.run(cmdString, displayOutput=True),
            self.display("Done."),
        ]
allActions.append(ViewScoresAction)
