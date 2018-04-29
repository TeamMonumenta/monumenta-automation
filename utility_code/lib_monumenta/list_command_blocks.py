#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
This lists the command block tile entities.
"""
import os
import shutil
import sys


# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from pymclevel-Unified
import pymclevel

from lib_monumenta.iter_entity import IterEntities

################################################################################
# Functions that display stuff while they work

idCmdBlockImpulse = 137
idCmdBlockRepeat = 210
idCmdBlockChain = 211

def _onEntity(args,entityDetails):
    # Check if tileEntity is being scanned
    commandBlocks = args["commandBlocks"]
    world = args["world"]
    entity = entityDetails["entity"]
    if entity["id"].value == "minecraft:command_block":
        x = entity["x"].value
        y = entity["y"].value
        z = entity["z"].value

        block = world.blockAt(x,y,z)
        command = entity["Command"].value

        if block == idCmdBlockImpulse:
            commandBlocks["impulse"].append((x,y,z,command))
        elif block == idCmdBlockRepeat:
            commandBlocks["repeat"].append((x,y,z,command))
        elif block == idCmdBlockChain:
            commandBlocks["chain"].append((x,y,z,command))
        else:
            # Unknown command block tile entity - bug?
            commandBlocks["other"].append((x,y,z,command))

def run(worldFolder,logFolder):
    print "Beginning scan..."
    world = pymclevel.loadWorld(worldFolder)

    # Create/empty the log folder, containing all command blocks
    shutil.rmtree(logFolder, True)
    os.makedirs(logFolder)

    commandBlocks = {
        "impulse":[],
        "repeat":[],
        "chain":[],
        "other":[],
    }

    args = {
        "world":world,
        "commandBlocks":commandBlocks,
    }

    for cmdBlockType in ["impulse","repeat","chain","other"]:
        strBuffer = ""

        if cmdBlockType == "other":
            strBuffer += "These command block tile entities do not appear to be in the same block as a command block - might be a bug?\n\n"

        strBuffer += "x, y, z, command\n\n"

        f = open(logFolder+"/"+cmdBlockType+".txt","w")
        f.write(strBuffer)
        f.close()

    # iterate over entities here
    cmdIter = IterEntities( ["block entities"], _onEntity, args )
    cmdIter.InWorld(world)

    for cmdBlockType in ["impulse","repeat","chain","other"]:
        if len(commandBlocks[cmdBlockType]):
            strBuffer = u""

            while len(commandBlocks[cmdBlockType]):
                aCmdBlock = commandBlocks[cmdBlockType].pop()

                x = aCmdBlock[0]
                y = aCmdBlock[1]
                z = aCmdBlock[2]
                cmd = unicode(aCmdBlock[3])

                strBuffer += u"{0}, {1}, {2}, {3}\n".format(x,y,z,cmd)

            f = open(logFolder+"/"+cmdBlockType+".txt","a")
            f.write(strBuffer.encode('utf8'))
            f.close()

    print "Done."

