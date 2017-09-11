#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This lists the tile entities that lack
a loot table within a box, filtering by type.
"""
# Required libraries have links where not part of a standard Python install.
import os
import shutil

# These are expected in your site-packages folder, see:
# https://stackoverflow.com/questions/31384639/what-is-pythons-site-packages-directory
import mclevel # from https://github.com/mcedit/pymclevel
from mclevel import mclevelbase
from mclevel import materials
from mclevel.box import BoundingBox, Vector
from mclevel import nbt

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
    elif aTileEntity["LootTable"].value in emptyLootTables:
        return False
    return True

def hasLootTableSeed(aTileEntity):
    if "LootTableSeed" not in aTileEntity:
        return False
    elif aTileEntity["LootTableSeed"].value == 0:
        return False
    return True

################################################################################
# Functions that display stuff while they work

def fillRegions(worldFolder,coordinatesToScan):
    """ Fill all regions with specified blocks to demonstrate coordinates """
    world = mclevel.loadWorld(worldFolder)
    
    # Fill the selected regions for debugging reasons
    for fillRegion in coordinatesToScan:
        print "Filling " + fillRegion[0] + " with " + fillRegion[4] + "..."
        box = getBox(fillRegion)
        block = world.materials[fillRegion[3]]
        world.fillBlocks(box, block)
    
    print "Saving...."
    world.generateLights()
    world.saveInPlace()

def listLootlessTileEntities(worldFolder,coordinatesToScan,tileEntitiesToCheck,logFolder):
    print "Beginning scan..."
    world = mclevel.loadWorld(worldFolder)
    
    # Create/empty the log folder, containing all command blocks
    shutil.rmtree(logFolder, True)
    os.makedirs(logFolder)
    
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
    
    allChunks = set(world.allChunks)
    for aScanBox in coordinatesToScan:
        print "[{0}/{1}] Scaning {2}...".format(scanNum,scanMax,aScanBox[0])
        
        # Make appropriate folder
        logFile = logFolder+"/"+aScanBox[0]+".txt"
        
        scanBox = getBox(aScanBox)
        
        for cmdBlockType in tileEntitiesToCheck:
            strBuffer = ""
            
            if cmdBlockType == "other":
                strBuffer += "These command block tile entities do not appear to be in the same block as a command block - might be a bug?\n\n"
            
            f = open(logFile,"w")
            f.write(strBuffer)
            f.close()
        
        # The function world.getTileEntitiesInBox() does not work.
        # Working around it, since it works for chunks but not worlds.
        selectedChunks = set(scanBox.chunkPositions)
        chunksToScan = list(selectedChunks.intersection(allChunks))
        for cx,cz in chunksToScan:
            
            # Get and loop through entities within chunk and box
            aChunk = world.getChunk(cx,cz)
            newTileEntities = aChunk.getTileEntitiesInBox(scanBox)
            for aTileEntity in newTileEntities:
                
                # Check if tileEntity is being scanned
                if aTileEntity["id"].value in tileIDList:
                    
                    # Detect missing loot table
                    if not hasLootTable(aTileEntity):
                        lootless.append(aTileEntity)
                    
                    # Detect fixed loot table seeds
                    elif hasLootTableSeed(aTileEntity):
                        print aTileEntity.json
                        lootless.append(aTileEntity)
                    
                    elif "LootTableSeed" in aTileEntity:
                        print aTileEntity
            
            if len(lootless):
                strBuffer = ""
                
                while len(lootless):
                    aTileEntity = lootless.pop()
                    
                    tileEntityID = aTileEntity["id"].value
                    x = aTileEntity["x"].value
                    y = aTileEntity["y"].value
                    z = aTileEntity["z"].value
                    
                    strBuffer += "{0} at ({1},{2},{3}) ".format(tileEntityID,x,y,z)
                    if not hasLootTable(aTileEntity):
                        strBuffer += "has no loot table set.\n"
                    elif hasLootTableSeed(aTileEntity):
                        strBuffer += "has a fixed loot table seed.\n"
                
                f = open(logFile,"a")
                f.write(strBuffer)
                f.close()
    

