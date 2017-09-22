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

import item_replace_lib
import item_replace_list

from monumenta_common import getBoxSize
from monumenta_common import getBoxPos
from monumenta_common import getBox
from monumenta_common import copyFile
from monumenta_common import copyFolder
from monumenta_common import copyFolders

################################################################################
# Function definitions

def replace(world, oldBlock, newBlock, box=None):
    world.fillBlocks(box, newBlock, blocksToReplace=[oldBlock])

def replaceSeveral(world, replaceList, boxList):
    for aBox in boxList:
        for replacePair in replaceList:
            oldBlock = world.materials[replacePair[0]]
            newBlock = world.materials[replacePair[1]]
            replace(world, oldBlock, newBlock, aBox)

def replaceGlobally(world, replaceList):
    for replacePair in replaceList:
        oldBlock = world.materials[replacePair[0]]
        newBlock = world.materials[replacePair[1]]
        replace(world, oldBlock, newBlock)

def movePlayers(worldFolder, point):
    """ Moves all players to the same location """
    # world.players returns an empty list for multiplayer worlds?
    # Lovely. Mojang changed the player data folder from world/player
    # to world/playerdata when they changed the files to be UUIDs.
    # Weird that pymclevel wasn't updated for that years ago.
    for aPlayerFile in os.listdir(worldFolder+"/playerdata"):
        aPlayerFile = worldFolder+"/playerdata/"+aPlayerFile
        aPlayer = nbt.load(aPlayerFile)

        # Set they players' position
        aPlayer["Pos"][0].value = point[0]
        aPlayer["Pos"][1].value = point[1]
        aPlayer["Pos"][2].value = point[2]

        # Face players the right way
        aPlayer["Rotation"][0].value = point[3]
        aPlayer["Rotation"][1].value = point[4]

        # We don't want players being flung around after a terrain reset
        aPlayer["FallDistance"].value = 0.0
        aPlayer["Motion"][0].value = 0.0
        aPlayer["Motion"][1].value = 0.0
        aPlayer["Motion"][2].value = 0.0

        # What if they reached the end dimention?
        # Yes....let them fall into the void...yes... >:D ....nah, I'll be nice.
        aPlayer["Dimension"].value = 0

        # Welcome to the ultimate healthcare service, here's your weekly checkup
        aPlayer["Fire"].value = -20
        aPlayer["Air"].value = 300
        aPlayer["foodLevel"].value = 20
        aPlayer["foodSaturationLevel"].value = 5.0
        aPlayer["foodExhaustionLevel"].value = 0.0
        aPlayer["Health"].value = 20.0
        aPlayer["DeathTime"].value = 0

        # save
        aPlayer.save(aPlayerFile)

# TODO: This doesn't quite work
def resetRegionalDifficulty(world):
    """ Resets the play time for the world, and the time in each chunk. """

    # Don't need to reset the server time, since it does not advance
    # world.root_tag["Data"]["Time"].value = 0

    for aChunk in world.getChunks():
        aChunk.root_tag["Level"]["InhabitedTime"].value = 0

################################################################################
# Functions that display stuff while they work

def copyBoxes(srcWorld, dstWorld, coordinatesToCopy, blockReplaceList):

    print "Starting transfer of boxes from player server..."
    copyNum = 1
    copyMax = len(coordinatesToCopy)
    blocksToCopy = range(materials.id_limit)

    # This is fine. The warning is known and can be ignored.
    warnings.filterwarnings("ignore", category=numpy.VisibleDeprecationWarning)

    for aCopy in coordinatesToCopy:
        print "[{0}/{1}] Copying {2}...".format(copyNum,copyMax,aCopy[0])

        pos = getBoxPos(aCopy)
        box = getBox(aCopy)

        tempSchematic = srcWorld.extractSchematic(box)

        # TODO: Need to figure out a good way to only replace these things in some regions 
        #       but not all of them (for example the guild room)
        # print "[{0}/{1}]   Replacing forbidden blocks in {2}...".format(copyNum,copyMax,aCopy[0])
        # replaceGlobally(tempSchematic, blockReplaceList);

        # Remove entities in destination
        dstWorld.removeEntitiesInBox(box)

        # Copy the schematic with edits in place
        dstWorld.copyBlocksFrom(tempSchematic, BoundingBox((0, 0, 0), pos),
                                pos, blocksToCopy)

        copyNum+=1

    print "Done transferring boxes from player server"

def terrainReset(config):
    localMainFolder = config["localMainFolder"]
    localBuildFolder = config["localBuildFolder"]
    localDstFolder = config["localDstFolder"]
    coordinatesToCopy = config["coordinatesToCopy"]
    blockReplaceList = config["blockReplaceList"]
    safetyTpLocation = config["safetyTpLocation"]

    print "Copying build world as base..."
    copyFolder(localBuildFolder, localDstFolder)

    # Copy various bits of player data from the main world
    print "Copying player data files from main world..."
    copyFolders(localMainFolder, localDstFolder, ["advancements/", "playerdata/", "stats/",])
    print "Copying player maps and scoreboard from main world..."
    copyFolders(localMainFolder, localDstFolder, ["data/",])
    print "Copying updated advancements, functions, and loot tables from build world..."
    copyFolders(localBuildFolder, localDstFolder, ["data/advancements/", "data/functions/", "data/loot_tables/",])

    print "Opening old play World..."
    srcWorld = mclevel.loadWorld(localMainFolder)

    # print "Compiling item replacement list..."
    # itemReplacementList = item_replace_lib.allReplacements(item_replace_list.itemReplacements)

    # print "Handling item replacements for tile entities..."
    # item_replace_lib.replaceItemsInWorld(srcWorld,item_replace_list)

    print "Opening Destination World..."
    dstWorld = mclevel.loadWorld(localDstFolder)

    print "Copying needed terrain from the main world..."
    copyBoxes(srcWorld, dstWorld, coordinatesToCopy, blockReplaceList)

    # TODO: Not working yet
    # print "Resetting difficulty..."
    # resetRegionalDifficulty(dstWorld)

    print "Saving...."
    dstWorld.generateLights()
    dstWorld.saveInPlace()

    print "Moving players..."
    movePlayers(localDstFolder, safetyTpLocation)

    # print "Handling item replacements for players..."
    # item_replace_lib.replaceItemsOnPlayers(localDstFolder, itemReplacementList)

    # TODO: Remove MCEdit temp files

    print "Done!"


