#!/usr/bin/env python3

import os

from lib_py3.copy_region import copy_region
from lib_py3.common import copy_paths, copy_folder
from lib_py3.world import World
from lib_py3.move_region import MoveRegion
from lib_py3.scoreboard import Scoreboard

def terrainResetInstance(config):
    shardName = config["server"]

    print("Starting reset for server {0}...".format(shardName))

    ################################################################################
    # Assign variables

    localMainFolder = config["localMainFolder"]
    localDstFolder = config["localDstFolder"]

    ################################################################################
    # Copy folders

    # Copy build or main as base world, depending on config
    if "copyBaseFrom" in config:
        if config["copyBaseFrom"] == "build":
            print("  Copying build world as base...")
            copy_folder(config["localBuildFolder"], localDstFolder)
        elif config["copyBaseFrom"] == "main":
            print("  Copying main world as base...")
            copy_folder(localMainFolder, localDstFolder)

    # Copy various bits of player data from the main world
    if "copyMainPaths" in config:
        print("  Copying paths from main world...")
        copy_paths(localMainFolder, localDstFolder, config["copyMainPaths"])

    print("  Opening Destination World...")
    dstWorld = World(localDstFolder)

    worldScores = Scoreboard(localDstFolder)

    if "playerScoreChanges" in config:
        print("  Adjusting player scores (dungeon scores)...")
        worldScores.batch_score_changes(config["playerScoreChanges"])

    if "preserveInstance" in config:
        instanceConfig = config["preserveInstance"]
        targetRegion = instanceConfig["targetRegion"]
        dungeonScore = instanceConfig["dungeonScore"]
        instancesPerWeek = 1000

        dungeonScoreObjects = worldScores.search_scores(Objective=dungeonScore,Score={"min":1})
        dungeonScores = set()
        for scoreObject in dungeonScoreObjects:
            dungeonScores.add(scoreObject.value["Score"].value)
        dungeonScores = sorted(list(dungeonScores))
        oldRegionDir = localMainFolder + 'region/'
        newRegionDir = localDstFolder + 'region/'

        print("  Instances preserved this week: ", dungeonScores)
        for instanceID in dungeonScores:
            # // is integer division
            instanceWeek   = instanceID // instancesPerWeek
            instanceInWeek = instanceID %  instancesPerWeek

            newRx = targetRegion["x"] + instanceWeek
            newRz = targetRegion["z"] + instanceInWeek - 1 # index starts at 1
            oldRx = newRx - 1
            oldRz = newRz

            if not MoveRegion(
                oldRegionDir,
                newRegionDir,
                oldRx,oldRz,
                newRx,newRz,
            ):
                # Failed to move the region file; this happens if the old file is missing.
                # This does not indicate that the player's instance was removed intentionally.

                # TODO: Tested this in 1.13, and because of the way error handling works in
                # the MoveRegion command, this is never called, even though it detects the region is
                # missing. Not a big deal, because this shouldn't happen in practice... but is a bug
                #
                dungeonScoreObjects = worldScores.search_scores(Objective=dungeonScore,Score=instanceID)
                for scoreObject in dungeonScoreObjects:
                    # Consider setting this value to -1 to indicate an error
                    scoreObject.value["Score"].value = 0
                continue

#~     ################################################################################
#~     # Perform world manipulations if required
#~     if (("coordinatesToFill" in config) or ("coordinatesToCopy" in config)):
#~
#~         print("  Opening old play World...")
#~         srcWorld = pymclevel.loadWorld(localMainFolder)
#~
#~         if "coordinatesToFill" in config:
#~             print("  Filling selected regions with specified blocks...")
#~             fillBoxes(dstWorld, config["coordinatesToFill"])
#~
#~         if "coordinatesToCopy" in config:
#~
#~             print("  Copying needed terrain from the main world...")
#~             copyBoxes(srcWorld, dstWorld, config["coordinatesToCopy"])
#~
#~         print("  Saving....")
#~         dstWorld.saveInPlace()

    # Save the scoreboards. This is always necessary regardless of pruning entities!
    worldScores.save()

#~     if "tagPlayers" in config:
#~         print("  Giving scoreboard tags to players...")
#~         tagPlayers(localDstFolder,config["tagPlayers"])
#~
#~     if ("tpToSpawn" in config and config["tpToSpawn"] is True):
#~         print("  Moving players to spawn...")
#~         spawnX = dstWorld.root_tag['Data']['SpawnX'].value
#~         spawnY = dstWorld.root_tag['Data']['SpawnY'].value
#~         spawnZ = dstWorld.root_tag['Data']['SpawnZ'].value
#~         if dstWorld.root_tag['Data']['GameType'].value != 2:
#~             """
#~             Servers with Adventure as the default game mode
#~             ignore standard spawn mechanics; this is what
#~             happens outside of adventure mode.
#~             """
#~             spawnY = 256
#~             block_air = 0
#~             while (
#~                 spawnY > 0 and
#~                 dstWorld.blockAt(spawnX,spawnY-1,spawnZ) == block_air
#~             ):
#~                 spawnY -= 1
#~         movePlayers(localDstFolder, (spawnX,spawnY,spawnZ,0.0,0.0))

dungeonScoreRules = [
    {"condition":{"Objective":"D1Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D1Access","Score":1000}]}},
    {"condition":{"Objective":"D1Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D1Access","Score":0},
            {"Objective":"D1Finished","Score":0}]}},
    {"condition":{"Objective":"D2Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D2Access","Score":1000}]}},
    {"condition":{"Objective":"D2Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D2Access","Score":0},
            {"Objective":"D2Finished","Score":0}]}},
    {"condition":{"Objective":"D3Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D3Access","Score":1000}]}},
    {"condition":{"Objective":"D3Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D3Access","Score":0},
            {"Objective":"D3Finished","Score":0}]}},
    {"condition":{"Objective":"D4Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D4Access","Score":1000}]}},
    {"condition":{"Objective":"D4Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D4Access","Score":0},
            {"Objective":"D4Finished","Score":0}]}},
    {"condition":{"Objective":"D5Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D5Access","Score":1000}]}},
    {"condition":{"Objective":"D5Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D5Access","Score":0},
            {"Objective":"D5Finished","Score":0}]}},
    {"condition":{"Objective":"DCAccess","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"DCAccess","Score":1000}]}},
    {"condition":{"Objective":"DCAccess","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"DCAccess","Score":0}]}},
    {"condition":{"Objective":"DB1Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"DB1Access","Score":1000}]}},
    {"condition":{"Objective":"DB1Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"DB1Access","Score":0}]}},
    {"condition":{"Objective":"DRAccess","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"DRAccess","Score":0}]}},
    {"condition":{"Objective":"VotesWeekly","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"VotesWeekly","Score":0}]}},
]


config = {
    "server":"orange",
    "localMainFolder":"/home/rock/5_SCRATCH/tmpreset/PRE_RESET/orange/Project_Epic-orange/",
    "localBuildFolder":"/home/rock/5_SCRATCH/tmpreset/TEMPLATE/orange/Project_Epic-orange/",
    "localDstFolder":"/home/rock/5_SCRATCH/tmpreset/POST_RESET/orange/Project_Epic-orange/",
    "copyBaseFrom":"build",
    "copyMainPaths":["advancements", "playerdata", "stats", "data"],
    "playerScoreChanges":dungeonScoreRules,
    "preserveInstance":{
        "dungeonScore":"D2Access",
        "targetRegion":{"x":-3, "z":-2},
    },
    "tagPlayers":["MidTransfer","resetMessage"],
    "tpToSpawn":True,
}

terrainResetInstance(config)
