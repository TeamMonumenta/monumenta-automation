#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../"))

import item_replace_list
import entity_update_list

config = {
    "server":"region_2",

    # Dst is the destination world, which gets overwritten by the build world.
    # Then, data from the main world replaces the relevant parts of the dst world.
    # Please note that no special care need be taken with whitespace in filenames.
    "localMainFolder":"/home/rock/project_epic/region_2/Project_Epic-region_2-prereplaceitems/",
    "localDstFolder":"/home/rock/project_epic/region_2/Project_Epic-region_2/",

    # Which folder to copy the base world from. Either "build", "main", or not set
    "copyBaseFrom":"main",

    # If this is set to True, instead of copying the coordinates from the Main server
    # it treats them as additional coordinatesToFill instead, filling those regions
    # so that their positions can be easily checked in-game
    #"coordinatesDebug":True,

    # List of places where entity updates should be run - options are "world", "schematics" (players not yet available, considering replacing creeper spawn eggs with a copy of Mr Snuggles that can't complete the Mr Snuggles quest)
    "entityUpdates":entity_update_list.KingsValleyBuild,
    "entityUpdateLocations":["world",],

    # List of places where item replacements should be run - options are "players", "world", "schematics"
    "itemReplacements":item_replace_list.KingsValleyBuild,
    "itemReplaceLocations":["players", "world",],
    "itemLog":"/home/rock/tmp/items_region_2.txt",
}

