import discord
import discord
import sys
import os
import enum
import json
import re
import random

import config
from interactive_search import InteractiveSearch
from common import split_string, get_list_match
from functools import cmp_to_key
from discord import app_commands
from discord.ext import commands

class SuggestionComponents(enum.Enum):
    description = "description"
    label = "label"
    image = "image"
    priority = "priority"
    complexity = "complexity"


class TaskDatabase(commands.GroupCog, name=config.DESCRIPTOR_SHORT):
    def __init__(self, bot):
        self._bot = bot
        self._stopping = False
        try:
            self._channel = None
            self._database_path = os.path.join(config.CONFIG_DIR, config.DATABASE_PATH)
            self._interactive_sessions = []
            self.load()
        except KeyError as e:
            sys.exit('Config missing key: {}'.format(e))
    
    async def reply(self, message, response):
        """
        Replies to a given message (in that channel)
        """
        await message.channel.send(response)
    
    def save(self):
        savedata = {
            'entries': self._entries,
            'next_index': self._next_index,
            'labels': self._labels,
            'complexities': self._complexities,
            'priorities': self._priorities,
            'notifications_disabled': list(self._notifications_disabled),
        }

        with open(self._database_path, 'w', encoding="utf-8") as f:
            json.dump(savedata, f, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': '))
    
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
                raise ValueError("{!r} is not a number".format(user_id))

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
                    raise ValueError("User {!r} not found".format(user))
                if len(matches) > 1:
                    multimatch = []
                    for member in matches:
                        if (member.name != member.display_name):
                            multimatch.append("{} ({})".format(member.name, member.display_name))
                        else:
                            multimatch.append("{}".format(member.name))
                    raise ValueError("Multiple users match {!r}: {}".format(user, "\n".join(multimatch)))

                user = matches[0].id

        return self._bot.get_user(user)

    async def validate_using_bot_channel(self, interaction : discord.Interaction, message):
        if interaction.channel_id == config.BOT_INPUT_CHANNEL and self._stopping == False:
            return True
        return False
    
    def load(self):
        if not os.path.exists(self._database_path):
            self._entries = {}
            self._next_index = 1
            self._labels = [
                "misc",
                "item",
                "mobs",
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
            print("Initialized new {} database".format(config.DESCRIPTOR_SINGLE), flush=True)
        else:
            with open(self._database_path, 'r', encoding="utf-8") as f:
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

            print("Loaded {} database".format(config.DESCRIPTOR_SINGLE), flush=True)

    def get_entry(self, index_str):
        """
        Gets an entry for a given string index number
        Throws ValueError if it does not exist or parsing fails
        """

        try:
            index = int(index_str)
        except:
            raise ValueError("{!r} is not a number".format(index_str))

        # Ugh, json keys need to be strings, not numbers
        index = str(index)

        if index not in self._entries:
            raise ValueError('{proper} #{index} not found!'.format(proper=config.DESCRIPTOR_PROPER, index=index))

        return index, self._entries[index]

    async def validate_or_get_posting_channel(self):
        if self._channel is None:
            self._channel = await self._bot.fetch_channel(config.CHANNEL_ID)
            if self._channel is not None:
                return True
            else:
                return False
        else:
            return True

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
    
    async def format_entry(self, index, entry, include_reactions=False, mention_assigned=False):
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
                    react_text += "{} {}    ".format(react.emoji, react.count)

        assigned_text = ''
        if "assignee" in entry:
            user = self.get_user_by_id(entry["assignee"], allow_empty=True)
            if user is not None:
                if mention_assigned:
                    assigned_text = '''`Assigned: `{}\n'''.format(user.mention)
                else:
                    assigned_text = '''`Assigned: {}`\n'''.format(user.display_name)

        complexity_emoji = self._complexities[entry["complexity"]]

        entry_text = '''`#{} [{} - {}] {}` {}
{}{}{}'''.format(index, ','.join(entry["labels"]), entry["priority"], author_name, complexity_emoji, assigned_text, entry["description"], react_text)

        if "close_reason" in entry:
            entry_text = '''~~{}~~
Closed: {}'''.format(entry_text, entry["close_reason"])

        embed = None
        if "image" in entry:
            embed = discord.Embed()
            embed.set_image(url=entry["image"])

        return entry_text, embed

    async def send_entry(self, index, entry):
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

        if needs_save:
            self.save()

        for reaction in config.REACTIONS:
            await msg.add_reaction(reaction)

    async def handle_discussion_message(self, message):
        pattern = re.compile(r"(" + config.DESCRIPTOR_SINGLE + ")-([0-9]+)", re.IGNORECASE)
        matches = pattern.finditer(message.content)
        list_of_links = []
        for match in matches:
            if match.group(2) is not None:
                testIndex = match.group(2)
                try:
                    index, entry = self.get_entry(testIndex)
                except Exception as e:
                    return

                if "message_id" in entry:
                    list_of_links.append("#" + str(index) + ": https://discord.com/channels/" + str(config.GUILD_ID) + "/" + str(config.CHANNEL_ID) + "/" + str(entry["message_id"]))
        if len(list_of_links) > 0:
            if (len(list_of_links) > 5):
                final_list = list_of_links[:5]
                await message.channel.send("Here are the links to the tasks you mentioned, limited to 5 links:\n" + "\n".join(final_list))
            else:
                final_list = list_of_links[:5]
                await message.channel.send("Here are the links to the tasks you mentioned:\n" + "\n".join(final_list))


    ### Report command aliases ###
    @app_commands.command(name="report", description="Add a " + config.DESCRIPTOR_SINGLE + " to the database")
    @app_commands.describe(description="Description of the " + config.DESCRIPTOR_SINGLE + " to add")
    @app_commands.describe(label="Labels, comma separated. ex: misc,item,mobs")
    async def slash_report(self, interaction: discord.Interaction, description: str, label: str = "", attachment: discord.Attachment = None):
        await self.slash_common_add(interaction, description, label, attachment)

    @slash_report.autocomplete('label')
    async def slash_report_label_autocomplete(self, interaction: discord.Interaction, current: str):
        return await self.slash_common_label_autocomplete(interaction, current)
    
    ### Add command and aliases ###
    @app_commands.command(name="add", description="Add a " + config.DESCRIPTOR_SINGLE + " to the database")
    @app_commands.describe(description="Description of the " + config.DESCRIPTOR_SINGLE + " to add")
    @app_commands.describe(label="Labels, comma separated. ex: misc,item,mobs")
    async def slash_add(self, interaction: discord.Interaction, description: str, label: str = "", attachment: discord.Attachment = None):
        await self.slash_common_add(interaction, description, label, attachment)

    @slash_add.autocomplete('label')
    async def slash_add_label_autocomplete(self, interaction: discord.Interaction, current: str):
        return await self.slash_common_label_autocomplete(interaction, current)
    
    async def slash_common_label_autocomplete(self, _: discord.Interaction, current: str):
        list_of_labels = []
        for label in self._labels:
            if current.lower() in label.lower():
                list_of_labels.append(app_commands.Choice(name=label, value=label))
        return list_of_labels


    async def slash_common_add(self, interaction: discord.Interaction, description: str, label: str = "", attachment: discord.Attachment = None):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            image = None
            if attachment is not None:
                image = attachment.url
            msg = await self.common_add(interaction.user, interaction.channel, label, description, image)
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)
    
    async def msg_add(self, message, args):
        if not args:
            raise ValueError('''How to submit a {single}:```
{prefix} add [label] <description>
```
Example:```
{prefix} add quest Bihahiahihaaravi refuses to talk to me when I'm wearing a fedora
```
You can also attach an image to your message to include it in the {single}
'''.format(prefix=config.PREFIX, single=config.DESCRIPTOR_SINGLE))
        
        part = args.split(maxsplit=1)
        # Parse the label and description
        labels = part[0].strip()
        suggestion = part[1].strip()
        image = None
        for attach in message.attachments:
            if attach.url:
                image = attach.url
        msg = await self.common_add(message.author, message.channel, labels, suggestion, image)
        await self.reply(message, msg)

    async def common_add(self, author, channel, label: str, suggestion: str, attachment: str):
        if await self.validate_or_get_posting_channel() == False:
            raise ValueError("Failed to get posting channel")
        if len(suggestion.split()) < 5:
            raise ValueError('Description must contain at least 5 words, to help increase the ability for others to find it in searches and increase visibility to developers.')

        if len(suggestion) != len(discord.utils.escape_mentions(suggestion)):
            raise ValueError('Please do not include pings in your {single}'.format(single=config.DESCRIPTOR_SINGLE))

        if len(suggestion) > 1600:
            raise ValueError('Please limit your {single} to 1600 characters to allow for formatting and close info (currently {} characters)'
                    .format(len(suggestion), single=config.DESCRIPTOR_SINGLE))
        
        labels = label.strip().lower().split(',')
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

        (index, entry) = self.add_entry(suggestion, labels=good_labels, author=author, image=attachment)

        # Post this new entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await channel.send(entry_text, embed=embed)
        return "#" + str(index) + " created successfully"


    ### Edit commands ###
    @app_commands.command(name="edit", description="Edit a " + config.DESCRIPTOR_SINGLE)
    @app_commands.describe(index=config.DESCRIPTOR_SINGLE + " #")
    @app_commands.describe(type="What to edit. One of: description, label, image, author, priority, complexity")
    @app_commands.describe(change="New value for the edit, required for all types except image")
    @app_commands.describe(attachment="New image for the edit, required for image type")
    async def slash_edit(self, interaction: discord.Interaction, index: int, type: SuggestionComponents, change: str = None, attachment: discord.Attachment = None):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            image = None
            if attachment is not None:
                image = attachment.url
            msg = await self.common_edit(interaction.user, interaction.channel, index, type.value, change, image)
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)
    
    @slash_edit.autocomplete('change')
    async def slash_edit_autocomplete(self, interaction: discord.Interaction, current: str):
        type = interaction.namespace.type
        print(type)
        if (type == SuggestionComponents.description.value or type == SuggestionComponents.image.value):
            return []
        elif (type == SuggestionComponents.label.value):
            print("autocomplete for label")
            labels = []
            for label in self._labels:
                if current.lower() in label.lower():
                    print("found match of " + label)
                    labels.append(app_commands.Choice(name=label, value=label))
            print("returning labels" + str(labels))
            return labels
        elif (type == SuggestionComponents.priority.value):
            return [
                app_commands.Choice(name="Critical", value="Critical"),
                app_commands.Choice(name="High", value="High"),
                app_commands.Choice(name="Medium", value="Medium"),
                app_commands.Choice(name="Low", value="Low"),
                app_commands.Choice(name="Zero", value="Zero"),
            ]
        elif (type == SuggestionComponents.complexity.value):
            return [
                app_commands.Choice(name="easy", value="easy"),
                app_commands.Choice(name="moderate", value="moderate"),
                app_commands.Choice(name="hard", value="hard"),
                app_commands.Choice(name="unknown", value="unknown"),
            ]
        else:
            return []


    async def msg_edit(self, message, args):
        part = args.split(maxsplit=2)
        if (not args) or (len(part) < 2):
            raise ValueError('''How to edit a {single}:```
{prefix} edit # [description | label | image | author | priority | complexity] edited stuff
```
For example:```
{prefix} edit 5 description Much more detail here
```
'''.format(prefix=config.PREFIX, single=config.DESCRIPTOR_SINGLE))
        index = part[0].strip()
        type = part[1].strip()
        change = part[2].strip()
        attachment = None
        for attach in message.attachments:
            if attach.url:
                attachment = attach.url
        msg = await self.common_edit(message.author, message.channel, int(index), type, change, attachment)
        await self.reply(message, msg)

    async def common_edit(self, author, channel, index: int, type: str, change: str, attachment: str):
        if await self.validate_or_get_posting_channel() == False:
            raise ValueError("Failed to get posting channel")
        index, entry = self.get_entry(index)

        operation = get_list_match(type, ['description', 'label', 'image', 'author', 'priority', 'complexity'])
        if operation is None:
            raise ValueError("Item to edit must be 'description', 'label', 'image', 'author', 'priority' or 'complexity'")

        min_priv = 4
        if operation in ['description', 'label', 'image']:
            min_priv = 1
        if operation in ['author', 'priority', 'complexity']:
            min_priv = 2

        if not self.has_privilege(min_priv, author, index=index):
            raise ValueError("You do not have permission to edit {} for entry #{}".format(operation, index))
        
        if operation == 'description':
            if change == "":
                raise ValueError("You need to actually supply a new description")
            
            if len(change) != len(discord.utils.escape_mentions(change)):
                raise ValueError('Please do not include pings in your {single}'.format(single=config.DESCRIPTOR_SINGLE))

            if len(change) > 1600:
                raise ValueError('Please limit your {single} to 1600 characters to allow for formatting and close info (currently {} characters)'
                        .format(len(change), single=config.DESCRIPTOR_SINGLE))

            entry["description"] = change

        elif operation == 'label':
            if change == "":
                raise ValueError("You need to actually supply a new label")

            labels = change.strip().lower().split(',')
            good_labels = []
            for label in labels:
                match = get_list_match(label.strip(), self._labels)
                if match is None:
                    raise ValueError("Labels must be one of: [{}]".format(",".join(self._labels)))
                good_labels.append(match)

            entry["labels"] = good_labels

        elif operation == 'image':
            image = attachment

            if image is None:
                raise ValueError("You need to attach an image")

            entry["image"] = image

        elif operation == 'priority':
            if change == "":
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

            priority = get_list_match(change.strip().lower(), self._priorities)
            if priority is None:
                raise ValueError("Priority must be one of: [{}]".format(",".join(self._priorities)))

            entry["priority"] = priority

        elif operation == 'complexity':
            if change == "":
                raise ValueError("Available complexities: [{}]".format(",".join(self._complexities.keys())))

            complexity = get_list_match(change.strip().lower(), self._complexities.keys())
            if complexity is None:
                raise ValueError("Complexity must be one of: [{}]".format(",".join(self._complexities.keys())))

            entry["complexity"] = complexity

        if entry["author"] == author.id:
            entry["pending_notification"] = False
        elif operation != "label":
            # If only the label changed, don't change the notification setting
            entry["pending_notification"] = True

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await channel.send(entry_text, embed=embed)
        return config.DESCRIPTOR_PROPER + " #" + str(index) + " updated successfully"

    ### Get command ###
    @app_commands.command(name="get", description="Get a " + config.DESCRIPTOR_SINGLE)
    @app_commands.describe(index=config.DESCRIPTOR_SINGLE + " #")
    async def slash_get(self, interaction: discord.Interaction, index: int):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            msg = await self.common_get(interaction.channel, index)
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)
    
    async def msg_get(self, message, args):
        if not args:
            raise ValueError("Usage: {prefix} get <number>".format(prefix=config.PREFIX))
        index = args.strip()
        msg = await self.common_get(message.channel, index)
        await self.reply(message, msg)
    
    async def common_get(self, channel, index: int):
        if await self.validate_or_get_posting_channel() == False:
            raise ValueError("Failed to get posting channel")
        index, entry = self.get_entry(index)
        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await channel.send(entry_text, embed=embed)
        return config.DESCRIPTOR_PROPER + " #" + str(index) + " retrieved successfully"


        ################################################################################


    async def print_search_results(self, responder, match_entries, limit=15, sort_entries=True, mention_assigned=False, include_reactions=True, ephemeral=False):
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
            entry_text, embed = await self.format_entry(index, entry, include_reactions=include_reactions, mention_assigned=mention_assigned)
            if ephemeral:
                await responder.send(entry_text, embed=embed, ephemeral=True)
            else:
                await responder.send(entry_text, embed=embed)

    ### Search Commands Section ###
    # Core helper for label/priority/complexity search
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
                raise ValueError('''No priority, label, complexity, or 'assigned' matching {!r}'''.format(item))

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

    ### Search command ###
    @app_commands.command(name="search", description="Search for a " + config.DESCRIPTOR_SINGLE)
    @app_commands.describe(type="Type of search to do")
    @app_commands.choices(type=[
        app_commands.Choice(name="Label, Priority, and/or Complexity", value="search"),
        app_commands.Choice(name="Description", value="dsearch"),
        app_commands.Choice(name="Interactive", value="isearch"),
        app_commands.Choice(name="Author", value="asearch"),
        app_commands.Choice(name="Reaction", value="rsearch"),
    ])
    @app_commands.describe(query="Query to search for")
    async def slash_search_core(self, interaction: discord.Interaction, type: app_commands.Choice[str], query: str):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        match type.value:
            case "search":
                await self.slash_search(interaction, query)
            case "dsearch":
                await self.slash_dsearch(interaction, query)
            case "isearch":
                await self.slash_isearch(interaction, query)
            case "asearch":
                await self.slash_asearch(interaction, query)
            case "rsearch":
                await self.slash_rsearch(interaction, query)
            case _:
                await interaction.response.send_message("Invalid search type")

    @slash_search_core.autocomplete('query')
    async def slash_edit_autocomplete(self, interaction: discord.Interaction, current: str):
        type = interaction.namespace.type
        if type == "search" or type == "isearch":
            final_list = []
            full_list = [
                app_commands.Choice(name="Critical", value="Critical"),
                app_commands.Choice(name="High", value="High"),
                app_commands.Choice(name="Medium", value="Medium"),
                app_commands.Choice(name="Low", value="Low"),
                app_commands.Choice(name="Zero", value="Zero"),
                app_commands.Choice(name="Easy", value="easy"),
                app_commands.Choice(name="Moderate", value="moderate"),
                app_commands.Choice(name="Hard", value="hard"),
                app_commands.Choice(name="Unknown", value="unknown"),
            ]
            for item in full_list:
                if current.lower() in item.value.lower():
                    final_list.append(item)
            for label in self._labels:
                if current.lower() in label.lower():
                    final_list.append(app_commands.Choice(name=label, value=label))
            return final_list
        elif type == "dsearch" or type == "asearch":
            return []
        elif type == "rsearch":
            reacts = []
            for react in config.REACTIONS:
                if current.lower() in react.lower():
                    reacts.append(app_commands.Choice(name=react, value=react))
            return reacts


    async def slash_search(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            msg = await self.common_search(interaction.channel, query)
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)

    async def msg_search(self, message, args):
        msg = await self.common_search(message, args)
        await self.reply(message, msg)

    async def common_search(self, channel, query: str):
        if await self.validate_or_get_posting_channel() == False:
            raise ValueError("Failed to get posting channel")
        match_entries, match_labels, match_priorities, match_complexities, max_count = await self.search_helper(query, max_count=10)

        await self.print_search_results(channel, match_entries, limit=max_count)

        return "{} {} found matching labels={} priorities={} complexities={}".format(
            len(match_entries), config.DESCRIPTOR_PLURAL,
            ",".join(match_labels), ",".join(match_priorities), ",".join(match_complexities))
        
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

    def get_flattened_priority(cls, entry):
        return entry[1]["priority"] + "," + entry[1]["complexity"]
    
    async def slash_isearch(self, interaction: discord.Interaction, query: str):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        if await self.validate_or_get_posting_channel() == False:
            await interaction.response.send_message("Failed to get posting channel")
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            match_entries, _, __, ___, ____ = await self.search_helper(query, max_count=100)
        except ValueError as e:
            await original_msg.edit(str(e))
            return

        if len(match_entries) <= 0:
            await original_msg.edit("No results to display")
            return

        await original_msg.edit(content="Enabling interactive search. Please continue with shorthand commands.")
        inter = InteractiveSearch(self, interaction.user, match_entries)
        self._interactive_sessions.append(inter)
        await inter.send_first_message(original_msg)

    async def handle_message(self, message):
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

    async def slash_dsearch(self, interaction: discord.Interaction, query: str):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            msg = await self.common_dsearch(interaction.channel, query)
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)

    async def msg_dsearch(self, message, args):
        msg = await self.common_dsearch(message.channel, args)
        await self.reply(message, msg)
    
    async def common_dsearch(self, channel, query: str):
        if await self.validate_or_get_posting_channel() == False:
            raise ValueError("Failed to get posting channel")
        match_entries, limit = await self.dsearch_internal(query, 15)
        await self.print_search_results(channel, match_entries, limit=limit)
        return f"{len(match_entries)} {config.DESCRIPTOR_PLURAL} found matching {query}"

    async def dsearch_internal(self, search_terms: str, limit: int):
        """Description search terms parser"""
        part = search_terms.replace(",", " ").split()
        if (not search_terms) or (len(part) < 1):
            raise ValueError('''Usage: {prefix} dsearch <search terms, count>'''.format(prefix=config.PREFIX))

        # Try to parse each argument as an integer - and if so, use that as the limit
        search_terms = []
        for term in part:
            try:
                limit = int(term)
            except Exception:
                # Don't search for numbers
                search_terms.append(term)

        if len(search_terms) < 1:
            raise ValueError('''Usage: {prefix} dsearch <search terms, count>'''.format(prefix=config.PREFIX))

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

    async def slash_asearch(self, interaction: discord.Interaction, query: str = None):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            msg = await self.common_asearch(interaction.guild, interaction.channel, interaction.user, query)
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)

    async def msg_asearch(self, message, args):
        msg = await self.common_asearch(message.guild, message.channel, message.author, args)
        await self.reply(message, msg)

    async def common_asearch(self, guild, channel, author, query: str = None):
        if await self.validate_or_get_posting_channel() == False:
            raise ValueError("Failed to get posting channel")
        if query:
            author = self.get_user(guild, query)

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

        await self.print_search_results(channel, match_entries)

        return "{} open {} of {} total from author {}".format(open_count, config.DESCRIPTOR_PLURAL, total_count, author.display_name)

    async def slash_rsearch(self, interaction: discord.Interaction, query: str):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            return
        try:
            if await self.validate_or_get_posting_channel() == False:
                raise ValueError("Failed to get posting channel")
            if (not query) or (" " in query):
                raise ValueError('''Usage: {prefix} rsearch <:reaction:>'''.format(prefix=config.PREFIX))

            async with interaction.channel.typing():
                await interaction.response.send_message("Getting a list of most-reacted entries. This will take some time...")

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
                                    if react.emoji == query:
                                        raw_entries.append((react.count, (index, entry)))
                                        break
                        except discord.errors.NotFound:
                            pass

                # TODO: Custom reaction searching support
                if not raw_entries:
                    await interaction.channel.send("No entries with reaction {!r} - note that custom reactions are not supported yet".format(query))

                raw_entries.sort(key=lambda kv: kv[0], reverse=True)
                match_entries = [x[1] for x in raw_entries]

                await self.print_search_results(interaction.channel, match_entries, sort_entries=False)
                await interaction.channel.send("Reaction search complete.")
        except Exception as e:
            await interaction.response.send_message("Error: " + str(e))
    
    async def msg_rsearch(self, message, args):
        if await self.validate_or_get_posting_channel() == False:
            raise ValueError("Failed to get posting channel")
        if (not args) or (" " in args):
            raise ValueError('''Usage: {prefix} rsearch <:reaction:>'''.format(prefix=config.PREFIX))

        async with message.channel.typing():
            await message.channel.send("Getting a list of most-reacted entries. This will take some time...")

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
                await message.channel.send("No entries with reaction {!r} - note that custom reactions are not supported yet".format(query))

            raw_entries.sort(key=lambda kv: kv[0], reverse=True)
            match_entries = [x[1] for x in raw_entries]

            await self.print_search_results(message.channel, match_entries, sort_entries=False)
            self.reply(message,"Reaction search complete.")


    ### Roulette Commands ###
    @app_commands.command(name="roulette", description="Pick a random " + config.DESCRIPTOR_SINGLE)
    @app_commands.describe(query = "Query to search for")
    @app_commands.describe(interactive="Interactive mode, iterating through " + config.DESCRIPTOR_PLURAL + ". Default is false")
    async def slash_roulette(self, interaction: discord.Interaction, query: str = None,  interactive: bool = False):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            return
        if await self.validate_or_get_posting_channel() == False:
            await interaction.response.send_message("Failed to get posting channel")
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            if query is not None:
                # If args are provided, use them to narrow the list
                match_entries, _, __, ___, ____ = await self.search_helper(query, max_count=10)
            else:
                # If no args, random from any open item
                match_entries = []
                for index in self._entries:
                    entry = self._entries[index]
                    if "close_reason" not in entry:
                        match_entries.append((index, entry))

            if not match_entries:
                await original_msg.edit(content="No {plural} found matching those search terms".format(plural=config.DESCRIPTOR_PLURAL))
            else:
                if interactive:
                    await original_msg.edit(content="Enabling interactive roulette. Please continue with shorthand commands.")
                    inter = InteractiveSearch(self, interaction.user, match_entries)
                    self._interactive_sessions.append(inter)
                    await inter.send_first_message(original_msg)
                else:
                    await self.print_search_results(interaction.channel, [random.choice(match_entries)])
                    await original_msg.edit(content="Random {single} selected".format(single=config.DESCRIPTOR_SINGLE))
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)


    ### Reject/Fix commands ###
    # All use common_reject, rejcct path requires response, fix doesn't
    @app_commands.command(name="reject", description="Reject a " + config.DESCRIPTOR_SINGLE)
    @app_commands.describe(index=config.DESCRIPTOR_SINGLE + " #")
    @app_commands.describe(reason="reason for rejection")
    async def slash_reject(self, interaction: discord.Interaction, index: int, reason: str):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            msg = await self.common_reject(interaction.channel, interaction.user, index, reason, False)
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)

    @app_commands.command(name="fix", description="Fix a " + config.DESCRIPTOR_SINGLE)
    @app_commands.describe(index=config.DESCRIPTOR_SINGLE + " #")
    @app_commands.describe(reason="Optional reasoning for fixing")
    async def slash_fix(self, interaction: discord.Interaction, index: int, reason: str = None):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            msg = await self.common_reject(interaction.channel, interaction.user, index, reason, True)
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)

    async def msg_reject(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) < 2):
            raise ValueError('''Usage: {prefix} reject <number> <required explanation>'''.format(prefix=config.PREFIX))

        reason = part[1].strip()
        msg = await self.common_reject(message.channel, message.author, int(part[0]), reason, False)
        await self.reply(message, msg)

    async def msg_fix(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) < 1):
            raise ValueError('''Usage: {prefix} fix <number> [optional explanation]'''.format(prefix=config.PREFIX))
        reason = None
        if len(part) > 1:
            reason = part[1].strip()
        msg = await self.common_reject(message.channel, message.author, int(part[0]), reason, True)
 
    async def common_reject(self, channel, user, index: int, reason: str = None, fix: bool = False):
        if await self.validate_or_get_posting_channel() == False:
            raise ValueError("Failed to get posting channel")
        index, entry = self.get_entry(index)

        if not self.has_privilege(1, user, index=index):
            raise ValueError("You do not have permission to fix/reject #{}".format(index))

        if reason is not None:
            entry["close_reason"] = reason
        else:
            entry["close_reason"] = "Fixed"

        if entry["author"] == user.id:
            entry["pending_notification"] = False
        else:
            entry["pending_notification"] = True

        if "assignee" in entry:
            entry.pop("assignee")

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await channel.send(entry_text, embed=embed)
        if fix:
            return "{proper} #{index} marked as fixed".format(proper=config.DESCRIPTOR_PROPER, index=index)
        else:
            return "{proper} #{index} rejected".format(proper=config.DESCRIPTOR_PROPER, index=index)


    ### Append command ###
    
    @app_commands.command(name="append", description="Append to a " + config.DESCRIPTOR_SINGLE)
    @app_commands.describe(index=config.DESCRIPTOR_SINGLE + " #")
    @app_commands.describe(append="text to append")
    async def slash_append(self, interaction: discord.Interaction, index: int, append: str):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            msg = await self.common_append(interaction.user, interaction.channel, index, append)
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)

    async def msg_append(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) < 2):
            raise ValueError('''Usage: {prefix} append <number> [additional description text]'''.format(prefix=config.PREFIX))
        msg = await self.common_append(message.author, message.channel, int(part[0]), part[1].strip())
        await self.reply(message, msg)

    async def common_append(self, user, channel, index: int, append: str):
        if await self.validate_or_get_posting_channel() == False:
            raise ValueError("Failed to get posting channel")
        index, entry = self.get_entry(index)

        if not self.has_privilege(1, user, index=index):
            raise ValueError("You do not have permission to append to #{}".format(index))
        
        if len(append) != len(discord.utils.escape_mentions(append)):
            raise ValueError('Please do not include pings in your {single}'.format(single=config.DESCRIPTOR_SINGLE))
        
        description = f'{entry["description"]}\n{append}'
        if len(description) > 1600:
            raise ValueError(f'Appending this message brings the length to {len(description)} which exceeds the 1600 character maximum to allow for formatting and close info')

        entry["description"] = description

        if entry["author"] == user.id:
            entry["pending_notification"] = False
        else:
            entry["pending_notification"] = True

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await channel.send(entry_text, embed=embed)
        return "{proper} #{index} edited".format(proper=config.DESCRIPTOR_PROPER, index=index)


    ### Unfix command ###
    @app_commands.command(name="unfix", description="Unfix a " + config.DESCRIPTOR_SINGLE)
    @app_commands.describe(index=config.DESCRIPTOR_SINGLE + " #")
    async def slash_unfix(self, interaction: discord.Interaction, index: int):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            msg = await self.common_unfix(interaction.user, interaction.channel, index)
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)

    async def msg_unfix(self, message, args):
        part = args.split(maxsplit=2)
        if (not args) or (len(part) != 1):
            raise ValueError('''Usage: {prefix} unfix <number>'''.format(prefix=config.PREFIX)) 
        msg = await self.common_unfix(message, message.author, message.channel, int(args))
        await self.reply(message, msg)

    async def common_unfix(self, user, channel, index: int):
        if await self.validate_or_get_posting_channel() == False:
            raise ValueError("Failed to get posting channel")
        index, entry = self.get_entry(index)

        if not self.has_privilege(1, user, index=index):
            raise ValueError("You do not have permission to unfix #{}".format(index))

        if "close_reason" in entry:
            entry.pop("close_reason")

        if entry["author"] == user.id:
            entry["pending_notification"] = False
        else:
            entry["pending_notification"] = True

        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await channel.send(entry_text, embed=embed)
        return "{proper} #{index} unmarked as fixed".format(proper=config.DESCRIPTOR_PROPER, index=index)


    ## Stats command ###
    @app_commands.command(name="stats", description="Get stats about the database")
    async def slash_stats(self, interaction: discord.Interaction):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            msg = await self.common_stats()
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)
    
    async def msg_stats(self, message, args):
        msg = await self.common_stats()
        await self.reply(message, msg)
    
    async def common_stats(self):
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

        stats_text = '''Current {single} stats:```'''.format(single=config.DESCRIPTOR_SINGLE)
        stats_text += f"{'' : <13}"
        for comp in self._complexities:
            stats_text += f"{comp.capitalize() : <10}"
        stats_text += f"{'Total' : <10}"
        for item in total:
            stats_text += '''
{} | '''.format(item.ljust(10))
            for comp in stats[item]:
                stats_text += f"{stats[item][comp] : <10}"
            stats_text += f"{total[item] : <10}"
        stats_text += '''
----------------
Total Open : {}
Closed     : {}```'''.format(total_open, total_closed)
        return stats_text


    ### Author stats command ###
    @app_commands.command(name="astats", description="Get stats about authors")
    async def slash_astats(self, interaction: discord.Interaction):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            stats = {}

            for index in self._entries:
                entry = self._entries[index]
                if "author" in entry and entry["author"] != 0:
                    author = entry["author"]
                    if author in stats:
                        stats[author] += 1
                    else:
                        stats[author] = 1
            await original_msg.edit(content='''Current {single} author stats:'''.format(single=config.DESCRIPTOR_SINGLE))
            stats_text = ''
            for author_id, count in sorted(stats.items(), key=lambda kv: kv[1], reverse=True):
                author = self.get_user_by_id(author_id)
                if author is not None:
                    stats_text += '''{} : {}\n'''.format(author.display_name.ljust(20), count)

            for chunk in split_string(stats_text):
                await interaction.channel.send('```python\n' + chunk + '```')
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)
    
    async def msg_astats(self, message, args):
        stats = {}

        for index in self._entries:
            entry = self._entries[index]
            if "author" in entry and entry["author"] != 0:
                author = entry["author"]
                if author in stats:
                    stats[author] += 1
                else:
                    stats[author] = 1

        await self.reply(message, '''Current {single} author stats:'''.format(single=config.DESCRIPTOR_SINGLE))
        stats_text = ''
        for author_id, count in sorted(stats.items(), key=lambda kv: kv[1], reverse=True):
            author = self.get_user_by_id(author_id)
            if author is not None:
                stats_text += '''{} : {}\n'''.format(author.display_name.ljust(20), count)

        for chunk in split_string(stats_text):
            await self.reply(message, '```python\n' + chunk + '```')

    
    ### Assign command ###
    @app_commands.command(name="assign", description="Assign a " + config.DESCRIPTOR_SINGLE + " to yourself")
    @app_commands.describe(index=config.DESCRIPTOR_SINGLE + " #")
    @app_commands.describe(assignee="user to assign to, leave empty to self assign")
    async def slash_assign(self, interaction: discord.Interaction, index: int, assignee: str = None):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            msg = await self.common_assign(interaction.user, interaction.channel, index, assignee)
            await original_msg.edit(content=msg)
        except ValueError as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)

    async def msg_assign(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) != 1):
            raise ValueError('''Usage: {prefix} assign <number>'''.format(prefix=config.PREFIX))
        msg = await self.common_assign(message.author, message.channel, int(part[0]))
        await self.reply(message, msg)
    
    async def common_assign(self, user, channel, index: int, target: str = None):
        if await self.validate_or_get_posting_channel() == False:
            raise ValueError("Failed to get posting channel")
        if not self.has_privilege(2, user):
            raise ValueError("You do not have permission to use this command")

        index, entry = self.get_entry(index)

        assignee = user
        if target is not None:
            assignee = self.get_user(channel.guild, target)

        entry["assignee"] = assignee.id
        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await channel.send(entry_text, embed=embed)
        return "{proper} #{index} assigned to {name}".format(proper=config.DESCRIPTOR_PROPER, index=index, name=assignee.display_name)


    ### Unassign command ###
    @app_commands.command(name="unassign", description="Unassign a " + config.DESCRIPTOR_SINGLE)
    @app_commands.describe(index=config.DESCRIPTOR_SINGLE + " #")
    async def slash_unassign(self, interaction: discord.Interaction, index: int):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            msg = await self.common_unassign(interaction.user, interaction.channel, index)
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)
    
    async def msg_unassign(self, message, args):
        part = args.split(maxsplit=1)
        if (not args) or (len(part) != 1):
            raise ValueError('''Usage: {prefix} unassign <number>'''.format(prefix=config.PREFIX))
        msg = await self.common_unassign(message.author, message.channel, int(part[0]))
        await self.reply(message, msg)
    
    async def common_unassign(self, user, channel, index: int):
        if await self.validate_or_get_posting_channel() == False:
            raise ValueError("Failed to get posting channel")
        if not self.has_privilege(2, user):
            raise ValueError("You do not have permission to use this command")

        index, entry = self.get_entry(index)

        if "assignee" not in entry:
            raise ValueError('{proper} #{index} is already unassigned'.format(proper=config.DESCRIPTOR_PROPER, index=index))

        entry.pop("assignee")
        self.save()

        # Update the entry
        await self.send_entry(index, entry)

        entry_text, embed = await self.format_entry(index, entry, include_reactions=True)
        msg = await channel.send(entry_text, embed=embed)
        return "{proper} #{index} unassigned".format(proper=config.DESCRIPTOR_PROPER, index=index)


    ### Remove command ###
    #Completely removes a task from the database, scrubbing info
    @app_commands.command(name="delete", description="Delete a " + config.DESCRIPTOR_SINGLE + " entirely, scrubbing info")
    @app_commands.describe(index=config.DESCRIPTOR_SINGLE + " #")
    async def slash_delete(self, interaction: discord.Interaction, index: int):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            if await self.validate_or_get_posting_channel() == False:
                raise ValueError("Failed to get posting channel")
            if not self.has_privilege(2, interaction.user):
                raise ValueError("You do not have permission to use this command")

            index, entry = self.get_entry(index)

            if "close_reason" in entry:
                entry["close_reason"] = ""
            if "pending_notification" in entry:
                entry["pending_notification"] = False
            if "description" in entry:
                entry["description"] = ""
            if "image" in entry:
                entry["image"] = ""

            self.save()

            # Update the entry
            await self.send_entry(index, entry)

            await original_msg.edit(content="{proper} #{index} deleted".format(proper=config.DESCRIPTOR_PROPER, index=index))
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)


    ### Operator section ###
    ### prune command ###
    #can't commonize, order of ops issue
    @app_commands.command(name="prune", description="Prune " + config.DESCRIPTOR_PLURAL)
    async def slash_prune(self, interaction: discord.Interaction):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        if await self.validate_or_get_posting_channel() == False:
            await interaction.response.send_message("Failed to get posting channel")
            return
        try:
            if not self.has_privilege(3, interaction.user):
                raise ValueError("You do not have permission to use this command")

            await interaction.response.send_message("Pruning suggestions. This will take some time...")

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

            await self.print_search_results(interaction.channel, match_entries, limit=99999)
            await interaction.channel.send("{} entries pruned successfully".format(count))
        except Exception as e:
            await interaction.channel.send("Error: " + str(e))

    async def msg_prune(self, message, args):
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
        await(self.reply(message, "{} entries pruned successfully".format(count)))


    ### Notify command ###
    @app_commands.command(name="notify", description="Enable/disable notifications for yourself")
    @app_commands.describe(state="on or off")
    @app_commands.choices(state=[
        app_commands.Choice(name="On", value="on"),
        app_commands.Choice(name="Off", value="off")])
    async def slash_notify(self, interaction: discord.Interaction, state: app_commands.Choice[str]):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            msg = await self.common_notify(interaction.user, interaction.channel, state.value)
            await original_msg.edit(content=msg)
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)

    async def msg_notify(self, message, args):
        if not args:
            raise ValueError('''Usage: {prefix} notify <on|off>'''.format(prefix=config.PREFIX))
        match = get_list_match(args.strip(), ["on", "off"])
        if match is None:
            raise ValueError("Argument to {prefix} notify must be one of: [on, off]")
        msg = await self.common_notify(message.author, message.channel, match)
        await self.reply(message, msg)
    
    async def common_notify(self, user, channel, state: str):
        if state == "on":
            if user.id in self._notifications_disabled:
                self._notifications_disabled.remove(user.id)
        else:
            self._notifications_disabled.add(user.id)

        self.save()

        if user.id in self._notifications_disabled:
            return '''You will __not__ be notified of changes to your {plural}.
To change this, {prefix} notify on'''.format(plural=config.DESCRIPTOR_PLURAL, prefix=config.PREFIX)
        else:
            return '''You **will** be notified of changes to your {plural}.
Notifications are on by default.
To change this, {prefix} notify off'''.format(plural=config.DESCRIPTOR_PLURAL, prefix=config.PREFIX)


    ### Send notifications command ###
    @app_commands.command(name="send_notifications", description="Send notifications to all users")
    async def slash_send_notifications(self, interaction: discord.Interaction):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        try:
            await interaction.response.send_message("Notification process started...")

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
                                entry_text = '''{mention} Your {single} was updated:
        {entry}'''.format(mention=user.mention, single=config.DESCRIPTOR_SINGLE, entry=entry_text)
                                msg = await interaction.channel.send(entry_text, embed=embed)
                        else:
                            no_user += 1
                    else:
                        no_user += 1
                    entry["pending_notification"] = False

                    # Might as well save a bunch of times in case this gets interrupted
                    self.save()

            await interaction.channel.send("{} notifications processed successfully, {} of which were suppressed by user opt-out, {} of which could not find a user to ping".format(count, opt_out, no_user))
        except Exception as e:
            await interaction.channel.send("Error: " + str(e))
    
    async def msg_send_notifications(self, message, args):
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
                            entry_text = '''{mention} Your {single} was updated:
    {entry}'''.format(mention=user.mention, single=config.DESCRIPTOR_SINGLE, entry=entry_text)
                            msg = await message.channel.send(entry_text, embed=embed)
                    else:
                        no_user += 1
                else:
                    no_user += 1

                entry["pending_notification"] = False

                # Might as well save a bunch of times in case this gets interrupted
                self.save()

        await(self.reply(message, "{} notifications processed successfully, {} of which were suppressed by user opt-out, {} of which could not find a user to ping".format(count, opt_out, no_user)))


    ### Channel Import Command ###
    @app_commands.command(name="import", description="Import database entries from a channel")
    @app_commands.describe(channel="channel to import from")
    async def slash_import(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            return
        try:
            if not self.has_privilege(4, interaction.user):
                raise ValueError("You do not have permission to use this command")

            part = args.split(maxsplit=2)
            if len(part) != 1 or len(part[0].strip()) < 10:
                raise ValueError("Usage: import #channel".format(config.PREFIX))

            import_channel = await self._bot.fetch_channel(channel.id)
            if import_channel is None:
                raise ValueError("Can not find channel {!r}".format(channel.id))

            await interaction.response.send_message("Import started, this will take some time...")

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
                        react_text += "    {} {}".format(react.emoji, react.count)

                to_import.append((msg.timestamp, msg.content + "\n\n" + created_text + "\n" + react_text, msg.author, image))

            # SORT
            to_import.sort(key=lambda x: x[0])

            for _, content, author, image in to_import:
                (index, entry) = self.add_entry(content, author=author, image=image)

                # Post this new entry
                await self.send_entry(index, entry)

            await interaction.channel.send("{} entries from channel {} imported successfully".format(len(to_import), part[0]))
        except Exception as e:
            await interaction.channel.send("Error: " + str(e))


    ### Repost command ###
    @app_commands.command(name="repost", description="Repost all database entries")
    async def slash_repost(self, interaction: discord.Interaction):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            return
        try:
            if not self.has_privilege(4, interaction.user):
                raise ValueError("You do not have permission to use this command")

            await interaction.response.send_message("Repost started, this will take some time...")

            await interaction.channel.send("Building a set of all valid {single} message ids...".format(single=config.DESCRIPTOR_SINGLE))

            valid = set()
            # Iterate a shallow copy of the entries table so new reports don't break it
            for index in self._entries.copy():
                entry = self._entries[index]
                if "message_id" in entry:
                    valid.add(entry["message_id"])

            await interaction.channel.send("Searching the channel for untracked messages...")

            def predicate(iter_msg):
                # Delete messages written by a bot that either wasn't this bot OR wasn't a valid message
                return iter_msg.author.bot and (iter_msg.author.id != self._bot.application_id or iter_msg.id not in valid)

            deleted = await self._channel.purge(limit=9999, check=predicate)
            count = 0
            for iter_msg in deleted:
                # Exit early if shutting down
                if self._stopping:
                    return

                await interaction.channel.send("Removing untracked message:")
                embed = None
                if iter_msg.embeds is not None and len(iter_msg.embeds) > 0:
                    embed = iter_msg.embeds[0]
                await interaction.channel.send(iter_msg.content, embed=embed)
                count += 1

            await interaction.channel.send("{} untracked messages removed successfully".format(count))

            await interaction.channel.send("Reposting missing messages...")

            count = 0
            for index in self._entries:
                # Exit early if shutting down
                if self._stopping:
                    return

                if "close_reason" not in self._entries[index]:
                    count += 1
                    await self.send_entry(index, self._entries[index])

            await interaction.channel.send("{} entries reposted successfully".format(count))
        except Exception as e:
            await interaction.response.send_message("Error: " + str(e))


    ### Add label command ###
    @app_commands.command(name="add_label", description="Add a label to the database")
    @app_commands.describe(label="label to add")
    async def slash_add_label(self, interaction: discord.Interaction, label: str):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            await interaction.response.send_message("Please use the bot channel for this command", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        original_msg = await interaction.original_response()
        try:
            if not self.has_privilege(3, interaction.user):
                raise ValueError("You do not have permission to use this command")

            args = label.lower()

            if (not args) or re.search("[^a-z]", args):
                raise ValueError('''Usage: {prefix} addlabel <label>
    Labels can only contain a-z characters'''.format(prefix=config.PREFIX))

            match = get_list_match(args, self._labels)
            if match is not None:
                raise ValueError('Can not add label {} because it matches {}'.format(args, match))

            self._labels.append(args)
            self.save()

            await original_msg.edit(content="Label {} added successfully".format(args))
        except Exception as e:
            await original_msg.edit(content="Error: " + str(e))
            await interaction.channel.send(interaction.user.mention)


    ### Remove label command ###
    @app_commands.command(name="remove_label", description="Remove a label from the database")
    @app_commands.describe(label="label to remove")
    async def slash_remove_label(self, interaction: discord.Interaction, label: str):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            return
        try:
            if not self.has_privilege(3, interaction.user):
                raise ValueError("You do not have permission to use this command")

            args = label.lower()

            if (not args) or re.search("[^a-z]", args):
                raise ValueError('''Usage: {prefix} dellabel <label>
    Labels can only contain a-z characters'''.format(prefix=config.PREFIX))

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

            interaction.response.send_message("Label {} removed successfully from {} {plural}".format(match, count, plural=config.DESCRIPTOR_PLURAL))
        except Exception as e:
            await interaction.channel.send("Error: " + str(e))

    @slash_remove_label.autocomplete("label")
    async def slash_remove_label_autocomplete(self, interaction: discord.Interaction, current: str):
        list_of_labels = []
        for label in self._labels:
            if current.lower() in label.lower():
                list_of_labels.append(app_commands.Choice(name=label, value=label))
        return list_of_labels


    ### Test perms command ###
    @app_commands.command(name="test_perms", description="Test your permissions")
    async def slash_test_perms(self, interaction: discord.Interaction):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            return
        try:
            if self.has_privilege(4, interaction.user):
                await interaction.response.send_message("Privilege: 4")
            elif self.has_privilege(3, interaction.user):
                await interaction.response.send_message("Privilege: 3")
            elif self.has_privilege(2, interaction.user):
                await interaction.response.send_message("Privilege: 2")
            elif self.has_privilege(1, interaction.user):
                await interaction.response.send_message("Privilege: 1")
            elif self.has_privilege(0, interaction.user):
                await interaction.response.send_message("Privilege: 0")
            else:
                await interaction.response.send_message("Privilege: None")
        except Exception as e:
            await interaction.response.send_message("Error: " + str(e))


    ### List assigned command ###
    @app_commands.command(name="list_assigned", description="List all entries assigned to a user")
    @app_commands.describe(user="user to list if not yourself. Use 'all' to list all assigned entries")
    async def slash_list_assigned(self, interaction: discord.Interaction, user: str = None):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            return
        try:
            if not self.has_privilege(2, interaction.user):
                raise ValueError("You do not have permission to use this command")

            match_assignee = interaction.user

            if user is not None:
                if user == "all":
                    # Match any non-empty assignee
                    match_assignee = None
                else:
                    # Match specific assignee
                    match_assignee = self.get_user(interaction.guild, user)

            match_entries = []
            count = 0
            for index in self._entries:
                entry = self._entries[index]
                if "close_reason" not in entry:
                    if "assignee" in entry:
                        if (match_assignee is None) or (entry["assignee"] == match_assignee.id):
                            count += 1
                            match_entries.append((index, entry))

            await self.print_search_results(interaction.channel, match_entries, limit=9999)

            if match_assignee is None:
                await interaction.response.send_message("{} total assigned {} found".format(count, config.DESCRIPTOR_PLURAL))
            else:
                await interaction.response.send_message("{} assigned {} found for user {}".format(count, config.DESCRIPTOR_PLURAL, match_assignee.display_name))
        except Exception as e:
            await interaction.response.send_message("Error: " + str(e))


    ### Ping assigned command ###
    @app_commands.command(name="ping_assigned", description="Ping all users assigned to entries")
    @app_commands.describe(channel="channel id to ping in")
    async def slash_ping_assigned(self, interaction: discord.Interaction, channel: str):
        if await self.validate_using_bot_channel(interaction, interaction.message) == False:
            return
        if await self.validate_or_get_posting_channel() == False:
            interaction.response.send_message("Failed to get posting channel")
            return
        try:
            if not self.has_privilege(3, interaction.user):
                raise ValueError("You do not have permission to use this command")
            
            try:
                channel_id = int(channel)
            except:
                raise ValueError("{!r} is not a number".format(channel))

            actual_channel = await self._bot.fetch_channel(channel_id)
            if actual_channel is None:
                raise Exception("Error getting channel!")

            await interaction.response.send_message("Starting notification process...")

            match_entries = []
            count = 0
            for index in self._entries:
                entry = self._entries[index]
                if "close_reason" not in entry:
                    if "assignee" in entry:
                        count += 1
                        match_entries.append((index, entry))

            await interaction.channel.send("Starting to ping users assigned to tasks within the database here...")
            await self.print_search_results(actual_channel, match_entries, limit=9999, mention_assigned=True)

            await interaction.channel.send("{} total assigned {} mentioned in channel {}".format(count, config.DESCRIPTOR_PLURAL, channel.name))

        except Exception as e:
            await interaction.channel.send("Error: " + str(e))



async def setup(bot):
    db = TaskDatabase(bot)
    await bot.add_cog(db)