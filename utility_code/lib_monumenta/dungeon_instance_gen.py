#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import multiprocessing as mp
import psutil
import tempfile

# Import pymclevel from MCLevel-Unified
import pymclevel
from pymclevel import materials
from pymclevel.box import BoundingBox, Vector

from lib_monumenta.common import fillBoxes, copyFolder, tempdir, resetRegionalDifficulty
from lib_monumenta.list_lootless_tile_entities import listLootlessTileEntities
from lib_monumenta.copy_region import copyRegion
from lib_monumenta.timing import timings
from lib_monumenta.gen_map_array import gen_map_array

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
    if "chestContentsLoreToIgnore" in dungeon:
        dungeonContentsLoreToIgnore = dungeon["chestContentsLoreToIgnore"]
    else:
        dungeonContentsLoreToIgnore  = None
    if "chestWhitelist" in dungeon:
        dungeonChestWhitelist = dungeon["chestWhitelist"]
    else:
        dungeonChestWhitelist = None
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
        oldRegionDir = tempDungeonRefCopy + "/region"
        newRegionDir = dstFolder + "region"
        rx=targetRegion["x"]
        rzInit=targetRegion["z"]
        for i in range(numDungeons):
            print "    {0}...".format(i)
            rz = rzInit + i
            copyRegion(
                oldRegionDir,
                newRegionDir,
                dungeonRegion["x"],dungeonRegion["z"],
                rx,rz
            )
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

        # If generateMaps is specified, do that
        if "generateMaps" in dungeon:
            print "  Generating maps...."
            startX = targetRegion["x"] * 512 + dungeon["generateMaps"]["offset"]["x"]
            startZ = targetRegion["z"] * 512 + dungeon["generateMaps"]["offset"]["z"]
            gen_map_array(dstFolder + "data/", numDungeons, startX, startZ, 0, 512)

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

