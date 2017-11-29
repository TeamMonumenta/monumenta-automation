#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import multiprocessing as mp
import tempfile

# The effective working directory for this script must always be the MCEdit-Unified directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
import pymclevel
from pymclevel import materials
from pymclevel.block_copy import copyBlocksFromIter
from pymclevel.box import BoundingBox, Vector
from pymclevel.mclevelbase import exhaust

from lib_monumenta.common import fillBoxes, copyFolder, tempdir
from lib_monumenta.list_lootless_tile_entities import listLootlessTileEntities

################################################################################
# Config section

config = {
    "dungeonRefFolder":"/home/rock/tmp/Project_Epic-dungeon/",
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
            ),
            "chestContentsLoreToIgnore":("Monument Block",),
            "chestWhitelist":(
                (-1409,  37, -776),
                (-1409,  37, -775),
                (-1443,  42, -828),
                (-1442,  42, -828),
                (-1458,  30, -816),
                (-1487,  71, -920),
                (-1529, 120, -975),
                (-1517,  32, -782),
                (-1387,  24, -756),
                (-1420,  42, -877),
            ),
        },{
            "name":"orange",
            "size":(320, 120, 352),
            "region":{"x":-3, "z":-1},
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 1), "materialName":"orange wool"},
            ),
            "chestContentsLoreToIgnore":("Monument Block",),
            "chestWhitelist":(),
        },{
            "name":"magenta",
            "size":(256, 256, 256),
            "region":{"x":-3, "z":0},
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 2), "materialName":"magenta wool"},
            ),
            "chestContentsLoreToIgnore":("Monument Block",),
            "chestWhitelist":(
                (-1381, 88, 91),
                (-1379, 88, 92),
            ),
        },{
            "name":"lightblue",
            "size":(288, 256, 272),
            "region":{"x":-3, "z":1},
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 3), "materialName":"light blue wool"},
            ),
            "chestContentsLoreToIgnore":("Monument Block", "D4 Key"),
            "chestWhitelist":(
                (-1381, 180, 645),
                (-1456, 170, 694),
                (-1371, 175, 598),
                (-1423, 178, 593),
                (-1265, 181, 598),
            ),
        },{
            "name":"yellow",
            "size":(256, 256, 256),
            "region":{"x":-3, "z":2},
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(35, 4), "materialName":"yellow wool"},
            ),
            "chestContentsLoreToIgnore":("Monument Block", "D5 Key"),
            "chestWhitelist":(
                (-1488,  65, 1086),
                (-1460,  90, 1239),
                (-1489,  65, 1087),
                (-1506, 103, 1165),
                (-1513,  40, 1152),
                (-1493,  65, 1095),
                (-1493,  65, 1096),
                (-1493,  63, 1094),
                (-1491,  65, 1089),
                (-1490,  65, 1088),
                (-1490,  65, 1098),
                (-1490,  63, 1098),
                (-1493,  40, 1094),
                (-1490,  42, 1098),
                (-1462, 140, 1104),
                (-1488,  65, 1098),
                (-1487,  65, 1098),
                (-1486,  63, 1098),
                (-1455, 104, 1178),
            ),
        },{
            "name":"r1bonus",
            "size":(288, 93, 368),
            "region":{"x":-3, "z":3},
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replace":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replace":True, "material":(18, 4), "materialName":"oak leaves"},
            ),
            "chestContentsLoreToIgnore":(),
            "chestWhitelist":(),
        },
    ),

    # If using only one item, ALWAYS use a trailing comma.
    # Possible values: "chest" (trapped chest shares ID), "dispenser", "dropper", "shulker_box", "hopper"
    # These are actually namespaced; default is "minecraft:*" in this code.
    "tileEntitiesToCheck":("chest",),

    # 16 chunks of void-biome padding on the -x and -z sides
    "voidPadding":16,

    # Dungeons placed in region -3,-2 - a region is 32x32 chunks
    "targetRegion":{"x":-3, "z":-2},

    # Number of dungeons
    "numDungeons":1,
}

def gen_dungeon_instance(config, dungeon, outputFile):
    # Redirect output to specified file
    sys.stdout = open(outputFile, "w")

    # Global config
    dungeonRefFolder = config["dungeonRefFolder"]
    templateFolder = config["templateFolder"]
    outFolder = config["outFolder"]
    voidPadding = config["voidPadding"]
    targetRegion = config["targetRegion"]
    numDungeons = config["numDungeons"]
    tileEntitiesToCheck = config["tileEntitiesToCheck"]

    # Per-dungeon config
    dungeonName = dungeon["name"]
    dungeonRegion = dungeon["region"]
    dungeonSize = Vector(*dungeon["size"])
    dungeonContentsLoreToIgnore = dungeon["chestContentsLoreToIgnore"]
    dungeonChestWhitelist = dungeon["chestWhitelist"]
    dstFolder = outFolder + dungeonName + '/Project_Epic-' + dungeonName + '/'

    # Compute dungeon parameters
    dungeonPos = Vector(*(dungeonRegion["x"] * 32 * 16, 0, dungeonRegion["z"] * 32 * 16))
    dungeonBox = BoundingBox(dungeonPos, dungeonSize)
    dstPos = Vector(*(targetRegion["x"] * 32 * 16, 0, targetRegion["z"] * 32 * 16))
    dstStep = Vector(*(0, 0, 32 * 16))
    voidPos = dstPos + Vector(*(-1 * voidPadding * 16, 0, -1 * voidPadding * 16))
    voidSize = Vector(*((32 + voidPadding) * 16, 256, (32 * numDungeons + voidPadding) * 16))
    voidBox = BoundingBox(voidPos, voidSize)
    blocksToCopy = range(materials.id_limit)

    # Make a temporary copy of the dungeon template folder
    with tempdir() as tempDungeonRefCopy:
        copyFolder(dungeonRefFolder, tempDungeonRefCopy)

        print "Starting work on dungeon: " + dungeonName

        print "  Opening dungeon reference world..."
        referenceWorld = pymclevel.loadWorld(tempDungeonRefCopy)

        print "  Copying template world as base..."
        copyFolder(templateFolder, dstFolder)

        print "  Opening dungeon world..."
        dstWorld = pymclevel.loadWorld(dstFolder)

        print "  Scanning dungeon for chests without loot tables..."
        listLootlessTileEntities(referenceWorld, dungeonBox, tileEntitiesToCheck, dungeonContentsLoreToIgnore, dungeonChestWhitelist)

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

        # Note resetting difficulty is unnecessary - all generated chunks lack the time inhabited tag
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
            pass


# Multiprocessing implementation based on:
# http://sebastianraschka.com/Articles/2014_multiprocessing.html
def gen_dungeon_instances(config):
    dungeonRefFolder = config["dungeonRefFolder"]
    templateFolder = config["templateFolder"]
    dungeons = config["dungeons"]

    # Fail if folders don't exist
    if not os.path.isdir(dungeonRefFolder):
        sys.exit("Dungeon reference folder does not exist.")
    if not os.path.isdir(templateFolder):
        sys.exit("Template world folder does not exist.")


    processes = []
    outputFiles = []
    for dungeon in dungeons:
        outputFile = tempfile.mktemp()
        processes.append({
            "process":mp.Process(target=gen_dungeon_instance, args=(config, dungeon, outputFile)),
            "outputFile":outputFile,
        })

    for p in processes:
        p["process"].start()

    for p in processes:
        p["process"].join()
        logFile = open(p["outputFile"], "r")
        print logFile.read()
        logFile.close()

    print "Done!"

################################################################################
gen_dungeon_instances(config)

