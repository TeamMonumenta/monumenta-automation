#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import warnings
import shutil
import numpy
import contextlib
import tempfile

from pymclevel import materials
from pymclevel.box import BoundingBox, Vector
from pymclevel import nbt

################################################################################
# Functions that do not require dictionaries as arguments

def getBoxSize(pos1, pos2):
    # Get the size of a box from
    # an element of coordinatesToScan
    sizeFix = Vector(*(1,1,1))
    min_pos = Vector(*map(min, zip(pos1, pos2)))
    max_pos = Vector(*map(max, zip(pos1, pos2)))
    return max_pos - min_pos + sizeFix

def getBoxMinPos(pos1, pos2):
    # Get the origin of a box from
    # an element of coordinatesToScan
    return Vector(*map(min, zip(pos1, pos2)))

def getBox(pos1, pos2):
    # Returns a box around from
    # an element of coordinatesToScan
    origin = getBoxMinPos(pos1, pos2)
    size   = getBoxSize(pos1, pos2)

    return BoundingBox(origin, size)

def replace(world, oldBlock, newBlock, box=None):
    world.fillBlocks(box, newBlock, blocksToReplace=[oldBlock], noData=True)

def replaceBlocksInBoxes(world, replaceList, boxList):
    for aBox in boxList:
        for replacePair in replaceList:
            oldBlock = world.materials[replacePair[0]]
            newBlock = world.materials[replacePair[1]]
            replace(world, oldBlock, newBlock, aBox)

def replaceGlobally(world, replaceList):
    for replacePair in replaceList:
        oldBlock = world.materials[replacePair[0]]
        newBlock = world.materials[replacePair[1]]
        replace(world, oldBlock, newBlock)

def copyFile(old, new):
    os.remove(new)
    if os.path.islink(old):
        linkto = os.readlink(old)
        os.symlink(linkto, new)
    else:
        shutil.copy2(old, new)

# Create a temporary directory which is automatically removed afterwards, even if the script crashes
# Use like:
#    with tempdir() as tempDungeonRefCopy:
#        <code using the folder tempDungeonRefCopy>
@contextlib.contextmanager
def tempdir():
    dirpath = tempfile.mkdtemp()
    try:
        yield dirpath
    finally:
        shutil.rmtree(dirpath)

def copyFolder(old, new):
    # This does not check if it's a path or a file, but there's another function for that case.
    if os.path.exists(old):
        shutil.rmtree(new, ignore_errors=True)
        shutil.copytree(old, new, symlinks=True)
    else:
        print "*** '{}' does not exist, preserving original.".format(old)

def copyFolders(old, new, subfolders):
    for folder in subfolders:
        print "    Copying " + folder + "..."
        try:
            copyFolder(old+folder, new+folder)
        except:
            print "*** " + folder + " could not be copied, may not exist."

""" Moves all players to the same location """
def movePlayers(worldFolder, safetyTpLocation):
    # world.players returns an empty list for multiplayer worlds?
    # Lovely. Mojang changed the player data folder from world/player
    # to world/playerdata when they changed the files to be UUIDs.
    # Weird that pymclevel wasn't updated for that years ago.
    for aPlayerFile in os.listdir(worldFolder+"/playerdata"):
        aPlayerFile = worldFolder+"/playerdata/"+aPlayerFile
        aPlayer = nbt.load(aPlayerFile)

        # Set they players' position
        aPlayer["Pos"][0].value = safetyTpLocation[0]
        aPlayer["Pos"][1].value = safetyTpLocation[1]
        aPlayer["Pos"][2].value = safetyTpLocation[2]

        # Face players the right way
        aPlayer["Rotation"][0].value = safetyTpLocation[3]
        aPlayer["Rotation"][1].value = safetyTpLocation[4]

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

        # Reset player spawn location (beds and /spawnpoint)
        if "SpawnX" in aPlayer:
            aPlayer.pop("SpawnX")
        if "SpawnY" in aPlayer:
            aPlayer.pop("SpawnY")
        if "SpawnZ" in aPlayer:
            aPlayer.pop("SpawnZ")
        if "SpawnForced" in aPlayer:
            aPlayer.pop("SpawnForced")

        # save
        aPlayer.save(aPlayerFile)

""" Resets the play time for the world, and the time in each chunk. """
def resetRegionalDifficulty(world):

    num_reset = 0
    num_missing_level_tag = 0
    num_missing_inhabited_tag = 0
    num_other_error = 0

    # This is the time the world has been played, not the in-game time.
    try:
        world.root_tag["Data"]["Time"].value = 0
    except:
        print 'The world does not have a "Time" tag.'

    for aChunk in world.getChunks():
        try:
            aChunk.root_tag["Level"]["InhabitedTime"].value = 0
            num_reset = num_reset + 1
        except:
            if "Level" not in aChunk.root_tag:
                num_missing_level_tag = num_missing_level_tag + 1
                # print 'Chunk ' + str(aChunk.chunkPosition) + ' does not have "Level" in its tags'
            elif "InhabitedTime" not in aChunk.root_tag["Level"]:
                num_missing_inhabited_tag = num_missing_inhabited_tag + 1
                # print 'Chunk ' + str(aChunk.chunkPosition) + ' does not have "InhabitedTime" in its "Level" tag'
            else:
                num_other_error = num_other_error + 1
                # print 'Unexpected error changing "InhabitedTime" in chunk ' + str(aChunk.chunkPosition)

    print "  {0} chunks reset, {1} missing level tag, {2} missing inhabited tag, {3} other errors".format(num_reset, num_missing_level_tag, num_missing_inhabited_tag, num_other_error)

################################################################################
# Functions that require dictionaries as arguments

"""
Fills a list of boxes with their specified blocks
coordinatesToFill should be an iterable tuple or list of dictionaries, like this:

(
    {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
        "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
    {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
        "replaceBlocks":True, "material":(35, 0), "materialName":"white wool"},
)
"""
def fillBoxes(world, coordinatesToFill):
    copyNum = 1
    copyMax = len(coordinatesToFill)

    for fillBox in coordinatesToFill:
        replaceBlocks = fillBox["replaceBlocks"]
        if replaceBlocks:
            boxName = fillBox["name"]
            boxMaterial = fillBox["material"]
            boxMaterialName = fillBox["materialName"]
            box = getBox(fillBox["pos1"], fillBox["pos2"])
            block = world.materials[boxMaterial]

            print "    [{0}/{1}] Filling {2} with {3}".format(copyNum, copyMax, boxName, boxMaterialName)
            world.fillBlocks(box, block)

def copyBoxes(srcWorld, dstWorld, coordinatesToCopy, blockReplacements, itemReplacements):
    """
    Copies a box from srcWorld to dstWorld at the same location, preserving entities
    coordinatesToCopy should be an iterable tuple or list of dictionaries, like this:
    (
        {"name":"Section_1", "pos1":(-1130, 0, -267), "pos2":(-897, 255,  318), "replaceBlocks":True, "material":( 41, 0), "materialName":"gold"),
        {"name":"Section_2", "pos1":( -896, 0,  208), "pos2":(-512, 255,  318), "replaceBlocks":True, "material":( 57, 0), "materialName":"diamond"),
    )
    If "replaceBlocks" == True, then block replacements will be done according to blockReplacements
    If "replaceItems" == True, then item replacements will be done according to itemReplacements
    """
    copyNum = 1
    copyMax = len(coordinatesToCopy)
    blocksToCopy = range(materials.id_limit)

    # This is fine. The warning is known and can be ignored.
    warnings.filterwarnings("ignore", category=numpy.VisibleDeprecationWarning)

    for copyBox in coordinatesToCopy:
        boxName = copyBox["name"]
        pos = getBoxMinPos(copyBox["pos1"], copyBox["pos2"])
        box = getBox(copyBox["pos1"], copyBox["pos2"])
        replaceBlocks = ("replaceBlocks" in copyBox) and (copyBox["replaceBlocks"] is True)
        replaceItems = ("replaceBlocks" in copyBox) and (copyBox["replaceItems"] is True)

        print "    [{0}/{1}] Copying {2}...".format(copyNum, copyMax, boxName)

        tempSchematic = srcWorld.extractSchematic(box, entities=True)

        # Replace blocks if needed
        if replaceBlocks and (blockReplacements is not None):
            print "    [{0}/{1}]   Replacing specified blocks in {2}...".format(copyNum,copyMax,boxName)
            replaceGlobally(tempSchematic, blockReplacements)

        # Replace items if needed
        if replaceItems and (itemReplacements is not None):
            print "    [{0}/{1}]   Handling item replacements for tile entities in {2}...".format(copyNum,copyMax,boxName)
            itemReplacements.InSchematic(tempSchematic)

        # Remove entities in destination
        dstWorld.removeEntitiesInBox(box)

        # Copy the schematic with edits in place
        dstWorld.copyBlocksFrom(tempSchematic, tempSchematic.bounds, pos, blocksToCopy, entities=True)

        copyNum+=1

def lockTileEntities(world, box, tileIDList):
    # The function world.getTileEntitiesInBox() does not work.
    # Working around it, since it works for chunks but not worlds.
    allChunks = set(world.allChunks)

    selectedChunks = set(box.chunkPositions)
    chunksToScan = list(selectedChunks.intersection(allChunks))
    for cx,cz in chunksToScan:
        # Get and loop through entities within chunk and box
        aChunk = world.getChunk(cx,cz)
        chunkDirty = False
        newTileEntities = aChunk.getTileEntitiesInBox(box)
        for aTileEntity in newTileEntities:

            # Check if tileEntity is being scanned
            if aTileEntity["id"].value in tileIDList:

                chunkDirty = True

                # Detect missing lock tag
                if ("Lock" not in aTileEntity):
                    # Add and set a lock tag
                    # String selection reasoning:
                    # - generated randomly
                    # - exceeds 32 character limit for anvil renaming
                    # - has a formatting code (obfuscate)
                    aTileEntity["Lock"] = nbt.Tag_STRING(u'''§kl{sC7v@6i-3g!% 22kTw?jhu.MML95,x?''')
                else:
                    # Set the lock tag
                    aTileEntity["Lock"].value = u'''§kl{sC7v@6i-3g!% 22kTw?jhu.MML95,x?'''

        if chunkDirty:
            aChunk.chunkChanged(False) # needsLighting=False

