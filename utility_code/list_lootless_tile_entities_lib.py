#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This lists the tile entities that lack
a loot table within a box, filtering by type.
"""
# Required libraries have links where not part of a standard Python install.
import os
import shutil

# These are expected in your site-packages folder, see:
# https://stackoverflow.com/questions/31384639/what-is-pythons-site-packages-directory
import mclevel # from https://github.com/mcedit/pymclevel
from mclevel import mclevelbase
from mclevel import materials
from mclevel.box import BoundingBox, Vector
from mclevel import nbt

from monumenta_common import getBoxSize
from monumenta_common import getBoxPos
from monumenta_common import getBox

################################################################################
# Function definitions

def containsIgnoredContents(aTileEntity):
    for item in aTileEntity["Items"]:
        try:
            for lore in item["tag"]["display"]["Lore"]:
                for loreIgnore in contentsLoreToIgnore:
                    if loreIgnore in lore.value:
                        if debugPrints:
                            print "{0} at ({1},{2},{3}) contains item with lore '{4}' matching '{5}'".format(aTileEntity["id"].value,
                                    aTileEntity["x"].value,
                                    aTileEntity["y"].value,
                                    aTileEntity["z"].value,
                                    lore.value.encode('utf-8'),
                                    loreIgnore)
                        return True
        except UnicodeEncodeError:
            print "THIS SHOULDN't HAPPEN"
            continue
        except:
            continue
    return False

def isWhitelisted(aTileEntity, chestWhitelist):
    x = aTileEntity["x"].value
    y = aTileEntity["y"].value
    z = aTileEntity["z"].value

    if (x,y,z) in chestWhitelist:
        return True
    return False


def hasLootTable(aTileEntity):
    emptyLootTables = ("", "empty", "minecraft:", "minecraft:empty")
    if "LootTable" not in aTileEntity:
        return False
    elif aTileEntity["LootTable"].value in emptyLootTables:
        return False
    return True

def hasLootTableSeed(aTileEntity):
    if "LootTableSeed" not in aTileEntity:
        return False
    elif aTileEntity["LootTableSeed"].value == 0:
        return False
    return True

################################################################################
# Functions that display stuff while they work

def run(worldFolder, coordinatesToScan, tileEntitiesToCheck, chestWhitelist):
    print "Beginning scan..."
    world = mclevel.loadWorld(worldFolder)

    # Build tile ID list, adding default namespace if needed
    tileIDList = []
    for tileID in tileEntitiesToCheck:
        if ":" in tileID:
            tileIDList.append(tileID)
        else:
            tileIDList.append("minecraft:"+tileID)

    scanNum = 1
    scanMax = len(coordinatesToScan)

    allChunks = set(world.allChunks)

    # This is fine. The warning is known and can be ignored.
    # warnings.filterwarnings("ignore", category=numpy.VisibleDeprecationWarning)

    for aScanBox in coordinatesToScan:
        print "[{0}/{1}] Scaning {2}...".format(scanNum,scanMax,aScanBox[0])
        lootless = []

        scanBox = getBox(aScanBox)

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
                    if aTileEntity["id"].value in tileIDList:

                        # Detect missing loot table
                        if ((not hasLootTable(aTileEntity)) and
                            (not containsIgnoredContents(aTileEntity)) and
                            (not isWhitelisted(aTileEntity, chestWhitelist))):
                            lootless.append(aTileEntity)

                        # Detect fixed loot table seeds
                        elif (hasLootTableSeed(aTileEntity) and
                              (not containsIgnoredContents(aTileEntity)) and
                              (not isWhitelisted(aTileEntity, chestWhitelist))):
                            lootless.append(aTileEntity)

                        elif "LootTableSeed" in aTileEntity:
                            print aTileEntity
            except:
                #print "Got exception in chunk (" + str(cx) + "," + str(cz) + ")"
                continue

        print "{0} tile entities found without a loot table:".format(len(lootless))
        for aTileEntity in lootless:
            tileEntityID = aTileEntity["id"].value
            x = aTileEntity["x"].value
            y = aTileEntity["y"].value
            z = aTileEntity["z"].value
            theProblem = ""
            if not hasLootTable(aTileEntity):
                theProblem = "has no loot table set."
            elif hasLootTableSeed(aTileEntity):
                theProblem = "has a fixed loot table seed."
            print "{0} {1} {2} - {3} {4}".format(x, y, z, tileEntityID, theProblem)

        print ""
        scanNum+=1


