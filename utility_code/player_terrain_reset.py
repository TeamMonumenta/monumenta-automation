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
    "/home/rock/tmp/dungeons-out/white/Project_Epic-white/",
    "/home/rock/tmp/dungeons-out/orange/Project_Epic-orange/",
    "/home/rock/tmp/dungeons-out/magenta/Project_Epic-magenta/",
    "/home/rock/tmp/dungeons-out/lightblue/Project_Epic-lightblue/",
    "/home/rock/tmp/dungeons-out/r1bonus/Project_Epic-r1bonus/",
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
