import os
import json
import sys
import re
import random
import logging
from functools import cmp_to_key
import discord
from discord.ext import commands
from discord import app_commands

import config
from interactive_search import InteractiveSearch
from common import get_list_match, split_string
from task_kanboard import TaskKanboard

class TaskDatabase(commands.Cog):
    """A specific instance of the task bot (bugs, suggestions, etc.)"""

    def __init__(self, bot, kanboard_client):
        self._bot = bot
        self._kanboard_client = kanboard_client
        self._kanboard = None
        self._stopping = False

        try:
            logging.debug("Attempting to get channel %s", config.CHANNEL_ID)
            self._channel = self._bot.get_channel(config.CHANNEL_ID)
            if self._channel is None:
                raise Exception("Error getting bot channel!")
            self._database_path = os.path.join(config.CONFIG_DIR, config.DATABASE_PATH)
            self._interactive_sessions = []
            self.load()
        except KeyError as e:
            sys.exit(f'Config missing key: {e}')

    def save(self):
        savedata = {
            'entries': self._entries,
            'next_index': self._next_index,
            'labels': self._labels,
            'complexities': self._complexities,
            'priorities': self._priorities,
            'notifications_disabled': list(self._notifications_disabled),
        }

        if self._kanboard is not None:
            savedata["kanboard"] = self._kanboard.save()

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
                "Critical",
                "High",
                "Medium",
                "Low",
                "Zero",
                "N/A",
            ]
            self._complexities = {
                "easy":     ":green_circle:",
                "moderate": ":orange_circle:",
                "hard":     ":red_circle:",
                "unknown":  ":white_circle:"
            }
            self._notifications_disabled = set([])
            self.save()
            print(f"Initialized new {config.DESCRIPTOR_SINGLE} database", flush=True)
        else:
            with open(self._database_path, 'r') as f:
                data = json.load(f)

            # Must exist
            self._entries = data['entries']
            self._next_index = data['next_index']

            # TODO: Scan through and add all labels
            if 'labels' in data:
                self._labels = data['labels']
            else:
                self._labels = [
                    "misc",
                ]

            if 'priorities' in data:
                self._priorities = data['priorities']
            else:
                self._priorities = [
                    "Critical",
                    "High",
                    "Medium",
                    "Low",
                    "Zero",
                    "N/A",
                ]

            if 'complexities' in data:
                self._complexities = data['complexities']
            else:
                self._complexities = {
                    "easy":     ":green_circle:",
                    "moderate": ":orange_circle:",
                    "hard":     ":red_circle:",
                    "unknown":  ":white_circle:"
                }

            if 'kanboard' in data and not self._kanboard_client is None:
                self._kanboard = TaskKanboard.load_kanboard(self, self._kanboard_client, data['kanboard'])

            self._notifications_disabled = set([])
            if 'notifications_disabled' in data:
                for author in data['notifications_disabled']:
                    self._notifications_disabled.add(int(author))

            changed = False
            for item_id in self._entries:
                entry = self._entries[item_id]
                if "pending_notification" not in entry:
                    entry["pending_notification"] = True
                    changed = True
                if "complexity" not in entry:
                    entry["complexity"] = "unknown"
                    changed = True

            if changed:
                self.save()

            print(f"Loaded {config.DESCRIPTOR_SINGLE} database", flush=True)

    async def on_webhook_post(self, json_msg):
        if self._kanboard is not None:
            if await self._kanboard.on_webhook_post(json_msg):
                self.save()

    def get_entry(self, index_str):
        """
        Gets an entry for a given string index number
        Throws ValueError if it does not exist or parsing fails
        """

        try:
            index = int(index_str)
        except:
            raise ValueError(f"{index_str!r} is not a number")

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._entries:
            raise ValueError(f'{config.DESCRIPTOR_PROPER} #{index} not found!')

        return index, self._entries[index]

    def get_user_by_id(self, user_id, allow_empty=False):
        """
        Gets a user given a user_id int or string int
        Throws ValueError if user does not exist or parsing fails
        If allow_empty is true:
          if user_id is 0 or None, returns None
        else:
          if user_id is 0 or None, throws exception
        """

        if (user_id is None) or user_id == "0" or user_id == 0:
            if allow_empty:
                return None
            else:
                raise ValueError("User ID is 0 or None")

        if type(user_id) is not int:
            try:
                user_id = int(user_id)
            except:
                raise ValueError(f"{user_id!r} is not a number")

        user = self._bot.get_user(user_id)

        return user

    def get_user(self, guild, user):
        """
        Gets a user given a display name, username, or user id
        Throws ValueError if user does not exist or parsing fails
        """

        if (user is None) or user == "0" or user == 0:
            raise ValueError("User ID is 0 or None")

        if type(user) is not int:
            try:
                user = int(user)
            except:
                # Try to find the user by name
                matches = []
                for member in guild.members:
                    if member.display_name.lower().startswith(user.lower()):
                        matches.append(member)
                    elif member.name.lower().startswith(user.lower()):
                        matches.append(member)

                if len(matches) < 1:
                    raise ValueError(f"User {user!r} not found")
                if len(matches) > 1:
                    multimatch = []
                    for member in matches:
                        if (member.name != member.display_name):
                            multimatch.append(f"{member.name} ({member.display_name})")
                        else:
                            multimatch.append(f"{member.name}")
                    raise ValueError("Multiple users match {!r}: {}".format(user, "\n".join(multimatch)))

                user = matches[0].id

        return self._bot.get_user(user)

    async def reply(self, message, response):
        """
        Replies to a given message (in that channel)
        """
        await message.channel.send(response)

    def has_privilege(self, min_privilege, author, index=None):
        priv = 0; # Everyone has this level

        # Get privilege based on user list
        priv = max(priv, config.USER_PRIVILEGES.get(author.id, 0))

        # Get privilege based on group role
        for role in author.roles:
            priv = max(priv, config.GROUP_PRIVILEGES.get(role.id, 0))

        # Get privilege based on entry ownership
        if index is not None:
            entry = self._entries.get(index, None)
            if entry is not None:
                if entry["author"] == author.id:
                    priv = max(priv, 1)

        return priv >= min_privilege

    def add_entry(self, description, labels=["misc"], author=None, image=None, priority="N/A", complexity="unknown"):
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

        entry["priority"] = priority
        entry["complexity"] = complexity
        entry["pending_notification"] = False

        index = self._next_index

        self._next_index += 1
        self._entries[str(index)] = entry

        self.save()

        return (index, entry)

    async def format_entry(self, index, entry, include_reactions=False, mention_assigned=False, include_link=False):
        author_name = ""
        user = self.get_user_by_id(entry["author"], allow_empty=True)
        if user is not None:
            author_name = user.display_name

        react_text = ""
        if include_reactions and "message_id" in entry:
            try:
                msg = await self._channel.fetch_message(entry["message_id"])
            except discord.errors.NotFound:
                msg = None
                pass
            if msg is not None and msg.reactions:
                react_text = '\n'
                for react in msg.reactions:
                    react_text += f"{react.emoji} {react.count}    "

        assigned_text = ''
        if "assignee" in entry:
            user = self.get_user_by_id(entry["assignee"], allow_empty=True)
            if user is not None:
                if mention_assigned:
                    assigned_text = f'''`Assigned: `{user.mention}\n'''
                else:
                    assigned_text = f'''`Assigned: {user.display_name}`\n'''

        link = ''
        if include_link:
            link = "\nhttps://discord.com/channels/" + str(config.GUILD_ID) + "/" + str(config.CHANNEL_ID) + "/" + str(entry["message_id"])

        complexity_emoji = self._complexities[entry["complexity"]]

        entry_text = f'''`#{index} [{','.join(entry["labels"])} - {entry["priority"]}] {author_name}` {complexity_emoji}
{assigned_text}{entry["description"]}{react_text}{link}'''

        if "close_reason" in entry:
            entry_text = f'''~~{entry_text}~~
Closed: {entry["close_reason"]}'''

        embed = None
        if "image" in entry:
            embed = discord.Embed()
            embed.set_image(url=entry["image"])

        return entry_text, embed

    async def send_entry(self, index, entry, kanboard_update=True):
        # Compute the new entry text
        entry_text, embed = await self.format_entry(index, entry, include_reactions=False)

        msg = None
        if "message_id" in entry:
            try:
                msg = await self._channel.fetch_message(entry["message_id"])
            except discord.errors.NotFound:
                msg = None
                pass

        needs_save = False

        if msg is not None:
            # Edit the existing message
            await msg.edit(content=entry_text, embed=embed)

        else:
            # Send a new message
            msg = await self._channel.send(entry_text, embed=embed)
            entry["message_id"] = msg.id
            needs_save = True

        if self._kanboard is not None and kanboard_update:
            if await self._kanboard.update_entry(index, entry):
                needs_save = True

        if needs_save:
            self.save()

        for reaction in config.REACTIONS:
            await msg.add_reaction(reaction)

    async def print_search_results(self, responder, match_entries, limit=15, sort_entries=True, mention_assigned=False, include_reactions=True, include_link=False, ephemeral=False):
        """
        Calls responder.send() with matching entries up to limit
        If ephemeral=true, will append epmeheral=true to call
        """
        # Sort the returned entries
        if sort_entries:
            print_entries = self.sort_entries_by_priority(match_entries)
        else:
            print_entries = match_entries

        # Limit to specified number of replies at a time
        if len(print_entries) > limit:
            if ephemeral:
                await responder.send(f'Limiting to top {limit} results', ephemeral=True)
            else:
                await responder.send(f'Limiting to top {limit} results')
            print_entries = print_entries[:limit]

        for index, entry in print_entries:
            entry_text, embed = await self.format_entry(index, entry, include_reactions=include_reactions, mention_assigned=mention_assigned, include_link=include_link)
            if ephemeral:
                await responder.send(entry_text, embed=embed, ephemeral=True)
            else:
                await responder.send(entry_text, embed=embed)


    async def handle_message(self, message):
        commands = {
            "add": self.cmd_add,
            "report": self.cmd_add,
            "get": self.cmd_get,
            "roulette": self.cmd_roulette,
            "iroulette": self.cmd_iroulette,
            "search": self.cmd_search,
            "dsearch": self.cmd_dsearch,
            "isearch": self.cmd_isearch,
            "asearch": self.cmd_asearch,
            "rsearch": self.cmd_rsearch,
            "delete": self.cmd_delete,
            "reject": self.cmd_reject,
            "edit": self.cmd_edit,
            "append": self.cmd_append,
            "fix": self.cmd_fix,
            "unfix": self.cmd_unfix,
            "prune": self.cmd_prune,
            "notify": self.cmd_notify,
            "send_notifications": self.cmd_send_notifications,
            "sync": self.cmd_sync,
            "import": self.cmd_import,
            "repost": self.cmd_repost,
            "stats": self.cmd_stats,
            "astats": self.cmd_astats,
            "addlabel": self.cmd_addlabel,
            "dellabel": self.cmd_dellabel,
            "test": self.cmd_test,
            "assign": self.cmd_assign,
            "unassign": self.cmd_unassign,
            "list_assigned": self.cmd_list_assigned,
            "ping_assigned": self.cmd_ping_assigned,
            "kanboard_create": self.cmd_kanboard_create,
            "kanboard_update_all": self.cmd_kanboard_update_all,
            "busty_debug": self.cmd_busty_debug,
        }

        # First try to handle this message with any ongoing iterative searches
        # Make a copy of the list so it can be modified during iteration
        for session in self._interactive_sessions[:]:
            try:
                if (await session.handle_message(message)):
                    # This message was handled here - don't process it further
                    return
            except EOFError:
                # This session is complete
                self._interactive_sessions.remove(session)

        part = message.content.split(maxsplit=2)
        if (not message.content) or (len(part) < 1):
            return

        match = get_list_match(part[0].strip(), [config.PREFIX, ])
        if match is None:
            return

        # Length check is janky to let multiple bots share a channel - minimum 4 characters for prefix
        if len(part) < 2 or len(part[0].strip()) < 4:
            await self.usage(message)
            return

        match = get_list_match(part[1].strip(), commands.keys())
        if match is None:
            await self.usage(message)
            return

        args = ""
        if len(part) > 2:
            args = part[2].strip()

        async with message.channel.typing():
            try:
                await commands[match](message, args)
            except ValueError as e:
                for chunk in split_string(str(e)):
                    await self.reply(message, chunk)

    ################################################################################
    # Usage
    async def usage(self, message):
        usage = '''
**Commands everyone can use:**
`{prefix} add [label1,label2,...] <description>`
    Adds a new {single} with the given (optional) label(s)
    Label must be one of: {labels}
    Alias: report

`{prefix} search labels,priorities,limit`
    Searches all {plural} for ones that are tagged with all the specified labels / priorities
    Only show the top #limit results to reduce chatspam
    For example:
        {prefix} search quest,class,high

`{prefix} dsearch <search terms, count>`
    Searches all {single} descriptions for ones that contain all the specified search terms

`{prefix} asearch [author]`
    Finds all {plural} added by self, or author if specified

`{prefix} rsearch <:reaction:>`
    Gets open {plural}, sorted by count of the specified reaction

`{prefix} get <number>`
    Gets the {single} with the specified number

`{prefix} notify [on|off]`
    Toggles whether you get notified of updates to your {plural}

`{prefix} roulette [search terms]`
    Gets a random {single} matching search terms

`{prefix} iroulette [search terms]`
    Starts an interactive search for matching search terms but in random order

`{prefix} stats`
    Gets current {single} statistics

`{prefix} astats`
    Gets current {single} author statistics

**Commands the original {single} author and team members can use:**
`{prefix} reject <number> <reason why>`
    Closes the specified {single} with the given reason

`{prefix} edit <number> <description | label | image> [argument]`
    Edits the specified field of the entry

`{prefix} append <number> text`
    Appends text to an existing {single}'s description
'''.format(prefix=config.PREFIX, single=config.DESCRIPTOR_SINGLE, plural=config.DESCRIPTOR_PLURAL, labels=" ".join(self._labels))

        if self.has_privilege(2, message.author):
            usage += '''
**Commands team members can use:**

`{prefix} delete <number>`
    Deletes the specified {single}, for the purposes of redacting a {single}

`{prefix} edit <number> [author | priority | complexity ] [argument]`
    Edits the specified field of the entry

`{prefix} fix number [optional explanation]`
    Marks the specified {single} as fixed. Default explanation is simply "Fixed"

`{prefix} unfix <number>`
    Unmarks the specified {single} as fixed

`{prefix} isearch <search terms>`
    Interactive search session

`{prefix} send_notifications`
    Notifies {single} authors about updates to their entries

`{prefix} assign <number> [user]`
    Assigns {single} to self, or user if specified

`{prefix} unassign <number>`
    Unassigns {single}

`{prefix} list_assigned [user | all]`
    Prints out open {plural} that are assigned to you, the specified user, or "all"

`{prefix} sync`
    Synchronizes bot /commands with Discord
'''.format(prefix=config.PREFIX, single=config.DESCRIPTOR_SINGLE, plural=config.DESCRIPTOR_PLURAL, labels=" ".join(self._labels))

        if self.has_privilege(3, message.author):
            usage += '''
**Commands only leads can use:**
`{prefix} addlabel <newlabel>`
    Adds a new label

`{prefix} dellabel <label>`
    Removes a label

`{prefix} prune`
    Removes all fixed {plural} from the tracking channel

`{prefix} ping_assigned channel_id`
    Prints out all open {plural} in specified channel, pinging assigned people
'''.format(prefix=config.PREFIX, plural=config.DESCRIPTOR_PLURAL)

        if self.has_privilege(4, message.author):
            usage += '''
**Commands only you can use:**
`{prefix} import <#channel>`
    Imports all messages in the specified channel as {plural}

`{prefix} repost`
    Reposts/edits all known {plural}

`{prefix} kanboard_create`
    Creates a kanboard project & posts all {plural} to it

`{prefix} kanboard_update_all`
    Updates all {plural} on an existing kanboard project
'''.format(prefix=config.PREFIX, plural=config.DESCRIPTOR_PLURAL)

        for chunk in split_string(usage):
            await self.reply(message, chunk)


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
    # discussion messages

    async def handle_discussion_message(self, message):
        if message.author.bot:
            return
        pattern = re.compile(r"(" + config.DESCRIPTOR_SHORT + ")-([0-9]+)", re.IGNORECASE)
        matches = pattern.finditer(message.content)
        list_of_entries = []
        list_of_links = []
        for match in matches:
            if match.group(2) is not None:
                testIndex = match.group(2)
                try:
                    index, entry = self.get_entry(testIndex)
                except Exception:
                    return
                if "message_id" in entry:
                    list_of_entries.append((index, entry))
                    list_of_links.append("#" + str(index) + ": https://discord.com/channels/" + str(config.GUILD_ID) + "/" + str(config.CHANNEL_ID) + "/" + str(entry["message_id"]))
        if len(list_of_links) > 0:
            final_list = list_of_links[:3]
            if len(list_of_links) > 3:
                await message.channel.send("Here are the links to the tasks you mentioned, limited to 3 links:\n" + "\n".join(final_list))
            elif len(list_of_links) == 1:
                entry_text, embed = await self.format_entry(index, entry, include_reactions=True, include_link=True)
                await message.channel.send(entry_text, embed=embed)
            else:
                await message.channel.send("\n".join(final_list))

    ################################################################################
    # add / report
    async def cmd_add(self, message, args):
        if not args:
            raise ValueError('''How to submit a {single}:```
{prefix} add [label] <description>
```
Example:```
{prefix} add quest Bihahiahihaaravi refuses to talk to me when I'm wearing a fedora
```
You can also attach an image to your message to include it in the {single}
'''.format(prefix=config.PREFIX, single=config.DESCRIPTOR_SINGLE))

        if len(args.split()) < 5:
            raise ValueError('Description must contain at least 5 words')

        if len(args) != len(discord.utils.escape_mentions(args)):
            raise ValueError(f'Please do not include pings in your {config.DESCRIPTOR_SINGLE}')

        part = args.split(maxsplit=1)

        labels = part[0].strip().lower().split(',')
        description = part[1].strip()

        if len(description) > 1600:
            raise ValueError(f'Please limit your {config.DESCRIPTOR_SINGLE} to 1600 characters to allow for formatting and close info (currently {len(description)} characters)')

        good_labels = []
        failed_labels = False
        for label in labels:
            match = get_list_match(label.strip(), self._labels)
            if match is None:
                failed_labels = True
            else:
                good_labels.append(match)

        if len(good_labels) > 0 and failed_labels:
            # One but not all of the specified labels matched
            raise ValueError("Labels must be one of: [{}]".format(",".join(self._labels)))

        if len(good_labels) <= 0:
            # No labels were specified
            # Assign the label 'misc' and use the entire input as the description
            good_labels = ["misc"]
            description = args.strip()

        image = None
        for attach in message.attachments:
            if attach.url:
                image = attach.url
        # TODO: Steal this code for something else?
        #for embed in message.embeds:
        #    print("EMBED URL: " + embed.url)
        #    print(embed)
        #    image = embed.url

        (index, entry) = self.add_entry(description, labels=good_labels, author=message.author, image=image)

        # Post this new entry
        await self.send_entry(index, entry)

        await(self.reply(message, f"#{index} created successfully"))

    ################################################################################
    # edit
    async def cmd_edit(self, message, args):
        part = args.split(maxsplit=2)
        if (not args) or (len(part) < 2):
            raise ValueError('''How to edit a {single}:```
{prefix} edit # [description | label | image | author | priority | complexity] edited stuff
```
For example:```
{prefix} edit 5 description Much more detail here
```
'''.format(prefix=config.PREFIX, single=config.DESCRIPTOR_SINGLE))

        index, entry = self.get_entry(part[0].strip())

        operation = get_list_match(part[1].strip(), ['description', 'label', 'image', 'author', 'priority', 'complexity'])
        if operation is None:
            raise ValueError("Item to edit must be 'description', 'label', 'image', 'author', 'priority' or 'complexity'")

        min_priv = 4
        if operation in ['description', 'label', 'image']:
            min_priv = 1
        if operation in ['author', 'priority', 'complexity']:
            min_priv = 2

        if not self.has_privilege(min_priv, message.author, index=index):
            raise ValueError(f"You do not have permission to edit {operation} for entry #{index}")

        if operation == 'description':
            if len(part) < 3:
                raise ValueError("You need to actually supply a new description")

            description = part[2].strip()
            if len(description) > 1600:
                raise ValueError(f'Please limit your {config.DESCRIPTOR_SINGLE} to 1600 characters to allow for formatting and close info (currently {len(description)} characters)')

            entry["description"] = description

        elif operation == 'label':
            if len(part) < 3:
                raise ValueError("You need to actually supply a new label")

            labels = part[2].strip().lower().split(',')
            good_labels = []
            for label in labels:
                match = get_list_match(label.strip(), self._labels)
                if match is None:
                    raise ValueError("Labels must be one of: [{}]".format(",".join(self._labels)))
                good_labels.append(match)

            entry["labels"] = good_labels

        elif operation == 'image':
            image = None
            for attach in message.attachments:
                if attach.url:
                    image = attach.url

            if image is None:
                raise ValueError("You need to attach an image")

            entry["image"] = image

        elif operation == 'author':
            #TODO
            raise ValueError("NOT IMPLEMENTED YET")

        elif operation == 'priority':
            if len(part) < 3:
                raise ValueError('''
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

            priority = get_list_match(part[2].strip().lower(), self._priorities)
            if priority is None:
                raise ValueError("Priority must be one of: [{}]".format(",".join(self._priorities)))

            entry["priority"] = priority

        elif operation == 'complexity':
            complexities_str = ",".join(self._complexities.keys())
            if len(part) < 3:
                raise ValueError(f"Available complexities: [{complexities_str}]")

            complexity = get_list_match(part[2].strip().lower(), self._complexities.keys())
            if complexity is None:
                raise ValueError(f"Complexity must be one of: [{complexities_str}]")

            entry["complexity"] = complexity

        if entry["author"] == message.author.id:
            entry["pending_notification"] = False
        elif operation != "label":
            # If only the label changed, don't change the notification setting
            entry["pending_notification"] = True

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await message.channel.send(entry_text, embed=embed)
        await(self.reply(message, f"{config.DESCRIPTOR_PROPER} #{index} updated successfully"))

    ################################################################################
    # append
    async def cmd_append(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) < 2):
            raise ValueError(f'''Usage: {config.PREFIX} append <number> [additional description text]''')

        index, entry = self.get_entry(part[0].strip())

        if not self.has_privilege(1, message.author, index=index):
            raise ValueError(f"You do not have permission to append to #{index}")

        description = f'{entry["description"]}\n{part[1].strip()}'
        if len(description) > 1600:
            raise ValueError(f'Appending this message brings the length to {len(description)} which exceeds the 1600 character maximum to allow for formatting and close info')

        entry["description"] = description

        if entry["author"] == message.author.id:
            entry["pending_notification"] = False
        else:
            entry["pending_notification"] = True

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await message.channel.send(entry_text, embed=embed)
        await(self.reply(message, f"{config.DESCRIPTOR_PROPER} #{index} edited"))

    ################################################################################
    # get
    async def cmd_get(self, message, args):
        if not args:
            raise ValueError(f"Usage: {config.PREFIX} get <number>")

        match_entries = [(self.get_entry(args.strip()))]
        await self.print_search_results(message.channel, match_entries)

    ################################################################################
    # roulette
    async def cmd_roulette(self, message, args):
        if args:
            # If args are provided, use them to narrow the list
            match_entries, _, __, ___, ____ = await self.search_helper(args, max_count=10)
        else:
            # If no args, random from any open item
            match_entries = []
            for index in self._entries:
                entry = self._entries[index]
                if "close_reason" not in entry:
                    match_entries.append((index, entry))
        if not match_entries:
            await self.reply(message, f"No {config.DESCRIPTOR_PLURAL} found matching those search terms")
        else:
            await self.print_search_results(message.channel, [random.choice(match_entries)])

    ################################################################################
    # iroulette
    async def cmd_iroulette(self, message, args):
        if args:
            # If args are provided, use them to narrow the list
            match_entries, _, __, ___, ____ = await self.search_helper(args, max_count=10)
        else:
            # If no args, random from any open item
            match_entries = []
            for index in self._entries:
                entry = self._entries[index]
                if "close_reason" not in entry:
                    match_entries.append((index, entry))

        if not match_entries:
            await self.reply(message, f"No {config.DESCRIPTOR_PLURAL} found matching those search terms")
        else:
            random.shuffle(match_entries)
            inter = InteractiveSearch(self, message.author, match_entries)
            self._interactive_sessions.append(inter)
            await inter.send_first_message(message)

    ################################################################################
    # stats
    async def cmd_stats(self, message, args):
        stats = {}
        total = {}
        for priority in self._priorities:
            stats[priority] = {}
            for complexity in self._complexities:
                stats[priority][complexity] = 0
            total[priority] = 0


        total_open = 0
        total_closed = 0
        for index in self._entries:
            entry = self._entries[index]
            if "close_reason" in entry:
                total_closed += 1
            else:
                total[entry["priority"]] += 1
                stats[entry["priority"]][entry["complexity"]] += 1
                total_open += 1

        stats_text = f'''Current {config.DESCRIPTOR_SINGLE} stats:```'''
        stats_text += f"{'' : <13}"
        for comp in self._complexities:
            stats_text += f"{comp.capitalize() : <10}"
        stats_text += f"{'Total' : <10}"
        for item in total:
            stats_text += f'''
{item.ljust(10)} | '''
            for comp in stats[item]:
                stats_text += f"{stats[item][comp] : <10}"
            stats_text += f"{total[item] : <10}"
        stats_text += f'''
----------------
Total Open : {total_open}
Closed     : {total_closed}```'''
        await self.reply(message, stats_text)

    ################################################################################
    # astats
    async def cmd_astats(self, message, args):
        stats = {}

        for index in self._entries:
            entry = self._entries[index]
            if "author" in entry and entry["author"] != 0:
                author = entry["author"]
                if author in stats:
                    stats[author] += 1
                else:
                    stats[author] = 1

        await self.reply(message, f'''Current {config.DESCRIPTOR_SINGLE} author stats:''')
        stats_text = ''
        for author_id, count in sorted(stats.items(), key=lambda kv: kv[1], reverse=True):
            author = self.get_user_by_id(author_id)
            if author is not None:
                stats_text += f'''{author.display_name.ljust(20)} : {count}\n'''

        for chunk in split_string(stats_text):
            await self.reply(message, '```python\n' + chunk + '```')

    ################################################################################
    # search core helper
    async def search_helper(self, args, max_count):
        part = args.replace(","," ").split()
        if (not args) or (len(part) < 1):
            raise ValueError('''Usage: {prefix} search labels,priorities,complexities,assigned,max_count

Search for items by tags. Note this does **not** search by description - use dsearch for that. Search items can be separated by commas or spaces.

Will not show zero priority things by default.

You can combine multiple different tags to search for specific things. For example:
> `{prefix} search plugin cmd moderate hard assigned 5`

This will search for items labeled plugin AND cmd, have complexity=hard OR complexity=moderate, are assigned to someone, and at most return 5 results

Default limit is 10 results
If using multiple labels, all specified labels must match
If using multiple priorities or complexities, at least one must match

Available labels: {labels}
Available priorities: {priorities}
Available complexities: {complexities}'''.format(prefix=config.PREFIX, labels=self._labels, priorities=self._priorities, complexities=self._complexities.keys()))

        match_labels = []
        match_priorities = []
        match_complexities = []
        # If False, don't check assigned.
        # If None, any assigned user matches
        # Otherwise, only specific user matches
        match_assigned = False
        for item in part:
            item = item.strip()
            label_match = get_list_match(item, self._labels)
            priority_match = get_list_match(item, self._priorities)
            complexity_match = get_list_match(item, self._complexities.keys())

            if item.strip().lower() == "assigned":
                match_assigned = None
            elif label_match is not None:
                match_labels.append(label_match)
            elif complexity_match is not None:
                match_complexities.append(complexity_match)
            elif priority_match is not None:
                match_priorities.append(priority_match)
            elif re.search("^[0-9][0-9]*$", item):
                max_count = int(item)
            else:
                raise ValueError(f'''No priority, label, complexity, or 'assigned' matching {item!r}''')

        if len(match_labels) == 0 and len(match_priorities) == 0 and len(match_complexities) == 0 and match_assigned is False:
            raise ValueError('Must specify something to search for')

        if len(match_priorities) == 0:
            # Iterate a shallow copy of the entries table so new reports don't break it
            match_priorities = self._priorities.copy()
            if "Zero" in match_priorities:
                match_priorities.remove("Zero")

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

                if (len(match_complexities) > 0) and (entry["complexity"] not in match_complexities):
                    matches = False

                if match_assigned is None:
                    if "assignee" not in entry:
                        matches = False
                elif match_assigned is not False:
                    # TODO
                    raise NotImplementedError("Searching against a specific assigned user not implemented")

                if matches:
                    count += 1
                    match_entries.append((index, entry))

        return (match_entries, match_labels, match_priorities, match_complexities, max_count)

    ################################################################################
    # search
    async def cmd_search(self, message, args):
        match_entries, match_labels, match_priorities, match_complexities, max_count = await self.search_helper(args, max_count=10)

        await self.print_search_results(message.channel, match_entries, limit=max_count, include_link=True)

        await self.reply(message, "{} {} found matching labels={} priorities={} complexities={}".format(
            len(match_entries), config.DESCRIPTOR_PLURAL,
            ",".join(match_labels), ",".join(match_priorities), ",".join(match_complexities)))

    ################################################################################
    # dsearch
    async def cmd_dsearch(self, message, args):
        """Description search ~command"""
        match_entries, limit = await self.dsearch_internal(args, 15)
        await message.channel.send(f"{len(match_entries)} {config.DESCRIPTOR_PLURAL} found matching {args}")
        await self.print_search_results(message.channel, match_entries, limit=limit, include_link=True)

    @app_commands.command(name=f'{config.DESCRIPTOR_SINGLE}_description_search',
                          description=f'Searches all {config.DESCRIPTOR_SINGLE} descriptions for ones that contain all the specified search terms')
    @app_commands.describe(search_terms='Text to search for',
                           limit='Maximum number of matches to return')
    async def slash_dsearch(self, message, search_terms: str, limit: int = 99):
        """Description search /command"""
        match_entries, limit = await self.dsearch_internal(search_terms, limit)
        await message.response.send_message(f"{len(match_entries)} {config.DESCRIPTOR_PLURAL} found matching {search_terms}", ephemeral=True)
        await self.print_search_results(message.followup, match_entries, limit=limit, ephemeral=True, include_link=True)

    async def dsearch_internal(self, search_terms: str, limit: int):
        """Description search terms parser"""
        part = search_terms.replace(",", " ").split()
        if (not search_terms) or (len(part) < 1):
            raise ValueError(f'''Usage: {config.PREFIX} dsearch <search terms, count>''')

        # Try to parse each argument as an integer - and if so, use that as the limit
        search_terms = []
        for term in part:
            try:
                limit = int(term)
            except Exception:
                # Don't search for numbers
                search_terms.append(term)

        if len(search_terms) < 1:
            raise ValueError(f'''Usage: {config.PREFIX} dsearch <search terms, count>''')

        match_entries = []
        for index in self._entries:
            entry = self._entries[index]
            if "close_reason" not in entry:
                matches = True
                for term in search_terms:
                    if term.strip().lower() not in entry["description"].lower():
                        matches = False

                if matches:
                    match_entries.append((index, entry))

        return match_entries, limit


    ################################################################################
    # isearch
    async def cmd_isearch(self, message, args):
        match_entries, _, __, ___, ____ = await self.search_helper(args, max_count=100)

        if len(match_entries) <= 0:
            raise ValueError("No results to display")

        inter = InteractiveSearch(self, message.author, match_entries)
        self._interactive_sessions.append(inter)
        await inter.send_first_message(message)

    ################################################################################
    # asearch
    async def cmd_asearch(self, message, args):
        author = message.author
        if args:
            author = self.get_user(message.guild, args)

        match_entries = []
        open_count = 0
        total_count = 0
        for index in self._entries:
            entry = self._entries[index]
            if "author" in entry and entry["author"] == author.id:
                total_count += 1
                if "close_reason" not in entry:
                    match_entries.append((index, entry))
                    open_count += 1

        await self.print_search_results(message.channel, match_entries, include_link=True)

        await(self.reply(message, f"{open_count} open {config.DESCRIPTOR_PLURAL} of {total_count} total from author {author.display_name}"))

    ################################################################################
    # rsearch
    async def cmd_rsearch(self, message, args):
        if (not args) or (" " in args):
            raise ValueError(f'''Usage: {config.PREFIX} rsearch <:reaction:>''')

        await self.reply(message, "Getting a list of most-reacted entries. This will take some time...")

        # Will be a list with entries of the form (reaction count, (index, entry))
        raw_entries = []
        # Iterate a shallow copy of the entries table so new reports don't break it
        for index in self._entries.copy():
            # Exit early if shutting down
            if self._stopping:
                return

            entry = self._entries[index]
            if ("message_id" in entry) and ("close_reason" not in entry):
                try:
                    msg = await self._channel.fetch_message(entry["message_id"])
                    if msg is not None and msg.reactions:
                        react_text = '\n'
                        for react in msg.reactions:
                            if react.emoji == args:
                                raw_entries.append((react.count, (index, entry)))
                                break
                except discord.errors.NotFound:
                    pass

        # TODO: Custom reaction searching support
        if not raw_entries:
            raise ValueError(f"No entries with reaction {args!r} - note that custom reactions are not supported yet")

        raw_entries.sort(key=lambda kv: kv[0], reverse=True)
        match_entries = [x[1] for x in raw_entries]

        await self.print_search_results(message.channel, match_entries, sort_entries=False)

    ################################################################################
    # addlabel
    async def cmd_addlabel(self, message, args):
        if not self.has_privilege(3, message.author):
            raise ValueError("You do not have permission to use this command")

        args = args.lower()

        if (not args) or re.search("[^a-z]", args):
            raise ValueError(f'''Usage: {config.PREFIX} addlabel <label>
Labels can only contain a-z characters''')

        match = get_list_match(args, self._labels)
        if match is not None:
            raise ValueError(f'Can not add label {args} because it matches {match}')

        self._labels.append(args)
        self.save()

        await(self.reply(message, f"Label {args} added successfully"))

    ################################################################################
    # dellabel
    async def cmd_dellabel(self, message, args):
        if not self.has_privilege(3, message.author):
            raise ValueError("You do not have permission to use this command")

        args = args.lower()

        if (not args) or re.search("[^a-z]", args):
            raise ValueError(f'''Usage: {config.PREFIX} dellabel <label>
Labels can only contain a-z characters''')

        match = get_list_match(args, self._labels)
        if match is None:
            raise ValueError('Input {} does not match any existing labels [{}]'.format(args, ",".join(self._labels)))

        self._labels.remove(match)

        count = 0

        # Remove label from all entries
        for index in self._entries:
            # Exit early if shutting down
            if self._stopping:
                return

            entry = self._entries[index]
            changed = False
            if match in entry["labels"]:
                changed = True
                entry["labels"].remove(match)
                count += 1
            # Make sure there is at least one label
            if len(entry["labels"]) == 0:
                entry["labels"].append("misc")

            # Update the entry in the task channel
            if changed and (("close_reason" not in entry) or ("message_id" in entry)):
                await self.send_entry(index, entry)

        self.save()

        await(self.reply(message, f"Label {match} removed successfully from {count} {config.DESCRIPTOR_PLURAL}"))


    ################################################################################
    # delete
    async def cmd_delete(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) < 1):
            raise ValueError(f'''Usage: {config.PREFIX} delete <number>''')
        if not self.has_privilege(1, message.author):
            raise ValueError("You do not have permission to use this command")

        index, entry = self.get_entry(part[0].strip())

        if "close_reason" in entry:
            entry["close_reason"] = ""
        if "pending_notification" in entry:
            entry["pending_notification"] = False
        if "description" in entry:
            entry["description"] = "redacted"
        if "image" in entry:
            entry.pop("image")

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        await(self.reply(message, f"{config.DESCRIPTOR_PROPER} #{index} deleted. You still need to manually delete any messages related to this in other channels."))

    ################################################################################
    # reject
    async def cmd_reject(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) < 2):
            raise ValueError(f'''Usage: {config.PREFIX} reject <number> <required explanation>''')

        index, entry = self.get_entry(part[0].strip())

        if not self.has_privilege(1, message.author, index=index):
            raise ValueError(f"You do not have permission to reject #{index}")

        entry["close_reason"] = part[1].strip()

        if entry["author"] == message.author.id:
            entry["pending_notification"] = False
        else:
            entry["pending_notification"] = True

        if "assignee" in entry:
            entry.pop("assignee")

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await message.channel.send(entry_text, embed=embed)
        await(self.reply(message, f"{config.DESCRIPTOR_PROPER} #{index} rejected"))

    ################################################################################
    # fix
    # TODO: Change this to re-use reject code, lots of duplication here
    async def cmd_fix(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) < 1):
            raise ValueError(f'''Usage: {config.PREFIX} fix <number> [optional explanation]''')

        index, entry = self.get_entry(part[0].strip())

        if not self.has_privilege(1, message.author, index=index):
            raise ValueError(f"You do not have permission to fix #{index}")

        if len(part) > 1:
            entry["close_reason"] = part[1].strip()
        else:
            entry["close_reason"] = "Fixed"

        if entry["author"] == message.author.id:
            entry["pending_notification"] = False
        else:
            entry["pending_notification"] = True

        if "assignee" in entry:
            entry.pop("assignee")

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await message.channel.send(entry_text, embed=embed)
        await(self.reply(message, f"{config.DESCRIPTOR_PROPER} #{index} marked as fixed"))

    ################################################################################
    # unfix
    async def cmd_unfix(self, message, args):
        part = args.split(maxsplit=2)
        if (not args) or (len(part) != 1):
            raise ValueError(f'''Usage: {config.PREFIX} unfix <number>''')

        index, entry = self.get_entry(part[0].strip())

        if not self.has_privilege(1, message.author, index=index):
            raise ValueError(f"You do not have permission to unfix #{index}")

        if "close_reason" in entry:
            entry.pop("close_reason")

        if entry["author"] == message.author.id:
            entry["pending_notification"] = False
        else:
            entry["pending_notification"] = True

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await message.channel.send(entry_text, embed=embed)
        await(self.reply(message, f"{config.DESCRIPTOR_PROPER} #{index} unmarked as fixed"))

    ################################################################################
    # prune
    async def cmd_prune(self, message, args):
        if not self.has_privilege(3, message.author):
            raise ValueError("You do not have permission to use this command")

        await(self.reply(message, "Prune started, this will take some time..."))

        match_entries = []
        count = 0
        # Iterate a shallow copy of the entries table so new reports don't break it
        for index in self._entries.copy():
            # Exit early if shutting down
            if self._stopping:
                return

            entry = self._entries[index]
            # If the entry is both closed AND present in the entry channel
            if ("close_reason" in entry) and ("message_id" in entry):
                try:
                    msg = await self._channel.fetch_message(entry["message_id"])
                except discord.errors.NotFound:
                    msg = None
                    pass
                if msg is not None:
                    await msg.delete()

                    # Since this message is no longer there...
                    entry.pop("message_id")
                    match_entries.append((index, entry))
                    count += 1

        self.save()

        await self.print_search_results(message.channel, match_entries, limit=99999)
        await(self.reply(message, f"{count} entries pruned successfully"))

    ################################################################################
    # notify
    async def cmd_notify(self, message, args):
        if not args:
            if message.author.id in self._notifications_disabled:
                await(self.reply(message, f'''You will __not__ be notified of changes to your {config.DESCRIPTOR_PLURAL}.
To change this, `{config.PREFIX} notify on`'''))
            else:
                await(self.reply(message, f'''You **will** be notified of changes to your {config.DESCRIPTOR_PLURAL}.
Notifications are on by default.
To change this, `{config.PREFIX} notify off`'''))
            return

        match = get_list_match(args.strip(), ["on", "off"])
        if match is None:
            raise ValueError(f"Argument to {config.PREFIX} notify must be 'on' or 'off'")

        if match == "on":
            if message.author.id in self._notifications_disabled:
                self._notifications_disabled.remove(message.author.id)
        else:
            self._notifications_disabled.add(message.author.id)

        self.save()

        if message.author.id in self._notifications_disabled:
            await(self.reply(message, f'''You will __not__ be notified of changes to your {config.DESCRIPTOR_PLURAL}.
To change this, {config.PREFIX} notify on'''))
        else:
            await(self.reply(message, f'''You **will** be notified of changes to your {config.DESCRIPTOR_PLURAL}.
Notifications are on by default.
To change this, {config.PREFIX} notify off'''))


    ################################################################################
    # send_notifications
    async def cmd_send_notifications(self, message, args):
        if not self.has_privilege(2, message.author):
            raise ValueError("You do not have permission to use this command")

        await(self.reply(message, "Notification process started..."))

        count = 0
        opt_out = 0
        no_user = 0
        # Iterate a shallow copy of the entries table so new reports don't break it
        for index in self._entries.copy():
            # Exit early if shutting down
            if self._stopping:
                return

            entry = self._entries[index]
            if entry["pending_notification"]:
                count += 1
                if "author" in entry:
                    user = self.get_user_by_id(entry["author"], allow_empty=True)
                    if user is not None:
                        if entry["author"] in self._notifications_disabled:
                            opt_out += 1
                        else:
                            entry_text, embed = await self.format_entry(index, entry, include_reactions=False)
                            entry_text = f'''{user.mention} Your {config.DESCRIPTOR_SINGLE} was updated:
    {entry_text}'''
                            msg = await message.channel.send(entry_text, embed=embed)
                    else:
                        no_user += 1
                else:
                    no_user += 1

                entry["pending_notification"] = False

                # Might as well save a bunch of times in case this gets interrupted
                self.save()

        await(self.reply(message, f"{count} notifications processed successfully, {opt_out} of which were suppressed by user opt-out, {no_user} of which could not find a user to ping"))

    ################################################################################
    # repost
    async def cmd_repost(self, message, _):
        if not self.has_privilege(4, message.author):
            raise ValueError("You do not have permission to use this command")

        await(self.reply(message, "Repost started, this will take some time..."))

        await(self.reply(message, f"Building a set of all valid {config.DESCRIPTOR_SINGLE} message ids..."))

        valid = set()
        # Iterate a shallow copy of the entries table so new reports don't break it
        for index in self._entries.copy():
            entry = self._entries[index]
            if "message_id" in entry:
                valid.add(entry["message_id"])

        await(self.reply(message, "Searching the channel for untracked messages..."))

        def predicate(iter_msg):
            # Delete messages written by a bot that either wasn't this bot OR wasn't a valid message
            return iter_msg.author.bot and (iter_msg.author.id != self._bot.application_id or iter_msg.id not in valid)

        deleted = await self._channel.purge(limit=9999, check=predicate)
        count = 0
        for iter_msg in deleted:
            # Exit early if shutting down
            if self._stopping:
                return

            await(self.reply(message, "Removing untracked message:"))
            embed = None
            if iter_msg.embeds is not None and len(iter_msg.embeds) > 0:
                embed = iter_msg.embeds[0]
            await message.channel.send(iter_msg.content, embed=embed)
            count += 1

        await(self.reply(message, f"{count} untracked messages removed successfully"))

        await(self.reply(message, "Reposting missing messages..."))

        count = 0
        for index in self._entries:
            # Exit early if shutting down
            if self._stopping:
                return

            if "close_reason" not in self._entries[index]:
                count += 1
                await self.send_entry(index, self._entries[index])

        await(self.reply(message, f"{count} entries reposted successfully"))

    ################################################################################
    # sync
    async def cmd_sync(self, message, args):
        if not self.has_privilege(2, message.author):
            raise ValueError("You do not have permission to use this command")

        fmt = await self._bot.tree.sync(guild=message.guild)
        await self.reply(message, f'Synced {len(fmt)} commands.')

    ################################################################################
    # import
    async def cmd_import(self, message, args):
        if not self.has_privilege(4, message.author):
            raise ValueError("You do not have permission to use this command")

        part = args.split(maxsplit=2)
        if len(part) != 1 or len(part[0].strip()) < 10:
            raise ValueError(f"Usage: {config.PREFIX} import #channel")

        channel_id = part[0].strip()
        channel_id = channel_id[2:-1]
        import_channel = self._bot.get_channel(channel_id)
        if import_channel is None:
            raise ValueError(f"Can not find channel {channel_id!r}")

        await(self.reply(message, "Import started, this will take some time..."))

        to_import = []
        async for msg in self._bot.logs_from(import_channel, limit=1000, reverse=True):
            if not msg.content:
                continue

            image = None
            for attach in msg.attachments:
                if attach.url:
                    image = attach.url


            created_text = "Created: " + msg.timestamp.strftime("%Y-%m-%d")

            react_text = ""
            if msg.reactions:
                react_text = "Original Reactions:"
                for react in msg.reactions:
                    react_text += f"    {react.emoji} {react.count}"

            to_import.append((msg.timestamp, msg.content + "\n\n" + created_text + "\n" + react_text, msg.author, image))

        # SORT
        to_import.sort(key=lambda x: x[0])

        for _, content, author, image in to_import:
            (index, entry) = self.add_entry(content, author=author, image=image)

            # Post this new entry
            await self.send_entry(index, entry)

        await(self.reply(message, f"{len(to_import)} entries from channel {part[0]} imported successfully"))

    ################################################################################
    # assign
    async def cmd_assign(self, message, args):
        if not self.has_privilege(2, message.author):
            raise ValueError("You do not have permission to use this command")

        part = args.split(maxsplit=1)
        if (not args) or (not part):
            raise ValueError(f'''Usage: {config.PREFIX} assign <number> [user]''')

        index, entry = self.get_entry(part[0].strip())

        assignee = message.author

        if len(part) > 1:
            assignee = self.get_user(message.guild, part[1].strip())

        entry["assignee"] = assignee.id
        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await message.channel.send(entry_text, embed=embed)
        await(self.reply(message, f"{config.DESCRIPTOR_PROPER} #{index} assigned to {assignee.display_name}"))

    ################################################################################
    # unassign
    async def cmd_unassign(self, message, args):
        if not self.has_privilege(2, message.author):
            raise ValueError("You do not have permission to use this command")

        part = args.split(maxsplit=1)
        if (not args) or (not part):
            raise ValueError(f'''Usage: {config.PREFIX} unassign <number>''')

        index, entry = self.get_entry(part[0].strip())

        if "assignee" not in entry:
            raise ValueError(f'{config.DESCRIPTOR_PROPER} #{index} is already unassigned')

        entry.pop("assignee")
        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await message.channel.send(entry_text, embed=embed)
        await(self.reply(message, f"{config.DESCRIPTOR_PROPER} #{index} unassigned"))

    ################################################################################
    # list_assigned
    async def cmd_list_assigned(self, message, args):
        if not self.has_privilege(2, message.author):
            raise ValueError("You do not have permission to use this command")

        match_assignee = message.author

        if args:
            if args.lower() == "all":
                # Match any non-empty assignee
                match_assignee = None
            else:
                # Match specific assignee
                match_assignee = self.get_user(message.guild, args)

        match_entries = []
        count = 0
        for index in self._entries:
            entry = self._entries[index]
            if "close_reason" not in entry:
                if "assignee" in entry:
                    if (match_assignee is None) or (entry["assignee"] == match_assignee.id):
                        count += 1
                        match_entries.append((index, entry))

        await self.print_search_results(message.channel, match_entries, limit=9999)

        if match_assignee is None:
            await self.reply(message, f"{count} total assigned {config.DESCRIPTOR_PLURAL} found")
        else:
            await self.reply(message, f"{count} assigned {config.DESCRIPTOR_PLURAL} found for user {match_assignee.display_name}")

    ################################################################################
    # ping_assigned
    async def cmd_ping_assigned(self, message, args):
        if not self.has_privilege(3, message.author):
            raise ValueError("You do not have permission to use this command")

        try:
            channel_id = int(args)
        except:
            raise ValueError(f"{args!r} is not a number")

        channel = self._bot.get_channel(channel_id)
        if self._channel is None:
            raise Exception("Error getting channel!")

        await self.reply(message, "Starting notification process...")

        match_entries = []
        count = 0
        for index in self._entries:
            entry = self._entries[index]
            if "close_reason" not in entry:
                if "assignee" in entry:
                    count += 1
                    match_entries.append((index, entry))

        await self.print_search_results(channel, match_entries, limit=9999, mention_assigned=True)

        await self.reply(message, f"{count} total assigned {config.DESCRIPTOR_PLURAL} mentioned in channel {channel.name}")


    def get_flattened_priority(cls, entry):
        return entry[1]["priority"] + "," + entry[1]["complexity"]

    def sort_entries_by_priority(cls, entry_list):
        priority = {
            "Critical,easy": 1,
            "Critical,moderate": 2,
            "Critical,hard": 3,
            "Critical,unknown": 4,
            "High,easy": 5,
            "High,moderate": 6,
            "Medium,easy": 7,
            "High,hard": 8,
            "High,unknown": 9,
            "Medium,moderate": 10,
            "Low,easy": 11,
            "N/A,easy": 12,
            "Medium,hard": 13,
            "Medium,unknown": 14,
            "Low,moderate": 15,
            "N/A,moderate": 16,
            "Zero,easy": 17,
            "N/A,unknown": 18,
            "N/A,hard": 19,
            "Low,hard": 20,
            "Low,unknown": 21,
            "Zero,moderate": 22,
            "Zero,hard": 23,
            "Zero,unknown": 24,
        }
        def cmp(a, b):
            return (a > b) - (a < b)

        # Sort first by the above list. If not in the list, sort by lex
        return sorted(entry_list, key=cmp_to_key(lambda x, y: cmp(priority[cls.get_flattened_priority(x)], priority[cls.get_flattened_priority(y)])))

    async def cmd_kanboard_create(self, message, args):
        if not self.has_privilege(4, message.author):
            raise ValueError("You do not have permission to use this command")

        await self.reply(message, "Starting kanboard create...")

        if self._kanboard_client is None:
            await self.reply(message, "Kanboard is not configured for this bot")
            return

        # Disassociate the existing entries with existing kanboard
        for index in self._entries:
            entry = self._entries[index]
            if "kanboard_id" in entry:
                entry.pop("kanboard_id")

        self._kanboard = await TaskKanboard.create_kanboard(self, self._kanboard_client, config.DESCRIPTOR_PLURAL)
        await self._kanboard.update_all_entries()
        self.save()

        await self.reply(message, "Kanboard create complete.")


    async def cmd_kanboard_update_all(self, message, args):
        if not self.has_privilege(4, message.author):
            raise ValueError("You do not have permission to use this command")

        if self._kanboard is None:
            raise ValueError("This project does not have a kanboard")

        await self.reply(message, "Starting update of all kanboard entries...")

        await self._kanboard.update_all_entries()
        self.save()

        await self.reply(message, "Kanboard update complete.")

    async def cmd_busty_debug(self, message, args):
        if not self.has_privilege(4, message.author):
            raise ValueError("You do not have permission to use this command")

        await self.reply(message, "Starting BustyDebug:TM:")

        if self._kanboard is None:
            raise ValueError("This project does not have a kanboard")

        for project in await self._kanboard_client.getAllProjects_async():
            await self._kanboard_client.removeProject_async(project_id=project["id"])

        await self.reply(message, "Finished BustyDebug:TM:")


