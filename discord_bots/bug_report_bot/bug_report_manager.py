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
bugs = {
    # Key is buf report number - fixed forever
    42 : {
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

class BugReportManager(object):
    def __init__(self, client, config):
        """
        """
        self._client = client

        # Sanity check:
        for key in ["bot_input_channels", "bug_reports_channel_id", "user_privileges", "group_privileges"]:
            if key not in config:
                sys.exit('Config missing key: {}'.format(key))

        pprint(config)
        self._user_privileges = config["user_privileges"]
        self._group_privileges = config["group_privileges"]
        self._bug_reports_channel_id = config["bug_reports_channel_id"]
        self._prefix = config["prefix"]
        self._bug_reports_channel = None
        self._database_path = config["database_path"]
        self.load()

    def save(self):
        savedata = {
            'bugs': self._bugs,
            'next_index': self._next_index,
            'labels': self._labels,
            'priorities': self._priorities,
        }

        with open(self._database_path, 'w') as f:
            json.dump(savedata, f, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': '))

    def load(self):
        if not os.path.exists(self._database_path):
            self._bugs = {}
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

            self._bugs = data['bugs']
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
            bug = self._bugs.get(index, None)
            if bug is not None:
                if bug["author"] == author.id:
                    priv = max(priv, 1)

        return priv >= min_privilege

    def add_bug(self, description, labels=["misc"], author=None, image=None, priority="N/A"):
        bug = {
            "description": description,
            "labels": labels,
        }

        if author is None:
            bug["author"] = 0
        else:
            bug["author"] = author.id

        if image is not None:
            bug["image"] = image

        if priority is not None:
            bug["priority"] = priority

        index = self._next_index

        self._next_index += 1
        self._bugs[str(index)] = bug

        self.save()

        return (index, bug)

    async def format_bug(self, index, bug):
        author_id = bug["author"]
        if author_id != 0 and author_id != "0":
            author_name = (await self._client.get_user_info(author_id)).display_name
        else:
            author_name = ""

        bug_text = '''`
#{} [{} - {}] {}`
{}'''.format(index, ','.join(bug["labels"]), bug["priority"], author_name, bug["description"])

        if "close_reason" in bug:
            bug_text = '''~~{}~~
Closed: {}'''.format(bug_text, bug["close_reason"])

        embed = None
        if "image" in bug:
            embed = discord.Embed()
            embed.set_image(url=bug["image"])

        return bug_text, embed

    async def send_entry(self, index, bug):
        # Fetch the channel if not already stored
        if self._bug_reports_channel is None:
            self._bug_reports_channel = self._client.get_channel(self._bug_reports_channel_id)
            if self._bug_reports_channel is None:
                raise Exception("Error getting channel!")

        # Compute the new bug text
        bug_text, embed = await self.format_bug(index, bug)

        msg = None
        if "message_id" in bug:
            try:
                msg = await self._client.get_message(self._bug_reports_channel, bug["message_id"])
            except:
                pass

        if msg is not None:
            # Edit the existing message
            await self._client.edit_message(msg, bug_text, embed=embed)

        else:
            # Send a new message
            msg = await self._client.send_message(self._bug_reports_channel, bug_text, embed=embed);
            bug["message_id"] = msg.id
            self.save()

        await self._client.add_reaction(msg, "\U0001f44d")

    async def print_search_results(self, message, match_bugs, limit=10):
        # Sort the returned bugs
        # TODO: This sort is garbage text based
        print_bugs = sorted(match_bugs, key=lambda k: (k[1]['priority'], int(k[0])))

        # Limit to specified number of replies at a time
        if len(print_bugs) > limit:
            await self.reply(message, 'Limiting to top {} results'.format(limit))
            print_bugs = print_bugs[:limit]

        for index, bug in print_bugs:
            bug_text, embed = await self.format_bug(index, bug)
            msg = await self._client.send_message(message.channel, bug_text, embed=embed);


    async def handle_message(self, message):
        commands = {
            "report": (self.cmd_report),
            "get": (self.cmd_get),
            "roulette": (self.cmd_roulette),
            "search": (self.cmd_search),
            "dsearch": (self.cmd_dsearch),
            "reject": (self.cmd_reject),
            "edit": (self.cmd_edit),
            "append": (self.cmd_append),
            "fix": (self.cmd_fix),
            "unfix": (self.cmd_unfix),
            "prune": (self.cmd_prune),
            "import": (self.cmd_import),
            "repost": (self.cmd_repost),
            "addlabel": (self.cmd_addlabel),
            "test": (self.cmd_test),
        }

        part = content.split(maxsplit=2)
        if (not content) or (len(part) < 1):
            return

        match = get_list_match(part[0].strip(), self._prefix)
        if match is None or (len(part) < 2):
            return

        match = get_list_match(part[1].strip(), commands.keys())
        if match is None:
            await self.cmd_bug(message)

        args = ""
        if len(part) > 2:
            args = part[3].strip()

        await commands[match][0](message, args)

    ################################################################################
    # Usage
    async def cmd_bug(self, message):
        usage = '''
**Commands everyone can use:**
`{1} report <label> <description>`
    Reports a bug with the given label
    Label must be one of: {2}

`{1} search labels,priorities,limit`
    Searches all bugs for ones that are tagged with all the specified labels / priorities
    Only show the top #limit results to reduce chatspam
    For example:
        {1} search quest,class,high

`{1} dsearch <search terms>`
    Searches all bug descriptions for ones that contain all the specified search terms

`{1} get <number>`
    Gets the bug with the specified number

`{1} roulette`
    Gets a random bug

**Commands the original bug reporter and team members can use:**
`{1} reject <number> <reason why>`
    Closes the specified bug with the given reason

`{1} edit <number> <description | label | image> [argument]`
    Edits the specified field of the entry

`{1} append <number> text`
    Appends text to an existing bug's description

**Commands team members can use:**
`{1} edit <number> [author | priority] [argument]`
    Edits the specified field of the entry

`{1} fix number [optional explanation]`
    Marks the specified bug as fixed. Default explanation is simply "Fixed"

`{1} unfix <number>`
    Unmarks the specified bug as fixed

`{1} addlabel <newlabel>`
    Adds a new label - a-z characters only
'''.format(self._prefix, " ".join(self._labels))

        if self.has_privilege(3, message.author):
            usage += '''
**Commands only leads can use:**
`{1} prune`
    Removes all fixed bug reports from the bug reports channel
'''.format(self._prefix)

        if self.has_privilege(4, message.author):
            usage += '''
**Commands only you can use:**
`{1} import <#channel>`
    Imports all messages in the specified channel as bugs

`{1} repost`
    Reposts/edits all known bug reports
'''.format(self._prefix)

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
    # report
    async def cmd_report(self, message, args):
        if not args:
            await self.reply(message, '''How to submit a bug report:```
{1} report <label> <description>
```
Example bug report:```
{1} report quest Bihahiahihaaravi doesn't yodel at me when hit with a fish
```
You can also attach an image to the message to include it in the bug report
'''.format(self._prefix))
            return

        part = args.split(maxsplit=1)
        if len(part) < 2:
            await self.reply(message, 'Bug report must contain both a label and a description')
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

        (index, bug) = self.add_bug(description, labels=good_labels, author=message.author, image=image)

        # Post this new bug report
        await self.send_entry(index, bug)

        await(self.reply(message, "Bug report #{} created successfully".format(index)))

    ################################################################################
    # edit
    async def cmd_edit(self, message, args):
        part = args.split(maxsplit=2)
        if (not args) or (len(part) < 2):
            await self.reply(message, '''How to edit a bug report:```
{1} edit # [description | label | image | author | priority] edited stuff
```
For example:```
{1} edit 5 description Much more detail here
```
'''.format(self._prefix))
            return

        index_str = part[0].strip()
        try:
            index = int(index_str)
        except:
            await self.reply(message, "'{}' is not a number".format(index_str))
            return

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._bugs:
            await self.reply(message, 'Bug #{} not found!'.format(index))
            return

        bug = self._bugs[index]

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
            await self.reply(message, "You do not have permission to edit {} for bug {}".format(operation, index))
            return

        if operation == 'description':
            if len(part) < 3:
                await self.reply(message, "You need to actually supply a new description")
                return

            bug["description"] = part[2].strip()

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

            bug["labels"] = good_labels

        elif operation == 'image':
            image = None
            for attach in message.attachments:
                if "url" in attach:
                    image = attach["url"]

            if image is None:
                await self.reply(message, "You need to attach an image")
                return

            bug["image"] = image

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

            bug["priority"] = priority

        self.save()

        # Update the bug
        await self.send_entry(index, bug)

        bug_text, embed = await self.format_bug(index, bug)
        msg = await self._client.send_message(message.channel, bug_text, embed=embed);
        await(self.reply(message, "Bug report #{} updated successfully".format(index)))

    ################################################################################
    # append
    async def cmd_append(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) < 2):
            await self.reply(message, '''Usage: {1} append <number> [additional description text]'''.format(self._prefix))
            return

        index_str = part[0].strip()
        try:
            index = int(index_str)
        except:
            await self.reply(message, "'{}' is not a number".format(index_str))
            return

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._bugs:
            await self.reply(message, 'Bug #{} not found!'.format(index))
            return

        if not self.has_privilege(1, message.author, index=index):
            await self.reply(message, "You do not have permission to append to bug #{}".format(index))
            return

        bug = self._bugs[index]

        bug["description"] = "{}\n{}".format(bug["description"], part[1].strip())

        self.save()

        # Update the bug
        await self.send_entry(index, bug)

        bug_text, embed = await self.format_bug(index, bug)
        msg = await self._client.send_message(message.channel, bug_text, embed=embed);
        await(self.reply(message, "Bug report #{} edited".format(index)))

    ################################################################################
    # get
    async def cmd_get(self, message, args):
        if not args:
            await self.reply(message, "Usage: bug get <number>")
            return

        index_str = args.strip()
        try:
            index = int(index_str)
        except:
            await self.reply(message, "'{}' is not a number".format(index_str))
            return

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._bugs:
            await self.reply(message, "Bug report {} does not exist".format(index_str))
            return

        match_bugs = [(index, self._bugs[index])]
        await self.print_search_results(message, match_bugs)

    ################################################################################
    # roulette
    async def cmd_roulette(self, message, args):
        match_bugs = []
        for index in self._bugs:
            bug = self._bugs[index]
            if "close_reason" not in bug:
                match_bugs.append((index, bug))

        await self.print_search_results(message, [random.choice(match_bugs)])

    ################################################################################
    # search
    async def cmd_search(self, message, args):
        part = args.replace(","," ").split()
        if (not args) or (len(part) < 1):
            await self.reply(message, '''Usage: {1} search labels,priorities
Default limit is 10 results - include more by adding a number to the search terms
If using multiple labels, all specified labels must match
If using multiple priorities, at least one must match'''.format(self._prefix))
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

        match_bugs = []
        count = 0
        for index in self._bugs:
            bug = self._bugs[index]
            if "close_reason" not in bug:
                matches = True
                for label in match_labels:
                    if label not in bug["labels"]:
                        matches = False

                if (len(match_priorities) > 0) and (bug["priority"] not in match_priorities):
                    matches = False

                if matches:
                    count += 1
                    match_bugs.append((index, bug))

        await self.print_search_results(message, match_bugs, limit=max_count)

        await(self.reply(message, "{} bugs found matching labels={} priorities={}".format(count, ",".join(match_labels), ",".join(match_priorities))))

    ################################################################################
    # dsearch
    async def cmd_dsearch(self, message, args):
        part = args.replace(","," ").split()
        if (not args) or (len(part) < 1):
            await self.reply(message, '''Usage: {1} dsearch <search terms>'''.format(self.prefix))
            return

        match_bugs = []
        count = 0
        for index in self._bugs:
            bug = self._bugs[index]
            if "close_reason" not in bug:
                matches = True
                for term in part:
                    if term.strip().lower() not in bug["description"].lower():
                        matches = False

                if matches:
                    count += 1
                    match_bugs.append((index, bug))

        await self.print_search_results(message, match_bugs)

        await(self.reply(message, "{} bugs found matching {}".format(count, ",".join(part))))

    ################################################################################
    # addlabel
    async def cmd_addlabel(self, message, args):
        if not self.has_privilege(2, message.author):
            await self.reply(message, "You do not have permission to use this command")
            return

        args = args.lower()

        if (not args) or re.search("[^a-z]", args):
            await self.reply(message, '''Usage: {1} addlabel <label>
Labels can only contain a-z characters'''.format(self._prefix))
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
            await self.reply(message, '''Usage: {1} reject <number> <required explanation>'''.format(self._prefix))
            return

        index_str = part[0].strip()
        try:
            index = int(index_str)
        except:
            await self.reply(message, "'{}' is not a number".format(index_str))
            return

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._bugs:
            await self.reply(message, 'Bug #{} not found!'.format(index))
            return

        if not self.has_privilege(1, message.author, index=index):
            await self.reply(message, "You do not have permission to reject bug #{}".format(index))
            return

        bug = self._bugs[index]

        bug["close_reason"] = part[1].strip().lower()

        self.save()

        # Update the bug
        await self.send_entry(index, bug)

        bug_text, embed = await self.format_bug(index, bug)
        msg = await self._client.send_message(message.channel, bug_text, embed=embed);
        await(self.reply(message, "Bug report #{} rejected".format(index)))

    ################################################################################
    # fix
    async def cmd_fix(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) < 1):
            await self.reply(message, '''Usage: {1} fix <number> [optional explanation]'''.format(self._prefix))
            return

        index_str = part[0].strip()
        try:
            index = int(index_str)
        except:
            await self.reply(message, "'{}' is not a number".format(index_str))
            return

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._bugs:
            await self.reply(message, 'Bug #{} not found!'.format(index))
            return

        if not self.has_privilege(1, message.author, index=index):
            await self.reply(message, "You do not have permission to fix bug #{}".format(index))
            return

        bug = self._bugs[index]

        if len(part) > 1:
            bug["close_reason"] = part[1].strip().lower()
        else:
            bug["close_reason"] = "Fixed"

        self.save()

        # Update the bug
        await self.send_entry(index, bug)

        bug_text, embed = await self.format_bug(index, bug)
        msg = await self._client.send_message(message.channel, bug_text, embed=embed);
        await(self.reply(message, "Bug report #{} marked as fixed".format(index)))

    ################################################################################
    # unfix
    async def cmd_unfix(self, message, args):
        part = args.split(maxsplit=2)
        if (not args) or (len(part) != 1):
            await self.reply(message, '''Usage: {1} unfix <number>'''.format(self._prefix))
            return

        index_str = part[0].strip()
        try:
            index = int(index_str)
        except:
            await self.reply(message, "'{}' is not a number".format(index_str))
            return

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._bugs:
            await self.reply(message, 'Bug #{} not found!'.format(index))
            return

        if not self.has_privilege(1, message.author, index=index):
            await self.reply(message, "You do not have permission to unfix bug #{}".format(index))
            return

        bug = self._bugs[index]

        if "close_reason" in bug:
            bug.pop("close_reason")

        self.save()

        # Update the bug
        await self.send_entry(index, bug)

        bug_text, embed = await self.format_bug(index, bug)
        msg = await self._client.send_message(message.channel, bug_text, embed=embed);
        await(self.reply(message, "Bug report #{} unmarked as fixed".format(index)))

    ################################################################################
    # prune
    async def cmd_prune(self, message, args):
        if not self.has_privilege(3, message.author):
            await self.reply(message, "You do not have permission to use this command")
            return

        if self._bug_reports_channel is None:
            self._bug_reports_channel = self._client.get_channel(self._bug_reports_channel_id)
            if self._bug_reports_channel is None:
                raise Exception("Error getting bug reports channel!")

        match_bugs = []
        count = 0
        for index in self._bugs:
            bug = self._bugs[index]
            # If the bug is both closed AND present in the bug channel
            if ("close_reason" in bug) and ("message_id" in bug):
                try:
                    msg = await self._client.get_message(self._bug_reports_channel, bug["message_id"])
                    if msg is not None:
                        await self._client.delete_message(msg)

                        # Since this message is no longer there...
                        bug.pop("message_id")
                        match_bugs.append((index, bug))
                        count += 1
                except:
                    pass

        await self.print_search_results(message, match_bugs, limit=99999)
        await(self.reply(message, "{} bugs pruned successfully".format(count)))

    ################################################################################
    # repost
    async def cmd_repost(self, message, args):
        if not self.has_privilege(4, message.author):
            await self.reply(message, "You do not have permission to use this command")
            return

        count = 0
        for index in self._bugs:
            if "close_reason" not in self._bugs[index]:
                count += 1
                await self.send_entry(index, self._bugs[index])

        await(self.reply(message, "{} bugs reposted successfully".format(count)))

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

        count = 0
        async for msg in self._client.logs_from(import_channel, limit=1000, reverse=True):
            if not msg.content:
                continue

            count += 1

            image = None
            for attach in msg.attachments:
                if "url" in attach:
                    image = attach["url"]

            (index, bug) = self.add_bug(msg.content, author=msg.author, image=image)

            # Post this new bug report
            await self.send_entry(index, bug)

        await(self.reply(message, "{} bugs from channel {} imported successfully".format(count, part[0])))

def get_list_match(item, lst):
    tmpitem = item.lower()

    match = None
    for x in lst:
        if x.lower().startswith(tmpitem):
            if match is None:
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
