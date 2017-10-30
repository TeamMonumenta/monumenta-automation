#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Moves players and handles item replacement for them during resets on dungeon servers
"""

import os
import warnings
import shutil

import item_replace_lib
import item_replace_list

from terrain_reset_lib import movePlayers

folders = (
    "/home/rock/tmp/POST_RESET/betaplots/Project_Epic-betaplots/",
    "/home/rock/tmp/POST_RESET/lightblue/Project_Epic-lightblue/",
    "/home/rock/tmp/POST_RESET/magenta/Project_Epic-magenta/",
    "/home/rock/tmp/POST_RESET/orange/Project_Epic-orange/",
    "/home/rock/tmp/POST_RESET/purgatory/Project_Epic-purgatory/",
    "/home/rock/tmp/POST_RESET/region_1/Project_Epic-region_1/",
    "/home/rock/tmp/POST_RESET/r1bonus/Project_Epic-r1bonus/",
    "/home/rock/tmp/POST_RESET/r1plots/Project_Epic-r1plots/",
    "/home/rock/tmp/POST_RESET/tutorial/Project_Epic-tutorial/",
    "/home/rock/tmp/POST_RESET/white/Project_Epic-white/",
    "/home/rock/tmp/POST_RESET/yellow/Project_Epic-yellow/",
)
safetyTpLocation = (-1450, 241, -1498, 270.0, 0.0)

print "Compiling item replacement list..."
compiledItemReplacementList = item_replace_lib.allReplacements(item_replace_list.itemReplacements)

for folder in folders:
    print "Starting work on folder '" + folder + "'"

    print "  Handling item replacements for players..."
    item_replace_lib.replaceItemsOnPlayers(folder, compiledItemReplacementList)

    print "  Moving players..."
    movePlayers(folder, safetyTpLocation)

print "Done!"
