#!/usr/bin/env python3

import os
import sys
import codecs
import traceback

import datetime

from lib_py3.common import copy_paths, copy_folder, copy_maps
from lib_py3.world import World
from lib_py3.move_region import MoveRegion
from lib_py3.common import eprint
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path

def terrain_reset_instance(config, outputFile=None, statusQueue=None):
    shard_name = config["server"]
    replacements_log = {}

    try:
        # Redirect output to specified file
        if outputFile is not None:
            sys.stdout = codecs.getwriter('utf8')(open(outputFile, "wb"))

        ##################################################################################
        print("Starting reset for server {0}...".format(shard_name))
        time_start = datetime.datetime.utcnow()

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
                if not os.path.exists(config["localBuildFolder"]):
                    raise Exception("ERROR: Build folder {!r} does not exist!!".format(config["localBuildFolder"]))
                print("  Copying build world as base...")
                copy_folder(config["localBuildFolder"], localDstFolder)
            elif config["copyBaseFrom"] == "main":
                if not os.path.exists(config["localMainFolder"]):
                    raise Exception("ERROR: Main folder {!r} does not exist!!".format(config["localMainFolder"]))
                print("  Copying main world as base...")
                copy_folder(localMainFolder, localDstFolder)


        # Copy various bits of player data from the main world
        if "copyMainPaths" in config:
            print("  Copying paths from main world...")
            copy_paths(localMainFolder, localDstFolder, config["copyMainPaths"])

        if "copyMaps" in config:
            if config["copyMaps"] == "build":
                print("  Copying maps from build...")
                copy_maps(config["localBuildFolder"], localDstFolder)
            elif config["copyMaps"] == "main":
                print("  Copying maps from main...")
                copy_maps(localMainFolder, localDstFolder)
            else:
                raise Exception("ERROR: Could not copy maps from {!r}, invalid config!".format(config["copyMaps"]))

        print("  Opening Destination World...")
        dstWorld = World(localDstFolder)

        if "datapacks" in config:
            print("  Changing enabled datapacks...")
            dstWorld.enabled_data_packs = config["datapacks"]
            dstWorld.save_data_packs()

        if "coordinatesToFill" in config:
            print("  Filling selected regions with specified blocks...")
            for section in config["coordinatesToFill"]:
                print("    Filling " + repr(section["name"]) + " with " + str(section["block"]))
                dstWorld.fill_blocks(section["pos1"], section["pos2"], {"block": section["block"]})

        if "coordinatesToCopy" in config:
            print("  Opening old play World...")
            old_world = World(localMainFolder)

            print("  Copying needed terrain from the main world...")
            for section in config["coordinatesToCopy"]:
                print("    Copying " + repr(section["name"]))
                dstWorld.restore_area(section["pos1"], section["pos2"], old_world);
                if "replace_items" in section:
                    item_replace_manager = section["replace_items"]
                    for item, _, entity_path in dstWorld.items(readonly=False, no_players=True, pos1=section["pos1"], pos2=section["pos2"]):
                        item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=get_debug_string_from_entity_path(entity_path))

        if "localMainFolder" in config and not os.path.exists(config["localMainFolder"]):
            eprint("!!!!!! WARNING: Missing previous week main folder {!r}!".format(config["localBuildFolder"]))
            eprint("If you are not adding a shard, this is a critical problem!")
            if statusQueue is not None:
                statusQueue.put({"server":shard_name, "done":True, "replacements_log":replacements_log})
            # Needed to actually commit datapack changes
            dstWorld.save()
            return

        if "worldScoreChanges" in config:
            print("  Adjusting world scores...")
            worldScores = dstWorld.scoreboard
            worldScores.batch_score_changes(config["worldScoreChanges"])
            worldScores.save()

        if "preserveInstance" in config:
            instanceConfig = config["preserveInstance"]
            targetRegion = instanceConfig["targetRegion"]
            dungeonScore = instanceConfig["dungeonScore"]
            redisScoreboard = instanceConfig["redisScoreboard"]
            instancesPerWeek = 1000

            dungeonScoreObjects = redisScoreboard.search_scores(Objective=dungeonScore,Score={"min":1})
            dungeonScores = set()
            for scoreObject in dungeonScoreObjects:
                dungeonScores.add(scoreObject.at_path("Score").value)
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
                    eprint("WARNING: Missing dungeon instance {}".format(instanceID))
                    dungeonScoreObjects = redisScoreboard.search_scores(Objective=dungeonScore,Score=instanceID)
                    for scoreObject in dungeonScoreObjects:
                        scoreObject.at_path("Score").value = 0
                    continue

                # Looks good! Replace items if specified
                if "replace_items" in instanceConfig:
                    item_replace_manager = instanceConfig["replace_items"]
                    for item, _, entity_path in dstWorld.items(readonly=False, no_players=True, pos1=(newRx * 512, 0, newRz * 512), pos2=((newRx + 1) * 512 - 1, 255, (newRz + 1) * 512 - 1)):
                        item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=get_debug_string_from_entity_path(entity_path))

        # Replace items worldwide if specified
        if "replace_items_globally" in config:
            item_replace_manager = config["replace_items_globally"]
            for item, _, entity_path in dstWorld.items(readonly=False, no_players=True):
                item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=get_debug_string_from_entity_path(entity_path))

        dstWorld.save()
        time_end = datetime.datetime.utcnow()
        print("Total time: {}".format(str(time_end - time_start)))
        ##################################################################################

        if statusQueue is not None:
            statusQueue.put({"server":shard_name, "done":True, "replacements_log":replacements_log})

    except:
        e = traceback.format_exc()
        if statusQueue is not None:
            statusQueue.put({"server":shard_name, "done":True, "replacements_log":replacements_log, "error":e})
