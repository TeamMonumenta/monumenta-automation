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

class FetchResetBundleAction(ShellAction):
    '''Dangerous!
Deletes in-progress terrain reset info on the play server
Downloads the terrain reset bundle from the build server and unpacks it'''
    command = "fetch reset bundle"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])

        estimated_space_left = get_available_storage('/')
        # Multiplier roughly accounts for compression; 3x is more accurate, 4x is to be safe.
        estimated_space_left -= 4 * get_size("/home/rock/4_SHARED/project_epic_build_template_pre_reset_" + datestr() + ".tgz")

        if estimated_space_left < min_free_gb * bytes_per_gb:
            self._commands = [self.display("Estimated less than {} GB disk space free after operation ({} GB), aborting.".format(min_free_gb, estimated_space_left // bytes_per_gb)),]
            return

        self._commands = [
            self.display("Unpacking reset bundle..."),
            self.run("rm -rf /home/rock/5_SCRATCH/tmpreset", None),
            self.run("mkdir -p /home/rock/5_SCRATCH/tmpreset"),
            self.cd("/home/rock/5_SCRATCH/tmpreset"),
            self.run("tar xzf /home/rock/4_SHARED/project_epic_build_template_pre_reset_" + datestr() + ".tgz"),
            self.display("Build server template data retrieved and ready for reset."),
            self.mention(),
        ]
allActions.append(FetchResetBundleAction)

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

class StageAction(ShellAction):
    '''List and restore pre-terrain reset backups. Intended for use with
the stage servers. NOT YET WORKING.

Syntax:
```
{cmdPrefix}stage list
{cmdPrefix}stage restore <file>
```'''
    command = "stage"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command)+1:].split()
        usage = [
            self.display('''Syntax:
```
`{cmdPrefix}stage list`
`{cmdPrefix}stage restore <file>`
```'''.replace('{cmdPrefix}',cmdPrefix)),
        ]
        botName = botConfig["name"]
        playName = botName.replace("stage","play")
        if len(commandArgs) == 0:
            self._commands = usage
        elif commandArgs[0] == 'list':
            self._commands = [
                self.cd("/home/rock/4_SHARED/"),
                self.run("ls project_epic_pre_reset_{server}_* | sed 's/project_epic_pre_reset_{server}_//' | sed 's/.tgz//'".replace('{server}',playName), displayOutput=True),
            ]
        elif commandArgs[0] == 'restore':
            if len(commandArgs) < 2:
                self._commands = usage
            else:
                self._commands = [
                    self.cd("/home/rock/"),
                    self.run("rm -rf /home/rock/project_epic"),
                    self.run("tar xzf 4_SHARED/project_epic_pre_reset_{server}_{file}.tgz".replace('{server}',playName).replace('{file}',commandArgs[1])),
                    self.display("Restored {file}".replace('{file}',commandArgs[1])),
                ]
        else:
            self._commands = usage
allActions.append(StageAction)

class StopAndBackupAction(ShellAction):
    '''Dangerous!
Brings down all play server shards and backs them up in preparation for terrain reset.
DELETES TUTORIAL AND PURGATORY AND DUNGEON CORE PROTECT DATA'''
    command = "stop and backup"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])

        estimated_space_left = get_available_storage('/')

        if estimated_space_left < min_free_gb * bytes_per_gb:
            self._commands = [self.display("Estimated less than {} GB disk space free after operation ({} GB), aborting.".format(min_free_gb, estimated_space_left // bytes_per_gb)),]
            return

        allShards = botConfig["shards"].keys()
        self._commands = [
            self.display("Stopping all shards..."),
            self.run("mark2 sendall ~stop", None),
            self.sleep(10),
            # TODO: These three commands need to be replaced with one that actually checks everything is down
            self.run("mark2 list", displayOutput=True),
            self.run("mark2 send -n region_1 test", 1),
            self.sleep(5),

            self.display("Removing unneeded large files..."),
            self.run("rm -rf /home/rock/project_epic/white/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/orange/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/magenta/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/lightblue/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/yellow/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/lime/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/pink/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/gray/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/lightgray/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/cyan/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/nightmare/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/r1bonus/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/tutorial/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/purgatory/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/roguelike/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/sanctum/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/region_1/plugins/FastAsyncWorldEdit/clipboard"),
            self.run("rm -rf /home/rock/project_epic/region_2/plugins/FastAsyncWorldEdit/clipboard"),
            self.run("rm -rf /home/rock/project_epic/region_1/plugins/FastAsyncWorldEdit/history"),
            self.run("rm -rf /home/rock/project_epic/region_2/plugins/FastAsyncWorldEdit/history"),
            self.run("rm -rf /home/rock/project_epic/region_1/plugins/FastAsyncWorldEdit/sessions"),
            self.run("rm -rf /home/rock/project_epic/region_2/plugins/FastAsyncWorldEdit/sessions"),
            self.run("rm -rf /home/rock/project_epic/*/cache"),
            self.run("rm -rf /home/rock/project_epic/purgatory /home/rock/project_epic/tutorial"),

            self.display("Performing backup..."),
        ]
        if "region_1" in allShards:
            self._commands += [
                self.run("cp -a /home/rock/project_epic/region_1/banned-ips.json /home/rock/4_SHARED/op-ban-sync/region_1/"),
                self.run("cp -a /home/rock/project_epic/region_1/banned-players.json /home/rock/4_SHARED/op-ban-sync/region_1/"),
                self.run("cp -a /home/rock/project_epic/region_1/ops.json /home/rock/4_SHARED/op-ban-sync/region_1/"),
            ]
        self._commands += [
            self.cd("/home/rock"),
            self.run("tar czf /home/rock/1_ARCHIVE/project_epic_pre_reset_" + botConfig["name"] + "_" + datestr() + ".tgz project_epic"),

            self.display("Backups complete! Ready for reset."),
            self.mention(),
        ]
allActions.append(StopAndBackupAction)

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

class TerrainResetAction(ShellAction):
    '''Dangerous!
Performs the terrain reset on the play server. Requires StopAndBackupAction.'''
    command = "terrain reset"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])

        estimated_space_left = get_available_storage('/')
        # There will briefly be 3x project_epic folders, one of which is in 5_SCRATCH.
        estimated_space_left -= 2 * get_size("/home/rock/project_epic")

        if estimated_space_left < min_free_gb * bytes_per_gb:
            self._commands = [self.display("Estimated less than {} GB disk space free after operation ({} GB), aborting.".format(min_free_gb, estimated_space_left // bytes_per_gb)),]
            return

        resetdir = "/home/rock/5_SCRATCH/tmpreset"
        allShards = botConfig["shards"].keys()

        self._commands = [
            # TODO: These three commands need to be replaced with one that actually checks everything is down
            self.run("mark2 list", displayOutput=True),
            self.run("mark2 send -n region_1 test", 1),
            self.sleep(5),

            self.display("Moving the project_epic directory to PRE_RESET"),
            self.run("cp -a /home/rock/5_SCRATCH/tmpreset/TEMPLATE/server_config /home/rock/5_SCRATCH/tmpreset/POST_RESET/"),
            self.run("cp -a /home/rock/5_SCRATCH/tmpreset/TEMPLATE/purgatory /home/rock/5_SCRATCH/tmpreset/POST_RESET/"),
            self.run("mv /home/rock/project_epic /home/rock/5_SCRATCH/tmpreset/PRE_RESET"),
        ]

        if "region_1" in allShards:
            self._commands += [
                self.display("Raffle results:"),
                self.run(_top_level + "/utility_code/raffle_results.py /home/rock/5_SCRATCH/tmpreset/PRE_RESET/region_1/Project_Epic-region_1 2", displayOutput=True),
            ]

        if "bungee" in allShards:
            self._commands += [
                self.display("Moving bungeecord..."),
                self.run("mv /home/rock/5_SCRATCH/tmpreset/PRE_RESET/bungee /home/rock/5_SCRATCH/tmpreset/POST_RESET/"),
            ]

        if "build" in allShards:
            self._commands += [
                self.display("Moving the build shard..."),
                self.run("mv /home/rock/5_SCRATCH/tmpreset/PRE_RESET/build /home/rock/5_SCRATCH/tmpreset/POST_RESET/"),
            ]

        if "tutorial" in allShards:
            self._commands += [
                self.display("Moving the tutorial shard..."),
                self.run("mv /home/rock/5_SCRATCH/tmpreset/TEMPLATE/tutorial /home/rock/5_SCRATCH/tmpreset/POST_RESET/"),
            ]

        self._commands += [
            self.display("Removing pre-reset server_config..."),
            self.run("rm -rf /home/rock/5_SCRATCH/tmpreset/PRE_RESET/server_config"),

            self.display("Running actual terrain reset (this will take a while!)..."),
            self.run(_top_level + "/utility_code/terrain_reset.py " + " ".join(allShards)),
        ]

        for shard in ["r1plots", "betaplots", "region_1"]:
            if shard in allShards:
                self._commands += [
                    self.display("Preserving coreprotect for {0}...".format(shard)),
                    self.run("mkdir -p {0}/POST_RESET/{1}/plugins/CoreProtect".format(resetdir, shard)),
                    self.run("mv {0}/PRE_RESET/{1}/{2} {0}/POST_RESET/{1}/{2}".format(resetdir, shard, "plugins/CoreProtect/database.db")),
                ]

        for shard in ["r1plots", "betaplots", "region_1", "region_2"]:
            if shard in allShards:
                self._commands += [
                    self.display("Preserving warps for {0}...".format(shard)),
                    self.run("mkdir -p {0}/POST_RESET/{1}/plugins/EpicWarps".format(resetdir, shard)),
                    self.run("mv {0}/PRE_RESET/{1}/{2} {0}/POST_RESET/{1}/{2}".format(resetdir, shard, "plugins/EpicWarps/warps.yml")),
                ]

        for shard in allShards:
            if shard in ["build","bungee"]:
                continue
            self._commands += [
                self.run("cp -af /home/rock/4_SHARED/op-ban-sync/region_1/banned-ips.json /home/rock/5_SCRATCH/tmpreset/POST_RESET/{}/".format(shard)),
                self.run("cp -af /home/rock/4_SHARED/op-ban-sync/region_1/banned-players.json /home/rock/5_SCRATCH/tmpreset/POST_RESET/{}/".format(shard)),
                self.run("cp -af /home/rock/4_SHARED/op-ban-sync/region_1/ops.json /home/rock/5_SCRATCH/tmpreset/POST_RESET/{}/".format(shard)),
            ]

        self._commands += [
            self.display("Generating per-shard config..."),
            self.cd("/home/rock/5_SCRATCH/tmpreset/POST_RESET"),
            self.run(_top_level + "/utility_code/gen_server_config.py --play " + " ".join(allShards)),

            # TODO: This should probably print a warning and proceed anyway if some are found
            self.display("Checking for broken symbolic links..."),
            self.run("find /home/rock/5_SCRATCH/tmpreset/POST_RESET -xtype l", displayOutput=True),

            self.display("Renaming the reset directory..."),
            self.run("mv /home/rock/5_SCRATCH/tmpreset/POST_RESET /home/rock/5_SCRATCH/tmpreset/project_epic"),

            self.display("Backing up post-reset artifacts..."),
            self.cd("/home/rock/5_SCRATCH/tmpreset"),
            self.run("tar czf /home/rock/1_ARCHIVE/project_epic_post_reset_" + botConfig["name"] + "_" + datestr() + ".tgz project_epic"),

            self.display("Moving the project_epic result back where it should be..."),
            self.run("mv /home/rock/5_SCRATCH/tmpreset/project_epic /home/rock/"),

            self.display("Done."),
            self.mention(),
        ]

allActions.append(TerrainResetAction)

class ReplaceItemsAndMobsAction(ShellAction):
    '''Runs item and mob replacements on a given shard
Syntax:
`{cmdPrefix}run replacements shard region_1 region_2 orange`'''
    command = "run replacements"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])

        estimated_space_left = get_available_storage('/')

        if estimated_space_left < min_free_gb * bytes_per_gb:
            self._commands = [self.display("Estimated less than {} GB disk space free after operation ({} GB), aborting.".format(min_free_gb, estimated_space_left // bytes_per_gb)),]
            return

        commandArgs = message.content[len(commandPrefix + self.command)+1:].split()

        baseShellCommand = _top_level + "/discord_bots/server_shell_bots/bin/start_shards.sh"
        shellCommand = baseShellCommand
        allShards = botConfig["shards"]
        replace_shards = []

        for arg in commandArgs:
            if arg in allShards.keys():
                replace_shards.append(arg)
            else:
                raise ValueError("Shard {} not available on this server".format(arg))

        if not replace_shards:
            self._commands = [
                self.display("Nothing to do"),
            ]
            return

        self._commands = [
            self.display("Replacing both mobs AND items on [{}]. If this is not what you want, kill the bot with ~restart bot now!".format(" ".join(replace_shards))),
        ]
        for shard in replace_shards:
            base_backup_name = "/home/rock/0_OLD_BACKUPS/Project_Epic-{}_pre_entity_loot_updates_{}".format(shard, datestr())
            self._commands += [
                self.display("Stopping shard {}".format(shard)),
                self.cd(allShards[shard]),
                self.run("mark2 send -n {} ~stop".format(shard), None),
                self.sleep(10),
                self.run("mark2 send -n {} test".format(shard), 1),
                self.run("tar czf {}.tgz Project_Epic-{}".format(base_backup_name, shard)),
                self.run("/home/rock/MCEdit-And-Automation/utility_code/replace_items_in_world.py --world Project_Epic-{} --logfile {}_items.txt".format(shard, base_backup_name), displayOutput=True),
                self.run("/home/rock/MCEdit-And-Automation/utility_code/replace_mobs_in_world.py --world Project_Epic-{} --logfile {}_mobs.txt".format(shard, base_backup_name), displayOutput=True),
                self.run("mark2 start"),
                self.display("Starting shard {}".format(shard)),
            ]
        self._commands.append(self.mention())

allActions.append(ReplaceItemsAndMobsAction)

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
