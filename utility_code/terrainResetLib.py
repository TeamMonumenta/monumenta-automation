#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).

This does so as directly as possible while providing many features.
Entities within the build world that are in areas copied from the
main world are removed.
Scoreboard values are maintained from the play area.
Players are teleported to safety

Fair warning, some of the optimization is done by removing error handling.
Python will tell you if/when the script crashes.
If it's going to crash, it won't damage the original worlds.
Just fix what broke, and run again.

In progress:
Universal item replacement/deletion, for when an item is outdated.

Current task:
convert MCEdit's NBT notation to string and vice versa (vanilla command style)

Planned:
Preservation of map items from both worlds (requires item replacement).
1.13 support (will start writing changes during snapshots)

Unused features:
A block replacement list and functions to use them
are provided, and were used for testing.

Known bugs:
When testing this on single player worlds, the inventory from
    the build world is seemingly kept over the main one.
    This is because single player keeps track of the only player
    differently from multiplayer (level.dat I think).
    Player data is still transfered correctly, but is overwritten
    by the single player player data.
    This will not occur for server files.
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
from mclevel import nbt
from mclevel.box import BoundingBox, Vector

import itemReplaceLib
import itemReplaceList

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
    for aMovingBox in movingBoxList:
        boxList.append(getBox(aMovingBox))
    return tuple(boxList) # turn the list into a tuple, write-protecting it

def filesInBox(aBox):
    # returns a list of (x,z) pairs in terms of .mca files
    # Useful for reducing the number of files being transfered.
    # Untested, but should work.
    
    return itertools.product( xrange(self.minx >> 9, self.maxx >> 9),
                              xrange(self.minz >> 9, self.maxz >> 9))

def replace(world,oldBlock,newBlock,box=None):
    world.fillBlocks(box, newBlock, blocksToReplace=[oldBlock])

def replaceSeveral(world,replaceList,boxList):
    # replace everything in replaceList within all boxes in boxList
    # For materials, see levl.materials[] in materials.py, line 119
    # "Let's be magic." - finds the right material from several formats
    # For whatever reason, does not take idStr (ie minecraft:log)
    for aBox in boxList:
        for replacePair in replaceList:
            oldBlock = world.materials[replacePair[0]]
            newBlock = world.materials[replacePair[1]]
            replace(world,oldBlock,newBlock,aBox)

def movePlayers(worldFolder,point):
    """ Moves all players to the same location """
    # world.players returns an empty list for multiplayer worlds?
    # Lovely. Mojang changed the player data folder from world/player
    # to world/playerdata when they changed the files to be UUIDs.
    # Weird that pymclevel wasn't updated for that years ago.
    for aPlayerFile in os.listdir(worldFolder+"/playerdata"):
        aPlayerFile = worldFolder+"/playerdata/"+aPlayerFile
        aPlayer = nbt.load(aPlayerFile)
        
        # Set they players' position
        aPlayer["Pos"][0].value = point[0]
        aPlayer["Pos"][1].value = point[1]
        aPlayer["Pos"][2].value = point[2]
        
        # Face players the right way
        aPlayer["Rotation"][0].value = point[3]
        aPlayer["Rotation"][1].value = point[4]
        
        # We don't want players being flung around after a terrain reset
        aPlayer["FallDistance"].value = 0.0
        aPlayer["Motion"][0].value = 0.0
        aPlayer["Motion"][1].value = 0.0
        aPlayer["Motion"][2].value = 0.0
        
        # What if they reached the end dimention?
        # Yes....let them fall into the void...yes... >:D ....nah, I'll be nice.
        aPlayer["Dimension"].value = 0
        
        # Welcome to the ultimate healthcare service, here's your weekly checkup
        aPlayer["Fire"].value = -20
        aPlayer["Air"].value = 300
        aPlayer["foodLevel"].value = 20
        aPlayer["foodSaturationLevel"].value = 5.0
        aPlayer["foodExhaustionLevel"].value = 0.0
        aPlayer["Health"].value = 20.0
        aPlayer["DeathTime"].value = 0
        
        # save
        aPlayer.save(aPlayerFile)

def resetRegionalDifficulty(world):
    """ Resets the play time for the world, and the time in each chunk. """
    world.root_tag["Data"]["Time"].value = 0
    for aChunk in world.getChunks():
        aChunk.root_tag["Level"]["InhabitedTime"].value = 0

################################################################################
# Functions that display stuff while they work

def copyFile(old,new):
    os.remove(new)
    shutil.copy2(old, new)

def copyFolder(old,new):
    shutil.rmtree(new, True)
    shutil.copytree(old, new)

def copyFolders(old,new,subfolders):
    for folder in subfolders:
        print "Copying " + folder + "..."
        copyFolder(old+folder, new+folder)

def replaceBlocksInBoxList(config,replaceList,coordinatesToCopy,worldStr):
    localMainFolder = config["localMainFolder"]
    localBuildFolder = config["localBuildFolder"]
    localDstFolder = config["localDstFolder"]
    SafetyTpLocation = config["SafetyTpLocation"]
    coordinatesToCopy = config["coordinatesToCopy"]
    
    print "Opening world..."
    if worldStr == "main":
        world = mclevel.loadWorld(localMainFolder)
    elif worldStr == "build":
        world = mclevel.loadWorld(localBuildFolder)
    else:
        return
    
    boxList = getBoxList(coordinatesToCopy)
    
    print "Replacing blocks..."
    replaceSeveral(world,replaceList,boxList)
    
    print "Saving..."
    world.generateLights()
    world.saveInPlace()
    
    print "Done."

def replaceBlocksGlobally(config,replaceList,worldStr):
    localMainFolder = config["localMainFolder"]
    localBuildFolder = config["localBuildFolder"]
    localDstFolder = config["localDstFolder"]
    SafetyTpLocation = config["SafetyTpLocation"]
    coordinatesToCopy = config["coordinatesToCopy"]
    
    print "Opening world..."
    if worldStr == "main":
        world = mclevel.loadWorld(localMainFolder)
    elif worldStr == "build":
        world = mclevel.loadWorld(localBuildFolder)
    else:
        return
    
    print "Replacing blocks..."
    
    replaceNum = 1 # used only for display
    replaceMax = len(replaceList)
    
    for replacePair in replaceList:
        oldBlock = world.materials[replacePair[0]]
        newBlock = world.materials[replacePair[1]]
        
        print "[{0}/{1}]: {2} -> {3}".format(replaceNum,replaceMax,
                                             replacePair[0],replacePair[1])
        replaceNum += 1
        
        replace(world,oldBlock,newBlock)
    
    print "Saving..."
    world.generateLights()
    world.saveInPlace()
    
    print "Done."

def copyBoxes(config,blockReplaceList,itemReplaceList):
    localMainFolder = config["localMainFolder"]
    localBuildFolder = config["localBuildFolder"]
    localDstFolder = config["localDstFolder"]
    SafetyTpLocation = config["SafetyTpLocation"]
    coordinatesToCopy = config["coordinatesToCopy"]
    
    print "Opening Source World..."
    srcWorld = mclevel.loadWorld(localMainFolder)
    
    print "Handling item replacements for tile entities..."
    itemReplaceLib.replaceItemsInWorld(srcWorld,itemReplaceList)
    
    print "Opening Destination World..."
    dstWorld = mclevel.loadWorld(localDstFolder)
    
    print "Beginning transfer..."
    copyNum = 1
    copyMax = len(coordinatesToCopy)
    blocksToCopy = range(materials.id_limit)
    
    # This is fine. The warning is known and can be ignored.
    warnings.filterwarnings("ignore", category=numpy.VisibleDeprecationWarning)
    
    for aCopy in coordinatesToCopy:
        print "[{0}/{1}] Copying {2}...".format(copyNum,copyMax,aCopy[0])
        
        pos = getBoxPos(aCopy)
        box = getBox(aCopy)
        
        tempSchematic = srcWorld.extractSchematic(box)
        
        # Edit the schematic while copying
        for blockReplacement in blockReplaceList:
            oldBlock = tempSchematic.materials[blockReplacement[0]]
            newBlock = tempSchematic.materials[blockReplacement[1]]
            replace(tempSchematic,oldBlock,newBlock)
        
        # Remove entities in destination
        dstWorld.removeEntitiesInBox(box)
        
        # Copy the schematic with edits in place
        dstWorld.copyBlocksFrom(tempSchematic, BoundingBox((0, 0, 0), pos),
                                pos, blocksToCopy)
        
        copyNum+=1
    
    print "Resetting difficulty..."
    resetRegionalDifficulty(dstWorld)
    
    print "Saving...."
    dstWorld.generateLights()
    dstWorld.saveInPlace()
    
    print "Done."

def fillRegions(config):
    """ Fill all regions with specified blocks to demonstrate coordinates """
    
    localBuildFolder = config["localBuildFolder"]
    localDstFolder = config["localDstFolder"]
    coordinatesToCopy = config["coordinatesToCopy"]
    
    # Delete the dst world for a clean slate to start from
    shutil.rmtree(localDstFolder,True)
    
    # Copy the build world to the dst world
    shutil.copytree(localBuildFolder,localDstFolder)
    
    dstWorld = mclevel.loadWorld(localDstFolder)
    
    # Fill the selected regions for debugging reasons
    for fillRegion in coordinatesToCopy:
        print "Filling " + fillRegion[0] + " with " + fillRegion[4] + "..."
        box = getBox(fillRegion)
        block = dstWorld.materials[fillRegion[3]]
        dstWorld.fillBlocks(box, block)
    
    print "Saving...."
    dstWorld.generateLights()
    dstWorld.saveInPlace()

def terrainReset(config,blockReplaceList):
    """
    This is it! I'll try to improve this when I can. Ideas welcome!
    - NickNackGus
    """
    keepPlayerMapItems = False # Working on it!
    
    localMainFolder = config["localMainFolder"]
    localBuildFolder = config["localBuildFolder"]
    localDstFolder = config["localDstFolder"]
    SafetyTpLocation = config["SafetyTpLocation"]
    coordinatesToCopy = config["coordinatesToCopy"]
    
    print "Compiling item replacement list..."
    itemReplacementList = itemReplaceLib.allReplacements( itemReplaceList.itemReplacements )
    
    # Copy the build world to the dst world
    print "Copying build world as base..."
    copyFolder(localBuildFolder,localDstFolder)
    
    # Copy various bits of player data from the main world
    folderList = [
        "advancements/",
        "playerdata/",
        "stats/",
    ]
    print "Copying files from main world..."
    copyFolders(localMainFolder, localDstFolder, folderList)
    
    if keepPlayerMapItems:
        # Copy various bits of player data from the main world
        folderList = [
            "data/",
        ]
        copyFolders(localMainFolder, localDstFolder, folderList)
        
        # Copy data/functions and data/advancements from the build world
        folderList = [
            "data/advancements",
            "data/functions",
        ]
        print "Copying files from build world..."
        copyFolders(localBuildFolder, localDstFolder, folderList)
    else: # Remove player map item data
        # Copy scoreboard from the main world
        print "Copying data/scoreboard.dat from main world..."
        copyFile(localMainFolder+"data/scoreboard.dat",
                 localDstFolder+"data/scoreboard.dat")
    
    print "Copying needed terrain from the main world..."
    copyBoxes(config,blockReplaceList,itemReplacementList)
    
    print "Moving players..."
    movePlayers(localDstFolder,SafetyTpLocation)
    
    print "Handling item replacements for players..."
    itemReplaceLib.replaceItemsOnPlayers(localDstFolder,itemReplacementList)
    
    print "Done!"


