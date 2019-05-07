import asyncio
import discord
import os
import json
import sys
import re
import random
from collections import OrderedDict
from pprint import pprint


# Data Schema

'''
entries = {
    # Key is entry number - fixed forever. Key is a string representation of an integer... for reasons.
    "42" : {
        "author": "302298391969267712", # Must be non-empty and a valid discord user
        "description": "Stuff", # Must be non-empty, escape input strings/etc.
        "labels": ["Misc"], # Must be non-empty
        # Automatically set to "N/A" on creation
        "priority": "High", # Case sensitive for matching, do case insensitive compare for input

        # Optional:
        "image": None, # Might be None OR not present at all

        # If this is present, the item is closed
        "close_reason": "string"

        # Automatically added/managed
        "message_id": <discord message ID>
    }
]
'''

class TaskDatabase(object):
    def __init__(self, client, config):
        """
        """
        self._client = client

        # Sanity check:
        for key in ["bot_input_channels", "channel_id", "user_privileges", "group_privileges"]:
            if key not in config:
                sys.exit('Config missing key: {}'.format(key))

        self._user_privileges = config["user_privileges"]
        self._group_privileges = config["group_privileges"]
        self._channel_id = config["channel_id"]
        self._prefix = config["prefix"]
        self._descriptor_single = config["descriptor_single"]
        self._descriptor_plural = config["descriptor_plural"]
        self._descriptor_proper = config["descriptor_proper"]
        self._channel = None
        self._database_path = config["database_path"]
        self.load()

    def save(self):
        savedata = {
            'entries': self._entries,
            'next_index': self._next_index,
            'labels': self._labels,
            'priorities': self._priorities,
        }

        with open(self._database_path, 'w') as f:
            json.dump(savedata, f, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': '))

    def load(self):
        if not os.path.exists(self._database_path):
            self._entries = {}
            self._next_index = 1
            self._labels = [
                "misc",
            ]
            self._priorities = [
                "N/A",
                "Critical",
                "High",
                "Medium",
                "Low",
                "Zero",
            ]
            self.save()
        else:
            with open(self._database_path, 'r') as f:
                data = json.load(f)

            self._entries = data['entries']
            self._next_index = data['next_index']
            # TODO: Scan through and add all labels
            self._labels = data['labels']
            self._priorities = data['priorities']

    async def reply(self, message, response):
        """
        Replies to a given message (in that channel)
        """
        await self._client.send_message(message.channel, response)

    def has_privilege(self, min_privilege, author, index=None):
        priv = 0; # Everyone has this level

        # Get privilege based on user list
        priv = max(priv, self._user_privileges.get(author.id, 0))

        # Get privilege based on group role
        for role in author.roles:
            priv = max(priv, self._group_privileges.get(role.id, 0))

        # Get privilege based on entry ownership
        if index is not None:
            entry = self._entries.get(index, None)
            if entry is not None:
                if entry["author"] == author.id:
                    priv = max(priv, 1)

        return priv >= min_privilege

    def add_entry(self, description, labels=["misc"], author=None, image=None, priority="N/A"):
        entry = {
            "description": description,
            "labels": labels,
        }

        if author is None:
            entry["author"] = 0
        else:
            entry["author"] = author.id

        if image is not None:
            entry["image"] = image

        if priority is not None:
            entry["priority"] = priority

        index = self._next_index

        self._next_index += 1
        self._entries[str(index)] = entry

        self.save()

        return (index, entry)

    async def format_entry(self, index, entry):
        author_id = entry["author"]
        if author_id != 0 and author_id != "0":
            author_name = (await self._client.get_user_info(author_id)).display_name
        else:
            author_name = ""

        entry_text = '''`
#{} [{} - {}] {}`
{}'''.format(index, ','.join(entry["labels"]), entry["priority"], author_name, entry["description"])

        if "close_reason" in entry:
            entry_text = '''~~{}~~
Closed: {}'''.format(entry_text, entry["close_reason"])

        embed = None
        if "image" in entry:
            embed = discord.Embed()
            embed.set_image(url=entry["image"])

        return entry_text, embed

    async def send_entry(self, index, entry):
        # Fetch the channel if not already stored
        if self._channel is None:
            self._channel = self._client.get_channel(self._channel_id)
            if self._channel is None:
                raise Exception("Error getting channel!")

        # Compute the new entry text
        entry_text, embed = await self.format_entry(index, entry)

        msg = None
        if "message_id" in entry:
            try:
                msg = await self._client.get_message(self._channel, entry["message_id"])
            except:
                pass

        if msg is not None:
            # Edit the existing message
            await self._client.edit_message(msg, entry_text, embed=embed)

        else:
            # Send a new message
            msg = await self._client.send_message(self._channel, entry_text, embed=embed);
            entry["message_id"] = msg.id
            self.save()

        await self._client.add_reaction(msg, "\U0001f44d")

    async def print_search_results(self, message, match_entries, limit=10):
        # Sort the returned entries
        # TODO: This sort is garbage text based
        print_entries = sorted(match_entries, key=lambda k: (k[1]['priority'], int(k[0])))

        # Limit to specified number of replies at a time
        if len(print_entries) > limit:
            await self.reply(message, 'Limiting to top {} results'.format(limit))
            print_entries = print_entries[:limit]

        for index, entry in print_entries:
            entry_text, embed = await self.format_entry(index, entry)
            msg = await self._client.send_message(message.channel, entry_text, embed=embed);


    async def handle_message(self, message):
        commands = {
            "add": (self.cmd_add, ),
            "report": (self.cmd_add, ),
            "get": (self.cmd_get, ),
            "roulette": (self.cmd_roulette, ),
            "search": (self.cmd_search, ),
            "dsearch": (self.cmd_dsearch, ),
            "reject": (self.cmd_reject, ),
            "edit": (self.cmd_edit, ),
            "append": (self.cmd_append, ),
            "fix": (self.cmd_fix, ),
            "unfix": (self.cmd_unfix, ),
            "prune": (self.cmd_prune, ),
            "import": (self.cmd_import, ),
            "repost": (self.cmd_repost, ),
            "addlabel": (self.cmd_addlabel, ),
            "test": (self.cmd_test, ),
        }

        part = message.content.split(maxsplit=2)
        if (not message.content) or (len(part) < 1):
            return

        match = get_list_match(part[0].strip(), [self._prefix, ])
        if match is None:
            return

        if len(part) < 2:
            await self.usage(message)
            return

        match = get_list_match(part[1].strip(), commands.keys())
        if match is None:
            await self.usage(message)
            return

        args = ""
        if len(part) > 2:
            args = part[2].strip()

        await commands[match][0](message, args)

    ################################################################################
    # Usage
    async def usage(self, message):
        usage = '''
**Commands everyone can use:**
`{prefix} add <label> <description>`
    Adds a new suggestion {single} with the given label
    Label must be one of: {labels}
    Alias: report

`{prefix} search labels,priorities,limit`
    Searches all {plural} for ones that are tagged with all the specified labels / priorities
    Only show the top #limit results to reduce chatspam
    For example:
        {prefix} search quest,class,high

`{prefix} dsearch <search terms>`
    Searches all {single} descriptions for ones that contain all the specified search terms

`{prefix} get <number>`
    Gets the {single} with the specified number

`{prefix} roulette`
    Gets a random {single}

**Commands the original {single} author and team members can use:**
`{prefix} reject <number> <reason why>`
    Closes the specified {single} with the given reason

`{prefix} edit <number> <description | label | image> [argument]`
    Edits the specified field of the entry

`{prefix} append <number> text`
    Appends text to an existing {single}'s description

**Commands team members can use:**
`{prefix} edit <number> [author | priority] [argument]`
    Edits the specified field of the entry

`{prefix} fix number [optional explanation]`
    Marks the specified {single} as fixed. Default explanation is simply "Fixed"

`{prefix} unfix <number>`
    Unmarks the specified {single} as fixed

`{prefix} addlabel <newlabel>`
    Adds a new label
'''.format(prefix=self._prefix, single=self._descriptor_single, plural=self._descriptor_plural, labels=" ".join(self._labels))

        if self.has_privilege(3, message.author):
            usage += '''
**Commands only leads can use:**
`{prefix} prune`
    Removes all fixed {plural} from the tracking channel
'''.format(prefix=self._prefix, plural=self._descriptor_plural)

        if self.has_privilege(4, message.author):
            usage += '''
**Commands only you can use:**
`{prefix} import <#channel>`
    Imports all messages in the specified channel as {plural}

`{prefix} repost`
    Reposts/edits all known {plural}
'''.format(prefix=self._prefix, plural=self._descriptor_plural)

        await self.reply(message, usage)


    ################################################################################
    # test
    async def cmd_test(self, message, args):
        if self.has_privilege(4, message.author):
            await self.reply(message, "Privilege: 4")
        elif self.has_privilege(3, message.author):
            await self.reply(message, "Privilege: 3")
        elif self.has_privilege(2, message.author):
            await self.reply(message, "Privilege: 2")
        elif self.has_privilege(1, message.author):
            await self.reply(message, "Privilege: 1")
        elif self.has_privilege(0, message.author):
            await self.reply(message, "Privilege: 0")
        else:
            await self.reply(message, "Privilege: None")

    ################################################################################
    # add / report
    async def cmd_add(self, message, args):
        if not args:
            await self.reply(message, '''How to submit a {single}:```
{prefix} add <label> <description>
```
Example:```
{prefix} add quest Bihahiahihaaravi refuses to talk to me when I'm wearing a fedora
```
You can also attach an image to your message to include it in the {single}
'''.format(prefix=self._prefix, single=self._descriptor_single))
            return

        part = args.split(maxsplit=1)
        if len(part) < 2:
            await self.reply(message, 'Must contain both a label and a description')
            return

        labels = part[0].strip().lower().split(',')
        description = part[1].strip()

        good_labels = []
        for label in labels:
            match = get_list_match(label.strip(), self._labels)
            if match is None:
                await self.reply(message, "Labels must be one of: [{}]".format(",".join(self._labels)))
                return
            good_labels.append(match)

        if not description:
            await self.reply(message, 'Description can not be empty!')

        image = None
        for attach in message.attachments:
            if "url" in attach:
                image = attach["url"]
        # TODO: Steal this code for something else?
        #for embed in message.embeds:
        #    print("EMBED URL: " + embed.url)
        #    print(embed)
        #    image = embed.url

        (index, entry) = self.add_entry(description, labels=good_labels, author=message.author, image=image)

        # Post this new entry
        await self.send_entry(index, entry)

        await(self.reply(message, "#{} created successfully".format(index)))

    ################################################################################
    # edit
    async def cmd_edit(self, message, args):
        part = args.split(maxsplit=2)
        if (not args) or (len(part) < 2):
            await self.reply(message, '''How to edit a {single}:```
{prefix} edit # [description | label | image | author | priority] edited stuff
```
For example:```
{prefix} edit 5 description Much more detail here
```
'''.format(prefix=self._prefix, single=self._descriptor_single))
            return

        index_str = part[0].strip()
        try:
            index = int(index_str)
        except:
            await self.reply(message, "'{}' is not a number".format(index_str))
            return

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._entries:
            await self.reply(message, '{proper} #{index} not found!'.format(proper=self._descriptor_proper, index=index))
            return

        entry = self._entries[index]

        operation = get_list_match(part[1].strip(), ['description', 'label', 'image', 'author', 'priority'])
        if operation is None:
            await self.reply(message, "Item to edit must be 'description', 'label', 'image', 'author', or 'priority'")
            return

        min_priv = 4
        if operation in ['description', 'label', 'image']:
            min_priv = 1
        if operation in ['author', 'priority']:
            min_priv = 2

        if not self.has_privilege(min_priv, message.author, index=index):
            await self.reply(message, "You do not have permission to edit {} for entry #{}".format(operation, index))
            return

        if operation == 'description':
            if len(part) < 3:
                await self.reply(message, "You need to actually supply a new description")
                return

            entry["description"] = part[2].strip()

        elif operation == 'label':
            if len(part) < 3:
                await self.reply(message, "You need to actually supply a new label")
                return

            labels = part[2].strip().lower().split(',')
            good_labels = []
            for label in labels:
                match = get_list_match(label.strip(), self._labels)
                if match is None:
                    await self.reply(message, "Labels must be one of: [{}]".format(",".join(self._labels)))
                    return
                good_labels.append(match)

            entry["labels"] = good_labels

        elif operation == 'image':
            image = None
            for attach in message.attachments:
                if "url" in attach:
                    image = attach["url"]

            if image is None:
                await self.reply(message, "You need to attach an image")
                return

            entry["image"] = image

        elif operation == 'author':
            #TODO
            await self.reply(message, "NOT IMPLEMENTED YET")
            return

        elif operation == 'priority':
            if len(part) < 3:
                await self.reply(message, '''
__Available Priorities:__
**Critical**
- Portions of the game are unplayable
- At least a few people are expected to be affected.

**High**
- Significantly impacts the game
- Affects many players but moderator help not required to work around OR affects very few players

**Medium**
- Would be really nice to have
- Either it's not important enough to be high or it is sort of is but requires a ton of work to fix

**Low**
- Worth doing someday when there's time

**Zero**
- Even if this is a good idea, not worth the effort required to make happen.

**N/A**
- No priority assigned''')
                return

            priority = get_list_match(part[2].strip().lower(), self._priorities)
            if priority is None:
                await self.reply(message, "Priority must be one of: [{}]".format(",".join(self._priorities)))
                return

            entry["priority"] = priority

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry)
        msg = await self._client.send_message(message.channel, entry_text, embed=embed);
        await(self.reply(message, "{proper} #{index} updated successfully".format(proper=self._descriptor_proper, index=index)))

    ################################################################################
    # append
    async def cmd_append(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) < 2):
            await self.reply(message, '''Usage: {prefix} append <number> [additional description text]'''.format(prefix=self._prefix))
            return

        index_str = part[0].strip()
        try:
            index = int(index_str)
        except:
            await self.reply(message, "'{}' is not a number".format(index_str))
            return

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._entries:
            await self.reply(message, '{proper} #{index} not found!'.format(proper=self._descriptor_proper, index=index))
            return

        if not self.has_privilege(1, message.author, index=index):
            await self.reply(message, "You do not have permission to append to #{}".format(index))
            return

        entry = self._entries[index]

        entry["description"] = "{}\n{}".format(entry["description"], part[1].strip())

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry)
        msg = await self._client.send_message(message.channel, entry_text, embed=embed);
        await(self.reply(message, "{proper} #{index} edited".format(proper=self._descriptor_proper, index=index)))

    ################################################################################
    # get
    async def cmd_get(self, message, args):
        if not args:
            await self.reply(message, "Usage: {prefix} get <number>".format(prefix=self._prefix))
            return

        index_str = args.strip()
        try:
            index = int(index_str)
        except:
            await self.reply(message, "'{}' is not a number".format(index_str))
            return

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._entries:
            await self.reply(message, '{proper} #{index} not found!'.format(proper=self._descriptor_proper, index=index))
            return

        match_entries = [(index, self._entries[index])]
        await self.print_search_results(message, match_entries)

    ################################################################################
    # roulette
    async def cmd_roulette(self, message, args):
        match_entries = []
        for index in self._entries:
            entry = self._entries[index]
            if "close_reason" not in entry:
                match_entries.append((index, entry))

        await self.print_search_results(message, [random.choice(match_entries)])

    ################################################################################
    # search
    async def cmd_search(self, message, args):
        part = args.replace(","," ").split()
        if (not args) or (len(part) < 1):
            await self.reply(message, '''Usage: {prefix} search labels,priorities
Default limit is 10 results - include more by adding a number to the search terms
If using multiple labels, all specified labels must match
If using multiple priorities, at least one must match'''.format(prefix=self._prefix))
            return

        match_labels = []
        match_priorities = []
        max_count = 10
        for item in part:
            item = item.strip()
            label_match = get_list_match(item, self._labels)
            priority_match = get_list_match(item, self._priorities)

            if label_match is not None:
                match_labels.append(label_match)
            elif priority_match is not None:
                match_priorities.append(priority_match)
            elif re.search("^[0-9][0-9]*$", item):
                max_count = int(item)
            else:
                await self.reply(message, '''No priority or label matching "{}"'''.format(item))
                return

        if len(match_labels) == 0 and len(match_priorities) == 0:
            await self.reply(message, 'Must specify something to search for')
            return

        match_entries = []
        count = 0
        for index in self._entries:
            entry = self._entries[index]
            if "close_reason" not in entry:
                matches = True
                for label in match_labels:
                    if label not in entry["labels"]:
                        matches = False

                if (len(match_priorities) > 0) and (entry["priority"] not in match_priorities):
                    matches = False

                if matches:
                    count += 1
                    match_entries.append((index, entry))

        await self.print_search_results(message, match_entries, limit=max_count)

        await(self.reply(message, "{} {} found matching labels={} priorities={}".format(count, self._descriptor_plural, ",".join(match_labels), ",".join(match_priorities))))

    ################################################################################
    # dsearch
    async def cmd_dsearch(self, message, args):
        part = args.replace(","," ").split()
        if (not args) or (len(part) < 1):
            await self.reply(message, '''Usage: {prefix} dsearch <search terms>'''.format(prefix=self.prefix))
            return

        match_entries = []
        count = 0
        for index in self._entries:
            entry = self._entries[index]
            if "close_reason" not in entry:
                matches = True
                for term in part:
                    if term.strip().lower() not in entry["description"].lower():
                        matches = False

                if matches:
                    count += 1
                    match_entries.append((index, entry))

        await self.print_search_results(message, match_entries)

        await(self.reply(message, "{} {} found matching {}".format(count, self._descriptor_plural, ",".join(part))))

    ################################################################################
    # addlabel
    async def cmd_addlabel(self, message, args):
        if not self.has_privilege(2, message.author):
            await self.reply(message, "You do not have permission to use this command")
            return

        args = args.lower()

        if (not args) or re.search("[^a-z]", args):
            await self.reply(message, '''Usage: {prefix} addlabel <label>
Labels can only contain a-z characters'''.format(prefix=self._prefix))
            return

        match = get_list_match(args, self._labels)
        if match is not None:
            await self.reply(message, 'Can not add label {} because it matches {}'.format(args, match))
            return

        self._labels.append(args)
        self.save()

        await(self.reply(message, "Label {} added successfully".format(args)))

    ################################################################################
    # reject
    async def cmd_reject(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) < 2):
            await self.reply(message, '''Usage: {prefix} reject <number> <required explanation>'''.format(prefix=self._prefix))
            return

        index_str = part[0].strip()
        try:
            index = int(index_str)
        except:
            await self.reply(message, "'{}' is not a number".format(index_str))
            return

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._entries:
            await self.reply(message, '{proper} #{index} not found!'.format(proper=self._descriptor_proper, index=index))
            return

        if not self.has_privilege(1, message.author, index=index):
            await self.reply(message, "You do not have permission to reject #{}".format(index))
            return

        entry = self._entries[index]

        entry["close_reason"] = part[1].strip().lower()

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry)
        msg = await self._client.send_message(message.channel, entry_text, embed=embed);
        await(self.reply(message, "{proper} #{index} rejected".format(proper=self._descriptor_proper, index=index)))

    ################################################################################
    # fix
    async def cmd_fix(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) < 1):
            await self.reply(message, '''Usage: {prefix} fix <number> [optional explanation]'''.format(prefix=self._prefix))
            return

        index_str = part[0].strip()
        try:
            index = int(index_str)
        except:
            await self.reply(message, "'{}' is not a number".format(index_str))
            return

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._entries:
            await self.reply(message, '{proper} #{index} not found!'.format(proper=self._descriptor_proper, index=index))
            return

        if not self.has_privilege(1, message.author, index=index):
            await self.reply(message, "You do not have permission to fix #{}".format(index))
            return

        entry = self._entries[index]

        if len(part) > 1:
            entry["close_reason"] = part[1].strip().lower()
        else:
            entry["close_reason"] = "Fixed"

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry)
        msg = await self._client.send_message(message.channel, entry_text, embed=embed);
        await(self.reply(message, "{proper} #{index} marked as fixed".format(proper=self._descriptor_proper, index=index)))

    ################################################################################
    # unfix
    async def cmd_unfix(self, message, args):
        part = args.split(maxsplit=2)
        if (not args) or (len(part) != 1):
            await self.reply(message, '''Usage: {prefix} unfix <number>'''.format(prefix=self._prefix))
            return

        index_str = part[0].strip()
        try:
            index = int(index_str)
        except:
            await self.reply(message, "'{}' is not a number".format(index_str))
            return

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._entries:
            await self.reply(message, '{proper} #{index} not found!'.format(proper=self._descriptor_proper, index=index))
            return

        if not self.has_privilege(1, message.author, index=index):
            await self.reply(message, "You do not have permission to unfix #{}".format(index))
            return

        entry = self._entries[index]

        if "close_reason" in entry:
            entry.pop("close_reason")

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry)
        msg = await self._client.send_message(message.channel, entry_text, embed=embed);
        await(self.reply(message, "{proper} #{index} unmarked as fixed".format(proper=self._descriptor_proper, index=index)))

    ################################################################################
    # prune
    async def cmd_prune(self, message, args):
        if not self.has_privilege(3, message.author):
            await self.reply(message, "You do not have permission to use this command")
            return

        if self._channel is None:
            self._channel = self._client.get_channel(self._channel_id)
            if self._channel is None:
                raise Exception("Error getting bot channel!")

        await(self.reply(message, "Prune started, this will take some time..."))

        match_entries = []
        count = 0
        for index in self._entries:
            entry = self._entries[index]
            # If the entry is both closed AND present in the entry channel
            if ("close_reason" in entry) and ("message_id" in entry):
                try:
                    msg = await self._client.get_message(self._channel, entry["message_id"])
                    if msg is not None:
                        await self._client.delete_message(msg)

                        # Since this message is no longer there...
                        entry.pop("message_id")
                        match_entries.append((index, entry))
                        count += 1
                except:
                    pass

        await self.print_search_results(message, match_entries, limit=99999)
        await(self.reply(message, "{} entries pruned successfully".format(count)))

    ################################################################################
    # repost
    async def cmd_repost(self, message, args):
        if not self.has_privilege(4, message.author):
            await self.reply(message, "You do not have permission to use this command")
            return

        await(self.reply(message, "Repost started, this will take some time..."))

        count = 0
        for index in self._entries:
            if "close_reason" not in self._entries[index]:
                count += 1
                await self.send_entry(index, self._entries[index])

        await(self.reply(message, "{} entries reposted successfully".format(count)))

    ################################################################################
    # import
    async def cmd_import(self, message, args):
        if not self.has_privilege(4, message.author):
            await self.reply(message, "You do not have permission to use this command")
            return

        part = args.split(maxsplit=2)
        if len(part) != 1 or len(part[0].strip()) < 10:
            await self.reply(message, "Usage: import #channel".format(self._prefix))
            return

        channel_id = part[0].strip()
        channel_id = channel_id[2:-1]
        import_channel = self._client.get_channel(channel_id)
        if import_channel is None:
            await self.reply(message, "Can not find channel '{}'".format(channel_id))
            return

        await(self.reply(message, "Import started, this will take some time..."))

        count = 0
        async for msg in self._client.logs_from(import_channel, limit=1000, reverse=True):
            if not msg.content:
                continue

            count += 1

            image = None
            for attach in msg.attachments:
                if "url" in attach:
                    image = attach["url"]

            (index, entry) = self.add_entry(msg.content, author=msg.author, image=image)

            # Post this new entry
            await self.send_entry(index, entry)

        await(self.reply(message, "{} entries from channel {} imported successfully".format(count, part[0])))

def get_list_match(item, lst):
    tmpitem = item.lower()

    match = None
    for x in lst:
        if x.lower().startswith(tmpitem):
            if x.lower() == tmpitem:
                # Exact match - return it
                return x
            elif match is None:
                # Partial match - keep track of it
                match = x
            else:
                # Multiple matches - don't want to return the wrong one!
                return None
    return match

# TODO: These are duplicated!

import datetime
def datestr():
    return datetime.datetime.now().strftime("%Y_%m_%d")

def split_string(text):
    # Maximum number of characters in a single line
    n = 1950

    splits = text.splitlines()
    result = []
    cur = None
    for i in splits:
        while True:
            if cur is None and len(i) <= n:
                cur = i;
                break # Done with i
            elif cur is None and len(i) > n:
                # Annoying case - one uber long line. Have to split into chunks
                result = result + [i[:n]]
                i = i[n:]
                pass # Repeat this iteration
            elif len(cur) + len(i) < n:
                cur = cur + "\n" + i
                break # Done with i
            else:
                result = result + [cur]
                cur = None
                pass # Repeat this iteration

    if cur is not None:
        result = result + [cur]
        cur = None

    return result
