#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import os
import sys
from pprint import pformat

import logging
logger = logging.getLogger(__name__)

# TODO: Move this to config file
_file_depth = 3
_file = os.path.abspath(__file__)
_top_level = os.path.abspath( os.path.join( _file, '../'*_file_depth ) )

from lib_k8s import KubernetesManager

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../utility_code"))
from lib_py3.loot_table_manager import LootTableManager

from automation_bot_lib import get_list_match

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
            await commands[match](match, message)
        except PermissionsError as e:
            await message.channel.send("Sorry " + message.author.mention + ", you do not have permission to run this command")
        except ValueError as e:
            await message.channel.send(message, str(e))


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
        self.checkPermissions(cmd, message.author)

        commandArgs = message.content[len(self._prefix + cmd) + 1:].split()

        self._commands = []
        if (
            (
                '*' in commandArgs or
                self._name in commandArgs
            ) ^
            self._listening.isListening(message)
        ):
            self._listening.toggle(message)
            if self._listening.isListening(message):
                self._commands = [
                    await message.channel.send(self._name + " is now listening for commands."),
                ]
            else:
                self._commands = [
                    await message.channel.send(self._name + " is no longer listening for commands."),
                ]
        elif self._listening.isListening(message):
            self._commands = [
                await message.channel.send(self._name + " is still listening for commands."),
            ]

    async def action_test(self, cmd, message):
        '''Simple test action that does nothing'''

        await message.channel.send("Testing successful!"),

    async def action_test_priv(self, cmd, message):
        '''Test if user has permission to use restricted commands'''

        self.checkPermissions(cmd, message.author)
        await message.channel.send("You've got the power"),

    async def action_test_unpriv(self, cmd, message):
        '''Test that a restricted command fails for all users'''

        self.checkPermissions(cmd, message.author)
        await message.channel.send("BUG: You definitely shouldn't have this much power"),

    async def action_list_shards(self, cmd, message):
        '''Lists currently running shards on this server'''

        self.checkPermissions(cmd, message.author)

        shards = self._k8s.list()
        # Format of this is:
        # {'bungee': {'available_replicas': 1, 'replicas': 1},
        #  'dungeon': {'available_replicas': 1, 'replicas': 1}
        #  'test': {'available_replicas': 0, 'replicas': 0}}

        await message.channel.send("Shard list: \n{}".format(pformat(shards))),
