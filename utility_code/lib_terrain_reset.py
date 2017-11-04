#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).

This does so as directly as possible while providing many features.

Fair warning, some of the optimization is done by removing error handling.
Python will tell you if/when the script crashes.
If it's going to crash, it won't damage the original worlds.
Just fix what broke, and run again.
"""

import os
import sys
import shutil

##### MAYBE NEW
import pymclevel
from pymclevel.box import BoundingBox, Vector

from lib_monumenta_common import fillBoxes, copyBoxes, copyFolder, copyFolders

import lib_item_replace
import item_replace_list

def terrainReset(config):
    localMainFolder = config["localMainFolder"]
    localBuildFolder = config["localBuildFolder"]
    localDstFolder = config["localDstFolder"]
    coordinatesToCopy = config["coordinatesToCopy"]
    coordinatesToFill = config["coordinatesToFill"]
    coordinatesDebug = config["coordinatesDebug"]
    itemReplaceList = item_replace_list.itemReplacements
    blockReplaceList = item_replace_list.blockReplacements
    safetyTpLocation = config["safetyTpLocation"]

    # Fail if build or main folders don't exist
    if not os.path.isdir(localMainFolder):
        sys.exit("Main world folder does not exist.")
    if not os.path.isdir(localBuildFolder):
        sys.exit("Build world folder does not exist.")

    print "Copying build world as base..."
    copyFolder(localBuildFolder, localDstFolder)

    print "Compiling item replacement list..."
    compiledItemReplacementList = lib_item_replace.allReplacements(itemReplaceList)

    # Copy various bits of player data from the main world
    print "Copying player data files from main world..."
    copyFolders(localMainFolder, localDstFolder, ["advancements/", "playerdata/", "stats/",])
    print "Copying player maps and scoreboard from main world..."
    copyFolders(localMainFolder, localDstFolder, ["data/",])

    # Note this part about advancements, functions, and loot tables is now done by gen_server_config (via symlinks)
    #print "Copying updated advancements, functions, and loot tables from build world..."
    #copyFolders(localBuildFolder, localDstFolder, ["data/advancements/", "data/functions/", "data/loot_tables/",])

    print "Handling item replacements for players..."
    lib_item_replace.replaceItemsOnPlayers(localDstFolder, compiledItemReplacementList)

    print "Opening old play World..."
    srcWorld = mclevel.loadWorld(localMainFolder)

    print "Opening Destination World..."
    dstWorld = mclevel.loadWorld(localDstFolder)

    print "Filling selected regions with specified blocks..."
    fillBoxes(dstWorld, coordinatesToFill)

    if (coordinatesDebug == False):
        print "Copying needed terrain from the main world..."
        copyBoxes(srcWorld, dstWorld, coordinatesToCopy, blockReplaceList, compiledItemReplacementList)
    else:
        print "DEBUG: Filling regions instead of copying them!"
        fillBoxes(dstWorld, coordinatesToCopy)

    print "Resetting difficulty..."
    resetRegionalDifficulty(dstWorld)

    print "Generating lights (should only happen on block changes!)...."
    dstWorld.generateLights()
    print "Saving...."
    dstWorld.saveInPlace()

    print "Moving players..."
    movePlayers(localDstFolder, safetyTpLocation)

    shutil.rmtree(localDstFolder+"##MCEDIT.TEMP##", ignore_errors=True)
    try:
        os.remove(localDstFolder+"mcedit_waypoints.dat")
    except Exception as e:
        pass

    print "Done!"

