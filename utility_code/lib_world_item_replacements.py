#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This takes a main world (play area), handles item
replacement, and saves to dstWorld (destination).

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

from lib_monumenta_common import fillBoxes, copyBoxes, copyFolder, copyFolders, replaceGlobally

import lib_item_replace
import item_replace_list

def resetItemsInWorld(config):
    localMainFolder = config["localMainFolder"]
    localDstFolder = config["localDstFolder"]
    coordinatesToFill = config["coordinatesToFill"]
    blockReplaceList = config["blockReplaceList"]
    itemReplaceList = item_replace_list.itemReplacements
    blockReplaceList = item_replace_list.blockReplacements
    #safetyTpLocation = config["safetyTpLocation"]

    # Fail if build or main folders don't exist
    if not os.path.isdir(localMainFolder):
        sys.exit("Main world folder does not exist.")
    if not os.path.isdir(localBuildFolder):
        sys.exit("Build world folder does not exist.")

    print "Copying play world to dst as base..."
    copyFolder(localMainFolder, localDstFolder)

    print "Compiling item replacement list..."
    compiledItemReplacementList = lib_item_replace.allReplacements(item_replace_list.itemReplacements)

    print "Handling item replacements for players..."
    lib_item_replace.replaceItemsOnPlayers(localDstFolder, compiledItemReplacementList)

    print "Opening Destination World..."
    dstWorld = mclevel.loadWorld(localDstFolder)

    print "Replacing blocks where needed..."
    replaceGlobally(dstWorld, blockReplaceList)
    
    print "Filling selected regions with specified blocks..."
    fillBoxes(dstWorld, coordinatesToFill)

    print "Resetting difficulty..."
    resetRegionalDifficulty(dstWorld)

    print "Generating lights (should only happen on block changes!)...."
    dstWorld.generateLights()
    print "Saving...."
    dstWorld.saveInPlace()

    # Players should be safe in plot worlds
    #print "Moving players..."
    #movePlayers(localDstFolder, safetyTpLocation)

    shutil.rmtree(localDstFolder+"##MCEDIT.TEMP##", ignore_errors=True)
    try:
        os.remove(localDstFolder+"mcedit_waypoints.dat")
    except Exception as e:
        pass

    print "Done!"

