#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).
"""

import time

from lib_monumenta.terrain_reset import terrainReset
import item_replace_list

configList = [{
    "server":"region_1",

    # Dst is the destination world, which gets overwritten by the build world.
    # Then, data from the main world replaces the relevant parts of the dst world.
    # Please note that no special care need be taken with whitespace in filenames.
    "localMainFolder":"/home/rock/tmp/Project_Epic-region_1-prereplaceitems/",
    "localDstFolder":"/home/rock/tmp/Project_Epic-region_1/",

    # Which folder to copy the base world from. Either "build", "main", or not set
    "copyBaseFrom":"main",

    # If this is set to True, instead of copying the coordinates from the Main server
    # it treats them as additional coordinatesToFill instead, filling those regions
    # so that their positions can be easily checked in-game
    #"coordinatesDebug":True,

    # List of places where item replacements should be run - options are "players", "world", "schematics"
    "itemReplacements":item_replace_list.itemReplacements,
    "itemReplaceLocations":["players", "world",],
    "itemLog":"/home/rock/tmp/items_region_1.txt",
}]

print "If you didn't edit the replacement list to remove the decayed items, hit control+C now!"
time.sleep(5)
terrainReset(configList)
print "Done"

