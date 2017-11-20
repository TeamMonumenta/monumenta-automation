#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
from pymclevel import nbt

shulkerIDNames = [
    "minecraft:white_shulker_box",
    "minecraft:orange_shulker_box",
    "minecraft:magenta_shulker_box",
    "minecraft:light_blue_shulker_box",
    "minecraft:yellow_shulker_box",
    "minecraft:lime_shulker_box",
    "minecraft:pink_shulker_box",
    "minecraft:gray_shulker_box",
    "minecraft:silver_shulker_box",
    "minecraft:cyan_shulker_box",
    "minecraft:purple_shulker_box",
    "minecraft:blue_shulker_box",
    "minecraft:brown_shulker_box",
    "minecraft:green_shulker_box",
    "minecraft:red_shulker_box",
    "minecraft:black_shulker_box",
]

# used to ignore data values that aren't damage
ItemsWithRealDamage = [
    ############
    # Armor

    # Leather
    "minecraft:leather_helmet",
    "minecraft:leather_chestplate",
    "minecraft:leather_leggings",
    "minecraft:leather_boots",

    # Chainmail
    "minecraft:chainmail_helmet",
    "minecraft:chainmail_chestplate",
    "minecraft:chainmail_leggings",
    "minecraft:chainmail_boots",

    # Iron
    "minecraft:iron_helmet",
    "minecraft:iron_chestplate",
    "minecraft:iron_leggings",
    "minecraft:iron_boots",

    # Gold
    "minecraft:golden_helmet",
    "minecraft:golden_chestplate",
    "minecraft:golden_leggings",
    "minecraft:golden_boots",

    # Diamond
    "minecraft:diamond_helmet",
    "minecraft:diamond_chestplate",
    "minecraft:diamond_leggings",
    "minecraft:diamond_boots",

    ############
    # Tools

    # Wood
    "minecraft:wooden_axe",
    "minecraft:wooden_hoe",
    "minecraft:wooden_pickaxe",
    "minecraft:wooden_shovel",
    "minecraft:wooden_sword",

    # Stone
    "minecraft:stone_axe",
    "minecraft:stone_hoe",
    "minecraft:stone_pickaxe",
    "minecraft:stone_shovel",
    "minecraft:stone_sword",

    # Iron
    "minecraft:iron_axe",
    "minecraft:iron_hoe",
    "minecraft:iron_pickaxe",
    "minecraft:iron_shovel",
    "minecraft:iron_sword",

    # Gold
    "minecraft:golden_axe",
    "minecraft:golden_hoe",
    "minecraft:golden_pickaxe",
    "minecraft:golden_shovel",
    "minecraft:golden_sword",

    # Diamond
    "minecraft:diamond_axe",
    "minecraft:diamond_hoe",
    "minecraft:diamond_pickaxe",
    "minecraft:diamond_shovel",
    "minecraft:diamond_sword",

    # Misc

    "minecraft:carrot_on_a_stick",
    "minecraft:fishing_rod",
    "minecraft:elytra",
    "minecraft:shears",
    "minecraft:flint_and_steel",
]

containerTagNames = [
    # Humanoid Entities
    "HandItems",
    "ArmorItems",

    # Horses
    "ArmorItem",
    "SaddleItem",
    "Items",

    # Item Frames
    "Item",

    # Players
    "Inventory", # villagers too, apparently
    "EnderItems",
]

formatCodes = {
    "colors":u'0123456789abcdef',
    "styles":u'klmnor',
    "list":[
        {"id":u"0","display":u"Black","technical":u"black",},
        {"id":u"1","display":u"Dark Blue","technical":u"dark_blue",},
        {"id":u"2","display":u"Dark Green","technical":u"dark_green",},
        {"id":u"3","display":u"Dark Aqua","technical":u"dark_aqua",},
        {"id":u"4","display":u"Dark Red","technical":u"dark_red",},
        {"id":u"5","display":u"Dark Purple","technical":u"dark_purple",},
        {"id":u"6","display":u"Gold","technical":u"gold",},
        {"id":u"7","display":u"Gray","technical":u"gray",},
        {"id":u"8","display":u"Dark Gray","technical":u"dark_gray",},
        {"id":u"9","display":u"Blue","technical":u"blue",},
        {"id":u"a","display":u"Green","technical":u"green",},
        {"id":u"b","display":u"Aqua","technical":u"aqua",},
        {"id":u"c","display":u"Red","technical":u"red",},
        {"id":u"d","display":u"Light Purple","technical":u"light_purple",},
        {"id":u"e","display":u"Yellow","technical":u"yellow",},
        {"id":u"f","display":u"White","technical":u"white",},

        {"id":u"k","display":u"Obfuscated","technical":u"obfuscated",},
        {"id":u"l","display":u"Bold","technical":u"bold",},
        {"id":u"m","display":u"Strikethrough","technical":u"strikethrough",},
        {"id":u"n","display":u"Underline","technical":u"underlined",},
        {"id":u"o","display":u"Italic","technical":u"italic",},
        {"id":u"r","display":u"Reset","technical":u"reset",},
    ],
}

################################################################################
# Item stack finding code

class ReplaceItems(object):
    """
    Item replacement util; give it an uncompiled
    list of items to replace, then tell it where
    to replace things.

    debug is a list of strings:
    "init" - displays each replacement's description as it is loaded
    "global count" - counts the occurances of all items, ignoring
                     contained items, damage, and other data that
                     players are likely to change.
    """
    def __init__(self,debug=[],replacementList=None):
        if "init" in debug:
            print u"  New item replacement list loading..."
        if replacementList is None:
            self.replacements = None
            if "init" in debug:
                print u"  ┗╸Dummy list, does nothing."
        else:
            self.log_data = {}
            self.log_data["debug"] = debug
            self.log_data["global"] = {}
            self.replacements = allReplacements(replacementList,self.log_data)
            if "global count" in debug:
                self.log_data["global"]["global count"] = {}

    def InWorld(self,world):
        if self.replacements is None:
            return

        self.log_data["current"] = {}

        for cx,cz in world.allChunks:
            aChunk = world.getChunk(cx,cz)

            if "Level" not in aChunk.root_tag:
                # This chunk is invalid, skip it!
                # It has no data.
                continue

            # shallow copy this list, or we won't have entities in the main world.
            # Also, we don't need a TAG_List; a normal list is fine.
            self.entityList = []
            for entity in aChunk.root_tag["Level"]["Entities"]:
                self.entityList.append(entity)
            for entity in aChunk.root_tag["Level"]["TileEntities"]:
                self.entityList.append(entity)
            self._OnEntities()

            aChunk.chunkChanged(False) # needsLighting=False

    def InSchematic(self,schematic):
        if self.replacements is None:
            return

        self.log_data["current"] = {}

        # shallow copy this list, or we won't have entities in the main world.
        # Also, we don't need a TAG_List; a normal list is fine.
        self.entityList = []
        for entity in schematic.Entities:
            self.entityList.append(entity)
        for entity in schematic.TileEntities:
            self.entityList.append(entity)
        self._OnEntities()

    def OnPlayers(self,worldDir):
        if self.replacements is None:
            return

        self.log_data["current"] = {}

        for playerFile in os.listdir(worldDir+"playerdata"):
            playerFile = worldDir+"playerdata/" + playerFile
            self.log_data["player file"] = playerFile
            player = nbt.load(playerFile)
            # In this case, we can easily copy the only entity to a list.
            self.entityList = [player]
            self._OnEntities()
            player.save(playerFile)
        self.log_data.pop("player file")

    def PrintGlobalLog(self):
        if "global count" in self.log_data["global"]:
            print u"Items found:"
            for item in self.log_data["global"]["global count"]:
                print u"* {}x {}".format(
                    self.log_data["global"]["global count"][item],
                    item
                )

    def _OnEntities(self):
        while len(self.entityList) > 0:
            self.entity = self.entityList.pop()
            self.log_data["entity"] = self.entity
            if (
                ("Pos" in self.entity) or
                ("x" in self.entity)
            ):
                # The entity exists in the world/schematic directly,
                # not inside something.
                self.rootEntity = self.entity
                self.log_data["rootEntity"] = self.rootEntity

            # Handle villager trades
            if (
                ("Offers" in self.entity) and
                ("Recipes" in self.entity["Offers"])
            ):
                for trade in self.entity["Offers"]["Recipes"]:
                    #if "maxUses" in trade:
                    #    # make the villager support the maximum allowed trades
                    #    trade["maxUses"] = 2147483647
                    # trade["uses"] is the number of times a trade is used;
                    # we can use it for player shops, as long as it starts at 1
                    # if it starts at 0, trades will get refreshed, resetting
                    # other trades to 0, reducing their max use, and potentially
                    # opening another trade.
                    if "buy" in trade:
                        self._InStack(trade["buy"])
                    if "buyB" in trade:
                        self._InStack(trade["buyB"])
                    if "sell" in trade:
                        self._InStack(trade["sell"])

            for containerTagName in containerTagNames:
                if containerTagName in self.entity:
                    # Replace hand items if they can drop
                    if containerTagName == "HandItems":
                        if "HandDropChances" in self.entity:
                            for i in range(2):
                                if self.entity["HandDropChances"][i] > -1.00:
                                    self._InStack(self.entity[containerTagName][i])
                        else:
                            self._InStack(self.entity[containerTagName])

                    # Replace armor items if they can drop
                    elif containerTagName == "ArmorItems":
                        if "ArmorDropChances" in self.entity:
                            for i in range(4):
                                if self.entity["ArmorDropChances"][i] > -1.00:
                                    self._InStack(self.entity[containerTagName][i])
                        else:
                            self._InStackList(self.entity[containerTagName])

                    # Replace other items; they always drop
                    else:
                        self._InStackList(self.entity[containerTagName])

        self.entity = None
        self.log_data["entity"] = None
        self.rootEntity = None
        self.log_data["rootEntity"] = None

    def _InStackList(self,itemStackList):
        if type(itemStackList) is nbt.TAG_List:
            for itemStack in itemStackList:
                self._InStack(itemStack)
        elif type(itemStackList) is nbt.TAG_Compound:
            self._InStack(itemStackList)

    def _InStack(self,itemStack):
        if type(itemStack) != nbt.TAG_Compound:
            # Invalid itemStack type
            return
        if "id" not in itemStack:
            # No item in this slot (mob armor/hand items)
            return
        # Handle item replacement on this item first
        self.replacements.run(itemStack,self.log_data)
        # Now that this item has been altered/removed, try these:
        if "tag" in itemStack:
            if "BlockEntityTag" in itemStack["tag"]:
                # This is enough info to loop over blocks with
                # NBT held as items, like shulker boxes.
                blockEntity = itemStack["tag"]["BlockEntityTag"]
                self.entityList.append(blockEntity)
            if "EntityTag" in itemStack["tag"]:
                # Handles spawn eggs, and potentially other cases.
                entity = itemStack["tag"]["EntityTag"]
                self.entityList.append(entity)
        if "global count" in self.log_data["debug"]:
            globalCounts = self.log_data["global"]["global count"]

            # In order to simplify the item list, certain
            # details must be removed; a fake item is
            # used to handle these changes, and is
            # discarded afterwards.
            fakeItem = nbt.json_to_tag(itemStack.json)
            # If we put this in a sub-tag ,we need to fix it
            if "id" not in fakeItem:
                fakeItem = fakeItem[fakeItem.keys()[0]]
                # Remove the name so it matches with the others
                fakeItem.name = ""

            if "Count" in fakeItem:
                count = fakeItem["Count"].value
                fakeItem.pop("Count")
            else:
                count = 1
            if fakeItem["id"].value in ItemsWithRealDamage:
                fakeItem.pop("Damage")
            if "Slot" in fakeItem:
                fakeItem.pop("Slot")
            if "tag" in fakeItem:
                if "BlockEntityTag" in fakeItem["tag"]:
                    for containerTagName in containerTagNames:
                        if containerTagName in fakeItem["tag"]["BlockEntityTag"]:
                            fakeItem["tag"]["BlockEntityTag"].pop(containerTagName)
                # EntityTag is left alone because of spawn eggs;
                # may need to be left out if we let players store
                # their animals as spawn eggs (donkey inventory, for example)

                # ench (enchantments) tag might need to be sorted, but this
                # changes the order the enchantments appear in game, sooo...

                # AttributeModifiers - similar story, order is not checked in
                # game, but causes items to be "different" here

                # CustomPotionEffects - guess what else is unsorted?

                if "display" in fakeItem["tag"]:
                    if "color" in fakeItem["tag"]["display"]:
                        fakeItem["tag"]["display"].pop("color")

                ################
                # Fireworks:
                # Because I highly doubt we care
                if "Explosion" in fakeItem["tag"]:
                    fakeItem["tag"].pop("Explosion")
                if "Fireworks" in fakeItem["tag"]:
                    fakeItem["tag"].pop("Fireworks")

            # I think that's all the tags we want to ignore.
            itemString = fakeItem.json
            if itemString not in globalCounts:
                globalCounts[itemString] = count
            else:
                globalCounts[itemString] += count


################################################################################
# Replacement list optimizer

class allReplacements(list):
    def __init__(self,replacementList,log_data):
        self._replacements = []
        for aReplacement in replacementList:
            self._replacements.append(replacement(aReplacement,log_data))
        print u"  Found " + unicode(len(self._replacements)) + u" replacements."

    def run(self,itemStack,log_data):
        for replacement in self._replacements:
            replacement.run(itemStack,log_data)

class replacement(object):
    def __init__(self,replacementPair,log_data):
        matches = replacementPair[0]
        actions = replacementPair[1]

        if "init" in log_data["debug"]:
            print u"  ┣╸Adding a replacement:"
            print u"  ┃ ╟╴If all of these are true:"

        # TODO create new matches for all/any/none groups of matches
        
        # matches is the list of uncompiled matches
        # self.matches is the list of compiled matches
        self.matches = []
        for key in matches:
            if key == "any":
                newMatch = matchAny()
            if key == "count":
                newMatch = matchCount(matches)
            if key == "damage":
                newMatch = matchDamage(matches)
            if key == "id":
                newMatch = matchID(matches)
            if key == "name":
                newMatch = matchName(matches)
            if key == "nbt":
                newMatch = matchNBT(matches)
            if key == "none":
                newMatch = matchNone()

            self.matches.append(newMatch)
            if "init" in log_data["debug"]:
                print u"  ┃ ║ └╴" + newMatch.str()

        if len(self.matches) == 0:
            newMatch = matchNone()
            self.matches.append(newMatch)
            if "init" in log_data["debug"]:
                print u"  ┃ ║ └╴" + newMatch.str()
        if "init" in log_data["debug"]:
            print u"  ┃ ╙╴Then do these in order:"

        # actions is the uncompiled list of actions
        # self.actions is the list of compiled actions
        self.actions = []
        while len(actions):
            action = actions.pop(0)
            if action == "count":
                newAction = actCount(actions)
            if action == "damage":
                newAction = actDamage(actions)
            if action == "id":
                newAction = actID(actions)
            if action == "location":
                newAction = actLocation(actions)
            if action == "name":
                newAction = actName(actions)
            if action == "nbt":
                newAction = actNBT(actions)
            if action == "print":
                newAction = actPrint(actions)
            if action == "print item":
                newAction = actPrintItem(actions)
            if action == "remove":
                newAction = actRemove(actions)

            self.actions.append(newAction)
            if "init" in log_data["debug"]:
                print u"  ┃   └╴" + newAction.str()

    def run(self,itemStack,log_data):
        if all(rule == itemStack for rule in self.matches):
            #print "*** Found match:"
            #print itemStack.json
            #print "Matched rules:"
            #for rule in self.matches:
            #    print rule.str()
            #print "Actions:"
            for action in self.actions:
                #print action.str()
                action.run(itemStack,log_data)
            #print ""

# Matching optimizers

class matchAny(object):
    """
    This is a special case to match anything;
    used by itself to match all items
    """
    def __eq__(self,itemStack):
        return True

    def str(self):
        return u'True'

class matchCount(object):
    """
    This stores item counts to match later
    """
    def __init__(self,matchOptions):
        count = matchOptions["count"]
        if (type(count) != list) and (type(count) != tuple):
            self._count = [count]
        else:
            self._count = count

    def __eq__(self,itemStack):
        try:
            return itemStack["Count"].value in self._count
        except:
            return False

    def str(self):
        return u'Item count is in ' + str(self._count)

class matchDamage(object):
    """
    This stores damage values to match later
    """
    def __init__(self,matchOptions):
        damage = matchOptions["damage"]
        if (type(damage) != list) and (type(damage) != tuple):
            self._damage = [damage]
        else:
            self._damage = damage

    def __eq__(self,itemStack):
        try:
            return itemStack["Damage"].value in self._damage
        except:
            return False

    def str(self):
        return u'Item damage is in ' + str(self._damage)

class matchID(object):
    """
    This stores an ID to match later
    """
    def __init__(self,matchOptions):
        self._id = matchOptions["id"]

    def __eq__(self,itemStack):
        try:
            return self._id == itemStack["id"].value
        except:
            return False

    def str(self):
        return u'Item ID is "' + self._id + u'"'

class matchName(object):
    """
    This stores a name to match later without color
    """
    def __init__(self,matchOptions):
        self._name = matchOptions["name"]
        if type(self._name) == str:
            self._name = unicode(self._name)

    def __eq__(self,itemStack):
        if (
            ("tag" not in itemStack) or
            ("display" not in itemStack["tag"]) or
            ("Name" not in itemStack["tag"]["display"])
        ):
            return self._name is None
        elif self._name is None:
            return False
        else:
            nameNoFormat = itemStack["tag"]["display"]["Name"].value
            while u'§' in nameNoFormat:
                i = nameNoFormat.find(u'§')
                nameNoFormat = nameNoFormat[:i]+nameNoFormat[i+2:]
            return nameNoFormat == self._name

    def str(self):
        if self._name == None:
            return u'Item has no name'
        else:
            return u'Item name matches "' + self._name + '" regardless of color'

class matchNBT(object):
    """
    This stores NBT to match later
    """
    def __init__(self,matchOptions):
        json = matchOptions["nbt"]

        if "nbtStrict" in matchOptions:
            self._exact = matchOptions["nbtStrict"]
        else:
            self._exact = False

        if json is None:
            self._nbt = None
        else:
            self._nbt = nbt.json_to_tag(json)

    def __eq__(self,itemStack):
        if self._nbt is None:
            return "tag" not in itemStack
        elif "tag" not in itemStack:
            return False

        if self._exact:
            return self._nbt.eq(itemStack["tag"])
        else:
            return self._nbt.issubset(itemStack["tag"])

    def str(self):
        if self._nbt is None:
            return u'Item has no NBT'
        elif self._exact:
            return u'Item NBT exactly matches ' + self._nbt.json
        else:
            return u'Item NBT loosely matches ' + self._nbt.json

class matchNone(object):
    """
    This is a special case to never match anything;
    used for invalid item replacements
    """
    def __eq__(self,itemStack):
        return False

    def str(self):
        return u'False'


# Action optimizers

class actCount(object):
    """
    Stores a count action to apply later
    """
    def __init__(self,actionOptions):
        self._operation = actionOptions.pop(0)
        self._opValue = actionOptions.pop(0)

    def run(self,itemStack,log_data):
        if self._operation == "=":
            itemStack["Count"].value = self._opValue
            return
        if self._operation == "+":
            itemStack["Count"].value += self._opValue
            return
        if self._operation == "-":
            itemStack["Count"].value -= self._opValue
            return
        if self._operation == "*":
            itemStack["Count"].value *= self._opValue
            return
        if self._operation == "/":
            itemStack["Count"].value /= self._opValue
            return
        if self._operation == "%":
            itemStack["Count"].value %= self._opValue
            return
        if self._operation == "max":
            newVal = min(itemStack["Count"].value,self._opValue)
            itemStack["Count"].value = newVal
            return
        if self._operation == "min":
            newVal = max(itemStack["Count"].value,self._opValue)
            itemStack["Count"].value = newVal
            return

    def str(self):
        if self._operation == "=":
            return u'Set count to ' + str(self._opValue)
        if self._operation == "+":
            return u'Add ' + str(self._opValue) + u' to count'
        if self._operation == "-":
            return u'Subtract ' + str(self._opValue) + u' from count'
        if self._operation == "*":
            return u'Multiply count by ' + str(self._opValue)
        if self._operation == "/":
            return u'Divide count by ' + str(self._opValue)
        if self._operation == "%":
            return u'Set count to itself modulo ' + str(self._opValue)
        if self._operation == "max":
            return u'Prevent count from being greater than ' + str(self._opValue)
        if self._operation == "min":
            return u'Prevent count from being less than ' + str(self._opValue)

class actDamage(object):
    """
    Stores a damage action to apply later
    """
    def __init__(self,actionOptions):
        self._operation = actionOptions.pop(0)
        self._opValue = actionOptions.pop(0)

    def run(self,itemStack,log_data):
        if self._operation == "=":
            itemStack["Damage"].value = self._opValue
            return
        if self._operation == "+":
            itemStack["Damage"].value += self._opValue
            return
        if self._operation == "-":
            itemStack["Damage"].value -= self._opValue
            return
        if self._operation == "*":
            itemStack["Damage"].value *= self._opValue
            return
        if self._operation == "/":
            itemStack["Damage"].value /= self._opValue
            return
        if self._operation == "%":
            itemStack["Damage"].value %= self._opValue
            return
        if self._operation == "max":
            newVal = min(itemStack["Damage"].value,self._opValue)
            itemStack["Damage"].value = newVal
            return
        if self._operation == "min":
            newVal = max(itemStack["Damage"].value,self._opValue)
            itemStack["Damage"].value = newVal
            return

    def str(self):
        if self._operation == "=":
            return u'Set damage to ' + str(self._opValue)
        if self._operation == "+":
            return u'Add ' + str(self._opValue) + u' to damage'
        if self._operation == "-":
            return u'Subtract ' + str(self._opValue) + u' from damage'
        if self._operation == "*":
            return u'Multiply damage by ' + str(self._opValue)
        if self._operation == "/":
            return u'Divide damage by ' + str(self._opValue)
        if self._operation == "%":
            return u'Set damage to itself modulo ' + str(self._opValue)
        if self._operation == "max":
            return u'Prevent damage from being greater than ' + str(self._opValue)
        if self._operation == "min":
            return u'Prevent damage from being less than ' + str(self._opValue)

class actID(object):
    """
    Stores an ID to apply later
    """
    def __init__(self,actionOptions):
        self._id = actionOptions.pop(0)

    def run(self,itemStack,log_data):
        itemStack["id"].value = self._id

    def str(self):
        return u'Change ID to "' + self._id + u'"'

class actLocation(object):
    """
    Print the player file or location of the root entity
    """
    def __init__(self,actionOptions):
        return

    def run(self,itemStack,log_data):
        if "player file" in log_data:
            print u"Item is in player file " + log_data["player file"]
        elif "Pos" in log_data["rootEntity"]:
            print u"Item is on {} at {},{},{}".format(
                log_data["rootEntity"]["id"].value,
                round(log_data["rootEntity"]["Pos"][0].value,3),
                round(log_data["rootEntity"]["Pos"][1].value,3),
                round(log_data["rootEntity"]["Pos"][2].value,3)
            )
        elif "x" in log_data["rootEntity"]:
            print u"Item is in {} at {},{},{}".format(
                log_data["rootEntity"]["id"].value,
                log_data["rootEntity"]["x"].value,
                log_data["rootEntity"]["y"].value,
                log_data["rootEntity"]["z"].value
            )
        else:
            print u"Item is on an entity without location? " + log_data["rootEntity"].json

    def str(self):
        return u'Print the player file name or location of the root entity'

class actName(object):
    """
    Modify an item name
    """
    def __init__(self,actionOptions):
        self._cmd = actionOptions.pop(0)
        if self._cmd == "color":
            self._color = None
            color = actionOptions.pop(0)
            if type(color) == int:
                # assumes color is a number from 0-15
                self._color = formatCodes["list"][color]["id"]
            elif (
                (type(color) == str) or
                (type(color) == unicode)
            ):
                # assumes color is a name or character like '7' as in '§7'
                # use '' to mean "no color"
                for formatCode in formatCodes["list"]:
                    if (
                        (color.lower() == formatCode["id"].lower()) or
                        (color.lower() == formatCode["display"].lower()) or
                        (color.lower() == formatCode["technical"].lower())
                    ):
                        self._color = formatCode
            # If self._color is None by here, assume it should be no color
        if self._cmd == "set":
            self._setName = None
            name = actionOptions.pop(0)
            if (
                (type(name) == str) or
                (type(name) == unicode)
            ):
                self._setName = name
            # If self._setName is None by here, assume it should be no name
        else:
            print u"!!! Unknown subcommand for actName: {}".format(self._cmd)
            # put the subcommand back
            actionOptions.insert(0,self._cmd)
            self._cmd = None

    def run(self,itemStack,log_data):
        if self._cmd == "color":
            if (
                ("tag" not in itemStack) or
                ("display" not in itemStack["tag"]) or
                ("Name" not in itemStack["tag"]["display"])
            ):
                # not applicable (unless default name is obtained)
                return
            formatList = u""
            name = itemStack["tag"]["display"]["Name"].value
            while name[0] == u'§':
                formatList += name[1]
                name = name[2:]
            while len(formatList):
                color = formatList[-1]
                formatList = formatList[:-1]
                if color not in formatCodes["colors"]:
                    name = u'§' + color + name
            if self._color is not None:
                name = u'§' + self._color["id"] + name
            itemStack["tag"]["display"]["Name"].value = name

        elif self._cmd == "set":
            if self._setName is None:
                # delete the item name
                if "tag" in itemStack:
                    if "display" in itemStack["tag"]:
                        if "Name" in itemStack["tag"]["display"]:
                            itemStack["tag"]["display"].pop("Name")
                        if len(itemStack["tag"]["display"].keys()) == 0:
                            itemStack["tag"].pop("display")
                    if len(itemStack["tag"].keys()) == 0:
                        itemStack.pop("tag")
            else:
                # set the item name
                if "tag" not in itemStack:
                    itemStack["tag"] = nbt.TAG_Compound()
                if "display" not in itemStack:
                    itemStack["tag"]["display"] = nbt.TAG_Compound()
                if "Name" not in itemStack["tag"]["display"]:
                    itemStack["tag"]["display"]["Name"] = nbt.TAG_String(self._setName)
                else:
                    itemStack["tag"]["display"]["Name"].value = self._setName

    def str(self):
        if self._cmd == "color":
            return u'Update name color to {} if name exists'.format(self._color["display"])
        elif self._cmd == "set":
            if self._setName is None:
                return u'Remove item name'
            else:
                return u'Set name to "{}"'.format(self._setName)
        else:
            return u'Invalid color subcommand; does nothing'

class actNBT(object):
    """
    Stores an NBT action to apply later
    """
    def __init__(self,actionOptions):
        self._operation = actionOptions.pop(0)
        if (
                (self._operation == "set")
                or (self._operation == "replace")
        ):
            self._nbt = nbt.json_to_tag( actionOptions.pop(0) )

    def run(self,itemStack,log_data):
        if (
                (self._operation == "clear")
                or (self._operation == "replace")
        ) and ("tag" in itemStack):
            itemStack.pop("tag")
        if (
                (self._operation == "update")
                or (self._operation == "replace")
        ):
            if "tag" not in itemStack:
                itemStack["tag"] = nbt.TAG_Compound()
            itemStack["tag"].update(self._nbt)

    def str(self):
        if self._operation == "clear":
            return u'Remove NBT'
        if self._operation == "update":
            return u'Update existing NBT with ' + self._nbt.json
        if self._operation == "replace":
            return u'Replace NBT with ' + self._nbt.json

class actPrint(object):
    """
    Print a constant string to the terminal
    """
    def __init__(self,actionOptions):
        self._msg = actionOptions.pop(0)

    def run(self,itemStack,log_data):
        print self._msg

    def str(self):
        return u'Print "' + self._msg + '"'

class actPrintItem(object):
    """
    Print the item to the terminal as json
    """
    def __init__(self,actionOptions):
        return

    def run(self,itemStack,log_data):
        print itemStack.json

    def str(self):
        return u'Print the item details as json'

class actRemove(object):
    """
    Stores a stack removal action to apply later
    """
    def __init__(self,actionOptions):
        return

    def run(self,itemStack,log_data):
        # item stacks with count 0 are deleted when loading the world
        itemStack["Count"].value = 0
        if "tag" in itemStack:
            itemStack.pop("tag")

    def str(self):
        return u'Set item count to 0; the server will delete it on load'

"""
NYI - more promising now that we can track which player holds an item;
I'd like to track player plots too, but that needs more work first.
class actScoreboard(object):
    ""
    Stores a scoreboard action to apply later
    ""
    def __init__(self,actionOptions):
        self._operation = actionOptions.pop(0)
        self._opValue = actionOptions.pop(0)

    def run(self,itemStack):
        if self._operation == "=":
            itemStack["Damage"].value = self._opValue
            return
        if self._operation == "+":
            itemStack["Damage"].value += self._opValue
            return
        if self._operation == "-":
            itemStack["Damage"].value -= self._opValue
            return
        if self._operation == "*":
            itemStack["Damage"].value *= self._opValue
            return
        if self._operation == "/":
            itemStack["Damage"].value /= self._opValue
            return
        if self._operation == "%":
            itemStack["Damage"].value %= self._opValue
            return
        if self._operation == "max":
            newVal = min(itemStack["Damage"].value,self._opValue)
            itemStack["Damage"].value = newVal
            return
        if self._operation == "min":
            newVal = max(itemStack["Damage"].value,self._opValue)
            itemStack["Damage"].value = newVal
            return
"""

