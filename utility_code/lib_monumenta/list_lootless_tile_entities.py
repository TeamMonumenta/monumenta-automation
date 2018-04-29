#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
This lists the tile entities that lack
a loot table within a box, filtering by type.
"""

from __future__ import print_function
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

################################################################################
# Function definitions

def containsNoIgnoredContents(aTileEntity, contentsLoreToIgnore, debugPrints):
    if (
        contentsLoreToIgnore is None or
        len(contentsLoreToIgnore) == 0
    ):
        return True
    for item in aTileEntity["Items"]:
        try:
            if (
                "tag" not in item or
                "display" not in item["tag"] or
                "Lore" not in item["tag"]["display"]
            ):
                # This also skips the occasional empty item, as in {Slot:5b} or {}
                continue
            for lore in item["tag"]["display"]["Lore"]:
                for loreIgnore in contentsLoreToIgnore:
                    if loreIgnore in lore.value:
                        if debugPrints:
                            print("{0} at ({1},{2},{3}) contains item with lore '{4}' matching '{5}'".format(aTileEntity["id"].value,
                                    aTileEntity["x"].value,
                                    aTileEntity["y"].value,
                                    aTileEntity["z"].value,
                                    lore.value.encode('utf-8'),
                                    loreIgnore))
                        return False
        except UnicodeEncodeError:
            print("UnicodeEncodeError in containsNoIgnoredContents")
            continue
        except:
            if debugPrints:
                print("Caught general exception in containsNoIgnoredContents")
            continue
    return True

def isNotWhitelisted(aTileEntity, chestWhitelist):
    x = aTileEntity["x"].value
    y = aTileEntity["y"].value
    z = aTileEntity["z"].value

    if chestWhitelist is None or (x,y,z) in chestWhitelist:
        return False
    return True


def hasNoLootTable(aTileEntity):
    emptyLootTables = ("", "empty", "minecraft:", "minecraft:empty")
    if "LootTable" not in aTileEntity:
        return True
    elif aTileEntity["LootTable"].value in emptyLootTables:
        return True
    return False

def hasLootTableSeed(aTileEntity):
    if "LootTableSeed" not in aTileEntity:
        return False
    elif aTileEntity["LootTableSeed"].value == 0:
        return False
    return True

def listLootlessTileEntities(world, scanBox, tileEntitiesToCheck, contentsLoreToIgnore, chestWhitelist, areaName, debugPrints=False):
    lootless = []

    # Build tile ID list, adding default namespace if needed
    tileIDList = []
    for tileID in tileEntitiesToCheck:
        if ":" in tileID:
            tileIDList.append(tileID)
        else:
            tileIDList.append("minecraft:"+tileID)

    # This is needed to avoid errors when a box contains chunks that do not exist
    # This comment is to remind me of that problem
    allChunks = set(world.allChunks)

    # The function world.getTileEntitiesInBox() does not work.
    # Working around it, since it works for chunks but not worlds.
    selectedChunks = set(scanBox.chunkPositions)
    chunksToScan = list(selectedChunks.intersection(allChunks))
    for cx,cz in chunksToScan:
        try:
            # Get and loop through entities within chunk and box
            aChunk = world.getChunk(cx,cz)
            newTileEntities = aChunk.getTileEntitiesInBox(scanBox)
            for aTileEntity in newTileEntities:

                # Check if tileEntity is being scanned
                if (
                    aTileEntity["id"].value in tileIDList and
                    isNotWhitelisted(aTileEntity, chestWhitelist) and
                    containsNoIgnoredContents(aTileEntity, contentsLoreToIgnore, debugPrints)
                ):
                    # Detect missing loot table
                    if hasNoLootTable(aTileEntity):
                        lootless.append(aTileEntity)

                    # Detect fixed loot table seeds
                    elif hasLootTableSeed(aTileEntity):
                        lootless.append(aTileEntity)

                    elif "LootTableSeed" in aTileEntity:
                        print(aTileEntity)
        except KeyError:
            if debugPrints:
                print("Got KeyError exception in chunk (" + str(cx) + "," + str(cz) + ")")
            continue

    eprint("    {0} tile entities found without a loot table in {1}:".format(len(lootless),areaName))
    for aTileEntity in lootless:
        tileEntityID = aTileEntity["id"].value
        x = aTileEntity["x"].value
        y = aTileEntity["y"].value
        z = aTileEntity["z"].value
        theProblem = ""
        if hasNoLootTable(aTileEntity):
            theProblem = "has no loot table set."
        elif hasLootTableSeed(aTileEntity):
            theProblem = "has a fixed loot table seed."
        eprint("      {0} {1} {2}".format(x, y, z))

    eprint("")

