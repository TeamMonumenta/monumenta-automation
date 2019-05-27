import datetime
import asyncio
import discord
import os
import json
import sys
import re
import random
from collections import OrderedDict
from pprint import pprint

from common import get_list_match

class InteractiveSearch(object):
    def __init__(self, db, author, entries):
        self._db = db
        self._author_id = author.id
        self._entries = entries
        self._last_index = None
        self._num_help_prompts = 0
        self._last_active_time = datetime.datetime.now()

        # Constant settings
        self._max_auto_help_prompts = 2
        self._max_inactive_seconds = 60 * 30

    async def send_first_message(self, message):
        await(self.reply(message, "Started interactive session with {} entries".format(len(self._entries))))

        # Send the first message
        index, entry = self._entries.pop(0)
        entry_text, embed = await self._db.format_entry(index, entry, include_reactions=True)
        msg = await self._db._client.send_message(message.channel, entry_text, embed=embed);

        self._last_index = index

    async def handle_message(self, message):
        '''
        Returns True if this message was handled here, False otherwise
        '''

        async def cmd_help(message, args):
            await(self.reply(message, "Valid responses are: ```{}```".format(" ".join(commands.keys()))))

        commands = {
            "reject": self._db.cmd_reject,
            "edit": self._db.cmd_edit,
            "append": self._db.cmd_append,
            "fix": self._db.cmd_fix,
            "unfix": self._db.cmd_unfix,
            "help": cmd_help,
            "next": None,
            "stop": None
        }

        if message.author.id == self._author_id:
            # Author matches - attempt to parse this message as a command

            time_delta = datetime.datetime.now() - self._last_active_time
            if (time_delta.total_seconds() > self._max_inactive_seconds):
                await(self.reply(message, "Interactive session aborted due to inactivity"))
                raise EOFError

            part = message.content.split(maxsplit=1)
            if (not message.content) or (len(part) < 1):
                if (self._num_help_prompts < self._max_auto_help_prompts):
                    await(self.reply(message, "Valid responses are: ```{}```".format(" ".join(commands.keys()))))
                    self._num_help_prompts += 1

                    if (self._num_help_prompts == self._max_auto_help_prompts):
                        await(self.reply(message, "To see these options again, say `help`"))
                return False

            match = get_list_match(part[0].strip(), commands.keys())
            if match is None:
                if (self._num_help_prompts < self._max_auto_help_prompts):
                    await(self.reply(message, "Valid responses are: ```{}```".format(" ".join(commands.keys()))))
                    self._num_help_prompts += 1

                    if (self._num_help_prompts == self._max_auto_help_prompts):
                        await(self.reply(message, "To see these options again, use 'help'"))
                return False

            if match == "stop":
                await(self.reply(message, "Iteration aborted"))
                raise EOFError

            elif match == "next":
                if len(self._entries) <= 0:
                    # Nothing left to do here
                    await(self.reply(message, "No more results to display"))
                    raise EOFError

                # Print the next entry
                index, entry = self._entries.pop(0)
                self._last_index = index

                entry_text, embed = await self._db.format_entry(index, entry, include_reactions=True)
                msg = await self._db._client.send_message(message.channel, entry_text, embed=embed);
            elif match != "next":
                # An actual command
                args = ""
                if len(part) > 1:
                    args = part[1].strip()

                try:
                    await commands[match](message, (str(self._last_index) + " " + args).strip())
                except ValueError as e:
                    await self.reply(message, str(e))


            self._last_active_time = datetime.datetime.now()

            return True

        return False

    async def close(self, message):
        # Clear this so it can't trigger anymore
        self._author_id = None
        self._entries = []

    async def reply(self, message, response):
        await self._db.reply(message, response)

