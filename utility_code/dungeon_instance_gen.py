#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required libraries have links where not part of a standard Python install.
import os
import sys
import warnings
import shutil

import numpy
from numpy import zeros, bincount
import itertools

# These are expected in your site-packages folder, see:
# https://stackoverflow.com/questions/31384639/what-is-pythons-site-packages-directory
import mclevel # from https://github.com/mcedit/pymclevel
from mclevel import materials
from mclevel.box import BoundingBox, Vector

from monumenta_common import copyFile
from monumenta_common import copyFolder
from monumenta_common import copyFolders

from terrain_reset_lib import resetRegionalDifficulty

################################################################################
# Config section

config = {
    "dungeonFolder":"/home/rock/tmp/dungeons/",
    "templateFolder":"/home/rock/tmp/template/",
    "outFolder":"/home/rock/tmp/out/",

    "dungeons":(
        {"name":"white",     "pos1":(-2528, 0, -1296), "pos2":(-2369, 255, -945 )},
        {"name":"orange",    "pos1":(-2336, 0, -1296), "pos2":(-2017, 119, -945 )},
        {"name":"magenta",   "pos1":(-1984, 0, -1296), "pos2":(-1729, 255, -1041)},
        {"name":"lightblue", "pos1":(-1696, 0, -1296), "pos2":(-1409, 255, -1025)},
        #{"name":"yellow",    "pos1":(-1376, 0, -1296), "pos2":(-1121, 255, -1041)},
        {"name":"r1bonus1",  "pos1":(-1088, 0, -1296), "pos2":(-801,  92,  -929 )},
    ),

    # 16 chunks of void-biome padding on the -x and -z sides
    "voidPadding":16,

    # Dungeons placed in region -3,-2 - a region is 32x32 chunks
    "targetRegion":{"x":-3, "z":-2},

    # Number of dungeons
    "numDungeons":50,
}

################################################################################
# TODO: Dictionary functions to move to common

def getBoxSize(pos1, pos2):
    # Get the size of a box from
    # an element of coordinatesToScan
    sizeFix = Vector(*(1,1,1))
    min_pos = Vector(*map(min, zip(pos1, pos2)))
    max_pos = Vector(*map(max, zip(pos1, pos2)))
    return max_pos - min_pos + sizeFix

def getBoxMinPos(pos1, pos2):
    # Get the origin of a box from
    # an element of coordinatesToScan
    return Vector(*map(min, zip(pos1, pos2)))

def getBox(pos1, pos2):
    # Returns a box around from
    # an element of coordinatesToScan
    origin = getBoxMinPos(pos1, pos2)
    size   = getBoxSize(pos1, pos2)

    return BoundingBox(origin, size)

################################################################################
# Function definitions

def gen_dungeon_instances(config):
    dungeonFolder = config["dungeonFolder"]
    templateFolder = config["templateFolder"]
    outFolder = config["outFolder"]
    dungeons = config["dungeons"]
    voidPadding = config["voidPadding"]
    targetRegion = config["targetRegion"]
    numDungeons = config["numDungeons"]

    # Fail if folders don't exist
    if not os.path.isdir(dungeonFolder):
        sys.exit("Dungeon reference folder does not exist.")
    if not os.path.isdir(templateFolder):
        sys.exit("Template world folder does not exist.")

    print "Opening dungeon reference world..."
    referenceWorld = mclevel.loadWorld(dungeonFolder)

    for dungeon in dungeons: 
        dungeonName = dungeon["name"]
        dungeonBox = getBox(dungeon["pos1"], dungeon["pos2"])
        dstFolder = outFolder + dungeonName + '/'

        dstPos = Vector(*(targetRegion["x"] * 32 * 16, 0, targetRegion["z"] * 32 * 16))
        dstStep = Vector(*(0, 0, 32 * 16))
        voidPos = dstPos + Vector(*(-1 * voidPadding * 16, 0, -1 * voidPadding * 16))
        voidSize = Vector(*((32 + voidPadding) * 16, 256, (32 * numDungeons + voidPadding) * 16))
        voidBox = BoundingBox(voidPos, voidSize)

        blocksToCopy = range(materials.id_limit)

        #print dungeonBox
        #print dstPos
        #print dstStep
        #print voidPos
        #print voidSize
        #print voidBox

        print "Starting work on dungeon: " + dungeonName

        print "  Copying template world as base..."
        copyFolder(templateFolder, dstFolder)

        print "  Opening dungeon world..."
        dstWorld = mclevel.loadWorld(dstFolder)

        print "  Copying dungeon schematic..."
        tempSchematic = referenceWorld.extractSchematic(dungeonBox, entities=True)

        print "  Creating void chunks..."
        chunksCreated = dstWorld.createChunksInBox(voidBox)
        print "  Created {0} chunks." .format(len(chunksCreated))

        print "  Changing all chunks to void biome..."
        for aChunk in dstWorld.getChunks():
            aChunk.root_tag["Level"]["Biomes"].value.fill(127)
            aChunk.chunkChanged(True)

        print "  Creating dungeon instances..."
        for i in range(numDungeons):
            print "  {0}...".format(i)
            dstWorld.copyBlocksFrom(tempSchematic, tempSchematic.bounds, 
                                     dstPos + dstStep * i, blocksToCopy, 
                                     create=True, entities=True, biomes=True)

        # Note resetting difficulty is unnecessary - all generated chunks
        #   lack the time inhabited tag
        # print "  Resetting difficulty..."
        # resetRegionalDifficulty(dstWorld)

        print "  Saving...."
        dstWorld.generateLights()
        dstWorld.saveInPlace()

        try: 
            shutil.rmtree(dstFolder + "##MCEDIT.TEMP##", ignore_errors=True)
            os.remove(dstFolder + "mcedit_waypoints.dat")
        except Exception as e:
            continue

    sys.exit(0)

    print "Done!"


gen_dungeon_instances(config)

