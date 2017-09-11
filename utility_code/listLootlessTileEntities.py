#!/usr/bin/python
# -*- coding: utf-8 -*-

import listLootlessTileEntitiesLib

################################################################################
# Config section

# Dst is the destination world, which gets overwritten by the build world.
# Then, data from the main world replaces the relevant parts of the dst world.
 Please note that no special care need be taken with whitespace in filenames.
worldFolder = "/home/rock/tmp/Project Epic"

coordinatesToScan = (
    # ("region name",        (lowerCoordinate),  (upperCoordinate),  ( id, dmg), "block name (comment)"),
    ("main template region", (-30000, 0, -30000), (30000, 255,30000), (   7, 0 ), "bedrock"),
)

tileEntitiesToCheck = ("chest",)
# If using only one item, ALWAYS use a trailing comma.
# Possible values: "chest" (trapped chest shares ID), "dispenser", "dropper", "shulker_box", "hopper"
# These are actually namespaced; default is "minecraft:*" in this code.

################################################################################
# Main Code

# This shows where the selected regions are, as your old script does.
# WARNING: This version saves in place!
#listLootlessTileEntitiesLib.fillRegions(worldFolder,coordinatesToScan)

# This scans for tile entities that don't have a loot table
listLootlessTileEntitiesLib.listLootlessTileEntities(worldFolder,coordinatesToScan,tileEntitiesToCheck,logFolder)



