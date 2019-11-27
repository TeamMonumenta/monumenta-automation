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
        self._prev_entries = []
        self._current_index = None
        self._num_help_prompts = 0
        self._last_active_time = datetime.datetime.now()

        # Constant settings
        self._max_auto_help_prompts = 2
        self._max_inactive_seconds = 60 * 60 * 6

    async def send_first_message(self, message):
        await(self.reply(message, "Started interactive session with {} entries".format(len(self._entries))))

        # Send the first message
        index, entry = self._entries.pop(0)
        self._prev_entries.insert(0, (index, entry))
        entry_text, embed = await self._db.format_entry(index, entry, include_reactions=True)
        msg = await message.channel.send(entry_text, embed=embed);

        self._current_index = index

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
            "assign": self._db.cmd_assign,
            "unassign": self._db.cmd_unassign,
            "help": cmd_help,
            "next": None,
            "prev": None,
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

            if match == "next" or match == "prev":
                # Parse args to next as a counter
                args = ""
                if len(part) > 1:
                    args = part[1].strip()

                try:
                    count = int(args)
                except:
                    count = 1
                if count < 1:
                    count = 1

            if match == "stop":
                await(self.reply(message, "Iteration aborted"))
                raise EOFError

            elif match == "next":
                # Pop that many entries off the next list
                while count > 0:
                    count -= 1
                    if len(self._entries) <= 0:
                        # Nothing left to do here
                        await(self.reply(message, "No more results to display"))
                        raise EOFError

                    # Print the next entry
                    index, entry = self._entries.pop(0)
                    self._prev_entries.insert(0, (index, entry))
                    self._current_index = index

                entry_text, embed = await self._db.format_entry(index, entry, include_reactions=True)
                msg = await message.channel.send(entry_text, embed=embed);

            elif match == "prev":
                if len(self._prev_entries) < 2:
                    # _prev_entries list always needs to contain at least one thing
                    # which is the "current" thing being considered
                    await(self.reply(message, "Nothing to go back to"))
                else:
                    # _prev_entries contains at least two things (previous things, current thing)

                    # Pop that many entries off the prev list and back onto the next list
                    while count > 0:
                        count -= 1
                        if len(self._prev_entries) < 2:
                            # Nothing left to do here
                            await(self.reply(message, "Reached beginning of list"))
                            break

                        self._entries.insert(0, self._prev_entries.pop(0))

                    index, entry = self._prev_entries[0]
                    self._current_index = index
                    entry_text, embed = await self._db.format_entry(index, entry, include_reactions=True)
                    msg = await message.channel.send(entry_text, embed=embed);

            elif match != "next":
                # An actual command
                args = ""
                if len(part) > 1:
                    args = part[1].strip()

                try:
                    await commands[match](message, (str(self._current_index) + " " + args).strip())
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

