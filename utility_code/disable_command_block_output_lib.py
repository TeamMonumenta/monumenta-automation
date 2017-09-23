#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This lists the tile entities that lack
a loot table within a box, filtering by type.
"""
# Required libraries have links where not part of a standard Python install.
import os

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

def run(worldFolder,coordinatesToScan):
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
            chunkDirty = False
            
            # Get and loop through entities within chunk and box
            aChunk = world.getChunk(cx,cz)
            newTileEntities = aChunk.getTileEntitiesInBox(scanBox)
            for aTileEntity in newTileEntities:
                # Check if tileEntity is being scanned
                if aTileEntity["id"].value == "minecraft:command_block":
                    chunkDirty = True
                    aTileEntity["TrackOutput"].value = 0
                    if "LastOutput" in aTileEntity:
                        aTileEntity.pop("LastOutput")
            
            if chunkDirty:
                aChunk.chunkChanged(False) # needsLighting=False
    
    print "Saving..."
    world.saveInPlace()
    print "Done."

