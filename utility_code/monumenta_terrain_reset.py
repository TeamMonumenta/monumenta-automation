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
    "localMainFolder":"/home/rock/tmp/PRE_RESET/region_1/Project_Epic-region_1/",
    "localBuildFolder":"/home/rock/project_epic/region_1/Project_Epic-region_1/",
    "localDstFolder":"/home/rock/tmp/POST_RESET/region_1/Project_Epic-region_1/",

    # No 0.5 offset here, add it yourself if you like.
    # (x,y,z,ry,rx)
    "safetyTpLocation":(-1450, 241, -1498, 270.0, 0.0),

    # These get filled with the block specified - ie, the magic block with air.
    # Disable with replaceBlocks or comment it out
    "coordinatesToFill":(
        # ("a unique name",        (lowerCoordinate),  (upperCoordinate), replaceBlocks, ( id, dmg), "block name (comment)"),
        ("Magic Block",            (-1441,   2,-1441), (-1441,   2,-1441), True,  (  0, 0 ), "air"),
    ),

    "coordinatesToCopy":(
        # ("a unique name",        (lowerCoordinate),  (upperCoordinate), replaceBlocks, ( id, dmg), "block name (comment)"),
        ("Apartments_100",         ( -874,  99,   44), (-809, 96,  44),   False, (  41, 0 ), "gold"),
        ("Apartments_200",         ( -874,  99,   36), (-809, 96,  36),   False, (  41, 0 ), "gold"),
        ("Apartments_300",         ( -874,  99,   31), (-809, 96,  31),   False, (  41, 0 ), "gold"),
        ("Apartments_400",         ( -874,  99,   23), (-809, 96,  23),   False, (  41, 0 ), "gold"),
        ("Apartments_500",         ( -864,  99,   23), (-813, 96,  23),   False, (  41, 0 ), "gold"),
        ("Apartments_600",         ( -864,  99,   23), (-813, 96,  23),   False, (  41, 0 ), "gold"),
        ("Apartments_700_800",     ( -874,  99,   18), (-809, 96,  18),   False, (  41, 0 ), "gold"),
        ("Apartments_units",       ( -817, 113,   87), (-859, 164, 16),   False, (  41, 0 ), "gold"),
        ("Guild_Room",             ( -800, 109,  -75), (-758, 104, -102), False, (  41, 0 ), "gold"),
        ("Guild_1",                (-586,    0, 137 ), (-622, 255, 105),  True,  (  19, 0 ), "sponge"),
        ("Guild_2",                (-570,    0, 112 ), (-534, 255, 154),  True,  (  19, 0 ), "sponge"),
        ("Guild_3",                (-581,    0, 150 ), (-613, 255, 186),  True,  (  19, 0 ), "sponge"),
        ("Guild_4",                (-649,    0, 275 ), (-617, 255, 311),  True,  (  19, 0 ), "sponge"),
        ("Guild_5",                (-683,    0, 275 ), (-651, 255, 311),  True,  (  19, 0 ), "sponge"),
        ("Guild_6",                (-685,    0, 275 ), (-717, 255, 311),  True,  (  19, 0 ), "sponge"),
        ("Guild_7",                (-816,    0, 235 ), (-780, 255, 267),  True,  (  19, 0 ), "sponge"),
        ("Guild_8",                (-832,    0, 257 ), (-868, 255, 289),  True,  (  19, 0 ), "sponge"),
        ("Guild_9",                (-816,    0, 269 ), (-780, 255, 301),  True,  (  19, 0 ), "sponge"),
        ("Guild_10",               (-937,    0, 272 ), (-969, 255, 308),  True,  (  19, 0 ), "sponge"),
        ("Guild_11",               (-969,    0, 256 ), (-937, 255, 220),  True,  (  19, 0 ), "sponge"),
        ("Guild_12",               (-958,    0, 104 ), (-994, 255, 136),  True,  (  19, 0 ), "sponge"),
        ("Guild_13",               (-942,    0, 93  ), (-906, 255, 125),  True,  (  19, 0 ), "sponge"),
        ("Guild_14",               (-958,    0, 70  ), (-994, 255, 102),  True,  (  19, 0 ), "sponge"),
        ("Guild_15",               (-920,    0, -88 ), (-952, 255, -52),  True,  (  19, 0 ), "sponge"),
        ("Guild_16",               (-936,    0, -102), (-900, 255, -134), True,  (  19, 0 ), "sponge"),
        ("Guild_17",               (-955,    0, -106), (-987, 255, -70),  True,  (  19, 0 ), "sponge"),
        ("Guild_18",               (-954,    0, -120), (-990, 255, -152), True,  (  19, 0 ), "sponge"),
        ("Guild_19",               (-936,    0, -168), (-900, 255, -136), True,  (  19, 0 ), "sponge"),
        ("Guild_20",               (-751,    0, -230), (-787, 255, -198), True,  (  19, 0 ), "sponge"),
        ("Guild_21",               (-787,    0, -232), (-751, 255, -264), True,  (  19, 0 ), "sponge"),
        ("Guild_22",               (-600,    0, -191), (-564, 255, -159), True,  (  19, 0 ), "sponge"),
        ("Guild_23",               (-615,    0, -180), (-651, 255, -212), True,  (  19, 0 ), "sponge"),
        ("Guild_24",               (-564,    0, -192), (-600, 255, -224), True,  (  19, 0 ), "sponge"),
        ("Guild_25",               (-581,    0, -64 ), (-613, 255, -100), True,  (  19, 0 ), "sponge"),
        ("Guild_26",               (-596,    0, -46 ), (-564, 255, -10),  True,  (  19, 0 ), "sponge"),
        ("Guild_27",               (-548,    0, -64 ), (-580, 255, -100), True,  (  19, 0 ), "sponge"),

        #("Apartments_buying_room", ( -809,  99,   47), ( -874,  96,    4), False, (  41, 0 ), "gold"),
        #("Plot_Pressure_Plates",   ( -719, 106, -118), ( -665, 106,  -74), False, (  41, 0 ), "gold"),
        #("Section_1",              (-1130,   0, -267), ( -897, 255,  318), True,  (  41, 0 ), "gold"),
        #("Section_2",              ( -896,   0,  208), ( -512, 255,  318), True,  (  57, 0 ), "diamond"),
        #("Section_3",              ( -896,   0,  207), ( -788, 255,  119), True,  (  42, 0 ), "iron"),
        #("Section_4",              ( -896,   0, -267), ( -825, 255,  -28), True,  (  22, 0 ), "lapis"),
        #("Section_5",              ( -512,   0,  207), ( -640, 255, -273), True,  (  24, 0 ), "sandstone"),
        #("Section_6",              ( -824,   0, -169), ( -641, 255, -272), True,  ( 152, 0 ), "redstone"),
        #("Section_7",              ( -641,   0, -168), ( -677, 255, -132), True,  ( 155, 0 ), "quartz"),
        #("Section_8",              ( -774,   0, -168), ( -813, 255, -150), True,  (  17, 14), "birch wood"),
        #("Section_9",              ( -641,   0,  -25), ( -655, 255,  -52), True,  (  17, 15), "jungle wood"),
        #("Section_10",             ( -680,   0,  183), ( -641, 255,  207), True,  (  19, 0 ), "sponge"),
        #("Section_11",             ( -668,   0,  -14), ( -641, 255,   25), True,  (   1, 1 ), "granite"),
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



