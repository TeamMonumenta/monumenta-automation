#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required libraries have links where not part of a standard Python install.
import os
import sys
import shutil

# The effective working directory for this script must always be the MCEdit-Unified directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))

import pymclevel
from pymclevel import materials
from pymclevel.block_copy import copyBlocksFromIter
from pymclevel.box import BoundingBox, Vector
from pymclevel.mclevelbase import exhaust

################################################################################
# Config section

config = {
    "dungeonFolder":"/home/rock/tmp/Project_Epic-dungeon/",
    "templateFolder":"/home/rock/tmp/Project_Epic-template/",
    "outFolder":"/home/rock/tmp/dungeons-out/",

    # Dungeons are placed one per MC region file (32x32 chunks)
    # Each dungeon starts in the most-negative corner of the region
    # Regions with dungeons form a line of consecutive regions in +z
    #
    # Each region containing a dungeon is full of void biome
    # There is a padding layer of void biome in the -x and -z directions as specified below
    #
    # All dungeons fit in a region file; even corrupted sierhaven is only 30x24 chunks

    "dungeons":(
        {
            "name":"white",
            "size":(160, 256, 352),
            "region":{"x":-3, "z":-2},
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 0), "materialName":"white wool"},
            )
        },{
            "name":"orange",
            "size":(320, 120, 352),
            "region":{"x":-3, "z":-1},
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 1), "materialName":"orange wool"},
            )
        },{
            "name":"magenta",
            "size":(256, 256, 256),
            "region":{"x":-3, "z":0},
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 2), "materialName":"magenta wool"},
            )
        },{
            "name":"lightblue",
            "size":(288, 256, 272),
            "region":{"x":-3, "z":1},
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 3), "materialName":"light blue wool"},
            )
        },{
            "name":"yellow",
            "size":(256, 256, 256),
            "region":{"x":-3, "z":2},
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 4), "materialName":"yellow wool"},
            )
        },{
            "name":"r1bonus",
            "size":(288, 93, 368),
            "region":{"x":-3, "z":3},
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(18, 4), "materialName":"oak leaves"},
            )
        },
    ),

    # 16 chunks of void-biome padding on the -x and -z sides
    "voidPadding":16,

    # Dungeons placed in region -3,-2 - a region is 32x32 chunks
    "targetRegion":{"x":-3, "z":-2},

    # Number of dungeons
    "numDungeons":50,
}

################################################################################
# TODO: Dictionary functions to move to common

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

def fillBoxes(world, coordinatesToFill):
    """ Fill all boxes with specified blocks """

    # Fill the selected regions
    for fillBox in coordinatesToFill:
        shouldReplaceBlocks = fillBox["replace"]
        if shouldReplaceBlocks:
            boxName = fillBox["name"]
            boxMaterial = fillBox["material"]
            boxMaterialName = fillBox["materialName"]
            print "    Filling " + boxName + " with " + boxMaterialName + "..."
            box = getBox(fillBox["pos1"], fillBox["pos2"])
            block = world.materials[boxMaterial]
            world.fillBlocks(box, block)

def copyFolder(old, new):
    shutil.rmtree(new, ignore_errors=True)
    shutil.copytree(old, new, symlinks=True)

################################################################################
# Function definitions

def gen_dungeon_instances(config):
    dungeonFolder = config["dungeonFolder"]
    templateFolder = config["templateFolder"]
    outFolder = config["outFolder"]
    dungeons = config["dungeons"]
    voidPadding = config["voidPadding"]
    targetRegion = config["targetRegion"]
    numDungeons = config["numDungeons"]

    # Fail if folders don't exist
    if not os.path.isdir(dungeonFolder):
        sys.exit("Dungeon reference folder does not exist.")
    if not os.path.isdir(templateFolder):
        sys.exit("Template world folder does not exist.")

    print "Opening dungeon reference world..."
    referenceWorld = pymclevel.loadWorld(dungeonFolder)

    for dungeon in dungeons:
        dungeonName = dungeon["name"]
        dungeonRegion = dungeon["region"]
        dungeonSize = Vector(*dungeon["size"])
        dungeonPos = Vector(*(dungeonRegion["x"] * 32 * 16, 0, dungeonRegion["z"] * 32 * 16))
        dungeonBox = BoundingBox(dungeonPos, dungeonSize)
        dstFolder = outFolder + dungeonName + '/Project_Epic-' + dungeonName + '/'

        dstPos = Vector(*(targetRegion["x"] * 32 * 16, 0, targetRegion["z"] * 32 * 16))
        dstStep = Vector(*(0, 0, 32 * 16))
        voidPos = dstPos + Vector(*(-1 * voidPadding * 16, 0, -1 * voidPadding * 16))
        voidSize = Vector(*((32 + voidPadding) * 16, 256, (32 * numDungeons + voidPadding) * 16))
        voidBox = BoundingBox(voidPos, voidSize)

        blocksToCopy = range(materials.id_limit)

        #print dungeonName
        #print dungeonRegion
        #print dungeonSize
        #print dungeonPos
        #print dungeonBox
        #print dstPos
        #print dstStep
        #print voidPos
        #print voidSize
        #print voidBox

        print "Starting work on dungeon: " + dungeonName

        print "  Copying template world as base..."
        copyFolder(templateFolder, dstFolder)

        print "  Opening dungeon world..."
        dstWorld = pymclevel.loadWorld(dstFolder)

        print "  Creating void chunks..."
        chunksCreated = dstWorld.createChunksInBox(voidBox)
        print "    Created {0} chunks." .format(len(chunksCreated))

        print "  Changing all chunks to void biome..."
        for aChunk in dstWorld.getChunks():
            aChunk.root_tag["Level"]["Biomes"].value.fill(127)
            aChunk.chunkChanged(True)

        print "  Creating dungeon instances..."
        for i in range(numDungeons):
            print "    {0}...".format(i)

            exhaust(copyBlocksFromIter(destLevel=dstWorld, sourceLevel=referenceWorld, sourceBox=dungeonBox,
                                       destinationPoint=(dstPos + dstStep * i), blocksToCopy=blocksToCopy,
                                       entities=True, create=True, biomes=True, tileTicks=True,
                                       staticCommands=False, moveSpawnerPos=False, regenerateUUID=True,
                                       first=False, cancelCommandBlockOffset=False)) # Not sure what these last two do - defaults

        # Note resetting difficulty is unnecessary - all generated chunks
        #   lack the time inhabited tag
        # print "  Resetting difficulty..."
        # resetRegionalDifficulty(dstWorld)

        print "  Filling regions..."
        fillBoxes(dstWorld, dungeon["coordinatesToFill"])

        print "  Saving...."
        dstWorld.generateLights()
        dstWorld.saveInPlace()

        try:
            shutil.rmtree(dstFolder + "##MCEDIT.TEMP##", ignore_errors=True)
            shutil.rmtree(dstFolder + "playerdata", ignore_errors=True)
            shutil.rmtree(dstFolder + "advancements", ignore_errors=True)
            shutil.rmtree(dstFolder + "stats", ignore_errors=True)
            os.remove(dstFolder + "mcedit_waypoints.dat")
        except Exception as e:
            continue

    sys.exit(0)

    print "Done!"


gen_dungeon_instances(config)

