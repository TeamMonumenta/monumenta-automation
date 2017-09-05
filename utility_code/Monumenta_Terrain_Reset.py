#!/usr/bin/python
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
import TerrainResetLib
import ItemReplaceLib

################################################################################
# Config section

# Dst is the destination world, which gets overwritten by the build world.
# Then, data from the main world replaces the relevant parts of the dst world.
# Please note that no special care need be taken with whitespace in filenames.
localMainFolder = "/home/rock/tmp/Project Epic Source"
localBuildFolder = "/home/rock/tmp/Project Epic"
localDstFolder = "/home/rock/tmp/Project Epic Updated"

# No 0.5 offset here, add it yourself if you like.
# (x,y,z,ry,rx)
SafetyTpLocation = (-734.0, 105.5, 50.0, 0.0, 0.0)

coordinatesToCopy = (
    # ("a unique name",        (lowerCoordinate),  (upperCoordinate), ( id, dmg), "block name (comment)"),
    ("Apartments_buying_room", ( -809,  99,   47), (-874,  96,    4), (  41, 0 ), "gold"),
    ("Apartments_units",       ( -817, 113,   87), (-859, 164,   16), (  41, 0 ), "gold"),
    ("Plot_Pressure_Plates",   ( -719, 106, -118), (-665, 106,  -74), (  41, 0 ), "gold"),
    ("Guild_Room",             ( -800, 109,  -75), (-758, 104, -102), (  41, 0 ), "gold"),
    ("Section_1",              (-1120,   0, -267), (-897, 255,  318), (  41, 0 ), "gold"),
    ("Section_2",              ( -896,   0,  208), (-512, 255,  318), (  57, 0 ), "diamond"),
    ("Section_3",              ( -896,   0,  207), (-788, 255,  119), (  42, 0 ), "iron"),
    ("Section_4",              ( -896,   0, -267), (-825, 255,  -28), (  22, 0 ), "lapis"),
    ("Section_5",              ( -512,   0,  207), (-640, 255, -273), (  24, 0 ), "sandstone"),
    ("Section_6",              ( -824,   0, -169), (-641, 255, -272), ( 152, 0 ), "redstone"),
    ("Section_7",              ( -641,   0, -168), (-677, 255, -132), ( 155, 0 ), "quartz"),
    ("Section_8",              ( -774,   0, -168), (-813, 255, -150), (  17, 14), "birch wood"),
    ("Section_9",              ( -641,   0,  -25), (-655, 255,  -52), (  17, 15), "jungle wood"),
    ("Section_10",             ( -680,   0,  183), (-641, 255,  207), (  19, 0 ), "sponge"),
    ("Section_11",             ( -668,   0,  -14), (-641, 255,   25), (   1, 1 ), "granite"),
    ("Lowtide",                (  672,  60,  416), ( 751, 255,  517), (   1, 3 ), "diorite"),
)

"""
List of blocks to not copy over for the regions above
"""
blocksToReplace = (
    ("iron_block", "air"),
    ("iron_ore", "air"),
    ("gold_block", "air"),
    ("gold_ore", "air"),
    ("lapis_block", "air"),
    ("lapis_ore", "air"),
    ("diamond_block", "air"),
    ("diamond_ore", "air"),
    ("emerald_block", "air"),
    ("emerald_ore", "air"),
    
    ("beacon", "air"),
    
    # Not sure about this section
    #("enchanting_Table", "air"),
    #("quartz_ore", "air"),
    #("hopper", "air"),
    
    # anvils
    ((145,0), "air"),
    ((145,1), "air"),
    ((145,2), "air"),
    ((145,4), "air"),
    ((145,5), "air"),
    ((145,6), "air"),
    ((145,8), "air"),
    ((145,9), "air"),
    ((145,10), "air"),
    ((145,12), "air"),
    ((145,13), "air"),
    ((145,14), "air"),
)

################################################################################
# In development:

#ItemReplaceLib.replaceItemsOnPlayers("/home/tim/MCserver/1.12.1/world",None)

#world = mclevel.loadWorld("/home/tim/MCserver/1.12.1/world")
#ItemReplaceLib.replaceItemsInWorld(world,None)


################################################################################
# Main Code

#TerrainResetLib.replaceBlocksInBoxList(blocksToReplace,coordinatesToCopy,"main")
#TerrainResetLib.replaceBlocksGlobally(blocksToReplaceB,"build")

# This shows where the selected regions are, as your old script does.
#TerrainResetLib.fillRegions()

# This does the move itself - copy areas, entities, scoreboard, etc.
TerrainResetLib.terrainReset()


