#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This lists the command block tile entities.
"""
import os
import sys

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from pymclevel-Unified
import pymclevel

from lib_monumenta.common import getBoxName, getBoxSize, getBoxPos, getBox
from lib_monumenta.common import getBox, getBoxMaterial, getBoxMaterialName
from lib_monumenta.iter_entity import IterEntities

################################################################################
# Functions that display stuff while they work

def run(worldFolder,coordinatesToScan,logFolder):
    print "Beginning scan..."
    world = pymclevel.loadWorld(worldFolder)

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
        boxName = getBoxName(aScanBox)
        print "[{0}/{1}] Scaning {2}...".format(scanNum,scanMax,boxName)

        # Make appropriate folder
        subFolder = logFolder+"/"+boxName
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

