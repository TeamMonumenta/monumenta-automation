#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lock_tile_entities_lib

################################################################################
# Config section

# Dst is the destination world, which gets overwritten by the build world.
# Then, data from the main world replaces the relevant parts of the dst world.
# Please note that no special care need be taken with whitespace in filenames.
worldFolder = "/home/rock/tmp/BUILD_Project_Epic"

coordinatesToScan = (
    # ("region name",        (lowerCoordinate),  (upperCoordinate),  ( id, dmg), "block name (comment)"),
    ("Apartments_units",       ( -817, 113,   87), ( -859, 164,   16), (  41, 0 ), "gold"),
    ("Section_1",              (-1130,   0, -267), ( -897, 255,  318), (  41, 0 ), "gold"),
    ("Section_2",              ( -896,   0,  208), ( -512, 255,  318), (  57, 0 ), "diamond"),
    ("Section_3",              ( -896,   0,  207), ( -788, 255,  119), (  42, 0 ), "iron"),
    ("Section_4",              ( -896,   0, -267), ( -825, 255,  -28), (  22, 0 ), "lapis"),
    ("Section_5",              ( -512,   0,  207), ( -640, 255, -273), (  24, 0 ), "sandstone"),
    ("Section_6",              ( -824,   0, -169), ( -641, 255, -272), ( 152, 0 ), "redstone"),
    ("Section_7",              ( -641,   0, -168), ( -677, 255, -132), ( 155, 0 ), "quartz"),
    ("Section_8",              ( -774,   0, -168), ( -813, 255, -150), (  17, 14), "birch wood"),
    ("Section_9",              ( -641,   0,  -25), ( -655, 255,  -52), (  17, 15), "jungle wood"),
    ("Section_10",             ( -680,   0,  183), ( -641, 255,  207), (  19, 0 ), "sponge"),
    ("Section_11",             ( -668,   0,  -14), ( -641, 255,   25), (   1, 1 ), "granite"),
)

tileEntitiesToCheck = ("chest", "dispenser", "dropper", "shulker_box", "hopper", "brewing_stand", "furnace")
# Possible values: "chest" (trapped chest shares ID), "dispenser", "dropper", "shulker_box", "hopper", "brewing_stand", "furnace"
# These are namespaced; default is "minecraft:*" in this code.

################################################################################
# Main Code

# This scans for tile entities that don't have a loot table
lock_tile_entities_lib.run(worldFolder, coordinatesToScan, tileEntitiesToCheck)

