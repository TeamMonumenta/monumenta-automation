#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import shutil
import sys

# The effective working directory for this script must always be the MCEdit-Unified directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
import pymclevel
from pymclevel import mclevelbase
from pymclevel.box import BoundingBox, Vector
from pymclevel import nbt

from lib_monumenta.common import getBox, lockTileEntities

################################################################################
# Config section

# Dst is the destination world, which gets overwritten by the build world.
# Then, data from the main world replaces the relevant parts of the dst world.
# Please note that no special care need be taken with whitespace in filenames.
worldFolder = "/home/rock/project_epic/region_1/Project_Epic-region_1"

coordinatesToScan = (
    # ("region name",        (lowerCoordinate),  (upperCoordinate),  ( id, dmg), "block name (comment)"),
    {"name":"Section_1",              "pos1":(-1130,   0, -267), "pos2":(-897, 255,  318), "replace":True,  "material":( 41,  0), "materialName":"gold"},
    {"name":"Section_2",              "pos1":( -896,   0,  208), "pos2":(-512, 255,  318), "replace":True,  "material":( 57,  0), "materialName":"diamond"},
    {"name":"Section_3",              "pos1":( -896,   0,  207), "pos2":(-788, 255,  119), "replace":True,  "material":( 42,  0), "materialName":"iron"},
    {"name":"Section_4",              "pos1":( -896,   0, -267), "pos2":(-825, 255,  -28), "replace":True,  "material":( 22,  0), "materialName":"lapis"},
    {"name":"Section_5",              "pos1":( -512,   0,  207), "pos2":(-640, 255, -273), "replace":True,  "material":( 24,  0), "materialName":"sandstone"},
    {"name":"Section_6",              "pos1":( -824,   0, -169), "pos2":(-641, 255, -272), "replace":True,  "material":(152,  0), "materialName":"redstone"},
    {"name":"Section_7",              "pos1":( -641,   0, -168), "pos2":(-677, 255, -132), "replace":True,  "material":(155,  0), "materialName":"quartz"},
    {"name":"Section_8",              "pos1":( -774,   0, -168), "pos2":(-813, 255, -150), "replace":True,  "material":( 17, 14), "materialName":"birch wood"},
    {"name":"Section_9",              "pos1":( -641,   0,  -25), "pos2":(-655, 255,  -52), "replace":True,  "material":( 17, 15), "materialName":"jungle wood"},
    {"name":"Section_10",             "pos1":( -680,   0,  183), "pos2":(-641, 255,  207), "replace":True,  "material":( 19,  0), "materialName":"sponge"},
    {"name":"Section_11",             "pos1":( -668,   0,  -14), "pos2":(-641, 255,   25), "replace":True,  "material":(  1,  1), "materialName":"granite"},
)

tileEntitiesToCheck = ("chest", "dispenser", "dropper", "shulker_box", "hopper", "brewing_stand", "furnace")
# Possible values: "chest" (trapped chest shares ID), "dispenser", "dropper", "shulker_box", "hopper", "brewing_stand", "furnace"
# These are namespaced; default is "minecraft:*" in this code.

################################################################################
# Main Code

def run(worldFolder, coordinatesToScan, tileEntitiesToCheck):
    print "Beginning scan..."
    world = pymclevel.loadWorld(worldFolder)

    # Build tile ID list, adding default namespace if needed
    tileIDList = []
    for tileID in tileEntitiesToCheck:
        if ":" in tileID:
            tileIDList.append(tileID)
        else:
            tileIDList.append("minecraft:"+tileID)

    scanNum = 1
    scanMax = len(coordinatesToScan)

    # This is fine. The warning is known and can be ignored.
    # warnings.filterwarnings("ignore", category=numpy.VisibleDeprecationWarning)

    for aScanBox in coordinatesToScan:
        print "[{0}/{1}] Scanning {2}...".format(scanNum, scanMax, aScanBox["name"])
        scanNum+=1

        scanBox = getBox(aScanBox["pos1"], aScanBox["pos2"])

        lockTileEntities(world, scanBox, tileIDList);

    print "Saving..."
    world.saveInPlace()
    print "Done."

# This scans for tile entities that don't have a loot table
run(worldFolder, coordinatesToScan, tileEntitiesToCheck)

