#!/usr/bin/env python
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

################################################################################
# Function definitions

def getBoxSize(box):
    # Get the size of a box from
    # an element of coordinatesToScan
    sizeFix = Vector(*(1,1,1))
    min_pos = Vector(*map(min, zip(box[1], box[2])))
    max_pos = Vector(*map(max, zip(box[1], box[2])))
    return max_pos - min_pos + sizeFix

def getBoxPos(box):
    # Get the origin of a box from
    # an element of coordinatesToScan
    return Vector(*map(min, zip(box[1], box[2])))

def getBox(box):
    # Returns a box around from
    # an element of coordinatesToScan
    origin = getBoxPos(box)
    size   = getBoxSize(box)

    return BoundingBox(origin,size)

def getBoxList(movingBoxList):
    boxList = []
    for aScaningBox in movingBoxList:
        boxList.append(getBox(aScaningBox))
    return tuple(boxList) # turn the list into a tuple, write-protecting it

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

def run(worldFolder,coordinatesToScan,logFolder):
    print "Beginning scan..."
    world = mclevel.loadWorld(worldFolder)
    
    # Create/empty the log folder, containing all command blocks
    shutil.rmtree(logFolder, True)
    os.makedirs(logFolder)
    
    idCmdBlockImpulse = 137
    idCmdBlockRepeat = 210
    idCmdBlockChain = 211
    
    commandBlocks = {
        "impulse":[],
        "repeat":[],
        "chain":[],
        "other":[],
    }
    
    scanNum = 1
    scanMax = len(coordinatesToScan)
    
    allChunks = set(world.allChunks)
    for aScanBox in coordinatesToScan:
        print "[{0}/{1}] Scaning {2}...".format(scanNum,scanMax,aScanBox[0])
        
        # Make appropriate folder
        subFolder = logFolder+"/"+aScanBox[0]
        os.makedirs(subFolder)
        
        scanBox = getBox(aScanBox)
        
        for cmdBlockType in ["impulse","repeat","chain","other"]:
            strBuffer = ""
            
            if cmdBlockType == "other":
                strBuffer += "These command block tile entities do not appear to be in the same block as a command block - might be a bug?\n\n"
            
            strBuffer += "x, y, z, command\n\n"
            
            f = open(subFolder+"/"+cmdBlockType+".txt","w")
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
                if aTileEntity["id"].value == "minecraft:command_block":
                    x = aTileEntity["x"].value
                    y = aTileEntity["y"].value
                    z = aTileEntity["z"].value
                    
                    block = world.blockAt(x,y,z)
                    command = aTileEntity["Command"].value.decode("unicode-escape")
                    
                    if block == idCmdBlockImpulse:
                        commandBlocks["impulse"].append((x,y,z,command))
                    elif block == idCmdBlockRepeat:
                        commandBlocks["repeat"].append((x,y,z,command))
                    elif block == idCmdBlockChain:
                        commandBlocks["chain"].append((x,y,z,command))
                    else:
                        # Unknown command block tile entity - bug?
                        commandBlocks["other"].append((x,y,z,command))
            
            for cmdBlockType in ["impulse","repeat","chain","other"]:
                if len(commandBlocks[cmdBlockType]):
                    strBuffer = ""
                    
                    while len(commandBlocks[cmdBlockType]):
                        aCmdBlock = commandBlocks[cmdBlockType].pop()
                        
                        x = aCmdBlock[0]
                        y = aCmdBlock[1]
                        z = aCmdBlock[2]
                        cmd = str(aCmdBlock[3])
                        
                        strBuffer += "{0}, {1}, {2}, {3}\n".format(x,y,z,cmd)
                    
                    f = open(subFolder+"/"+cmdBlockType+".txt","a")
                    f.write(strBuffer)
                    f.close()
        
    print "Done."

