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
    if "id" not in itemStack:
        # No item in this slot (mob armor/hand items)
        return
    if itemStack["id"].value in shulkerIDNames:
        shulkerBoxContents = itemStack["tag"]["BlockEntityTag"]["Items"]
        # TODO This recursive method should be changed to iterative!
        replaceItemStacks(shulkerBoxContents,replacementList)
    elif itemStack["id"].value == u"minecraft:spawn_egg":
        spawnEggEntity = itemStack["tag"]["EntityTag"]
        # TODO This recursive method should be changed to iterative!
        replaceItemsOnEntity(spawnEggEntity,replacementList)
    replacementList.run(itemStack)
    
def replaceItemStacks(itemStackContainer,replacementList):
    if type(itemStackContainer) is nbt.TAG_List:
        for itemStack in itemStackContainer:
            replaceItemStack(itemStack,replacementList)
    else:
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
            replaceItemStacks(entity[containerTagName],replacementList)

def replaceItemsInWorld(world,replacementList):
    for cx,cz in world.allChunks:
        aChunk = world.getChunk(cx,cz)
        
        if len(aChunk.root_tag) == 0:
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
        self._replacements = []
        for aReplacement in replacementList:
            self._replacements.append(replacement(aReplacement))
    
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
        
        self.matches = []
        if "id" in matches:
            self.matches.append(matchID(matches))
        if "damage" in matches:
            self.matches.append(matchDamage(matches))
        if "nbt" in matches:
            self.matches.append(matchNBT(matches))
        if "count" in matches:
            self.matches.append(matchCount(matches))
        if len(self.matches) == 0:
            self.matches.append(matchNone())
        
        self.actions = []
        while len(actions):
            action = actions.pop(0)
            if action == "id":
                self.actions.append( changeID(actions) )
            if action == "count":
                self.actions.append( changeCount(actions) )
            if action == "damage":
                self.actions.append( changeDamage(actions) )
            if action == "nbt":
                self.actions.append( changeNBT(actions) )
            if action == "remove":
                self.actions.append( changeRemove() )
    
    def run(self,itemStack):
        if all(rule == itemStack for rule in self.matches):
            for action in self.actions:
                action.run(itemStack)

# Matching optimizers

class matchNone(object):
    """
    This is a special case to never match anything;
    used for invalid item replacements
    """
    def __eq__(self,itemStack):
        return False

class matchID(object):
    """
    This stores an ID to match later
    """
    def __init__(self,matchOptions):
        self._id = matchOptions["id"]
    
    def __eq__(self,itemStack):
        return self._id == itemStack["id"].value

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
        return itemStack["Damage"].value in self._damage

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
        return itemStack["Count"].value in self._count


# Action optimizers

class changeID(object):
    """
    Stores an ID to apply later
    """
    def __init__(self,actionOptions):
        self._id = actionOptions.pop(0)
    
    def run(self,itemStack):
        itemStack["id"].value = self._id

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


