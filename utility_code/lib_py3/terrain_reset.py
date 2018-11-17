#!/usr/bin/env python3

import os

from lib_py3.copy_region import copy_region
from lib_py3.common import copy_paths, copy_folder
from lib_py3.world import World
from lib_py3.move_region import MoveRegion
from lib_py3.scoreboard import Scoreboard
from lib_py3.player import Player

def terrain_reset_instance(config):
    shardName = config["server"]

    print("Starting reset for server {0}...".format(shardName))

    ################################################################################
    # Assign variables

    if "localMainFolder" in config:
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
    # TODO: Would be nice to make this a property of the world also?
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
                dungeonScoreObjects = worldScores.search_scores(Objective=dungeonScore,Score=instanceID)
                for scoreObject in dungeonScoreObjects:
                    # Consider setting this value to -1 to indicate an error
                    scoreObject.value["Score"].value = 0
                continue

    if "coordinatesToFill" in config:
        print("  Filling selected regions with specified blocks...")
        for section in config["coordinatesToFill"]:
            print("    Filling '" + section["name"] + "' with " + str(section["block"]))
            dstWorld.fill_blocks(section["pos1"], section["pos2"], {"block": section["block"]})

    if "coordinatesToCopy" in config:
        print("  Opening old play World...")
        old_world = World(localMainFolder)

        print("  Copying needed terrain from the main world...")
        for section in config["coordinatesToCopy"]:
            print("    Copying '" + section["name"] + "'")
            dstWorld.restore_area(section["pos1"], section["pos2"], old_world);

    # Save the scoreboards. This is always necessary regardless of pruning entities!
    worldScores.save()

    # TODO: Would be nice to make the set of players a property of the world - not loaded unless you use them,
    # and if you modify them, # saving the world would save the players too
    if "tagPlayers" in config or ("tpToSpawn" in config and config["tpToSpawn"] == True):
        if "tagPlayers" in config:
            print("  Giving scoreboard tags to players...")

        if "tpToSpawn" in config and config["tpToSpawn"] == True:
            print("  Moving players to spawn (" + ",".join(str(e) for e in dstWorld.spawn) + ") ...")

        for uuid in dstWorld.players:
            player = Player(os.path.join(localDstFolder, 'playerdata', str(uuid) + '.dat'))
            player.full_heal()

            if "tagPlayers" in config:
                player.modify_tags(config["tagPlayers"])

            if "tpToSpawn" in config and config["tpToSpawn"] == True:
                player.spawn = dstWorld.spawn
                player.pos = dstWorld.spawn

            player.save()
