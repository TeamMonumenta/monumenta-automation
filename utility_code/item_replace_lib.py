#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import mclevel
from mclevel import nbt

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
]

################################################################################
# Item stack finding code

def replaceItemStack(itemStack,replacementList):
    if type(itemStack) != nbt.TAG_Compound:
        # Invalid itemStack type
        return
    if "id" not in itemStack:
        # No item in this slot (mob armor/hand items)
        return
    if itemStack["id"].value in shulkerIDNames:
        if (
            ( "tag" in itemStack ) and
            ( "BlockEntityTag" in itemStack["tag"] ) and
            ( "Items" in itemStack["tag"]["BlockEntityTag"] )
        ):
            shulkerBoxContents = itemStack["tag"]["BlockEntityTag"]["Items"]
            # TODO This recursive method should be changed to iterative!
            replaceItemStacks(shulkerBoxContents,replacementList)
    elif itemStack["id"].value == u"minecraft:spawn_egg":
        if (
            ( "tag" in itemStack ) and
            ( "EntityTag" in itemStack["tag"] )
        ):
            spawnEggEntity = itemStack["tag"]["EntityTag"]
            # TODO This recursive method should be changed to iterative!
            replaceItemsOnEntity(spawnEggEntity,replacementList)
    replacementList.run(itemStack)
    
def replaceItemStacks(itemStackContainer,replacementList):
    if type(itemStackContainer) is nbt.TAG_List:
        for itemStack in itemStackContainer:
            replaceItemStack(itemStack,replacementList)
    elif type(itemStackContainer) is nbt.TAG_Compound:
        replaceItemStack(itemStackContainer,replacementList)
    
def replaceItemsOnPlayers(worldDir,replacementList):
    for playerFile in os.listdir(worldDir+"playerdata"):
        playerFile = worldDir+"playerdata/" + playerFile
        player = nbt.load(playerFile)
        replaceItemStacks(player["Inventory"],replacementList)
        replaceItemStacks(player["EnderItems"],replacementList)
        player.save(playerFile)

def replaceItemsOnEntity(entity,replacementList):
    for containerTagName in containerTagNames:
        if containerTagName in entity:
            
            # Replace hand items if they can drop
            if containerTagName == "HandItems":
                if "HandDropChances" in entity:
                    for i in range(2):
                        if entity["HandDropChances"][i] > -1.00:
                            replaceItemStacks(entity[containerTagName][i],replacementList)
                else:
                    replaceItemStacks(entity[containerTagName],replacementList)
            
            # Replace armor items if they can drop
            elif containerTagName == "ArmorItems":
                if "ArmorDropChances" in entity:
                    for i in range(4):
                        if entity["ArmorDropChances"][i] > -1.00:
                            replaceItemStacks(entity[containerTagName][i],replacementList)
                else:
                    replaceItemStacks(entity[containerTagName],replacementList)
            
            # Replace other items; they always drop
            else:
                replaceItemStacks(entity[containerTagName],replacementList)

def replaceItemsInSchematic(schematic,replacementList):
    for entity in schematic.Entities:
        replaceItemsOnEntity(entity,replacementList)
    
    for tileEntity in schematic.TileEntities:
        replaceItemsOnEntity(tileEntity,replacementList)

def replaceItemsInWorld(world,replacementList):
    for cx,cz in world.allChunks:
        aChunk = world.getChunk(cx,cz)
        
        if "Level" not in aChunk.root_tag:
            # This chunk is invalid, skip it!
            # It has no data.
            continue
        
        for entity in aChunk.root_tag["Level"]["Entities"]:
            replaceItemsOnEntity(entity,replacementList)
        
        for tileEntity in aChunk.root_tag["Level"]["TileEntities"]:
            replaceItemsOnEntity(tileEntity,replacementList)
        
        aChunk.chunkChanged(False) # needsLighting=False

################################################################################
# Replacement list optimizer

class allReplacements(list):
    def __init__(self,replacementList):
        print "Compiling item replacement list..."
        self._replacements = []
        for aReplacement in replacementList:
            self._replacements.append(replacement(aReplacement))
        print "Found " + str(len(self._replacements)) + " replacements."
    
    def __len__(self):
        return len(self._replacements)
    
    def __getitem__(self,key):
        return self._replacements[key]
    
    def __setitem__(self,key,value):
        self._replacements[key] = replacement(value)
    
    def __iter__(self):
        return self._replacements
    
    def run(self,itemStack):
        for replacement in self._replacements:
            replacement.run(itemStack)

class replacement(object):
    def __init__(self,replacementPair):
        matches = replacementPair[0]
        actions = replacementPair[1]
        
        #print "Adding a replacement:"
        
        self.matches = []
        if "id" in matches:
            newMatch = matchID(matches)
            self.matches.append(newMatch)
            #print newMatch.str()
        if "damage" in matches:
            newMatch = matchDamage(matches)
            self.matches.append(newMatch)
            #print newMatch.str()
        if "nbt" in matches:
            newMatch = matchNBT(matches)
            self.matches.append(newMatch)
            #print newMatch.str()
        if "count" in matches:
            newMatch = matchCount(matches)
            self.matches.append(newMatch)
            #print newMatch.str()
        if len(self.matches) == 0:
            newMatch = matchNone()
            self.matches.append(newMatch)
            #print newMatch.str()
        
        self.actions = []
        while len(actions):
            action = actions.pop(0)
            if action == "id":
                newAction = changeID(actions)
                self.actions.append(newAction)
                #print newAction.str()
            if action == "count":
                newAction = changeCount(actions)
                self.actions.append(newAction)
                #print newAction.str()
            if action == "damage":
                newAction = changeDamage(actions)
                self.actions.append(newAction)
                #print newAction.str()
            if action == "nbt":
                newAction = changeNBT(actions)
                self.actions.append(newAction)
                #print newAction.str()
            if action == "remove":
                newAction = changeRemove()
                self.actions.append(newAction)
                #print newAction.str()
    
    def run(self,itemStack):
        if all(rule == itemStack for rule in self.matches):
            #print "*** Found match:"
            #print itemStack.json
            #print "Matched rules:"
            #for rule in self.matches:
            #    print rule.str()
            #print "Actions:"
            for action in self.actions:
                #print action.str()
                action.run(itemStack)
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
        return u'* Match damage value in "' + self._damage + u'"'

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
            return u'* Match NBT ' + self._nbt.json
        else:
            return u'* Match NBT ' + self._nbt.json + u' exactly'

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
        return u'* Match count value in "' + self._count + u'"'


# Action optimizers

class changeID(object):
    """
    Stores an ID to apply later
    """
    def __init__(self,actionOptions):
        self._id = actionOptions.pop(0)
    
    def run(self,itemStack):
        itemStack["id"].value = self._id
    
    def str(self):
        return u'* Change ID to "' + self._id + u'"'

class changeCount(object):
    """
    Stores a count action to apply later
    """
    def __init__(self,actionOptions):
        self._operation = actionOptions.pop(0)
        self._value = actionOptions.pop(0)
    
    def run(self,itemStack):
        if self._operation == "=":
            itemStack["Count"].value = self._value
            return
        if self._operation == "+":
            itemStack["Count"].value += self._value
            return
        if self._operation == "-":
            itemStack["Count"].value -= self._value
            return
        if self._operation == "*":
            itemStack["Count"].value *= self._value
            return
        if self._operation == "/":
            itemStack["Count"].value /= self._value
            return
        if self._operation == "%":
            itemStack["Count"].value %= self._value
            return
        if self._operation == "max":
            newVal = min(itemStack["Count"].value,self._value)
            itemStack["Count"].value = newVal
            return
        if self._operation == "min":
            newVal = max(itemStack["Count"].value,self._value)
            itemStack["Count"].value = newVal
            return
    
    def str(self):
        if self._operation == "=":
            return u'* Set count to ' + self._value
        if self._operation == "+":
            return u'* Add ' + self._value + u' to count'
        if self._operation == "-":
            return u'* Subtract ' + self._value + u' from count'
        if self._operation == "*":
            return u'* Multiply count by ' + self._value
        if self._operation == "/":
            return u'* Divide count by ' + self._value
        if self._operation == "%":
            return u'* Set count to itself modulo ' + self._value
        if self._operation == "max":
            return u'* Prevent count from being greater than ' + self._value
        if self._operation == "min":
            return u'* Prevent count from being less than ' + self._value

class changeDamage(object):
    """
    Stores a damage action to apply later
    """
    def __init__(self,actionOptions):
        self._operation = actionOptions.pop(0)
        self._value = actionOptions.pop(0)
    
    def run(self,itemStack):
        if self._operation == "=":
            itemStack["Damage"].value = self._value
            return
        if self._operation == "+":
            itemStack["Damage"].value += self._value
            return
        if self._operation == "-":
            itemStack["Damage"].value -= self._value
            return
        if self._operation == "*":
            itemStack["Damage"].value *= self._value
            return
        if self._operation == "/":
            itemStack["Damage"].value /= self._value
            return
        if self._operation == "%":
            itemStack["Damage"].value %= self._value
            return
        if self._operation == "max":
            newVal = min(itemStack["Damage"].value,self._value)
            itemStack["Damage"].value = newVal
            return
        if self._operation == "min":
            newVal = max(itemStack["Damage"].value,self._value)
            itemStack["Damage"].value = newVal
            return
    
    def str(self):
        if self._operation == "=":
            return u'* Set damage to ' + self._value
        if self._operation == "+":
            return u'* Add ' + self._value + u' to damage'
        if self._operation == "-":
            return u'* Subtract ' + self._value + u' from damage'
        if self._operation == "*":
            return u'* Multiply damage by ' + self._value
        if self._operation == "/":
            return u'* Divide damage by ' + self._value
        if self._operation == "%":
            return u'* Set damage to itself modulo ' + self._value
        if self._operation == "max":
            return u'* Prevent damage from being greater than ' + self._value
        if self._operation == "min":
            return u'* Prevent damage from being less than ' + self._value

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
            self._value = nbt.json_to_tag( actionOptions.pop(0) )
    
    def run(self,itemStack):
        if (
                (self._operation == "clear")
                or (self._operation == "replace")
        ) and ("tag" in itemStack):
            itemStack.pop("tag")
        if (
                (self._operation == "set")
                or (self._operation == "replace")
        ):
            if "tag" not in itemStack:
                itemStack["tag"] = nbt.TAG_Compound()
            itemStack["tag"].update(self._value)
    
    def str(self):
        if self._operation == "clear":
            return u'* Remove NBT'
        if self._operation == "set":
            return u'* Add ' + self._value.json + u' to existing NBT'
        if self._operation == "replace":
            return u'* Replace NBT with u' + self._value.json

"""
NYI
class changeScoreboard(object):
    ""
    Stores a scoreboard action to apply later
    ""
    def __init__(self,actionOptions):
        self._operation = actionOptions.pop(0)
        self._value = actionOptions.pop(0)
    
    def run(self,itemStack):
        if self._operation == "=":
            itemStack["Damage"].value = self._value
            return
        if self._operation == "+":
            itemStack["Damage"].value += self._value
            return
        if self._operation == "-":
            itemStack["Damage"].value -= self._value
            return
        if self._operation == "*":
            itemStack["Damage"].value *= self._value
            return
        if self._operation == "/":
            itemStack["Damage"].value /= self._value
            return
        if self._operation == "%":
            itemStack["Damage"].value %= self._value
            return
        if self._operation == "max":
            newVal = min(itemStack["Damage"].value,self._value)
            itemStack["Damage"].value = newVal
            return
        if self._operation == "min":
            newVal = max(itemStack["Damage"].value,self._value)
            itemStack["Damage"].value = newVal
            return
"""

class changeRemove(object):
    """
    Stores a stack removal action to apply later
    """
    def run(self,itemStack):
        itemStack["Count"].value = 0
    
    def str(self):
        return u'* Set item count to 0; the server will delete it on load'


