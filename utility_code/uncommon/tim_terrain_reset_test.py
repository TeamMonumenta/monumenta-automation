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
import mclevel
import terrain_reset_lib
import lib_item_replace
# import item_replace_list # This is where the item replacements are kept

from monumenta_common import getBoxName
from monumenta_common import getBoxSize
from monumenta_common import getBoxPos
from monumenta_common import getBox
from monumenta_common import getBoxMaterial
from monumenta_common import getBoxMaterialName

################################################################################
# Config section

################################################################################
# Testing sandbox

config = {
    "localMainFolder":"/home/tim/.minecraft/saves/main/",
    "localBuildFolder":"/home/tim/.minecraft/saves/build/",
    "localDstFolder":"/home/tim/.minecraft/saves/dst/",
    "safetyTpLocation":(149.0, 76.0, 133.0, 0.0, 0.0),
    "coordinatesToCopy":(
        ("hut1",           (      153, 68,      104), (      156, 73,      108), True,  (0,0), "air"),
        ("hut2fence",      (      159, 64,      112), (      163, 69,      116), True,  (0,0), "air"),
        ("hut3",           (      150, 70,      112), (      154, 75,      115), True,  (0,0), "air"),
        ("church",         (      138, 73,      113), (      146, 84,      117), False, (0,0), "air"),
        ("hut4",           (      113, 62,      126), (      116, 68,      130), True,  (0,0), "air"),
        ("farm1s",         (      120, 62,      122), (      126, 64,      130), True,  (0,0), "air"),
        ("hut5",           (      133, 70,      126), (      136, 74,      130), True,  (0,0), "air"),
        ("hut6",           (      155, 70,      126), (      158, 74,      130), True,  (0,0), "air"),
        ("farm2l",         (      164, 67,      122), (      176, 69,      130), True,  (0,0), "air"),
        ("well",           (      146, 58,      130), (      151, 73,      135), True,  (0,0), "air"),
        ("hut7",           (      111, 61,      134), (      115, 67,      138), True,  (0,0), "air"),
        ("farm3l",         (      118, 62,      134), (      130, 64,      142), True,  (0,0), "air"),
        ("hut8TShape",     (      136, 63,      136), (      147, 73,      144), True,  (0,0), "air"),
        ("hut9fence",      (      153, 68,      134), (      157, 74,      138), True,  (0,0), "air"),
        ("hut10fence",     (      150, 64,      139), (      154, 70,      143), True,  (0,0), "air"),
        ("farm4l",         (      164, 68,      134), (      176, 70,      142), True,  (0,0), "air"),
        ("farm5s",         (      150, 63,      146), (      158, 65,      152), True,  (0,0), "air"),
        ("farm6l",         (      138, 62,      153), (      146, 64,      165), True,  (0,0), "air"),
    ),

    "coordinatesToFill":(
        # ("a unique name",        (lowerCoordinate),  (upperCoordinate), replaceBlocks, ( id, dmg), "block name (comment)"),
        ("Meh block",     (       146, 72,      110), (      146, 72,      110), True,  (0,0), "air"),
    ),

    # List of blocks to not copy over for the regions above
    "blockReplaceList":(
        ("minecraft:iron_block", "air"),
        ("minecraft:iron_ore", "air"),
        #("minecraft:gold_block", "air"),
        #("minecraft:gold_ore", "air"),
        ("minecraft:diamond_block", "air"),
        ("minecraft:diamond_ore", "air"),
        #("minecraft:emerald_block", "air"),
        #("minecraft:emerald_ore", "air"),

        ("minecraft:beacon", "air"),

        # Not sure about this section
        #("enchanting_Table", "air"),
        #("quartz_ore", "air"),
        #("hopper", "air"),

        # anvils
        ((145,0), "air"),
        ((145,1), "air"),
        ((145,2), "air"),
        ((145,3), "air"),
        ((145,4), "air"),
        ((145,5), "air"),
        ((145,6), "air"),
        ((145,7), "air"),
        ((145,8), "air"),
        ((145,9), "air"),
        ((145,10), "air"),
        ((145,11), "air"),
    )
}

################################################################################
# Testing sandbox

def fillRegions(config):
    """ Fill all regions with specified blocks to demonstrate coordinates """

    localBuildFolder = config["localBuildFolder"]
    localDstFolder = config["localDstFolder"]
    coordinatesToCopy = config["coordinatesToCopy"]

    # Delete the dst world for a clean slate to start from
    shutil.rmtree(localDstFolder,True)

    # Copy the build world to the dst world
    shutil.copytree(localBuildFolder,localDstFolder)

    dstWorld = mclevel.loadWorld(localDstFolder)

    # Fill the selected regions for debugging reasons
    for fillRegion in coordinatesToCopy:
        boxName = getBoxName(fillRegion)
        boxMaterial = getBoxMaterial(fillRegion)
        boxMaterialName = getBoxMaterialName(fillRegion)
        print "Filling " + boxName + " with " + boxMaterialName + "..."
        box = getBox(fillRegion)
        block = dstWorld.materials[boxMaterial]
        dstWorld.fillBlocks(box, block)

    print "Saving...."
    dstWorld.generateLights()
    dstWorld.saveInPlace()

# This shows where the selected regions are, as your old script does.
#terrain_reset_lib.fillRegions(config)

################################################################################
# Main Code

# This does the move itself - copy areas, entities, scoreboard, etc.
terrain_reset_lib.terrainReset(config)


