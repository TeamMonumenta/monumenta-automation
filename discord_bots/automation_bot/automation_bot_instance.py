#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import subprocess
from pprint import pformat

import logging
logger = logging.getLogger(__name__)

# TODO: Move this to config file
_file_depth = 3
_file = os.path.abspath(__file__)
_top_level = os.path.abspath( os.path.join( _file, '../'*_file_depth ) )

BYTES_PER_GB = 1<<30

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../utility_code"))
from lib_py3.loot_table_manager import LootTableManager

from lib_k8s import KubernetesManager
from automation_bot_lib import get_list_match, get_available_storage, datestr

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
    def __init__(self, client, channel, config):
        self._client = client
        self._channel = channel

        try:
            self._name = config["name"]
            self._shards = config["shards"]
            self._prefix = config["prefix"]
            self._project_epic_dir = config["project_epic_dir"]
            self._commands = config["commands"]
            self._permissions = config["permissions"]
            # TODO: Hook this up to something
            self._debug = True
            self._listening = Listening()
            self._k8s = KubernetesManager(config["k8s_namespace"])
        except KeyError as e:
            sys.exit('Config missing key: {}'.format(e))

    async def handle_message(self, message):
        always_listening_commands = [
            "select",
        ]

        commands = {
            "test": self.action_test,
            "testpriv": self.action_test_priv,
            "testunpriv": self.action_test_unpriv,
            "select": self.action_select_bot,

            "list shards": self.action_list_shards,
            "start shard": self.action_start_shard,
            "stop shard": self.action_stop_shard,

            "update item": self.action_update_item,

            "generate instances": self.action_generate_instances,
            "prepare reset bundle": self.action_prepare_reset_bundle,
        }

        msg = message.content

        if msg.strip()[0] != self._prefix:
            return

        match = None
        for command in commands:
            if msg[1:].startswith(command):
                match = command
        if match is None:
            # TODO HELP GOES HERE
            return

        if (match not in always_listening_commands) and not self._listening.isListening(message):
            return

        try:
            self.checkPermissions(match, message.author)
            await commands[match](match, message)
        except PermissionsError as e:
            await message.channel.send("Sorry " + message.author.mention + ", you do not have permission to run this command")


    ################################################################################
    # Permissions

    def checkPermissions(self, command, author):
        logger.debug("author.id = {}".format(author.id))
        user_info = self._permissions["users"].get( author.id, {"rights":["@everyone"]} )
        logger.debug("User info = {}".format(pformat(user_info)))
        # This is a copy, not a reference
        user_rights = list(user_info.get("rights",["@everyone"]))
        for role in author.roles:
            permGroupName = self._permissions["groups_by_role"].get(role.id,None)
            if permGroupName is not None:
                user_rights = [permGroupName] + user_rights

        self.checkPermissionsExplicitly(command, user_rights)

    # Unlike checkPermissions, this does not get assigned to an object.
    # It checks exactly that the user_rights provided can run the command.
    def checkPermissionsExplicitly(self, command, user_rights):
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

        if not result:
            raise PermissionsError()

    async def display_verbatim(text):
        for chunk in split_string(text):
            await self._channel.send("```" + chunk + "```")

    async def cd(self, path):
        if self._debug:
            await self._channel.send("Changing path to `" + path + "`")
        os.chdir(path)

    async def run(self, cmd, ret=0, displayOutput=False):
        splitCmd = cmd.split(' ')
        if self._debug:
            await self._channel.send("Executing: ```" + str(splitCmd) + "```")
        process = await asyncio.create_subprocess_exec(*splitCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        rc = process.returncode

        if self._debug:
            await self._channel.send("Result: {}".format(rc))

        stdout = stdout.decode('utf-8')
        if stdout:
            if self._debug:
                await self._channel.send("stdout from command '{}':".format(cmd))

            if self._debug or displayOutput:
                await self.display_verbatim(stdout)

        stderr = stderr.decode('utf-8')
        if stderr:
            await self._channel.send("stderr from command '{}':".format(cmd))
            await self.display_verbatim(stderr)

        if ret != None and rc != ret:
            raise ValueError("Expected result {}, got result {} while processing '{}'".format(ret, rc, cmd))

        return stdout

    # Permissions
    ################################################################################

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
                await message.channel.send(self._name + " is now listening for commands.")
            else:
                await message.channel.send(self._name + " is no longer listening for commands.")
        elif self._listening.isListening(message):
            await message.channel.send(self._name + " is still listening for commands.")

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

        shards = self._k8s.list()
        # Format of this is:
        # {'bungee': {'available_replicas': 1, 'replicas': 1}
        #  'dungeon': {'available_replicas': 1, 'replicas': 1}
        #  'test': {'available_replicas': 0, 'replicas': 0}}

        await message.channel.send("Shard list: \n{}".format(pformat(shards)))

    async def action_start_shard(self, cmd, message):
        '''Start specified shards.
Syntax:
`{cmdPrefix}start shard *`
`{cmdPrefix}start shard region_1 region_2 orange`'''

        commandArgs = message.content[len(self._prefix + cmd)+1:].split()

        shardsChanged = []
        if '*' in commandArgs:
            for shard in self._shards.keys():
                shardsChanged.append(shard)
                self._k8s.start(shard)
        else:
            for shard in self._shards.keys():
                if shard in commandArgs:
                    shardsChanged.append(shard)
                    self._k8s.start(shard)

        if not shardsChanged:
            await message.channel.send("No specified shards on this server."),
        else:
            await message.channel.send("Started shards [{}]".format(",".join(shardsChanged))),

    async def action_stop_shard(self, cmd, message):
        '''Stop specified shards.
Syntax:
`{cmdPrefix}stop shard *`
`{cmdPrefix}stop shard region_1 region_2 orange`'''

        commandArgs = message.content[len(self._prefix + cmd)+1:].split()

        shardsChanged = []
        if '*' in commandArgs:
            for shard in self._shards.keys():
                shardsChanged.append(shard)
                self._k8s.stop(shard)
        else:
            for shard in self._shards.keys():
                if shard in commandArgs:
                    shardsChanged.append(shard)
                    self._k8s.stop(shard)

        if not shardsChanged:
            await message.channel.send("No specified shards on this server."),
        else:
            await message.channel.send("Stopped shards [{}]".format(",".join(shardsChanged))),

    async def action_generate_instances(self, cmd, message):
        '''Dangerous!
Deletes previous terrain reset data
Temporarily brings down the dungeon shard to generate dungeon instances.
Must be run before preparing the build server reset bundle'''

        # For brevity
        cnl = message.channel

        # TODO Space check
        # estimated_space_left = get_available_storage('/home/epic/4_SHARED')
        # await cnl.send("Space left: {}".format(estimated_space_left // BYTES_PER_GB))
        #if estimated_space_left < min_free_gb * BYTES_PER_GB:
        #    self._commands = [self.display("Estimated less than {} GB disk space free after operation ({} GB), aborting.".format(min_free_gb, estimated_space_left // BYTES_PER_GB)),]
        #    return

        await cnl.send("Cleaning up old terrain reset data...")
        await self.run("rm -rf /home/epic/5_SCRATCH/tmpreset", None)
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset")

        await cnl.send("Stopping the dungeon shard...")
        self._k8s.stop("dungeon")
        await asyncio.sleep(10)
        # TODO: Make sure dungeon stopped

        await cnl.send("Copying the dungeon master copies...")
        await self.run("cp -a /home/epic/project_epic/dungeon/Project_Epic-dungeon /home/epic/5_SCRATCH/tmpreset/Project_Epic-dungeon")

        await cnl.send("Restarting the dungeon shard...")
        await self.cd("/home/epic/project_epic/dungeon")
        self._k8s.start("dungeon")
        # TODO: Make sure dungeon started

        await cnl.send("Generating dungeon instances (this may take a while)...")
        await self.run(_top_level + "/utility_code/dungeon_instance_gen.py")
        await self.run("mv /home/epic/5_SCRATCH/tmpreset/dungeons-out /home/epic/5_SCRATCH/tmpreset/TEMPLATE")

        await cnl.send("Cleaning up instance generation temp files...")
        await self.run("rm -rf /home/epic/5_SCRATCH/tmpreset/Project_Epic-dungeon")
        await cnl.send("Dungeon instance generation complete!")
        await cnl.send(message.author.mention)

    async def action_prepare_reset_bundle(self, cmd, message):
        '''Dangerous!
Temporarily brings down the region_1 and region_2 shards to prepare for terrain reset
Packages up all of the pre-reset server components needed by the play server for reset
Must be run before starting terrain reset on the play server'''

        # For brevity
        cnl = message.channel

        # TODO Space check

        await cnl.send("Stopping region_1 and region_2...")
        self._k8s.stop("region_1")
        self._k8s.stop("region_2")
        await asyncio.sleep(10)
        # TODO: Make sure shards stopped

        await cnl.send("Copying region_1...")
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset/POST_RESET")
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset/TEMPLATE/region_1")
        await self.run("cp -a /home/epic/project_epic/region_1/Project_Epic-region_1 /home/epic/5_SCRATCH/tmpreset/TEMPLATE/region_1/")

        await cnl.send("Restarting the region_1 shard...")
        self._k8s.start("region_1")

        await cnl.send("Copying region_2...")
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset/POST_RESET")
        await self.run("mkdir -p /home/epic/5_SCRATCH/tmpreset/TEMPLATE/region_2")
        await self.run("cp -a /home/epic/project_epic/region_2/Project_Epic-region_2 /home/epic/5_SCRATCH/tmpreset/TEMPLATE/region_2/")

        await cnl.send("Restarting the region_2 shard...")
        self._k8s.start("region_2")

        await cnl.send("Copying bungee...")
        await self.run("cp -a /home/epic/project_epic/bungee /home/epic/5_SCRATCH/tmpreset/TEMPLATE/")

        await cnl.send("Copying purgatory...")
        await self.run("cp -a /home/epic/project_epic/purgatory /home/epic/5_SCRATCH/tmpreset/TEMPLATE/")

        await cnl.send("Copying server_config...")
        await self.run("cp -a /home/epic/project_epic/server_config /home/epic/5_SCRATCH/tmpreset/TEMPLATE/")

        await cnl.send("Packaging up reset bundle...")
        await self.cd("/home/epic/5_SCRATCH/tmpreset")
        await self.run("tar czf /home/epic/4_SHARED/project_epic_build_template_pre_reset_" + datestr() + ".tgz POST_RESET TEMPLATE")

        await cnl.send("Reset bundle ready!")
        await cnl.send(message.author.mention)

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
            await message.channel.send("Item argument required")
            return
        if '{' not in commandArgs:
            await message.channel.send("Item must be of the form minecraft:id{nbt}")
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
        locations = mgr.update_item_in_loot_tables(item_id, item_nbt_str=item_nbt_str)

        await message.channel.send("Updated item in loot tables:```" + "\n".join(locations) + "```"),
