#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required libraries have links where not part of a standard Python install.
import os
import sys
import shutil

# These are expected in your site-packages folder, see:
# https://stackoverflow.com/questions/31384639/what-is-pythons-site-packages-directory
import mclevel # from https://github.com/mcedit/pymclevel
from mclevel import materials
from mclevel.box import BoundingBox, Vector

from monumenta_common import copyFolder

################################################################################
# Config section

config = {
    "dungeonFolder":"/home/rock/tmp/Project_Epic-dungeon/",
    "templateFolder":"/home/rock/tmp/Project_Epic-template/",
    "outFolder":"/home/rock/tmp/out/",

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
            "name":"white", "pos1":(-2528, 0, -1296), "pos2":(-2369, 255, -945),
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 0), "materialName":"white wool"},
            )
        },{
            "name":"orange", "pos1":(-2336, 0, -1296), "pos2":(-2017, 119, -945),
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 1), "materialName":"orange wool"},
            )
        },{
            "name":"magenta", "pos1":(-1984, 0, -1296), "pos2":(-1729, 255, -1041),
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 2), "materialName":"magenta wool"},
            )
        },{
            "name":"lightblue", "pos1":(-1696, 0, -1296), "pos2":(-1409, 255, -1025),
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 3), "materialName":"light blue wool"},
            )
        },{
        #    "name":"yellow", "pos1":(-1376, 0, -1296), "pos2":(-1121, 255, -1041),
        #    "coordinatesToFill":(
        #        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
        #            "replace":True, "material":(0, 0), "materialName":"air"},
        #        {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
        #            "replace":True, "material":(35, 4), "materialName":"yellow wool"},
        #    )
        #},{
            "name":"r1bonus", "pos1":(-1088, 0, -1296), "pos2":(-801,  92,  -929),
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
    referenceWorld = mclevel.loadWorld(dungeonFolder)

    for dungeon in dungeons:
        dungeonName = dungeon["name"]
        dungeonBox = getBox(dungeon["pos1"], dungeon["pos2"])
        dstFolder = outFolder + dungeonName + '/Project_Epic-' + dungeonName + '/'

        dstPos = Vector(*(targetRegion["x"] * 32 * 16, 0, targetRegion["z"] * 32 * 16))
        dstStep = Vector(*(0, 0, 32 * 16))
        voidPos = dstPos + Vector(*(-1 * voidPadding * 16, 0, -1 * voidPadding * 16))
        voidSize = Vector(*((32 + voidPadding) * 16, 256, (32 * numDungeons + voidPadding) * 16))
        voidBox = BoundingBox(voidPos, voidSize)

        blocksToCopy = range(materials.id_limit)

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
        dstWorld = mclevel.loadWorld(dstFolder)

        print "  Copying dungeon schematic..."
        tempSchematic = referenceWorld.extractSchematic(dungeonBox, entities=True)
        #tempSchematic.saveToFile("/home/rock/" + dungeonName + ".schematic")

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
            dstWorld.copyBlocksFrom(tempSchematic, tempSchematic.bounds,
                                     dstPos + dstStep * i, blocksToCopy,
                                     create=True, entities=True, biomes=True)

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

