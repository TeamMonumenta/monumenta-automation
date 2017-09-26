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
import item_replace_lib
# import item_replace_list # This is where the item replacements are kept

from monumenta_common import getBoxName
from monumenta_common import getBoxSize
from monumenta_common import getBoxPos
from monumenta_common import getBox
from monumenta_common import getBoxMaterial
from monumenta_common import getBoxMaterialName

################################################################################
# Config section

config = {
    # Dst is the destination world, which gets overwritten by the build world.
    # Then, data from the main world replaces the relevant parts of the dst world.
    # Please note that no special care need be taken with whitespace in filenames.
    "localMainFolder":"/home/rock/tmp/BETA_Project_Epic/",
    "localBuildFolder":"/home/rock/tmp/BUILD_Project_Epic/",
    "localDstFolder":"/home/rock/tmp/RESET_Project_Epic/",

    # No 0.5 offset here, add it yourself if you like.
    # (x,y,z,ry,rx)
    "safetyTpLocation":(-1456, 240, -1498, 270.0, 0.0),

    # These get filled with the block specified - ie, the magic block with air.
    # Disable with replaceBlocks or comment it out
    "coordinatesToFill":(
        # ("a unique name",        (lowerCoordinate),  (upperCoordinate), replaceBlocks, ( id, dmg), "block name (comment)"),
        ("Magic Block",            (-1441,   2,-1441), (-1441,   2,-1441), True,  (  0, 0 ), "air"),
    ),

    "coordinatesToCopy":(
        # ("a unique name",        (lowerCoordinate),  (upperCoordinate), replaceBlocks, ( id, dmg), "block name (comment)"),
        ("Apartments_buying_room", ( -809,  99,   47), ( -874,  96,    4), False, (  41, 0 ), "gold"),
        ("Apartments_units",       ( -817, 113,   87), ( -859, 164,   16), False, (  41, 0 ), "gold"),
        ("Plot_Pressure_Plates",   ( -719, 106, -118), ( -665, 106,  -74), False, (  41, 0 ), "gold"),
        ("Guild_Room",             ( -800, 109,  -75), ( -758, 104, -102), False, (  41, 0 ), "gold"),
        ("Section_1",              (-1130,   0, -267), ( -897, 255,  318), True,  (  41, 0 ), "gold"),
        ("Section_2",              ( -896,   0,  208), ( -512, 255,  318), True,  (  57, 0 ), "diamond"),
        ("Section_3",              ( -896,   0,  207), ( -788, 255,  119), True,  (  42, 0 ), "iron"),
        ("Section_4",              ( -896,   0, -267), ( -825, 255,  -28), True,  (  22, 0 ), "lapis"),
        ("Section_5",              ( -512,   0,  207), ( -640, 255, -273), True,  (  24, 0 ), "sandstone"),
        ("Section_6",              ( -824,   0, -169), ( -641, 255, -272), True,  ( 152, 0 ), "redstone"),
        ("Section_7",              ( -641,   0, -168), ( -677, 255, -132), True,  ( 155, 0 ), "quartz"),
        ("Section_8",              ( -774,   0, -168), ( -813, 255, -150), True,  (  17, 14), "birch wood"),
        ("Section_9",              ( -641,   0,  -25), ( -655, 255,  -52), True,  (  17, 15), "jungle wood"),
        ("Section_10",             ( -680,   0,  183), ( -641, 255,  207), True,  (  19, 0 ), "sponge"),
        ("Section_11",             ( -668,   0,  -14), ( -641, 255,   25), True,  (   1, 1 ), "granite"),
    ),

    # List of blocks to not copy over for the regions above
    "blockReplaceList":(
        ("minecraft:iron_block", "air"),
        ("minecraft:iron_ore", "air"),
        #("minecraft:gold_block", "air"), # probably fine
        #("minecraft:gold_ore", "air"),
        ("minecraft:diamond_block", "air"),
        ("minecraft:diamond_ore", "air"),
        #("minecraft:emerald_block", "air"), # probably fine
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

# Remove the magic block when done



