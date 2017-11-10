#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required libraries have links where not part of a standard Python install.
import os
import shutil

# The effective working directory for this script must always be the MCEdit-Unified directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))

# These are expected in your site-packages folder, see:
# https://stackoverflow.com/questions/31384639/what-is-pythons-site-packages-directory
import pymclevel # from https://github.com/mcedit/pymclevel
from pymclevel import mclevelbase
from pymclevel.box import BoundingBox, Vector
from pymclevel import nbt

from lib_monumenta_common import getBox, lockTileEntities

################################################################################
# Config section

# Dst is the destination world, which gets overwritten by the build world.
# Then, data from the main world replaces the relevant parts of the dst world.
# Please note that no special care need be taken with whitespace in filenames.
worldFolder = "/home/rock/project_epic/test/Project_Epic-test"

coordinatesToScan = (
    # ("region name",        (lowerCoordinate),  (upperCoordinate),  ( id, dmg), "block name (comment)"),
    {"name":"PropPlots",         "pos1":(-1488, 0, -1433), "pos2":(-1512, 255, -1577), "replace":True, "material":( 41,  0), "materialName":"gold"},
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

