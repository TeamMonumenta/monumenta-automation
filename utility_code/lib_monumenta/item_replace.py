#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

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
    "minecraft:",
    "minecraft:",
    "minecraft:",
    "minecraft:",
    "minecraft:",
    
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
            print "New item replacement list loading..."
        if replacementList is None:
            self.replacements = None
            if "init" in debug:
                print "Dummy list, does nothing."
        else:
            self.log_data = {}
            self.log_data["debug"] = debug
            self.log_data["global"] = {}
            self.replacements = allReplacements(replacementList,self.log_data)
            if "global count" in debug:
                self.log_data["global count"] = {}

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
            player = nbt.load(playerFile)
            # In this case, we can easily copy the only entity to a list.
            self.entityList = [player]
            self._OnEntities()
            player.save(playerFile)

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

            # Handle spawners (done this way for spawner items with NBT)
            if "SpawnData" in self.entity:
                self.entityList.append(self.entity["SpawnData"])
            if "SpawnPotentials" in self.entity:
                for potentialSpawn in self.entity["SpawnPotentials"]:
                    self.entityList.append(potentialSpawn["Entity"])

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
            globalCounts = self.log_data["global count"]

            # In order to simplify the item list, certain
            # details must be removed; a fake item is
            # used to handle these changes, and is
            # discarded afterwards.
            fakeItem = nbt.json_to_tag(itemStack.json)
            count = fakeItem["Count"].value
            fakeItem.pop("Count")
            if fakeItem["id"].value in ItemsWithRealDamage:
                fakeItem.pop("Damage")
            if "Slot" in fakeItem:
                fakeItem.pop("Slot")
            if "tag" in fakeItem:
                if "BlockEntityTag" in fakeItem["tag"]:
                    for containerTagName in containerTagNames:
                        if containerTagName in fakeItem["tag"]["BlockEntityTag"]
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
                    if color in fakeItem["tag"]["display"]:
                        fakeItem["tag"]["display"].pop("color")
                
                ################
                # Fireworks:
                # Because I highly doubt we care
                if "Explosion" in fakeItem["tag"]:
                    fakeItem["tag"].pop("Explosion")
                if "Fireworks" in fakeItem["tag"]:
                    fakeItem["tag"].pop("Fireworks")
                
            # TODO


################################################################################
# Replacement list optimizer

class allReplacements(list):
    def __init__(self,replacementList,log_data):
        self._replacements = []
        for aReplacement in replacementList:
            self._replacements.append(replacement(aReplacement,log_data))
        print "  Found " + str(len(self._replacements)) + " replacements."

    def run(self,itemStack,log_data):
        for replacement in self._replacements:
            replacement.run(itemStack,log_data)

class replacement(object):
    def __init__(self,replacementPair,log_data):
        matches = replacementPair[0]
        actions = replacementPair[1]

        if "init" in log_data["debug"]:
            print "Adding a replacement:"

        self.matches = []
        for key in matches:
            if key == "id":
                newMatch = matchID(matches)
                self.matches.append(newMatch)
            if key == "damage":
                newMatch = matchDamage(matches)
                self.matches.append(newMatch)
            if key == "nbt":
                newMatch = matchNBT(matches)
                self.matches.append(newMatch)
            if key == "count":
                newMatch = matchCount(matches)
                self.matches.append(newMatch)
            if key == "none":
                newMatch = matchNone()
                self.matches.append(newMatch)
            if key == "any":
                newMatch = matchAny()
                self.matches.append(newMatch)
            if "init" in log_data["debug"]:
                print newMatch.str()
        if len(self.matches) == 0:
            newMatch = matchNone()
            self.matches.append(newMatch)
            if "init" in log_data["debug"]:
                print u"* No known match criteria provided."

        self.actions = []
        while len(actions):
            action = actions.pop(0)
            if action == "id":
                newAction = changeID(actions)
                self.actions.append(newAction)
            if action == "count":
                newAction = changeCount(actions)
                self.actions.append(newAction)
            if action == "damage":
                newAction = changeDamage(actions)
                self.actions.append(newAction)
            if action == "nbt":
                newAction = changeNBT(actions)
                self.actions.append(newAction)
            if action == "remove":
                newAction = changeRemove()
                self.actions.append(newAction)
            if action == "print":
                newAction = changePrint(actions)
                self.actions.append(newAction)
            if "init" in log_data["debug"]:
                print newAction.str()

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

class matchNone(object):
    """
    This is a special case to never match anything;
    used for invalid item replacements
    """
    def __eq__(self,itemStack):
        return False

    def str(self):
        return "* Match nothing"

class matchAny(object):
    """
    This is a special case to match anything;
    used by itself to match all items
    """
    def __eq__(self,itemStack):
        return True

    def str(self):
        return "* Match everything"

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
        return u'* Match ID "' + self._id + u'"'

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
        return u'* Match damage value in ' + str(self._damage)

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
            return u'* Match no NBT exactly'
        elif self._exact:
            return u'* Match NBT ' + self._nbt.json + u' exactly'
        else:
            return u'* Match NBT ' + self._nbt.json

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
        return u'* Match count value in ' + str(self._count)


# Action optimizers

class changeID(object):
    """
    Stores an ID to apply later
    """
    def __init__(self,actionOptions):
        self._id = actionOptions.pop(0)

    def run(self,itemStack,log_data):
        itemStack["id"].value = self._id

    def str(self):
        return u'* Change ID to "' + self._id + u'"'

class changeCount(object):
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
            return u'* Set count to ' + str(self._opValue)
        if self._operation == "+":
            return u'* Add ' + str(self._opValue) + u' to count'
        if self._operation == "-":
            return u'* Subtract ' + str(self._opValue) + u' from count'
        if self._operation == "*":
            return u'* Multiply count by ' + str(self._opValue)
        if self._operation == "/":
            return u'* Divide count by ' + str(self._opValue)
        if self._operation == "%":
            return u'* Set count to itself modulo ' + str(self._opValue)
        if self._operation == "max":
            return u'* Prevent count from being greater than ' + str(self._opValue)
        if self._operation == "min":
            return u'* Prevent count from being less than ' + str(self._opValue)

class changeDamage(object):
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
            return u'* Set damage to ' + str(self._opValue)
        if self._operation == "+":
            return u'* Add ' + str(self._opValue) + u' to damage'
        if self._operation == "-":
            return u'* Subtract ' + str(self._opValue) + u' from damage'
        if self._operation == "*":
            return u'* Multiply damage by ' + str(self._opValue)
        if self._operation == "/":
            return u'* Divide damage by ' + str(self._opValue)
        if self._operation == "%":
            return u'* Set damage to itself modulo ' + str(self._opValue)
        if self._operation == "max":
            return u'* Prevent damage from being greater than ' + str(self._opValue)
        if self._operation == "min":
            return u'* Prevent damage from being less than ' + str(self._opValue)

class changeNBT(object):
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
            return u'* Remove NBT'
        if self._operation == "update":
            return u'* Update existing NBT with ' + self._nbt.json
        if self._operation == "replace":
            return u'* Replace NBT with u' + self._nbt.json

"""
NYI
class changeScoreboard(object):
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

class changeRemove(object):
    """
    Stores a stack removal action to apply later
    """
    def run(self,itemStack,log_data):
        # item stacks with count 0 are deleted when loading the world
        itemStack["Count"].value = 0
        if "tag" in itemStack:
            itemStack.pop("tag")

    def str(self):
        return u'* Set item count to 0; the server will delete it on load'

class changePrint(object):
    """
    Print a constant string to the terminal
    """
    def __init__(self,actionOptions):
        self._msg = actionOptions.pop(0)

    def run(self,itemStack,log_data):
        print self._msg

    def str(self):
        return u'* Print "' + self._msg + '"'


