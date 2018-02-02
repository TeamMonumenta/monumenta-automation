#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import multiprocessing as mp
import psutil
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

from lib_monumenta.common import fillBoxes, copyFolder, tempdir, resetRegionalDifficulty
from lib_monumenta.list_lootless_tile_entities import listLootlessTileEntities
from lib_monumenta.copy_region_file import copyRegion
from lib_monumenta.timing import timings

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
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(35, 0), "materialName":"white wool"},
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
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(35, 1), "materialName":"orange wool"},
            ),
            "chestContentsLoreToIgnore":("Monument Block",),
            "chestWhitelist":(),
        },{
            "name":"magenta",
            "size":(256, 256, 256),
            "region":{"x":-3, "z":0},
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(35, 2), "materialName":"magenta wool"},
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
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(35, 3), "materialName":"light blue wool"},
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
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(35, 4), "materialName":"yellow wool"},
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
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(18, 4), "materialName":"oak leaves"},
            ),
            "chestContentsLoreToIgnore":(),
            "chestWhitelist":(),
        },{
            "name":"roguelike",
            "size":(464, 101, 464),
            "region":{"x":-2, "z":-1},
            "numDungeons":400,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(213, 0), "materialName":"magma block"},
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
}

def gen_dungeon_instance(config, dungeon, outputFile):
    mainTiming = timings(enabled=True)
    nextStep = mainTiming.nextStep

    # Per-dungeon config
    dungeonName = dungeon["name"]

    # Redirect output to specified file
    sys.stdout = open(outputFile, "w")

    nextStep(dungeonName + ": Thread started")

    # Global config
    dungeonRefFolder = config["dungeonRefFolder"]
    templateFolder = config["templateFolder"]
    outFolder = config["outFolder"]
    voidPadding = config["voidPadding"]
    targetRegion = config["targetRegion"]
    tileEntitiesToCheck = config["tileEntitiesToCheck"]

    # Per-dungeon config
    dungeonName = dungeon["name"]
    dungeonRegion = dungeon["region"]
    dungeonSize = Vector(*dungeon["size"])
    dungeonContentsLoreToIgnore = dungeon["chestContentsLoreToIgnore"]
    dungeonChestWhitelist = dungeon["chestWhitelist"]
    numDungeons = dungeon["numDungeons"]
    dstFolder = outFolder + dungeonName + '/Project_Epic-' + dungeonName + '/'

    nextStep(dungeonName + ": Config read")

    # Compute dungeon parameters
    dungeonPos = Vector(*(dungeonRegion["x"] * 32 * 16, 0, dungeonRegion["z"] * 32 * 16))
    dungeonBox = BoundingBox(dungeonPos, dungeonSize)

    nextStep(dungeonName + ": pre-calc done")

    # Make a temporary copy of the dungeon template folder
    with tempdir() as tempDungeonRefCopy:
        nextStep(dungeonName + ": Temp folder created")
        copyFolder(dungeonRefFolder, tempDungeonRefCopy)
        print "Starting work on dungeon: " + dungeonName

        print "  Opening dungeon reference world..."
        referenceWorld = pymclevel.loadWorld(tempDungeonRefCopy)
        nextStep(dungeonName + ": Opened reference world")

        print "  Scanning dungeon for chests without loot tables..."
        listLootlessTileEntities(referenceWorld, dungeonBox, tileEntitiesToCheck, dungeonContentsLoreToIgnore, dungeonChestWhitelist)
        nextStep(dungeonName + ": Finished scan")

        print "  Copying template world as base..."
        copyFolder(templateFolder, dstFolder)
        nextStep(dungeonName + ": Copy done")

        print "  Creating dungeon instances..."
        oldRegionFile = tempDungeonRefCopy + "/region/r.{}.{}.mca".format(dungeonRegion["x"],dungeonRegion["z"])
        rx=targetRegion["x"]
        rzInit=targetRegion["z"]
        for i in range(numDungeons):
            print "    {0}...".format(i)
            rz = rzInit + i
            newRegionFile = dstFolder + "region/r.{}.{}.mca".format(rx,rz)
            copyRegion(oldRegionFile,newRegionFile,rx,rz)
        nextStep(dungeonName + ": Created instances")

        print "  Opening dungeon world..."
        dstWorld = pymclevel.loadWorld(dstFolder)
        nextStep(dungeonName + ": Opened world")

        print "  Filling regions..."
        fillBoxes(dstWorld, dungeon["coordinatesToFill"])
        nextStep(dungeonName + ": Filled regions")

        print "  Saving...."
        #dstWorld.generateLights() # Shouldn't be needed;
        # template lights are right, and region lighting is copied.
        dstWorld.saveInPlace()
        nextStep(dungeonName + ": Saved")

        try:
            shutil.rmtree(dstFolder + "##MCEDIT.TEMP##", ignore_errors=True)
            shutil.rmtree(dstFolder + "playerdata", ignore_errors=True)
            shutil.rmtree(dstFolder + "advancements", ignore_errors=True)
            shutil.rmtree(dstFolder + "stats", ignore_errors=True)
            os.remove(dstFolder + "mcedit_waypoints.dat")
        except Exception as e:
            pass
        nextStep(dungeonName + ": Done!")


# Multiprocessing implementation based on:
# http://sebastianraschka.com/Articles/2014_multiprocessing.html
def gen_dungeon_instances(config):
    mainTiming = timings(enabled=True)
    nextStep = mainTiming.nextStep
    nextStep("Main: Starting timings")

    dungeonRefFolder = config["dungeonRefFolder"]
    templateFolder = config["templateFolder"]
    dungeons = config["dungeons"]

    # Fail if folders don't exist
    if not os.path.isdir(dungeonRefFolder):
        sys.exit("Dungeon reference folder does not exist.")
    if not os.path.isdir(templateFolder):
        sys.exit("Template world folder does not exist.")

    print "Preparing template world for use."
    referenceWorld = pymclevel.loadWorld(dungeonRefFolder)
    nextStep("Main: Loaded template world")

    print "Changing all chunks to void biome..."
    for aChunk in referenceWorld.getChunks():
        aChunk.root_tag["Level"]["Biomes"].value.fill(127)
        aChunk.chunkChanged(True)
    nextStep("Main: Changed biome")

    # We're not creating empty region files anymore, but copying existing ones;
    # difficulty must be reset
    print "Resetting difficulty..."
    resetRegionalDifficulty(referenceWorld)
    nextStep("Main: Reset difficulty")

    print "Saving in place..."
    referenceWorld.saveInPlace()
    nextStep("Main: Saved")

    print "Generating dungeon instances. There will be no output here until finished."

    # Decrease the priority for this work so it doesn't slow down other things
    parent = psutil.Process(os.getpid())
    parent.nice = 10
    nextStep("Main: Decreased main thread priority")

    processes = []
    outputFiles = []
    for dungeon in dungeons:
        outputFile = tempfile.mktemp()
        processes.append({
            "process":mp.Process(target=gen_dungeon_instance, args=(config, dungeon, outputFile)),
            "outputFile":outputFile,
        })
    nextStep("Main: Processes prepared")

    for p in processes:
        p["process"].start()
    nextStep("Main: Processes started, waiting for threads to join")

    for p in processes:
        p["process"].join()
        try:
            logFile = open(p["outputFile"], "r")
            print logFile.read()
            logFile.close()
            os.remove(p["outputFile"])
        except:
            pass

    print "Done!"
    nextStep("Main: Done.")

################################################################################
gen_dungeon_instances(config)

