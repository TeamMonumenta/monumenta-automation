import asyncio

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

        # Automatically added:
        "status": "Open" "Closed"
        "message_id": <discord message ID>
    }
]

labels = [
    "Kaul",
    "Boss",
    "Class",
    "Item",
    "Mob",
    "Quest",
    "Advancement",
    "Trivial",
    "Build",
    "Misc",
]

priority = [
    "High",
    "Med",
    "Low",
    "Zero",
]
'''

# Commands:
'''
# Privilege 0: Commands everyone can use:
    bug

    bug report
        <label>
        <description>

    bug search label [priority]

# Privilege 1: Commands only team members / moderators / the original poster can use:
    bug reject number
    [Optional reason why]

    bug edit [description | label | image]
        Whatever that field is

# Privilege 2: Commands only team members / moderators can use
    bug edit [author | priority]
        Whatever that field is

    bug fix number

    bug unfix number

# Privilege 3: Commands only leads can use:
    bug prune

# Plivilege 4: Commands only specific hardcoded users can use:
    bug import #channel
    (imports everything in the current channel)

    bug repost
'''


class BugReportManager(object):
    def __init__(self, client, user_privileges, group_privileges, bug_reports_channel_id):
        """
        """
        self._bugs = {}
        self._next_index = 1
        self._client = client
        self._user_privileges = user_privileges
        self._group_privileges = group_privileges
        self._bug_reports_channel_id = bug_reports_channel_id
        self._bug_reports_channel = None
        self.labels = [
            "kaul",
            "boss",
            "class",
            "item",
            "mob",
            "quest",
            "advancement",
            "trivial",
            "build",
            "misc",
        ]

    def save(self, filename):
        """
        """

    def load(self, filename):
        """
        """

    async def handle_message(self, message):
        if message.content.startswith("~bug report"):
            await self.cmd_report(message)
        elif message.content.startswith("~bug search"):
            await self.reply(message, "bug search - Not implemented yet")
        elif message.content.startswith("~bug reject"):
            await self.reply(message, "bug reject - Not implemented yet")
        elif message.content.startswith("~bug edit"):
            await self.cmd_edit(message)
        elif message.content.startswith("~bug fix"):
            await self.reply(message, "bug fix - Not implemented yet")
        elif message.content.startswith("~bug unfix"):
            await self.reply(message, "bug unfix - Not implemented yet")
        elif message.content.startswith("~bug prune"):
            await self.reply(message, "bug prune - Not implemented yet")
        elif message.content.startswith("~bug import"):
            await self.reply(message, "bug import - Not implemented yet")
        elif message.content.startswith("~bug repost"):
            await self.reply(message, "bug repost - Not implemented yet")
        elif message.content.startswith("~bug priv"):
            await self.cmd_priv(message)
        elif message.content.startswith("~bug"):
            await self.reply(message, "bug - Not implemented yet")

    async def reply(self, message, response):
        """
        Replies to a given message (in that channel)
        """
        await self._client.send_message(message.channel, response)
        print("Replying")

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

    async def cmd_priv(self, message):
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

    async def cmd_report(self, message):
        content = message.content[len("~bug report"):].strip()
        if not content:
            await self.reply(message, '''How to submit a bug report:```
~bug report
<type>
Description
```
Example bug report:```
~bug report
quest
Bihahiahihaaravi yodels at me when hit with a fish
```
You can also attach an image to the message to include it in the bug report
''')
            return

        part = content.split(maxsplit=1)
        label = part[0].strip().lower()
        description = part[1].strip()

        if label not in (name.lower() for name in self.labels):
            await self.reply(message, '''Label must be one of the following:```
''' + '''
'''.join(self.labels) + '```')
            return

        if not description:
            await self.reply(message, 'Description can not be empty!')

        (index, bug) = await self.add_bug(message.author, description, label, priority="N/A")
        print(bug)

        await(self.reply(message, "Bug report #{} created successfully".format(index)))

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

        operation = part[1].strip().lower()

        if index not in self._bugs:
            await self.reply(message, 'Bug #{} not found!'.format(index))
            return

        if operation not in ['description', 'label', 'image', 'author', 'priority']:
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
            await self.reply(message, "NOT IMPLEMENTED YET")
        elif operation == 'label':
            await self.reply(message, "NOT IMPLEMENTED YET")
        elif operation == 'image':
            await self.reply(message, "NOT IMPLEMENTED YET")
        elif operation == 'author':
            await self.reply(message, "NOT IMPLEMENTED YET")
        elif operation == 'priority':
            await self.reply(message, "NOT IMPLEMENTED YET")


    async def add_bug(self, author, description, label, image=None, priority=None):
        bug = {
            "author": author.id,
            "description": description,
            "labels": [label],
        }

        if image is not None:
            bug["image"] = image

        if priority is not None:
            bug["priority"] = priority

        index = self._next_index

        # Post this new bug report
        await self.send_bug(index, bug)

        self._next_index += 1
        self._bugs[index] = bug
        return (index, bug)

    async def send_bug(self, index, bug):
        # Fetch the channel if not already stored
        if self._bug_reports_channel is None:
            self._bug_reports_channel = self._client.get_channel(self._bug_reports_channel_id)
            if self._bug_reports_channel is None:
                raise Exception("Error getting bug reports channel!")

        # Compute the new bug text
        # TODO: Better author format
        # TODO: Images
        bug_text = '''```
#{} [{} - {}] {}```{}'''.format(index, ','.join(bug["labels"]), bug["priority"], bug["author"], bug["description"])

        msg = None
        if "message_id" in bug:
            msg = await self._client.get_message(self._bug_reports_channel, msg.id)

        if msg is not None:
            # Edit the existing message
            await self._client.edit_message(msg, bug_text)

        else:
            # Send a new message
            msg = await self._client.send_message(self._bug_reports_channel, bug_text);
            bug["message_id"] = msg.id

        await self._client.add_reaction(msg, "\U0001f44d")






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
