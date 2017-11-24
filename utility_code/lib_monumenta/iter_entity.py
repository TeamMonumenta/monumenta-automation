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

################################################################################
# Entity iterator code

# Needed for items containing mobs or block entities
itemTagNames = [
    "HandItems",
    "ArmorItems",
    "ArmorItem",
    "SaddleItem",
    "Items",
    "Item",
    "Inventory",
    "EnderItems",
]

class IterEntities(object):
    """
    A class used to iterate over entities and block entities.
    For each entity found, calls onMatch like so:

    ****
    onMatch(onMatchArgs,entityDetails)
    ****

    Entity details are provided as a dictionary like so:
    {
        "player file":<None or a player.dat file name>,
        "root entity":<True or entity's NBT>,
        "entity":<entity's NBT>,
        "is block entity":<True/False/"unknown">
    }

    Where a root entity is true for players, entities directly in worlds,
    and entities directly in schematics; this is the root entity instead for
    entities within items or commands (when commands are implemented)

    searchArgs is a list of strings, and may include:

    Which entities to pass to function (defaults to both)
    * "block entities" - search block entities
    * "entities" - search within entities

    Which entities to search inside of (root entities always searched)
    * "search item entities" - search for entities inside items
    * "search spawners" - search within spawners
    """
    def __init__(self,searchArgs=[],onMatch=None,onMatchArgs=None):
        if not callable(onMatch):
            print "!!! onMatch must be a callable function to run on matching entities"
            # Force a stack trace to help find the right line
            1/0

        if (
            "entities" not in searchArgs and
            "block entities" not in searchArgs
        ):
            searchArgs.append("entities")
            searchArgs.append("block entities")
        self._searchArgs = searchArgs
        self._onMatch = onMatch
        self._onMatchArgs = onMatchArgs

        self._entityList = []
        self._entityDetails = {
            "player file":None,
            "root entity":True,
            "entity":None,
            "is block entity":None
        }

    def InWorld(self,world):
        for cx,cz in world.allChunks:
            aChunk = world.getChunk(cx,cz)

            if "Level" not in aChunk.root_tag:
                # This chunk is invalid, skip it!
                # It has no data.
                continue

            # shallow copy this list, or we won't have entities in the world.
            # Also, we don't need a TAG_List; a normal list is fine.
            self._entityList = []
            for entity in aChunk.root_tag["Level"]["Entities"]:
                self._entityList.append(entity)
            for entity in aChunk.root_tag["Level"]["TileEntities"]:
                self._entityList.append(entity)
            self._OnEntities()

            # TODO move this into onMatch instead
            aChunk.chunkChanged(False) # needsLighting=False

    def InSchematic(self,schematic):
        # shallow copy this list, or we won't have entities in the schematic.
        # Also, we don't need a TAG_List; a normal list is fine.
        self._entityList = []
        for entity in schematic.Entities:
            self._entityList.append(entity)
        for entity in schematic.TileEntities:
            self._entityList.append(entity)
        self._OnEntities()

    def OnPlayers(self,worldDir):
        for playerFile in os.listdir(worldDir+"playerdata"):
            playerFile = worldDir+"playerdata/" + playerFile
            self._entityDetails["player file"] = playerFile
            player = nbt.load(playerFile)
            # In this case, we can easily copy the only entity to a list.
            self._entityList = [player]
            self._OnEntities()
            player.save(playerFile)
        self._entityDetails["player file"]=None

    def _OnEntities(self):
        while len(self._entityList) > 0:
            entity = self._entityList.pop()
            self._entityDetails["entity"] = entity
            if (
                ("Pos" in entity) or
                ("x" in entity)
            ):
                # The entity exists in the world/schematic directly,
                # not inside something.
                self._entityDetails["root entity"] = True

                if (
                    "block entities" in self._searchArgs and
                    "x" in entity
                ):
                    self._entityDetails["is block entity"] = True
                    self._onMatch(self._onMatchArgs,self._entityDetails)

                if (
                    "entities" in self._searchArgs and
                    "Pos" in entity
                ):
                    self._entityDetails["is block entity"] = False
                    self._onMatch(self._onMatchArgs,self._entityDetails)

            else:
                # The entity is inside of something else, and doesn't
                # have a Pos, x, y, or z tag - a list of (block)entity
                # IDs might be the only way to tell which is which.
                if "id" in entity:
                    # Child entity
                    self._entityDetails["is block entity"] = False
                    self._onMatch(self._onMatchArgs,self._entityDetails)
                else:
                    # Child block entity (id inferred from parent item)
                    self._entityDetails["is block entity"] = True
                    self._onMatch(self._onMatchArgs,self._entityDetails)

            # Handle villager trades
            if (
                ("Offers" in entity) and
                ("Recipes" in entity["Offers"])
            ):
                for trade in entity["Offers"]["Recipes"]:
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

            if "search item entities" in self._searchArgs:
                for containerTagName in itemTagNames:
                    if containerTagName in entity:
                        self._InStackList(entity[containerTagName])

            if "search spawners" in self._searchArgs:
                if "SpawnData" in entity:
                    self._entityList.append(entity["SpawnData"])
                if "SpawnPotentials" in entity:
                    for potential in entity["SpawnPotentials"]:
                        self._entityList.append(potential["Entity"])

            self._entityDetails["root entity"] = entity
        self._entityDetails["root entity"] = None

    def _InStackList(self,itemStackList):
        if type(itemStackList) is nbt.TAG_List:
            for itemStack in itemStackList:
                self._InStack(itemStack)
        elif type(itemStackList) is nbt.TAG_Compound:
            self._InStack(itemStackList)

    def _InStack(self,itemStack):
        """
        Iterate over entities inside of items if applicable.
        Handle modifications to items before running this.
        """
        if (
            # Search arguments say not to search inside items
            "search item entities" not in self._searchArgs or
            # Invalid itemStack type
            type(itemStack) != nbt.TAG_Compound or
            # No item in this slot (which is valid for mob armor/hand items)
            "id" not in itemStack or
            # Item doesn't contain entity data
            "tag" not in itemStack
        ):
            return
        if "BlockEntityTag" in itemStack["tag"]:
            # This is enough info to loop over blocks with
            # NBT held as items, like shulker boxes.
            blockEntity = itemStack["tag"]["BlockEntityTag"]
            self._entityList.append(blockEntity)
        if "EntityTag" in itemStack["tag"]:
            # Handles spawn eggs, and potentially other cases.
            entity = itemStack["tag"]["EntityTag"]
            self._entityList.append(entity)

