#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This lists the tile entities that lack
a loot table within a box, filtering by type.
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
from mclevel.box import BoundingBox, Vector
from mclevel import nbt

import listLootlessTileEntities_config

################################################################################
# Config section

worldFolder = listLootlessTileEntities_config.worldFolder
coordinatesToScan = listLootlessTileEntities_config.coordinatesToScan
tileEntitiesToCheck = listLootlessTileEntities_config.tileEntitiesToCheck

################################################################################
# Function definitions

def getBoxSize(aScaningBox):
    # Get the size of a box from
    # an element of coordinatesToScan
    sizeFix   = Vector(*(1,1,1))
    origin = Vector(*aScaningBox[1])
    pos2   = Vector(*aScaningBox[2])
    return pos2 - origin + sizeFix

def getBoxPos(aScaningBox):
    # Get the origin of a box from
    # an element of coordinatesToScan
    return Vector(*aScaningBox[1])
  
def getBox(aScaningBox):
    # Returns a box around from
    # an element of coordinatesToScan
    origin = getBoxPos(aScaningBox)
    size   = getBoxSize(aScaningBox)
    
    return BoundingBox(origin,size)

def getBoxList(movingBoxList):
    boxList = []
    for aScaningBox in movingBoxList:
        boxList.append(getBox(aScaningBox))
    return tuple(boxList) # turn the list into a tuple, write-protecting it

def hasLootTable(aTileEntity):
    emptyLootTables = ("", "empty", "minecraft:", "minecraft:empty")
    if "LootTable" not in aTileEntity:
        return False
    elif aTileEntity["LootTable"]._value in emptyLootTables:
        return False
    return True

def hasLootTableSeed(aTileEntity):
    if "LootTableSeed" not in aTileEntity:
        return False
    elif aTileEntity["LootTableSeed"]._value == 0:
        return False
    return True

################################################################################
# Functions that display stuff while they work

def fillRegions():
    """ Fill all regions with specified blocks to demonstrate coordinates """
    buildWorld = mclevel.loadWorld(worldFolder)
    
    # Fill the selected regions for debugging reasons
    for fillRegion in coordinatesToScan:
        print "Filling " + fillRegion[0] + " with " + fillRegion[4] + "..."
        box = getBox(fillRegion)
        block = world.materials[fillRegion[3]]
        buildWorld.fillBlocks(box, block)
    
    print "Saving...."
    buildWorld.generateLights()
    buildWorld.saveInPlace()

def listLootlessTileEntities():
    print "Beginning scan..."
    buildWorld = mclevel.loadWorld(worldFolder)
    
    # Build tile ID list, adding default namespace if needed
    tileIDList = []
    for tileID in tileEntitiesToCheck:
        if ":" in tileID:
            tileIDList.append(tileID)
        else:
            tileIDList.append("minecraft:"+tileID)
    
    lootless = []
    scanNum = 1
    scanMax = len(coordinatesToScan)
    
    # This is fine. The warning is known and can be ignored.
    # warnings.filterwarnings("ignore", category=numpy.VisibleDeprecationWarning)
    
    for aScanBox in coordinatesToScan:
        print "[{0}/{1}] Scaning {2}...".format(scanNum,scanMax,aScanBox[0])
        
        scanBox = getBox(aScanBox)
        
        # The function buildWorld.getTileEntitiesInBox() does not work.
        # Working around it, since it works for chunks but not worlds.
        for cx,cz in scanBox.chunkPositions:
            
            # Get and loop through entities within chunk and box
            aChunk = buildWorld.getChunk(cx,cz)
            newTileEntities = aChunk.getTileEntitiesInBox(scanBox)
            for aTileEntity in newTileEntities:
                
                # Check if tileEntity is being scanned
                if aTileEntity["id"]._value in tileIDList:
                    
                    # Detect missing loot table
                    if not hasLootTable(aTileEntity):
                        lootless.append(aTileEntity)
                    
                    # Detect fixed loot table seeds
                    elif hasLootTableSeed(aTileEntity):
                        lootless.append(aTileEntity)
                    
                    elif "LootTableSeed" in aTileEntity:
                        print aTileEntity
        
        print "Found {0} lootless tile entities so far.".format(len(lootless))
        scanNum+=1
    
    print "{0} tile entities found without a loot table:".format(len(lootless))
    for aTileEntity in lootless:
        tileEntityID = aTileEntity["id"]._value
        x = aTileEntity["x"]._value
        y = aTileEntity["y"]._value
        z = aTileEntity["z"]._value
        theProblem = ""
        if not hasLootTable(aTileEntity):
            theProblem = "has no loot table set."
        elif hasLootTableSeed(aTileEntity):
            theProblem = "has a fixed loot table seed."
        print "{0} at ({1},{2},{3}) {4}".format(tileEntityID,x,y,z,theProblem)

################################################################################
# Main Code

# This shows where the selected regions are, as your old script does.
# WARNING: This version saves in place!
#fillRegions()

# This scans for tile entities that don't have a loot table
listLootlessTileEntities()



