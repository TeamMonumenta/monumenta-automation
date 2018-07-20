#!/usr/bin/env python2.7
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
import traceback

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
import pymclevel

from lib_monumenta import item_replace
from lib_monumenta import scoreboard
from lib_monumenta.common import fillBoxes, copyBoxes, copyFolder, copyFolders, copyFiles
from lib_monumenta.common import resetRegionalDifficulty, movePlayers, replaceGlobally, tagPlayers
from lib_monumenta.list_uuids import listUUIDs
#from lib_monumenta.advancements import advancements
from lib_monumenta.move_region import moveRegion
from lib_monumenta.timing import timings

def terrainResetInstance(config, outputFile, statusQueue):
    shardName = config["server"]
    try:
        # Redirect output to specified file
        sys.stdout = codecs.getwriter('utf8')(open(outputFile, "w"))

        mainTiming = timings(enabled=True)
        nextStep = mainTiming.nextStep
        
        nextStep("[TIMING] Thread started")

        print "Starting reset for server {0}...".format(shardName)

        ################################################################################
        # Assign variables

        localMainFolder = config["localMainFolder"]
        localDstFolder = config["localDstFolder"]

        blockReplacements = config["blockReplacements"] if ("blockReplacements" in config) else None
        itemReplacements = config["itemReplacements"] if ("itemReplacements" in config) else None
        entityUpdates = config["entityUpdates"] if ("entityUpdates" in config) else None
        immovableFix  = config["immovableFix"] if ("immovableFix" in config) else None
        shouldResetDifficulty = config["resetRegionalDifficulty"] if ("resetRegionalDifficulty" in config) else False

        if "itemLog" in config:
            itemReplacements.enableGlobalCount()

        nextStep("[TIMING] Config read")

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

        # Copy various bits of player data from the main world
        if "copyMainFiles" in config:
            print "  Copying files from main world..."
            copyFiles(localMainFolder, localDstFolder, config["copyMainFiles"])

        nextStep("[TIMING] Copied base files/folders")

        # We need to read DstWorld, even if we don't edit it.
        # This lets us prune scores of dead entities.
        print "  Opening Destination World..."
        dstWorld = pymclevel.loadWorld(localDstFolder)

        nextStep("[TIMING] Loaded world")

        worldScores = scoreboard.scoreboard(localDstFolder)

        nextStep("[TIMING] Loaded scoreboard")

        if "playerScoreChanges" in config:
            print "  Adjusting player scores (dungeon scores)..."
            worldScores.batchScoreChanges(config["playerScoreChanges"])
            nextStep("[TIMING] Handled dungeon scores")

        if "preserveInstance" in config:
            instanceConfig = config["preserveInstance"]
            targetRegion = instanceConfig["targetRegion"]
            dungeonScore = instanceConfig["dungeonScore"]
            instancesPerWeek = 1000

            dungeonScoreObjects = worldScores.searchScores(Objective=dungeonScore,Score={"min":1})
            dungeonScores = set()
            for scoreObject in dungeonScoreObjects:
                dungeonScores.add(scoreObject["Score"].value)
            dungeonScores = sorted(list(dungeonScores))
            nextStep("[TIMING] Preserve dungeon instances: scores updated")

            oldRegionDir = localMainFolder + 'region/'
            newRegionDir = localDstFolder + 'region/'

            for instanceID in dungeonScores:
                # // is integer division
                instanceWeek   = instanceID // instancesPerWeek
                instanceInWeek = instanceID %  instancesPerWeek

                newRx = targetRegion["x"] + instanceWeek
                newRz = targetRegion["z"] + instanceInWeek - 1 # index starts at 1
                oldRx = newRx - 1
                oldRz = newRz

                if not moveRegion(
                    oldRegionDir,
                    newRegionDir,
                    oldRx,oldRz,
                    newRx,newRz,
                    itemReplacements,
                    entityUpdates
                ):
                    # Failed to move the region file; this happens if the old file is missing.
                    # This does not indicate that the player's instance was removed intentionally.
                    dungeonScoreObjects = worldScores.searchScores(Objective=dungeonScore,Score=instanceID)
                    for scoreObject in dungeonScoreObjects:
                        # Consider setting this value to -1 to indicate an error
                        scoreObject["Score"].value = 0
                    continue
            nextStep("[TIMING] Preserved dungeon instances")

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
            (immovableFix is not None) or
            (shouldResetDifficulty == True)
        ):

            print "  Opening old play World..."
            srcWorld = pymclevel.loadWorld(localMainFolder)
            nextStep("[TIMING] Loaded old play world")

            if "coordinatesToFill" in config:
                print "  Filling selected regions with specified blocks..."
                fillBoxes(dstWorld, config["coordinatesToFill"])
                nextStep("[TIMING] Filled selected regions (magic blocks)")

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
                    nextStep("[TIMING] Copied regions (includes block, item, and entity changes)")

            if (blockReplacements is not None) and ("world" in config["blockReplaceLocations"]):
                print "  Replacing specified blocks worldwide..."
                replaceGlobally(dstWorld, blockReplacements)
                nextStep("[TIMING] Replaced blocks throughout the world")

            if (itemReplacements is not None) and ("world" in config["itemReplaceLocations"]):
                print "  Replacing specified items worldwide..."
                itemReplacements.InWorld(dstWorld)
                nextStep("[TIMING] Finished item replacements throughout the world")

            if (entityUpdates is not None) and ("world" in config["entityUpdateLocations"]):
                print "  Updated specified entities worldwide..."
                entityUpdates.InWorld(dstWorld)
                nextStep("[TIMING] Finished entity updates throughout the world")

            if immovableFix is not None:
                print "  Making villagers immovable worldwide..."
                immovableFix.InWorld(dstWorld)
                nextStep("[TIMING] Made villagers unpushable worldwide (hopefully)")

            if (shouldResetDifficulty == True):
                print "  Resetting difficulty..."
                resetRegionalDifficulty(dstWorld)
                nextStep("[TIMING] Reset difficulty in world")

            print "  Generating lights (should only happen on block changes!)...."
            dstWorld.generateLights()
            nextStep("[TIMING] Finished generating lighting")
            print "  Saving...."
            dstWorld.saveInPlace()
            nextStep("[TIMING] Saved")

        print "  <DRY RUN!> Deleting scores for missing entities..."
        existingEntities = listUUIDs(dstWorld)
        nextStep("[TIMING] Found UUIDs in world")
        worldScores.pruneMissingEntities(existingEntities)
        nextStep("[TIMING] Pruned scores of missing entities.")
        worldScores.save()
        nextStep("[TIMING] Saved scoreboard changes")

        # TODO Disabled to test if this is revoking advancements it shouldn't.
        #if "revokeAdvancements" in config:
        if False:
            print "Revoking advancements from players..."
            dstAdvancements = advancements(localDstFolder)
            dstAdvancements.revoke(config["revokeAdvancements"])
            nextStep("[TIMING] Revoked advancements for bug fixes")

        if "players" in config["itemReplaceLocations"]:
            itemReplacements.OnPlayers(localDstFolder)
            nextStep("[TIMING] Replaced items on players")

        if "safetyTpLocation" in config:
            print "  Moving players to safety..."
            movePlayers(localDstFolder, config["safetyTpLocation"])
            nextStep("[TIMING] Teleported players to specified location")

        if "tagPlayers" in config:
            print "  Giving scoreboard tags to players..."
            tagPlayers(localDstFolder,config["tagPlayers"])
            nextStep("[TIMING] Tagged players")

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
            nextStep("[TIMING] Teleported players to spawn")

        try:
            shutil.rmtree(localDstFolder+"##MCEDIT.TEMP##", ignore_errors=True)
            os.remove(localDstFolder+"mcedit_waypoints.dat")
        except Exception as e:
            pass
        nextStep("[TIMING] Removed temporary MCEdit files/folders")

        if "itemLog" in config:
            itemReplacements.SaveGlobalLog(config["itemLog"])
            nextStep("[TIMING] Saved item log")

        nextStep("[TIMING] Declared self as done")
        statusQueue.put({"server":shardName,"done":True})

    except:
        e = traceback.format_exc()
        statusQueue.put({"server":shardName,"done":True,"error":e})

# Multiprocessing implementation based on:
# http://sebastianraschka.com/Articles/2014_multiprocessing.html
def terrainReset(configList):
    ################################################################################
    # Perform sanity checks on all config items
    serversSpecified = set()
    for config in configList:
        if "server" not in config:
            sys.exit('config["server"] must be specified in all configs')

        if config["server"] in serversSpecified:
            sys.exit('config["server"] must be unique in all configs')
        serversSpecified.add(config["server"])

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

    processes = {}
    statusQueue = mp.Queue()
    for config in configList:
        shardName = config["server"]
        outputFile = tempfile.mktemp()
        processes[shardName] = {
            "process":mp.Process(target=terrainResetInstance, args=(config, outputFile, statusQueue)),
            "outputFile":outputFile,
        }

    for p in processes.values():
        p["process"].start()

    while len(processes.keys()) > 0:
        statusUpdate = statusQueue.get()
        statusFrom = statusUpdate["server"]
        p = processes[statusFrom]

        if "done" in statusUpdate:
            p["process"].join()

            if "error" not in statusUpdate:
                print statusFrom + " completed successfully"

            try:
                logFile = codecs.open(p["outputFile"],'r',encoding='utf8')
                print logFile.read()
                logFile.close()
            except:
                print "Log file could not be read!"

            processes.pop(statusFrom)

        if "error" in statusUpdate:
            print "\n!!! " + statusFrom + " has crashed.\n"

            # stop all other subprocesses
            for p in processes.values():
                p["process"].terminate()

            raise RuntimeError(str(statusUpdate["error"]))

    print "Done!"
