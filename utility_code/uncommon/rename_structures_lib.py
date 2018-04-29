#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
This lists the tile entities that lack
a loot table within a box, filtering by type.
"""
# Required libraries have links where not part of a standard Python install.
import os
import shutil

import numpy
from numpy import zeros, bincount
import itertools

# These are expected in your site-packages folder, see:
# https://stackoverflow.com/questions/31384639/what-is-pythons-site-packages-directory
import mclevel # from https://github.com/mcedit/pymclevel
from mclevel import mclevelbase
from mclevel import materials
from mclevel.box import BoundingBox, Vector
from mclevel import nbt

from monumenta_common import getBoxName
from monumenta_common import getBoxSize
from monumenta_common import getBoxPos
from monumenta_common import getBox
from monumenta_common import getBoxMaterial
from monumenta_common import getBoxMaterialName

################################################################################
# Functions that display stuff while they work

def fillRegions(worldFolder,coordinatesToScan):
    """ Fill all regions with specified blocks to demonstrate coordinates """
    world = mclevel.loadWorld(worldFolder)

    # Fill the selected regions for debugging reasons
    for fillRegion in coordinatesToScan:
        boxName = getBoxName(fillRegion)
        boxMaterial = getBoxMaterial(fillRegion)
        boxMaterialName = getBoxMaterialName(fillRegion)
        print "Filling " + boxName + " with " + boxMaterialName + "..."
        box = getBox(fillRegion)
        block = world.materials[boxMaterial]
        world.fillBlocks(box, block)

    print "Saving...."
    world.generateLights()
    world.saveInPlace()

def rename(worldFolder,coordinatesToScan,renameList):
    print "Beginning scan..."
    world = mclevel.loadWorld(worldFolder)

    scanNum = 1
    scanMax = len(coordinatesToScan)

    allChunks = set(world.allChunks)
    for aScanBox in coordinatesToScan:
        boxName = getBoxName(aScanBox)
        print "[{0}/{1}] Scaning {2}...".format(scanNum,scanMax,boxName)

        scanBox = getBox(aScanBox)

        # The function world.getTileEntitiesInBox() does not work.
        # Working around it, since it works for chunks but not worlds.
        selectedChunks = set(scanBox.chunkPositions)
        chunksToScan = list(selectedChunks.intersection(allChunks))
        for cx,cz in chunksToScan:
            markDirty = False

            # Get and loop through entities within chunk and box
            aChunk = world.getChunk(cx,cz)
            tileEntities = aChunk.getTileEntitiesInBox(scanBox)
            for aTileEntity in tileEntities:
                # Check if tileEntity is being scanned
                if aTileEntity["id"].value == "minecraft:structure_block":
                    structureName = aTileEntity["name"].value.decode("unicode-escape")

                    for aReplacement in renameList:
                        old = aReplacement[0]
                        new = aReplacement[1]
                        if structureName[:len(old)] == old:
                            newName = new + structureName[len(old):]
                            newName = newName.encode("unicode-escape")
                            if structureName != newName:
                                aTileEntity["name"].value = newName
                                markDirty = True

            if markDirty:
                aChunk.chunkChanged(False) # needsLighting=False

    world.saveInPlace()
    print "Finished renaming items in world, now moving files."
    # If this part doesn't work, feel free to come up with your own solution.

    for aReplacement in renameList:
        oldPrefix = aReplacement[0]
        oldDir = worldFolder+"structures/"+oldPrefix
        temp = oldDir.rfind("/")
        oldDir = oldDir[:temp+1]
        temp = oldPrefix.rfind("/")
        if temp != -1:
            oldPrefix = oldPrefix[temp+1:]

        newPrefix = aReplacement[1]
        newDir = worldFolder+"structures/"+newPrefix
        temp = newDir.rfind("/")
        newDir = newDir[:temp+1]
        temp = newPrefix.rfind("/")
        if temp != -1:
            newPrefix = newPrefix[temp+1:]

        if not os.path.exists(newDir):
            os.makedirs(newDir)

        for aFile in os.listdir(oldDir):
            if aFile[:len(oldPrefix)] == oldPrefix:
                fromFile = oldDir+aFile
                toFile = newDir+newPrefix+aFile[len(oldPrefix):]

                os.rename(fromFile, toFile)

    print "Done."

