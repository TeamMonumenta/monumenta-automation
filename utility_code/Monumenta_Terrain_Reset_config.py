#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).

This does so as directly as possible while providing many features.
Entities within the build world that are in areas copied from the
main world are removed.
Scoreboard values are maintained from the play area.
Players are teleported to safety

Fair warning, some of the optimization is done by removing error handling.
Python will tell you if/when the script crashes.
If it's going to crash, it won't damage the original worlds.
Just fix what broke, and run again.

In progress:
Universal item replacement/deletion, for when an item is outdated.

Current task:
convert MCEdit's NBT notation to string and vice versa (vanilla command style)

Planned:
Preservation of map items from both worlds (requires item replacement).
1.13 support (will start writing changes during snapshots)

Unused features:
A block replacement list and functions to use them
are provided, and were used for testing.

Known bugs:
When testing this on single player worlds, the inventory from
    the build world is seemingly kept over the main one.
    This is because single player keeps track of the only player
    differently from multiplayer (level.dat I think).
    Player data is still transfered correctly, but is overwritten
    by the single player player data.
    This will not occur for server files.
"""
################################################################################
# Config section

# Dst is the destination world, which gets overwritten by the build world.
# Then, data from the main world replaces the relevant parts of the dst world.
# Please note that no special care need be taken with whitespace in filenames.
localMainFolder = "/home/rock/tmp/Project Epic Source"
localBuildFolder = "/home/rock/tmp/Project Epic"
localDstFolder = "/home/rock/tmp/Project Epic Updated"

# TODO: Update this value!
# No 0.5 offset here, add it yourself if you like.
SafetyTpLocation = (-734.0, 105.5, 50.0)

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
    ("Be_Nice_WIP_Ugly_Market",( -399,  95, -108), (-497, 255, -206), (   1, 5 ), "andesite"), # Don't worry, I won't say anything.
    ("Lowtide",                (  672,  60,  416), ( 751, 255,  517), (   1, 3 ), "diorite"),
)

# I used this as a test and to differentiate the test worlds
# Some of these materials I added myself.
# I updated slime blocks due to a lighting glitch on 11 Aug 2017
# These aren't meant to be pretty, only recognizable.
# The code relevant to this is commented out.
blocksToReplace = (
    # (old, new)
    ("Spruce Wood (Upright)", "Pillar Quartz Block (Upright)"),
    ("Spruce Wood Planks", (251,0)), # white concrete, not currently in my materials list (3nd to last!)
    ("Glass Pane", "White Stained Glass Pane"),
    ("Spruce Fence", "Birch Fence"),
    ("Cobblestone", (206,0)), # end bricks
    ("Dirt", (251,0)), # white concrete powder
    ("Stone Pressure Plate", "Weighted Pressure Plate (Heavy)"),
    
    (( 67, 0), (135, 0)), # cobblestone stairs to birch stairs
    (( 67, 1), (135, 1)), # repeat for all damage
    (( 67, 2), (135, 2)),
    (( 67, 3), (135, 3)),
    (( 67, 4), (135, 4)),
    (( 67, 5), (135, 5)),
    (( 67, 6), (135, 6)),
    (( 67, 7), (135, 7)),
    (( 67, 8), (135, 8)),
    (( 67, 9), (135, 9)),
    (( 67,10), (135,10)),
    (( 67,11), (135,11)),
    (( 67,12), (135,12)),
    (( 67,13), (135,13)),
    (( 67,14), (135,14)),
    (( 67,15), (135,15)),
    
    ((134, 0), (156, 0)), # spruce stairs to quartz stairs
    ((134, 1), (156, 1)),
    ((134, 2), (156, 2)),
    ((134, 3), (156, 3)),
    ((134, 4), (156, 4)),
    ((134, 5), (156, 5)),
    ((134, 6), (156, 6)),
    ((134, 7), (156, 7)),
    ((134, 8), (156, 8)),
    ((134, 9), (156, 9)),
    ((134,10), (156,10)),
    ((134,11), (156,11)),
    ((134,12), (156,12)),
    ((134,13), (156,13)),
    ((134,14), (156,14)),
    ((134,15), (156,15)),
    
    ((193,15), (194,15)), # spruce door to birch door
    ((193,14), (194,14)), # reverse order since damage 0 is greedy here
    ((193,13), (194,13)), # (matches all damage)
    ((193,12), (194,12)),
    ((193,11), (194,11)),
    ((193,10), (194,10)),
    ((193, 9), (194, 9)),
    ((193, 8), (194, 8)),
    ((193, 7), (194, 7)),
    ((193, 6), (194, 6)),
    ((193, 5), (194, 5)),
    ((193, 4), (194, 4)),
    ((193, 3), (194, 3)),
    ((193, 2), (194, 2)),
    ((193, 1), (194, 1)),
    ((193, 0), (194, 0))
    #you can leave a trailing comma at the end
    # of lists/tuples, and it will be ignored
)

# I used this as a test and to differentiate the test worlds
blocksToReplaceB = (
    # (old, new)
    ("Granite", "Light Gray Stained Terracotta"),
    ("Diorite", "White Stained Terracotta"),
    ("Andesite", "Cyan Stained Terracotta"),
    ("Stone", (251,8)), # light gray concrete
    
    ("Clay", (251,9)), # cyan concrete
    ("Sand", (252,0)), # white concrete powder
    
    ("Dirt", (251,12)), # brown concrete
    ("Grass", (252,5)), # lime concrete powder
    ((208,0), (252,1)), # path to orange concrete powder
    
    ("Oak Wood (Upright)", (216, 0)), # bone block, upright
    ("Oak Leaves (Decaying)", "Magenta Stained Glass"),
    ("Oak Leaves", "Magenta Stained Glass Pane"),
    
    ("Spruce Wood (Upright)", (216, 0)), # bone block, upright
    ("Spruce Leaves (Decaying)", "Purple Stained Glass"),
    ("Spruce Leaves", "Purple Stained Glass Pane"),
    
    ("Birch Wood (Upright)", (216, 0)), # bone block, upright
    ("Birch Leaves (Decaying)", "Pink Stained Glass"),
    ("Birch Leaves", "Pink Stained Glass Pane"),
    
    ("Water", "Slime Block"),
    ("Water (Flowing)", "Lime Stained Glass"),
)

