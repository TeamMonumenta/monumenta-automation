#!/usr/bin/env python
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
# Required libraries have links where not part of a standard Python install.
import os
import warnings
import shutil

import numpy
from numpy import zeros, bincount
import itertools

# These are expected in your site-packages folder, see:
# https://stackoverflow.com/questions/31384639/what-is-pythons-site-packages-directory
import mclevel # from https://github.com/mcedit/pymclevel
from mclevel import mclevelbase
from mclevel import materials
from mclevel import nbt
from mclevel.box import BoundingBox, Vector

import lib_item_replace
import item_replace_list

################################################################################
# Function definitions

print "Compiling item replacement list..."
compiledItemReplacementList = lib_item_replace.allReplacements(item_replace_list.itemReplacements)

print "Opening Destination World..."
dstWorld = mclevel.loadWorld("/home/rock/project_epic/test/Project_Epic-test")

print "Copying needed terrain from the main world..."
lib_item_replace.replaceItemsInWorld(dstWorld, compiledItemReplacementList)

print "Saving...."
dstWorld.saveInPlace()

print "Done!"


