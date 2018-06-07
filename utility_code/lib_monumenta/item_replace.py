#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import codecs

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
from pymclevel import nbt

from lib_monumenta.iter_entity import IterEntities

soulboundPrefix = u'Soulbound to '
replicaText = u'§5§o* Replica Item *'
hopeText = u'§7Hope'
infusedByPrefix = u'Infused by '

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
    "minecraft:bow",
    "minecraft:carrot_on_a_stick",
    "minecraft:elytra",
    "minecraft:fishing_rod",
    "minecraft:flint_and_steel",
    "minecraft:shears",
    "minecraft:shield",
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

    # Jukeboxes
    "RecordItem",
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

def removeFormatting(formattedString):
    nameNoFormat = formattedString
    while u'§' in nameNoFormat:
        i = nameNoFormat.find(u'§')
        nameNoFormat = nameNoFormat[:i]+nameNoFormat[i+2:]
    return nameNoFormat

def hopeify(lore,InfusedBy):
    newLore = nbt.TAG_List()
    hopeAdded = False
    nameAdded = False
    kingsValleyFound = False

    for loreEntryTag in lore:
        loreEntry = loreEntryTag.value

        if hopeText in loreEntry:
            return lore

        if u"King's Valley" in loreEntry:
            kingsValleyFound = True

        if (
            hopeAdded == False and
            (
                u"King's Valley" in loreEntry or
                len(removeFormatting(loreEntry)) == 0
            )
        ):
            newLore.append(nbt.TAG_String(hopeText))
            hopeAdded = True

        if (
            nameAdded == False and
            len(removeFormatting(loreEntry)) == 0
        ):
            newLore.append(nbt.TAG_String(infusedByPrefix + InfusedBy))
            nameAdded = True

        newLore.append(loreEntryTag)

    if nameAdded == False:
        newLore.append(nbt.TAG_String(infusedByPrefix + InfusedBy))

    if not kingsValleyFound:
        return lore

    return newLore

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
            return
        self.log_data = {}
        self.log_data["debug"] = debug
        self.log_data["global"] = {}
        self.replacements = allReplacements(replacementList,self.log_data)
        if "global count" in debug:
            self.enableGlobalCount()
        self.entityIter = IterEntities(
            [
                "block entities",
                "entities",
                "search item entities"
            ],
            self._OnEntities,
            None
        )

    def enableGlobalCount(self):
        if "global count" not in self.log_data["debug"]:
            self.log_data["debug"].append("global count")
        if "global count" not in self.log_data["global"]:
            self.log_data["global"]["global count"] = {}

    def InChunkTag(self,chunkTag):
        if self.replacements is None:
            return
        self.log_data["current"] = {}
        self.entityIter.InChunkTag(chunkTag)

    def InChunk(self,chunk):
        if self.replacements is None:
            return
        self.log_data["current"] = {}
        self.entityIter.InChunk(chunk)

    def InWorld(self,world):
        if self.replacements is None:
            return
        self.log_data["current"] = {}
        self.entityIter.InWorld(world)

    def InSchematic(self,schematic):
        if self.replacements is None:
            return
        self.log_data["current"] = {}
        self.entityIter.InSchematic(schematic)

    def OnPlayers(self,worldDir):
        if self.replacements is None:
            return
        self.log_data["current"] = {}
        self.entityIter.OnPlayers(worldDir)

    def PrintGlobalLog(self):
        if "global count" in self.log_data["global"]:
            print u"Items found:"
            for item in sorted(self.log_data["global"]["global count"].keys()):
                line = u"{}\t{}\n".format(
                    self.log_data["global"]["global count"][item],
                    item
                )
                print line

    def SaveGlobalLog(self,logPath=None):
        if logPath is None:
            print u"! Global Item Replacement log path not specified"
            return
        if "global count" in self.log_data["global"]:
            with codecs.open(logPath,'w',encoding='utf8') as f:
                f.write(u"Items found:\n")
                for item in sorted(self.log_data["global"]["global count"].keys()):
                    line = u"{}\t{}\n".format(
                        self.log_data["global"]["global count"][item],
                        item
                    )
                    f.write(line)
                f.close()

    def _OnEntities(self,dummyArg,entityDetails):
        entity = entityDetails["entity"]
        self.log_data["entity"] = entity
        self.log_data["player file"] = entityDetails["player file"]
        self.log_data["chunk"] = entityDetails["chunk"]

        # The entity exists in the world/schematic directly,
        # not inside something.
        if entityDetails["root entity"] is True:
            self.rootEntity = entityDetails["entity"]
        else:
            self.rootEntity = entityDetails["root entity"]
            self.log_data["rootEntity"] = self.rootEntity

        # Handle villager trades
        if (
            ("Offers" in entity) and
            ("Recipes" in entity["Offers"])
        ):
            for trade in entity["Offers"]["Recipes"]:
                if "buy" in trade:
                    self._InStack(trade["buy"])
                if "buyB" in trade:
                    self._InStack(trade["buyB"])
                if "sell" in trade:
                    self._InStack(trade["sell"])

        for containerTagName in containerTagNames:
            if containerTagName in entity:
                # Replace hand items if they can drop
                if containerTagName == "HandItems":
                    if "HandDropChances" in entity:
                        for i in range(2):
                            if entity["HandDropChances"][i] > -1.00:
                                self._InStack(entity[containerTagName][i])
                    else:
                        self._InStack(entity[containerTagName])

                # Replace armor items if they can drop
                elif containerTagName == "ArmorItems":
                    if "ArmorDropChances" in entity:
                        for i in range(4):
                            if entity["ArmorDropChances"][i] > -1.00:
                                self._InStack(entity[containerTagName][i])
                    else:
                        self._InStackList(entity[containerTagName])

                # Replace other items; they always drop
                else:
                    self._InStackList(entity[containerTagName])

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
        if "global count" in self.log_data["debug"]:
            globalCounts = self.log_data["global"]["global count"]

            # If you want all items and their details exactly as-is,
            # use this. Will be very verbose, not what we normally
            # want! Comment out every line of the function after
            # here to avoid double entries.
            """
            itemString = itemStack.json()
            fakeItem = nbt.json_to_tag(itemString)

            if "Count" in fakeItem:
                count = fakeItem["Count"].value
                fakeItem.pop("Count")
                itemString = fakeItem.json()
            else:
                count = 1

            if itemString not in globalCounts:
                globalCounts[itemString] = count
            else:
                globalCounts[itemString] += count
            """

            # In order to simplify the item list, certain
            # details must be removed; a fake item is
            # used to handle these changes, and is
            # discarded afterwards.

            # The list provided is used to sort the tags
            # within compounds, and causes all other
            # tags to be sorted alphabetically.
            # TAG_Lists are never sorted.
            itemJson = itemStack.json(["id","display","Name","Lore"])

            # TODO: This try/except hides a real crash in JSON parsing - need to fix
            try:
                fakeItem = nbt.json_to_tag(itemJson)
            except Exception:
                print "Failed to parse JSON: '" + itemJson + "'"
                return

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
            if fakeItem["id"].value == "minecraft:filled_map":
                fakeItem.pop("Damage")
            if "Slot" in fakeItem:
                fakeItem.pop("Slot")
            if "tag" in fakeItem:
                if "BlockEntityTag" in fakeItem["tag"]:
                    for containerTagName in containerTagNames:
                        # We don't care which items an item contains;
                        # We only care about how many items exist
                        if containerTagName in fakeItem["tag"]["BlockEntityTag"]:
                            fakeItem["tag"]["BlockEntityTag"].pop(containerTagName)

                    # Ignore banner/shield patterns
                    if "Patterns" in fakeItem["tag"]["BlockEntityTag"]:
                        fakeItem["tag"]["BlockEntityTag"].pop("Patterns")
                    if "Base" in fakeItem["tag"]["BlockEntityTag"]:
                        fakeItem["tag"]["BlockEntityTag"].pop("Base")

                    if len(fakeItem["tag"]["BlockEntityTag"].keys()) == 0:
                        fakeItem["tag"].pop("BlockEntityTag")

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
                    if len(fakeItem["tag"]["display"].keys()) == 0:
                        fakeItem["tag"].pop("display")

                ################
                # Fireworks:
                # Because I highly doubt we care
                if "Explosion" in fakeItem["tag"]:
                    fakeItem["tag"].pop("Explosion")
                if "Fireworks" in fakeItem["tag"]:
                    fakeItem["tag"].pop("Fireworks")

                if len(fakeItem["tag"].keys()) == 0:
                    fakeItem.pop("tag")

            # Skip book of souls
            if (
                ("tag" not in fakeItem) or
                ("author" not in fakeItem["tag"]) or
                (fakeItem["tag"]["author"].value != u"§6The Creator")
            ):
                # I think that's all the tags we want to ignore.
                itemString = fakeItem.json()
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
            if type(aReplacement) is ReplaceItems:
                if "init" in log_data["debug"]:
                    print u"  ┣╸Adding a replacement list"
                    print u"  ┃ ╙╴No code to track which one it is, sorry."
                self._replacements.append(aReplacement.replacements)
            else:
                self._replacements.append(replacement(aReplacement,log_data))
        print u"  Found " + unicode(len(self._replacements)) + u" replacements."

    def run(self,itemStack,log_data):
        for aReplacement in self._replacements:
            aReplacement.run(itemStack,log_data)

class replacement(object):
    def __init__(self,replacementPair,log_data):
        matches = replacementPair[0]
        actions = replacementPair[1]

        if "init" in log_data["debug"]:
            print u"  ┣╸Adding a replacement:"

        # matches is the list of uncompiled matches
        # self._matches is the list of compiled matches
        if (
            "any" in matches and
            len(matches.keys()) == 1
        ):
            # If is level only contains an OR, skip to it
            self._matches = matchAny(matches["any"])
        else:
            self._matches = matchAll(matches)
        if "init" in log_data["debug"]:
            print self._matches.str(u"  ┃ ")

        if "init" in log_data["debug"]:
            print u"  ┃ ╙╴Then do these in order:"

        # actions is the uncompiled list of actions
        # self._actions is the list of compiled actions
        self._actions = []
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
            if action == "unhope":
                newAction = actUnhope(actions)

            self._actions.append(newAction)
            if "init" in log_data["debug"]:
                print newAction.str(u"  ┃   ")

    def run(self,itemStack,log_data):
        if self._matches == itemStack:
            for action in self._actions:
                action.run(itemStack,log_data)

# Matching optimizers

class match(object):
    def __init__(self,matchOptions):
        pass

    def _grab_matches(self,matchOptions):
        for key in matchOptions:
            newMatch = None
            if key == "any":
                newMatch = matchAny(matchOptions[key])
            if key == "all":
                newMatch = matchAll(matchOptions[key])
            if key == "count":
                newMatch = matchCount(matchOptions[key])
            if key == "damage":
                newMatch = matchDamage(matchOptions[key])
            if key == "id":
                newMatch = matchID(matchOptions[key])
            if key == "name":
                newMatch = matchName(matchOptions[key])
            if key == "nbt":
                newMatch = matchNBT(matchOptions[key])
            if key == "none":
                newMatch = matchNone(matchOptions[key])
            if newMatch is not None:
                self._matches.append(newMatch)

    def __eq__(self,itemStack):
        return False

    def str(self,prefix=u''):
        return prefix + u'└╴Undefined matching pattern (returns False)'

class matchAll(match):
    """
    Logical AND
    Match if all sub matches are true;
    If no sub matches exist, always false;
    This is the default case
    """
    def __init__(self,matchOptions):
        self._matches = None
        if type(matchOptions) is list:
            self._matches = []
            for i in matchOptions:
                if len(i.keys()) == 1:
                    self._grab_matches(i)
                else:
                    subMatch=matchAll(i)
                    self._matches.append(subMatch)
        elif type(matchOptions) is dict:
            self._matches = []
            self._grab_matches(matchOptions)

    def __eq__(self,itemStack):
        if self._matches is None:
            return False
        else:
            return all(rule == itemStack for rule in self._matches)

    def str(self,prefix=u''):
        if self._matches is None:
            return prefix + u'└╴False'
        else:
            result = prefix + u'╟╴If all of these are true:'
            subprefix = prefix + u'║ '
            for match in self._matches:
                result += u'\n' + match.str(subprefix)
            return result

class matchAny(match):
    """
    Logical OR
    Match if any of the sub matches are true;
    If no sub matches exist, always true
    """
    def __init__(self,matchOptions):
        self._matches = None
        if type(matchOptions) is list:
            self._matches = []
            for i in matchOptions:
                if len(i.keys()) == 1:
                    self._grab_matches(i)
                else:
                    subMatch=matchAll(i)
                    self._matches.append(subMatch)
        elif type(matchOptions) is dict:
            self._matches = []
            self._grab_matches(matchOptions)

    def __eq__(self,itemStack):
        if self._matches is None:
            return True
        else:
            return any(rule == itemStack for rule in self._matches)

    def str(self,prefix=u''):
        if self._matches is None:
            return prefix + u'└╴True'
        else:
            result = prefix + u'╟╴If any of these are true:'
            subprefix = prefix + u'║ '
            for match in self._matches:
                result += u'\n' + match.str(subprefix)
            return result

class matchCount(match):
    """
    This stores item counts to match later
    """
    def __init__(self,matchOptions):
        count = matchOptions
        if (type(count) != list) and (type(count) != tuple):
            self._count = [count]
        else:
            self._count = count

    def __eq__(self,itemStack):
        try:
            return itemStack["Count"].value in self._count
        except:
            return False

    def str(self,prefix=u''):
        return prefix + u'└╴Item count is in ' + str(self._count)

class matchDamage(match):
    """
    This stores damage values to match later
    """
    def __init__(self,matchOptions):
        damage = matchOptions
        if (type(damage) != list) and (type(damage) != tuple):
            self._damage = [damage]
        else:
            self._damage = damage

    def __eq__(self,itemStack):
        try:
            return itemStack["Damage"].value in self._damage
        except:
            return False

    def str(self,prefix=u''):
        return prefix + u'└╴Item damage is in ' + str(self._damage)

class matchID(match):
    """
    This stores an ID to match later
    """
    def __init__(self,matchOptions):
        self._id = matchOptions

    def __eq__(self,itemStack):
        try:
            return self._id == itemStack["id"].value
        except:
            return False

    def str(self,prefix=u''):
        return prefix + u'└╴Item ID is "' + self._id + u'"'

class matchName(match):
    """
    This stores a name to match later without color
    """
    def __init__(self,matchOptions):
        self._name = matchOptions
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
            formattedName = itemStack["tag"]["display"]["Name"].value
            return removeFormatting(formattedName) == self._name

    def str(self,prefix=u''):
        if self._name == None:
            return prefix + u'└╴Item has no name'
        else:
            return prefix + u'└╴Item name matches "' + self._name + '" regardless of color'

class matchNBT(match):
    """
    This stores NBT to match later
    """
    def __init__(self,matchOptions):
        json = matchOptions

        if json is None:
            self._nbt = None
        else:
            self._exact = False
            if "strict" == json[:6]:
                self._exact = True
                json = json[6:]
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

    def str(self,prefix=u''):
        if self._nbt is None:
            return prefix + u'└╴Item has no NBT'
        elif self._exact:
            return prefix + u'└╴Item NBT exactly matches ' + self._nbt.json()
        else:
            return prefix + u'└╴Item NBT loosely matches ' + self._nbt.json()

class matchNone(match):
    """
    Logical NOR/NOT
    Match if none of the sub matches are true;
    If no sub matches exist, defaults to false;
    This is a special case to never match anything;
    used to invalidate item replacements
    """
    def __init__(self,matchOptions):
        self._matches = None
        if type(matchOptions) is list:
            self._matches = []
            for i in matchOptions:
                if len(i.keys()) == 1:
                    self._grab_matches(i)
                else:
                    subMatch=matchAll(i)
                    self._matches.append(subMatch)
        elif type(matchOptions) is dict:
            self._matches = []
            self._grab_matches(matchOptions)

    def __eq__(self,itemStack):
        if self._matches is None:
            return False
        else:
            return all(rule != itemStack for rule in self._matches)

    def str(self,prefix=u''):
        if self._matches is None:
            return prefix + u'└╴False'
        else:
            result = prefix + u'╟╴If none of these are true:'
            subprefix = prefix + u'║ '
            for match in self._matches:
                result += u'\n' + match.str(subprefix)
            return result


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

    def str(self,prefix=u''):
        if self._operation == "=":
            return prefix + u'└╴Set count to ' + str(self._opValue)
        if self._operation == "+":
            return prefix + u'└╴Add ' + str(self._opValue) + u' to count'
        if self._operation == "-":
            return prefix + u'└╴Subtract ' + str(self._opValue) + u' from count'
        if self._operation == "*":
            return prefix + u'└╴Multiply count by ' + str(self._opValue)
        if self._operation == "/":
            return prefix + u'└╴Divide count by ' + str(self._opValue)
        if self._operation == "%":
            return prefix + u'└╴Set count to itself modulo ' + str(self._opValue)
        if self._operation == "max":
            return prefix + u'└╴Prevent count from being greater than ' + str(self._opValue)
        if self._operation == "min":
            return prefix + u'└╴Prevent count from being less than ' + str(self._opValue)

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

    def str(self,prefix=u''):
        if self._operation == "=":
            return prefix + u'└╴Set damage to ' + str(self._opValue)
        if self._operation == "+":
            return prefix + u'└╴Add ' + str(self._opValue) + u' to damage'
        if self._operation == "-":
            return prefix + u'└╴Subtract ' + str(self._opValue) + u' from damage'
        if self._operation == "*":
            return prefix + u'└╴Multiply damage by ' + str(self._opValue)
        if self._operation == "/":
            return prefix + u'└╴Divide damage by ' + str(self._opValue)
        if self._operation == "%":
            return prefix + u'└╴Set damage to itself modulo ' + str(self._opValue)
        if self._operation == "max":
            return prefix + u'└╴Prevent damage from being greater than ' + str(self._opValue)
        if self._operation == "min":
            return prefix + u'└╴Prevent damage from being less than ' + str(self._opValue)

class actID(object):
    """
    Stores an ID to apply later
    """
    def __init__(self,actionOptions):
        self._id = actionOptions.pop(0)

    def run(self,itemStack,log_data):
        itemStack["id"].value = self._id

    def str(self,prefix=u''):
        return prefix + u'└╴Change ID to "' + self._id + u'"'

class actLocation(object):
    """
    Print the player file or location of the root entity
    """
    def __init__(self,actionOptions):
        return

    def run(self,itemStack,log_data):
        if log_data["player file"] is not None:
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
            print u"Item is on an entity without location? " + log_data["rootEntity"].json()

    def str(self,prefix=u''):
        return prefix + u'└╴Print the player file name or location of the root entity'

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
                self._color = formatCodes["list"][color]
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

    def str(self,prefix=u''):
        if self._cmd == "color":
            if self._color is None:
                return prefix + u'└╴Remove name color if name exists'
            else:
                return prefix + u'└╴Update name color to {} if name exists'.format(self._color["display"])
        elif self._cmd == "set":
            if self._setName is None:
                return prefix + u'└╴Remove item name'
            else:
                return prefix + u'└╴Set name to "{}"'.format(self._setName)
        else:
            return prefix + u'└╴Invalid color subcommand; does nothing'

class actNBT(object):
    """
    Stores an NBT action to apply later
    """
    def __init__(self,actionOptions):
        self._operation = actionOptions.pop(0)
        if (
                (self._operation == "update")
                or (self._operation == "replace")
        ):
            self._nbt = nbt.json_to_tag( actionOptions.pop(0) )

    def run(self,itemStack,log_data):
        ########################################
        # Preserve cosmetics and soulbound tag
        tagsToRestore = nbt.TAG_Compound()
        soulbound = None
        isReplica = False
        hopeifiedBy = None
        if "tag" in itemStack:
            tagsToRestore["tag"] = nbt.TAG_Compound()
            # armor color
            if "display" in itemStack["tag"]:
                displayTag = itemStack["tag"]["display"]
                tagsToRestore["tag"]["display"] = nbt.TAG_Compound()
                if "color" in displayTag:
                    tagsToRestore["tag"]["display"]["color"] = displayTag["color"]
                if "Lore" in displayTag:
                    for loreLine in displayTag["Lore"]:
                        if soulboundPrefix == loreLine.value[:len(soulboundPrefix)]:
                            soulbound = loreLine
                        if replicaText == loreLine.value:
                            isReplica = True
                        if infusedByPrefix == loreLine.value[:len(infusedByPrefix)]:
                            hopeifiedBy = loreLine.value[len(infusedByPrefix):]
            # banner/shield color/pattern
            if "BlockEntityTag" in itemStack["tag"]:
                tagsToRestore["tag"]["BlockEntityTag"] = nbt.TAG_Compound()
                if "Base" in itemStack["tag"]["BlockEntityTag"]:
                    tagsToRestore["tag"]["BlockEntityTag"]["Base"] = itemStack["tag"]["BlockEntityTag"]["Base"]
                if "Patterns" in itemStack["tag"]["BlockEntityTag"]:
                    tagsToRestore["tag"]["BlockEntityTag"]["Patterns"] = itemStack["tag"]["BlockEntityTag"]["Patterns"]

        ########################################
        # Clear NBT if needed
        if (
                (self._operation == "clear")
                or (self._operation == "replace")
        ) and ("tag" in itemStack):
            itemStack.pop("tag")

        ########################################
        # Set NBT if needed
        if (
                (self._operation == "update")
                or (self._operation == "replace")
        ):
            if "tag" not in itemStack:
                itemStack["tag"] = nbt.TAG_Compound()
            itemStack["tag"].update(self._nbt)

            ########################################
            # restore preserved tags here

            # if we intended to clear their NBT, it's probably
            # for a good reason. If we put it back, we put
            # player customizations back.
            itemStack.update(tagsToRestore)
            if (
                (soulbound is not None) or
                isReplica or
                (hopeifiedBy is not None)
            ):
                if "display" not in itemStack["tag"]:
                    itemStack["tag"]["display"] = nbt.TAG_Compound()
                if "Lore" not in itemStack["tag"]["display"]:
                    itemStack["tag"]["display"]["Lore"] = nbt.TAG_List()
                lore = itemStack["tag"]["display"]["Lore"]
                if soulbound is not None:
                    lore.append(soulbound)
                if isReplica:
                    for loreLine in lore:
                        if u'''Unique''' in loreLine.value:
                            loreLine.value = replicaText
                if hopeifiedBy is not None:
                    lore = hopeify(lore,hopeifiedBy)
                    itemStack["tag"]["display"]["Lore"] = lore

    def str(self,prefix=u''):
        if self._operation == "clear":
            return prefix + u'└╴Remove NBT'
        if self._operation == "update":
            return prefix + u'└╴Update existing NBT with ' + self._nbt.json()
        if self._operation == "replace":
            return prefix + u'└╴Replace NBT with ' + self._nbt.json()

class actPrint(object):
    """
    Print a constant string to the terminal
    """
    def __init__(self,actionOptions):
        self._msg = actionOptions.pop(0)

    def run(self,itemStack,log_data):
        print self._msg

    def str(self,prefix=u''):
        return prefix + u'└╴Print "' + self._msg + '"'

class actPrintItem(object):
    """
    Print the item to the terminal as json
    """
    def __init__(self,actionOptions):
        return

    def run(self,itemStack,log_data):
        print itemStack.json()

    def str(self,prefix=u''):
        return prefix + u'└╴Print the item details as json'

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

    def str(self,prefix=u''):
        return prefix + u'└╴Set item count to 0; the server will delete it on load'

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

class actUnhope(object):
    """
    Removes hope from any infused items; this should only be run the week before the 100% working fix is in place.
    """
    def __init__(self,actionOptions):
        "No initialization required"

    def run(self,itemStack,log_data):
        hopeInfused = False
        if "tag" in itemStack:
            if "display" in itemStack["tag"]:
                displayTag = itemStack["tag"]["display"]
                if "Lore" in displayTag:
                    loreTag = displayTag["Lore"]
                    for i in range(len(loreTag)-1,-1,-1):
                        loreLine = loreTag[i]
                        if infusedByPrefix == loreLine.value[:len(infusedByPrefix)]:
                            hopeInfused = True
                            loreTag.pop(i)
                        if hopeInfused and hopeText == loreLine.value:
                            loreTag.pop(i)

    def str(self,prefix=u''):
        return prefix + u'└╴Remove Hope (only if infused by player)'

