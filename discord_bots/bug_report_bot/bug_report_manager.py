import asyncio
import discord
import os
import json

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
'''

class BugReportManager(object):
    def __init__(self, client, user_privileges, group_privileges, bug_reports_channel_id, database_path):
        """
        """
        self._client = client
        self._user_privileges = user_privileges
        self._group_privileges = group_privileges
        self._bug_reports_channel_id = bug_reports_channel_id
        self._bug_reports_channel = None
        self._database_path = database_path
        self.load()

#        init_bugs = [
#    ('Low','''Relogging skips Heart of the Jungle CD'''),
#    ('High','''Laser spells can pass though 2 diagonal blocks (need to implement a better raymarching algorithm)'''),
#    ('High','''Spawners are still active, but invisible after amplifying PoIs. meaning constant and unstoppable spawn (torch use needed)'''),
#    ('Zero','''Some player heads are not displayed correctly, this includes (among others) quest markers.'''),
#    ('Low','''Golden strand is missing some NBT and cant stack with old ones'''),
#    ('Medium','''Activating a totem of undying resets all passive class buffs (health boost, speed, etc.)'''),
#    ('High','''Spawners in POIs that are disabled via torches but not broken do not reset their spawn count when the POI respawns.'''),
#    ('High','''Players sometimes can't take the chest from the sanctum loot room'''),
#    ('Medium','''Pig God can get behind fences'''),
#    ('Low','''R1plots Info signs not working'''),
#    ('Zero','''the message "You have Won the weekly vote raffle! Congratulation!" plays every time you transfer to region 1 if you have an unused raffle win'''),
#    ('High','''Chat settings of every type (current channel, ignore settings, etc.) are saved individually on each shard instead of globally'''),
#    ('High','''Patron Shrine buffs does not work in other shards than region_1'''),
#    ('Medium','''Kaul Massacre advancement not working as expected'''),
#    ('Medium','''Kaul M'Loci advancement not working as expected'''),
#    ('High','''During Clear as Glass Quest: Virius can be killed once he spawns once you find Nelfine in her cage and talk to her.'''),
#    ('High','''Yeigar dies upon Spawning'''),
#    ('Low','''Stair sitting feature still disabled'''),
#    ('Medium','''Swift Cuts particles stays after target death'''),
#    ('Medium','''Sybil tells people to go to do quests, despite them having already completed them.'''),
#    ('Low','''The Cloud Mobs in Light Blue can be killed with use of Vulnerability'''),
#    ('Medium','''Potions of infinite glowing from azacor only work until you log out or change shards.'''),
#    ('High','''Pig God Arena is not fully safezoned - eastern-centre quadrant?'''),
#    ('Medium','''Rogue: sometimes escape death activate health above 5 hearts'''),
#    ('High','''the abbot (?) does not advance your quest score to "kill SOTFs"'''),
#    ('High','''The redstone in the first Reflection event in Time to Reflect can get stuck on'''),
#    ('Zero','''Death messages not broadcasted across shards'''),
#    ('High','''You must ask a moderator for help when you change your name'''),
#    ('Zero','''Trident with Loyalty can disappear when thrown before a long range teleportation'''),
#    ('Zero','''You can't open chests while holding a Heart of the Jungle thats on cooldown'''),
#    ('Medium','''Non-moderators can't use /me'''),
#    ('Low','''Clucking potion can remove clucking from an equiped item'''),
#    ('Zero','''Tribal Chisel does not have the right 'curse of irreparability' lore line'''),
#    ('Medium','''Speedster advancement doesn't work'''),
#    ('Low','''Trading in queens greaves for kings greaves displays chat message for buying kings greaves'''),
#    ('Medium','''Snowball Fight leaderboard signs broken'''),
#    ('Medium','''Nightmare: after C'axtal: extra items past 12 are still generated but go in the command box for it (unreachable).'''),
#    ('Low','''Shulker stations don't work with regular anvils, Tlaxan Artifacts loot box, Azacor Uncommon loot box'''),
#    ('Low','''If you step on the Patron particle sample toggle, it removes Divine Aura particles permanently until you reapply them with the Relic'''),
#    ('Medium','''Kaul Wand damage inconsistant'''),
#    ('Medium','''Ticket Master V advancement not working'''),
#    ('Zero','''you cannot eat/shoot/right click while your offhand shield is charging back after blocking'''),
#    ('Zero','''Teleporters do not work with horses'''),
#    ('Zero','''Wand stacks will try to unstack, giving a stack of 1, and another of the rest (NBT issue)'''),
#    ('High','''Guild Join Buttons in guild room not working'''),
#    ('High','''Build shard players should not have permission to run /stop'''),
#    ('Medium','''Unseen minion teleport spell can teleport to players in the respawn room'''),
#    ('Medium','''If you have more than one regen item, have one equipped, then select the second, when you stop using the second again, the regen will go away even though the first item still exists.'''),
#    ('High','''Armour takes damage in the judgement section in kaul'''),
#    ('High','''Crafting the serum does not properly set the scores to let the player talk to the warden'''),
#    ('Low','''There's still copies of the old Greyskull's Spellcaster in existance'''),
#    ('High','''In Sanctum, inventory gets cleared over a weekly reset even without leaving the shard.'''),
#    ('Low','''Smokescreen does not triggers when aiming at a block'''),
#    ('Low','''If you happen to try to claim the voting raffle reward with a non-King's Valley item, it will consume your credit and do nothing.'''),
#    ('Medium','''Multiple pig gods can spawn when multiple people are doing the quest'''),
#    ('Low','''Multieffect potions with a negative attribute such as Earth's Might cannot be passed to other players using Heavenly Boon'''),
#    ('Medium','''Gluttony advancements broken'''),
#    ('Medium','''Our Lord and Savior advancement not working'''),
#    ('Low','''The system lets you gild a gilded item'''),
#    ('Medium','''Horse Jumps can break protected crop fields'''),
#    ('Low','''In old labs, mini tnt heads didn't disappear after breaking cache 1'''),
#    ('Low','''When you fill all the cauldrons in the witch village, message about corrupted caves pops up twice'''),
#    ('Low','''Erix's bloody boots in sanctum don't have a cloth/leather tag'''),
#    ('Medium','''Advancement for purchasing king's sabatons is not given'''),
#    ('Low','''Arrows sometimes seem to bounce off Kaul'''),
#    ('Low','''Point Blank seems to sometimes not work on Kaul'''),
#    ('Medium','''Somehow while playing sanctum it's possible to get your spawn point set close enough to C'Shura (on the island) that if you die, C'Shura will just kill you over and over and over every time you respawn. A player got their spawn point set to very close to the bridge, resulting in instant lag deaths every respawn. '''),
#    ('Medium','''After I completed the Workshop portion of A Pigculiar Problem, my quest compass still pointed towards the workshop, instead of Walter Jr.'''),
#    ('Medium','''Grasping Claws's activation is a bit weird: whether you're sneaking or not is tested when firing the arrow and will put the skill on cooldown, but, if you are not sneaking when the arrow hits an enemy or the ground, the arrow will do nothing.'''),
#    ('Medium','''If remapped by a moderator, the maps board in the teleport building does not preserve changes made- terrain reset sets it back to the build server copy which shows the guild plots as empty'''),
#    ('Medium','''The masked man black wool shard is... a hat for some reason'''),
#    ('Medium','''Scars: Bhavrivivvia likes to dialog-spam you the first time you talk to her after completing Scars of Magic '''),
#    ('Low','''Snuggles still doesn't go into his pen when you complete the runaway pet quest, though you do get credit for completing it'''),
#    ('Low','''You can "sequence break" Azacor's Quest if you log off in between the parts where you get teleported around the PoIs in the grove and then wait until terrain reset, unsure if bug or not, and unsure if it fixes itself after going to the PoI indicated by the quest compass but figured it's worth a post anyway'''),
#    ('High','''Soul of the forest talk with haynes and bhairavi after getting the relic is a bit buggy. It was playing the text for both people when either person clicked a chat option and some options didn't seem to function'''),
#    ('Medium','''I completed the magenta quest and it says its completed in the quest guide, but my advancements say that ive only Found and completed the dungeon, not the quest'''),
#    ('Medium','''mobs can spawn in the lab where you find Nelfine, and mobs can also spawn in a small corner in the back of the destroyed lab'''),
#    ('Medium','''Orange: Arvaya Statue can charge at players in the stands'''),
#    ('Medium','''In the light puzzle for scars of magic, stops the lights when you are a block away from the pressure plate'''),
#    ('Medium','''Items kept by the new keepinv system do not take durability damage.'''),
#    ('High','''Dodging triggers when being hit by an arrow that was blocked by a shield'''),
#    ('Low','''Vulnerability allows you to injure and kill immortal mobs'''),
#    ('Medium','''Royal Crystals don't have the royal crystal texture in the advancements when using the resource pack'''),
#    ('Low','''Display name for browncorp advancement too long - "The House at the End of the ..."'''),
#    ('High','''Advancement progress can only be made on region_1 and does not transfer between shards'''),
#    ('High','''Sometimes advancements are not viewable on other shards'''),
#    ('Medium','''Nightmare Harbringers are missing their glowing effects'''),
#    ('Medium','''Masked Man's AoE attack particles are not working (sound only)'''),
#    ('Low','''C'Axtal's safety teleport is buggy if the center chunk is unloaded'''),
#    ('Low','''C'Axtal drops sand on himself when he does his TNT attack'''),
#    ('High','''Trapdoors (Partial blocks?) do not block Azacor's lazer attack'''),
#    ('Medium','''The Cunning's flame AoE does not disappear if he dies mid charge (Azacor summon mob)'''),
#    ('Medium','''Mimcs tp'ing can tp into walls'''),
#    ('High','''Mimcs can TP to the spawn box if the target player dies at the exact right time '''),
#    ('Zero','''Mobs that split off the original spawn (such as baby slimes) from spawners do not conform to the 20 spawn exp/item drop cap.'''),
#    ('Low','''Splash potions of healing do not affect friendly mobs(cows) in r1plots'''),
#    ('Zero','''Guardian beams are invisible if you change shards (for example, going to Magenta). This is a minecraft client bug we can not fix. As a work around, if you are experiencing invisible guardian beams, all you have to do is log out and log back in. They will be fixed until you change shards again.'''),
#    ('High','''Absorption doesn't work in judgement'''),
#    ('Medium','''Riposte procs on Thorns damage'''),
#    ('Low','''If you get Celestial Blessing, then before it runs out you get that buff again (perhaps from a different cleric), the new one will still be removed when the original expires.'''),
#    ('Medium','''Celestial Blessing activates while shifting and breaking blocks'''),
#    ('Low','''Throwing an iron tincture (alch) into lava doesn't give it a reduced timer if no one picks it up because the item gets destroyed, meaning you have to wait the full cooldown time to get the skill off cooldown.'''),
#    ('Medium','''Vicious combos doesn't reset BmB if BmB was used to kill an elite'''),
#    ('Low','''Arena: Practice mode is missing'''),
#    ('Medium','''Arena Spectators receive a "What I cannot unsee" book'''),
#    ('High','''Double clicking signs in the arena advances the wave count two waves but the entities in the wave don’t change. Additionally, it spawns twice the mobs normally in the wave.'''),
#    ('Low','''Races don't tell you if you are going faster or slower than best time'''),
#    ('Medium','''You can break blocks and loot chests while racing'''),
#    ('Low','''No quick key shortcut to restart race'''),
#    ('High','''NPC dialogue can be activated with sweeping or with arrows/snowballs'''),
#    ('High','''You can't get Advancement Progress from Alexander or the Info Book.'''),
#    ('Medium','''Riposte can sometimes activate even while blocking'''),
#    ('Low','''Spider Eye Soup is missing Legacy tag'''),
#    ('Zero','''Identical Tipped Arrows crafted with Barrier Potions sometimes do not stack'''),
#    ('Low','''POI respawn box doesn't extend high enough into the trees for Southern Jaguar Village.'''),
#    ('Low','''You can apply Ice Aspect to the donkey in the polling station.'''),
#    ('Medium','''From BibleThump: "When I went into the plot shard with dolphin and fish spawn eggs from the circus, they turned into turtle spawn eggs"'''),
#    ('Medium','''Kaul can continue doing his thing during the Primordial Elemental phase, meaning both elementals can be up at the same time. Also, he doesn't take reduced damage from elementals during this time'''),
#    ('Medium','''Blocking Kaul's meteor during the actual meteor attack phase will send you flying regardless of nullifying the damage.'''),
#    ('Medium','''The "explorer" acheivements do not reflect the the number of pois I have explored. Each counter, except for azzy's grove, is less than the number of individual exploration achievements I have. According to a hand-count I've explored every poi in the game'''),
#    ('Low','''Elixir of the Serpent both has unique and Legacy tag'''),
#    ('Medium','''Azacor lasers targets player in safe room'''),
#    ('Medium','''Weird line break in Divine Watcher’s Sword lore text'''),
#    ('Medium','''falling into the water in Verdant Fortress when doing Unveiled doesn't teleport you back like it should'''),
#    ('Medium','''from the JP near the throne room. you can jump to the exit, with enough speed jump from the first redstone torch after first ladder'''),
#    ('Medium','''In Outer Demons, the basement of Azacor's Mansion allowed me to just walk through the particles and grab the book without doing anything else'''),
#    ('Medium','''In A Crew to Remember, after getting the navigator from the island, the ship wouldn't allow me to go back below deck until after I logged out and back in several times. The tripwire just kept teleporting me above deck.'''),
#]
#        for (priority, desc) in init_bugs:
#            (index, bug) = self.add_bug(desc, priority=priority)

        self.save()


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
                "Med",
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
        self._bugs[index] = bug

        self.save()

        return (index, bug)

    async def send_bug(self, index, bug):
        # Fetch the channel if not already stored
        if self._bug_reports_channel is None:
            self._bug_reports_channel = self._client.get_channel(self._bug_reports_channel_id)
            if self._bug_reports_channel is None:
                raise Exception("Error getting bug reports channel!")

        # Compute the new bug text

        author_id = bug["author"]
        if author_id != 0 and author_id != "0":
            author_name = (await self._client.get_user_info(author_id)).display_name
        else:
            author_name = ""

        bug_text = '''`
#{} [{} - {}] {}`
{}'''.format(index, ','.join(bug["labels"]), bug["priority"], author_name, bug["description"])

        msg = None
        if "message_id" in bug:
            msg = await self._client.get_message(self._bug_reports_channel, bug["message_id"])

        embed = None
        if "image" in bug:
            embed = discord.Embed()
            embed.set_image(url=bug["image"])

        if msg is not None:
            print("Editing, embed = {}".format(embed))
            # Edit the existing message
            await self._client.edit_message(msg, bug_text, embed=embed)

        else:
            # Send a new message
            print("New, embed = {}".format(embed))
            msg = await self._client.send_message(self._bug_reports_channel, bug_text, embed=embed);
            bug["message_id"] = msg.id
            self.save()

        await self._client.add_reaction(msg, "\U0001f44d")

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
    Must be one of: {}

`~bug search <labels> <priorities>`
    Searches all bugs for ones that match the specified labels / priorities
    Both labels and priorities can be one or a list, separated by commas
    For example: ~bug search quest,class high

**Commands the original bug reporter and team members can use:**
`~bug reject <number> [Optional reason why]`
    Closes the specified bug with the given reason

`~bug edit <number> <description | label | image> [argument]`
    Edits the specified field of the bug report

**Commands team members can use:**
`~bug edit [author | priority] [argument]`
    Edits the specified field of the bug report

`bug fix number`
    Marks the specified bug as fixed

`bug unfix number`
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
        if len(part) < 2:
            await self.reply(message, 'Bug report must contain both a label and a description')
            return

        label = part[0].strip().lower()
        description = part[1].strip()

        if label not in (name.lower() for name in self._labels):
            await self.reply(message, '''Label must be one of the following:```
''' + '''
'''.join(self._labels) + '```')
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

        (index, bug) = self.add_bug(description, labels=[label], author=message.author, image=image)

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

        operation = part[1].strip().lower()

        if index not in self._bugs:
            await self.reply(message, 'Bug #{} not found!'.format(index))
            return

        bug = self._bugs[index]

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
    # ~bug repost
    async def cmd_repost(self, message):
        count = 0
        for index in self._bugs:
            count += 1
            await self.send_bug(index, self._bugs[index])

        await(self.reply(message, "{} bugs reposted successfully".format(count)))

    ################################################################################
    # ~bug import
    async def cmd_import(self, message):
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

# TODO: Longest prefix match!
def get_list_match(item, lst):
    tmpitem = item.lower()
    for x in lst:
        if x.lower() == tmpitem:
            return x
    return None

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
