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
from automation_bot_lib import get_list_match, get_available_storage, display_verbatim

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
    def __init__(self, client, config):
        self._client = client

        try:
            self._name = config["name"]
            self._shards = config["shards"]
            self._prefix = config["prefix"]
            self._commands = config["commands"]
            self._permissions = config["permissions"]
            # TODO: Hook this up to something
            self._debug = True
            self._listening = Listening()
            self._k8s = KubernetesManager()
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
            "generate instances": self.action_generate_instances,
        }

        part = message.content.split(maxsplit=2)
        if (not message.content) or (len(part) < 1):
            return

        if part[0].strip()[0] != self._prefix:
            return

        match = get_list_match(part[0][1:].strip(), commands.keys())
        if match is None:
            # TODO HELP GOES HERE
            return

        if not (self._listening.isListening(message) or match in always_listening_commands):
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

    async def cd(self, channel, path):
        if self._debug:
            await channel.send("Changing path to `" + path + "`")
        os.chdir(path)

    async def run(self, channel, cmd, ret=0, displayOutput=False):
        splitCmd = cmd.split(' ')
        if self._debug:
            await channel.send("Executing: ```" + str(splitCmd) + "```")
        process = await asyncio.create_subprocess_exec(*splitCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        rc = process.returncode

        if self._debug:
            await channel.send("Result: {}".format(rc))

        stdout = stdout.decode('utf-8')
        if stdout:
            if self._debug:
                await channel.send("stdout from command '{}':".format(cmd))

            if self._debug or displayOutput:
                await display_verbatim(channel, stdout)

        stderr = stderr.decode('utf-8')
        if stderr:
            await channel.send("stderr from command '{}':".format(cmd))
            await display_verbatim(channel, stderr)

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
                await message.channel.send(self._name + " is now listening for commands."),
            else:
                await message.channel.send(self._name + " is no longer listening for commands."),
        elif self._listening.isListening(message):
            await message.channel.send(self._name + " is still listening for commands."),

    async def action_test(self, cmd, message):
        '''Simple test action that does nothing'''

        await message.channel.send("Testing successful!"),

    async def action_test_priv(self, cmd, message):
        '''Test if user has permission to use restricted commands'''

        await message.channel.send("You've got the power"),

    async def action_test_unpriv(self, cmd, message):
        '''Test that a restricted command fails for all users'''

        await message.channel.send("BUG: You definitely shouldn't have this much power"),

    async def action_list_shards(self, cmd, message):
        '''Lists currently running shards on this server'''

        shards = self._k8s.list()
        # Format of this is:
        # {'bungee': {'available_replicas': 1, 'replicas': 1},
        #  'dungeon': {'available_replicas': 1, 'replicas': 1}
        #  'test': {'available_replicas': 0, 'replicas': 0}}

        await message.channel.send("Shard list: \n{}".format(pformat(shards))),

    async def action_generate_instances(self, cmd, message):
        '''Dangerous!
    Deletes previous terrain reset data
    Temporarily brings down the dungeon shard to generate dungeon instances.
    Must be run before preparing the build server reset bundle'''

        # For brevity
        cnl = message.channel

        estimated_space_left = get_available_storage('/home/epic/4_SHARED')
        await cnl.send("Space left: {}".format(estimated_space_left // BYTES_PER_GB))

        # TODO
        #if estimated_space_left < min_free_gb * BYTES_PER_GB:
        #    self._commands = [self.display("Estimated less than {} GB disk space free after operation ({} GB), aborting.".format(min_free_gb, estimated_space_left // BYTES_PER_GB)),]
        #    return

        await cnl.send("Cleaning up old terrain reset data..."),
        await self.run(cnl, "rm -rf /home/epic/5_SCRATCH/tmpreset", None),
        await self.run(cnl, "mkdir -p /home/epic/5_SCRATCH/tmpreset"),

        await cnl.send("Stopping the dungeon shard..."),
        self._k8s.stop("dungeon")
        await asyncio.sleep(10),
        # TODO: Make sure dungeon stopped

        await cnl.send("Copying the dungeon master copies..."),
        await self.run(cnl, "cp -a /home/epic/project_epic/dungeon/Project_Epic-dungeon /home/epic/5_SCRATCH/tmpreset/Project_Epic-dungeon"),

        await cnl.send("Restarting the dungeon shard..."),
        await self.cd(cnl, "/home/epic/project_epic/dungeon"),
        self._k8s.start("dungeon")
        # TODO: Make sure dungeon started

        await cnl.send("Generating dungeon instances (this may take a while)..."),
        await self.run(cnl, _top_level + "/utility_code/dungeon_instance_gen.py"),
        await self.run(cnl, "mv /home/epic/5_SCRATCH/tmpreset/dungeons-out /home/epic/5_SCRATCH/tmpreset/TEMPLATE"),

        await cnl.send("Cleaning up instance generation temp files..."),
        await self.run(cnl, "rm -rf /home/epic/5_SCRATCH/tmpreset/Project_Epic-dungeon"),
        await cnl.send("Dungeon instance generation complete!"),
        await self.mention(),
