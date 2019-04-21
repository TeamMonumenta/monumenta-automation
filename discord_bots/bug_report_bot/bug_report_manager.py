import asyncio
import discord
import os
import json
import sys
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

        # If this is present, the bug is closed
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

    def has_privilege(self, min_privilege, author, bug_idx=None):
        priv = 0; # Everyone has this level

        # Get privilege based on user list
        priv = max(priv, self._user_privileges.get(author.id, 0))

        # Get privilege based on group role
        for role in author.roles:
            priv = max(priv, self._group_privileges.get(role.id, 0))

        # Get privilege based on bug report ownership
        if bug_idx is not None:
            bug = self._bugs.get(bug_idx, None)
            if bug is not None:
                # TODO: This check is wrong
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

    async def send_bug(self, index, bug):
        # Fetch the channel if not already stored
        if self._bug_reports_channel is None:
            self._bug_reports_channel = self._client.get_channel(self._bug_reports_channel_id)
            if self._bug_reports_channel is None:
                raise Exception("Error getting bug reports channel!")

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

    async def handle_message(self, message):
        if message.content.startswith("~bug report"):
            await self.cmd_report(message)
        elif message.content.startswith("~bug search"):
            await self.cmd_search(message)
        elif message.content.startswith("~bug reject"):
            await self.cmd_reject(message)
        elif message.content.startswith("~bug edit"):
            await self.cmd_edit(message)
        elif message.content.startswith("~bug fix"):
            await self.cmd_fix(message)
        elif message.content.startswith("~bug unfix"):
            await self.cmd_unfix(message)
        elif message.content.startswith("~bug prune"):
            await self.reply(message, "bug prune - Not implemented yet")
        elif message.content.startswith("~bug import"):
            await self.cmd_import(message)
        elif message.content.startswith("~bug repost"):
            await self.cmd_repost(message)
        elif message.content.startswith("~bug test"):
            await self.cmd_test(message)
        elif message.content.startswith("~bug"):
            await self.cmd_bug(message)


    ################################################################################
    # ~bug test
    async def cmd_test(self, message):
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
    # ~bug
    async def cmd_bug(self, message):
        usage = '''
**Commands everyone can use:**
`~bug`
    This usage text

`~bug report <label> <description>`
    Reports a bug with the given label
    Label must be one of: {}

`~bug search labels,priorities`
    Searches all bugs for ones that match the specified labels / priorities
    Only bugs matching all supplied arguments will be shown
    Both labels and priorities can be one or a list, separated by commas
    Some examples:
        ~bug search quest,class,high
        ~bug search high

**Commands the original bug reporter and team members can use:**
`~bug reject <number> <reason why>`
    Closes the specified bug with the given reason

`~bug edit <number> <description | label | image> [argument]`
    Edits the specified field of the bug report

**Commands team members can use:**
`~bug edit <number> [author | priority] [argument]`
    Edits the specified field of the bug report

`~bug fix number [optional explanation]`
    Marks the specified bug as fixed. Default explanation is simply "Fixed"

`~bug unfix number`
    Unmarks the specified bug as fixed
'''.format(" ".join(self._labels))

        if self.has_privilege(3, message.author):
            usage += '''
**Commands only leads can use:**
`~bug prune`
    Removes all fixed bug reports from the bug reports channel
'''

        if self.has_privilege(4, message.author):
            usage += '''
**Commands only you can use:**
`~bug import <#channel>`
    Imports all messages in the specified channel as bugs

`~bug repost`
    Reposts/edits all known bug reports
'''

        await self.reply(message, usage)

    ################################################################################
    # ~bug report
    async def cmd_report(self, message):
        content = message.content[len("~bug report"):].strip()
        if not content:
            await self.reply(message, '''How to submit a bug report:```
~bug report <label> <description>
```
Example bug report:```
~bug report quest Bihahiahihaaravi doesn't yodel at me when hit with a fish
```
You can also attach an image to the message to include it in the bug report
''')
            return

        part = content.split(maxsplit=1)
        if len(part) < 2:
            await self.reply(message, 'Bug report must contain both a label and a description')
            return

        label = part[0].strip().lower()
        description = part[1].strip()

        match = get_list_match(label.strip(), self._labels)
        if match is None:
            await self.reply(message, "Labels must be one of: [{}]".format(",".join(self._labels)))
            return

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

        (index, bug) = self.add_bug(description, labels=[match], author=message.author, image=image)

        # Post this new bug report
        await self.send_bug(index, bug)

        await(self.reply(message, "Bug report #{} created successfully".format(index)))

    ################################################################################
    # ~bug edit
    async def cmd_edit(self, message):
        content = message.content[len("~bug edit"):].strip()
        part = content.split(maxsplit=2)
        if (not content) or (len(part) < 2):
            await self.reply(message, '''How to edit a bug report:```
~bug edit # [description | label | image | author | priority] edited stuff
```
For example:```
~bug edit 5 description Much more detail here
```
''')
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

        if not self.has_privilege(min_priv, message.author, bug_idx=index):
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
                await self.reply(message, "You need to actually supply a new priority")
                return

            priority = get_list_match(part[2].strip().lower(), self._priorities)
            if priority is None:
                await self.reply(message, "Priority must be one of: [{}]".format(",".join(self._priorities)))
                return

            bug["priority"] = priority

        self.save()

        # Update the bug
        await self.send_bug(index, bug)

        await(self.reply(message, "Bug report #{} updated successfully".format(index)))

    ################################################################################
    # ~bug search
    async def cmd_search(self, message):
        content = message.content[len("~bug search"):].strip()
        part = content.replace(","," ").split(maxsplit=2)
        if (not content) or (len(part) < 1):
            await self.reply(message, '''Usage: ~bug search labels,priorities''')
            return

        match_labels = []
        match_priorities = []
        for item in part:
            label_match = get_list_match(item.strip(), self._labels)
            priority_match = get_list_match(item.strip(), self._priorities)

            if label_match is not None:
                match_labels.append(label_match)
            elif priority_match is not None:
                match_priorities.append(priority_match)
            else:
                await self.reply(message, '''No priority or label matching "{}"'''.format(item))
                return

        if len(match_priorities) > 1:
            await self.reply(message, '''Bugs can only have one priority''')
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
                for priority in match_priorities:
                    if priority != bug["priority"]:
                        matches = False

                if matches:
                    count += 1
                    match_bugs.append((index, bug))

        # Sort the returned bugs
        # TODO: This sort is garbage text based
        print_bugs = sorted(match_bugs, key=lambda k: (k[1]['priority'], int(k[0])))

        # Limit to 10 replies at a time
        if len(print_bugs) > 10:
            await self.reply(message, '''Limiting to top 10 results to avoid chatspam''')
            print_bugs = print_bugs[:10]

        # Update the bug
        for index, bug in print_bugs:
            bug_text, embed = await self.format_bug(index, bug)
            msg = await self._client.send_message(message.channel, bug_text, embed=embed);

        await(self.reply(message, "{} bugs found matching labels={} priorities={}".format(count, ",".join(match_labels), ",".join(match_priorities))))

    ################################################################################
    # ~bug reject
    async def cmd_reject(self, message):
        content = message.content[len("~bug reject"):].strip()
        part = content.split(maxsplit=1)
        if (not content) or (len(part) < 2):
            await self.reply(message, '''Usage: ~bug reject <number> <required explanation>''')
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

        if not self.has_privilege(1, message.author, bug_idx=index):
            await self.reply(message, "You do not have permission to reject bug #{}".format(index))
            return

        bug = self._bugs[index]

        bug["close_reason"] = part[1].strip().lower()

        self.save()

        # Update the bug
        await self.send_bug(index, bug)

        await(self.reply(message, "Bug report #{} rejected".format(index)))

    ################################################################################
    # ~bug fix
    async def cmd_fix(self, message):
        content = message.content[len("~bug fix"):].strip()
        part = content.split(maxsplit=1)
        if (not content) or (len(part) < 1):
            await self.reply(message, '''Usage: ~bug fix <number> [optional explanation]''')
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

        if not self.has_privilege(1, message.author, bug_idx=index):
            await self.reply(message, "You do not have permission to fix bug #{}".format(index))
            return

        bug = self._bugs[index]

        if len(part) > 1:
            bug["close_reason"] = part[1].strip().lower()
        else:
            bug["close_reason"] = "Fixed"

        self.save()

        # Update the bug
        await self.send_bug(index, bug)

        await(self.reply(message, "Bug report #{} marked as fixed".format(index)))

    ################################################################################
    # ~bug unfix
    async def cmd_unfix(self, message):
        content = message.content[len("~bug unfix"):].strip()
        part = content.split(maxsplit=2)
        if (not content) or (len(part) != 1):
            await self.reply(message, '''Usage: ~bug unfix <number>''')
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

        if not self.has_privilege(1, message.author, bug_idx=index):
            await self.reply(message, "You do not have permission to unfix bug #{}".format(index))
            return

        bug = self._bugs[index]

        if "close_reason" in bug:
            bug.pop("close_reason")

        self.save()

        # Update the bug
        await self.send_bug(index, bug)

        await(self.reply(message, "Bug report #{} unmarked as fixed".format(index)))

    ################################################################################
    # ~bug repost
    async def cmd_repost(self, message):
        if not self.has_privilege(4, message.author):
            await self.reply(message, "You do not have permission to use this command")
            return

        count = 0
        for index in self._bugs:
            count += 1
            await self.send_bug(index, self._bugs[index])

        await(self.reply(message, "{} bugs reposted successfully".format(count)))

    ################################################################################
    # ~bug import
    async def cmd_import(self, message):
        if not self.has_privilege(4, message.author):
            await self.reply(message, "You do not have permission to use this command")
            return

        content = message.content[len("~bug import"):].strip()
        part = content.split(maxsplit=2)
        if len(part) != 1 or len(part[0].strip()) < 10:
            await self.reply(message, "Usage: ~bug import #channel")
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
            await self.send_bug(index, bug)

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
