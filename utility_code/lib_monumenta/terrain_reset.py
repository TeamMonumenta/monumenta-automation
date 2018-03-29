#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).

This does so as directly as possible while providing many features.

Fair warning, some of the optimization is done by removing error handling.
Python will tell you if/when the script crashes.
If it's going to crash, it won't damage the original worlds.
Just fix what broke, and run again.
"""

import os
import sys
import codecs
import shutil
import multiprocessing as mp
import tempfile

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
import pymclevel

from lib_monumenta import item_replace
from lib_monumenta import scoreboard
from lib_monumenta.common import fillBoxes, copyBoxes, copyFolder, copyFolders
from lib_monumenta.common import resetRegionalDifficulty, movePlayers, replaceGlobally
from lib_monumenta.list_uuids import listUUIDs

def terrainResetInstance(config, outputFile):
    # Redirect output to specified file
    sys.stdout = codecs.getwriter('utf8')(open(outputFile, "w"))

    print "Starting reset for server {0}...".format(config["server"])

    ################################################################################
    # Assign variables

    localMainFolder = config["localMainFolder"]
    localDstFolder = config["localDstFolder"]

    blockReplacements = config["blockReplacements"] if ("blockReplacements" in config) else None
    itemReplacements = config["itemReplacements"] if ("itemReplacements" in config) else None
    entityUpdates = config["entityUpdates"] if ("entityUpdates" in config) else None
    shouldResetDifficulty = config["resetRegionalDifficulty"] if ("resetRegionalDifficulty" in config) else False

    if "itemLog" in config:
        itemReplacements.enableGlobalCount()

    ################################################################################
    # Copy folders

    # Copy build or main as base world, depending on config
    if "copyBaseFrom" in config:
        if config["copyBaseFrom"] == "build":
            print "  Copying build world as base..."
            copyFolder(config["localBuildFolder"], localDstFolder)
        elif config["copyBaseFrom"] == "main":
            print "  Copying main world as base..."
            copyFolder(localMainFolder, localDstFolder)
        # else enforced by main function

    # Copy various bits of player data from the main world
    if "copyMainFolders" in config:
        print "  Copying folders from main world..."
        copyFolders(localMainFolder, localDstFolder, config["copyMainFolders"])


    # We need to read DstWorld, even if we don't edit it.
    # This lets us prune scores of dead entities.
    print "  Opening Destination World..."
    dstWorld = pymclevel.loadWorld(localDstFolder)

    ################################################################################
    # Perform world manipulations if required
    if (
        ("coordinatesToFill" in config) or
        ("coordinatesToCopy" in config) or
        (blockReplacements is not None) or
        (
            (
                (itemReplacements is not None) or
                (entityUpdates is not None)
            ) and
            ("world" in config["itemReplaceLocations"])
        ) or
        (shouldResetDifficulty == True)
    ):

        print "  Opening old play World..."
        srcWorld = pymclevel.loadWorld(localMainFolder)

        if "coordinatesToFill" in config:
            print "  Filling selected regions with specified blocks..."
            fillBoxes(dstWorld, config["coordinatesToFill"])

        if "coordinatesToCopy" in config:
            if ("coordinatesDebug" in config) and (config["coordinatesDebug"] == True):
                print "  DEBUG: Filling regions instead of copying them!"
                fillBoxes(dstWorld, config["coordinatesToCopy"])
            else:
                # Only pass in replacement lists if specifically requested for schematics
                tmpBlockReplacements = blockReplacements if (blockReplacements is not None and "schematics" in config["blockReplaceLocations"]) else None
                tmpItemReplacements = itemReplacements if (itemReplacements is not None and "schematics" in config["itemReplaceLocations"]) else None
                tmpEntityUpdates = entityUpdates if (entityUpdates is not None and "schematics" in config["entityUpdateLocations"]) else None

                print "  Copying needed terrain from the main world..."
                copyBoxes(srcWorld, dstWorld, config["coordinatesToCopy"], tmpBlockReplacements, tmpItemReplacements, tmpEntityUpdates)

        if (blockReplacements is not None) and ("world" in config["blockReplaceLocations"]):
            print "  Replacing specified blocks worldwide..."
            replaceGlobally(dstWorld, blockReplacements)

        if (itemReplacements is not None) and ("world" in config["itemReplaceLocations"]):
            print "  Replacing specified items worldwide..."
            itemReplacements.InWorld(dstWorld)

        if (entityUpdates is not None) and ("world" in config["entityUpdateLocations"]):
            print "  Replacing specified items worldwide..."
            entityUpdates.InWorld(dstWorld)

        if (shouldResetDifficulty == True):
            print "  Resetting difficulty..."
            resetRegionalDifficulty(dstWorld)

        print "  Generating lights (should only happen on block changes!)...."
        dstWorld.generateLights()
        print "  Saving...."
        dstWorld.saveInPlace()

    print "  Deleting scores for missing entities..."
    existingEntities = listUUIDs(dstWorld)
    worldScores = scoreboard.scoreboard(localDstFolder)
    worldScores.pruneMissingEntities(existingEntities)

    if "playerScoreChanges" in config:
        print "  Adjusting player scores (dungeon scores)..."
        worldScores.batchScoreChanges(config["playerScoreChanges"])

    worldScores.save()

    if "players" in config["itemReplaceLocations"]:
        itemReplacements.OnPlayers(localDstFolder)

    if "safetyTpLocation" in config:
        print "  Moving players to safety..."
        movePlayers(localDstFolder, config["safetyTpLocation"])

    if (
        "tpToSpawn" in config and
        config["tpToSpawn"] is True
    ):
        print "  Moving players to spawn..."
        spawnX = dstWorld.root_tag['Data']['SpawnX'].value
        spawnY = dstWorld.root_tag['Data']['SpawnY'].value
        spawnZ = dstWorld.root_tag['Data']['SpawnZ'].value
        if dstWorld.root_tag['Data']['GameType'].value != 2:
            """
            Servers with Adventure as the default game mode
            ignore standard spawn mechanics; this is what
            happens outside of adventure mode.
            """
            spawnY = 256
            block_air = 0
            while (
                spawnY > 0 and
                dstWorld.blockAt(spawnX,spawnY-1,spawnZ) == block_air
            ):
                spawnY -= 1
        movePlayers(localDstFolder, (spawnX,spawnY,spawnZ,0.0,0.0))

    try:
        shutil.rmtree(localDstFolder+"##MCEDIT.TEMP##", ignore_errors=True)
        os.remove(localDstFolder+"mcedit_waypoints.dat")
    except Exception as e:
        pass

    if "itemLog" in config:
        itemReplacements.SaveGlobalLog(config["itemLog"])

# Multiprocessing implementation based on:
# http://sebastianraschka.com/Articles/2014_multiprocessing.html
def terrainReset(configList):
    ################################################################################
    # Perform sanity checks on all config items
    for config in configList:
        if "localMainFolder" in config:
            if not os.path.isdir(config["localMainFolder"]):
                sys.exit("localMainFolder world folder does not exist.")
        else:
            sys.exit("localMainFolder not specified.")

        if "localDstFolder" not in config:
            sys.exit("localDstFolder not specified.")

        if "localBuildFolder" in config:
            if not os.path.isdir(config["localBuildFolder"]):
                sys.exit("localBuildFolder world folder does not exist.")

        if ("coordinatesToCopy" in config) and ("localBuildFolder" not in config):
            sys.exit("coordinatesToCopy requires localBuildFolder")

        if ("blockReplacements" in config) ^ ("blockReplaceLocations" in config):
            sys.exit("blockReplacements and blockReplaceLocations must be used together")

        if ("itemReplacements" in config) ^ ("itemReplaceLocations" in config):
            sys.exit("itemReplacements and itemReplaceLocations must be used together")

        if ("entityUpdates" in config) ^ ("entityUpdateLocations" in config):
            sys.exit("entityUpdates and entityUpdateLocations must be used together")

        if "copyBaseFrom" in config:
            if config["copyBaseFrom"] != "build" and config["copyBaseFrom"] != "main":
                sys.exit("Illegal value '" + config["copyBaseFrom"] + "' for key 'copyBaseFrom'")

    ################################################################################
    # Run each config item in parallel
    print "Performing terrain reset(s). There will be no output here until finished."

    processes = []
    outputFiles = []
    for config in configList:
        outputFile = tempfile.mktemp()
        processes.append({
            "process":mp.Process(target=terrainResetInstance, args=(config, outputFile)),
            "outputFile":outputFile,
        })

    for p in processes:
        p["process"].start()

    for p in processes:
        p["process"].join()
        logFile = codecs.open(p["outputFile"],'r',encoding='utf8')
        print logFile.read()
        logFile.close()

    print "Done!"
