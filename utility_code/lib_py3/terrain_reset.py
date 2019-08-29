#!/usr/bin/env python3

import os
import sys
import codecs
import traceback

import datetime

from lib_py3.copy_region import copy_region
from lib_py3.common import copy_paths, copy_folder
from lib_py3.world import World
from lib_py3.move_region import MoveRegion
from lib_py3.scoreboard import Scoreboard
from lib_py3.player import Player
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
                    raise Exception("ERROR: Build folder '{}' does not exist!!".format(config["localBuildFolder"]))
                print("  Copying build world as base...")
                copy_folder(config["localBuildFolder"], localDstFolder)
            elif config["copyBaseFrom"] == "main":
                if not os.path.exists(config["localMainFolder"]):
                    raise Exception("ERROR: Main folder '{}' does not exist!!".format(config["localMainFolder"]))
                print("  Copying main world as base...")
                copy_folder(localMainFolder, localDstFolder)


        # Copy various bits of player data from the main world
        if "copyMainPaths" in config:
            print("  Copying paths from main world...")
            copy_paths(localMainFolder, localDstFolder, config["copyMainPaths"])

        print("  Opening Destination World...")
        dstWorld = World(localDstFolder)

        if "datapacks" in config:
            print("  Changing enabled datapacks...")
            dstWorld.enabled_data_packs = config["datapacks"]
            dstWorld.save_data_packs()

        if "coordinatesToFill" in config:
            print("  Filling selected regions with specified blocks...")
            for section in config["coordinatesToFill"]:
                print("    Filling '" + section["name"] + "' with " + str(section["block"]))
                dstWorld.fill_blocks(section["pos1"], section["pos2"], {"block": section["block"]})

        if "coordinatesToCopy" in config:
            print("  Opening old play World...")
            old_world = World(localMainFolder)

            print("  Preparing to copy needed terrain from the main world...")
            chunks_to_copy = set()
            chunks_to_replace_items = {}
            item_replace_chunk_count = 0
            for section in config["coordinatesToCopy"]:
                chunks_selected = 0
                pos1 = section["pos1"]
                pos2 = section["pos2"]

                min_x = min(pos1[0],pos2[0])
                min_y = min(pos1[1],pos2[1])
                min_z = min(pos1[2],pos2[2])

                max_x = max(pos1[0],pos2[0]) + 1
                max_y = max(pos1[1],pos2[1]) + 1
                max_z = max(pos1[2],pos2[2]) + 1

                min_pos = (min_x, min_y, min_z)
                max_pos = (max_x, max_y, max_z)

                cx_min = min_x // 16
                cz_min = min_z // 16
                cx_max = max_x // 16
                cz_max = max_z // 16

                for cx in range(cx_min, cx_max + 1):
                    for cz in range(cz_min, cz_max + 1):
                        chunks_selected += 1
                        chunks_to_copy.add((cx, cz))
                        if "replace_items" in section:
                            if (cx, cz) not in chunks_to_replace_items:
                                item_replace_chunk_count += 1

                            rx = cx // 32
                            rz = cz // 32

                            if (rx, rz) not in chunks_to_replace_items:
                                chunks_to_replace_items[(rx, rz)] = {}
                            if (cx, cz) not in chunks_to_replace_items[(rx, rz)]:
                                chunks_to_replace_items[(rx, rz)][(cx, cz)] = {
                                    "manager": section["replace_items"],
                                    "sections": []
                                }
                            chunks_to_replace_items[(rx, rz)][(cx, cz)]["sections"].append({
                                "min": min_pos, "max": max_pos
                            })

                print("    Prepared to copy {!r} ({} chunks)".format(section["name"], chunks_selected))

            print("  Copying needed terrain from the main world ({} chunks)...".format(len(chunks_to_copy)))
            dstWorld.restore_chunks(old_world, chunks_to_copy)
            
            print("  Running item replacements on copied terrain ({} chunks)...".format(item_replace_chunk_count)
            items_scanned = 0
            for rx_rz, region_chunks in chunks_to_replace_items.items():
                rx, rz = rx_rz
                for cx_cz, sections in region_chunks.items():
                    cx, cz = cx_cz
                    item_replace_chunk_count -= 1
                    item_replace_manager = sections["manager"]
                    for item, source_pos, entity_path in dstWorld.items(readonly=False, pos1=(cx*16, 0, cz*16), pos2=(cx*16+15, 255, cz*16+15)):
                        if source_pos is None:
                            continue

                        in_a_section = False
                        for section in sections["sections"]:
                            for i in range(3):
                                if (
                                    section["min"] <= source_pos[i]
                                    and source_pos[i] < section["max"]
                                ):
                                    in_a_section = True
                                    break
                            if in_a_section:
                                break
                        if not in_a_section:
                            continue

                        items_scanned += 1
                        item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=get_debug_string_from_entity_path(entity_path))
            print("  Ran item replacements on copied terrain ({} chunks not scanned, {} items scanned)...".format(item_replace_chunk_count, items_scanned)

        if "localMainFolder" in config and not os.path.exists(config["localMainFolder"]):
            eprint("!!!!!! WARNING: Missing previous week main folder '{}'!".format(config["localBuildFolder"]))
            eprint("If you are not adding a shard, this is a critical problem!")
            if statusQueue is not None:
                statusQueue.put({"server":shard_name, "done":True, "replacements_log":replacements_log})
            return

        worldScores = None
        if ("playerScoreChanges" in config) or ("preserveInstance" in config):
            worldScores = dstWorld.scoreboard

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
                    dungeonScoreObjects = worldScores.search_scores(Objective=dungeonScore,Score=instanceID)
                    for scoreObject in dungeonScoreObjects:
                        # Consider setting this value to -1 to indicate an error
                        scoreObject.at_path("Score").value = 0
                    continue

                # Looks good! Replace items if specified
                if "replace_items" in instanceConfig:
                    item_replace_manager = instanceConfig["replace_items"]
                    for item, _, entity_path in dstWorld.items(readonly=False, pos1=(newRx * 512, 0, newRz * 512), pos2=((newRx + 1) * 512 - 1, 255, (newRz + 1) * 512 - 1)):
                        item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=get_debug_string_from_entity_path(entity_path))

        # Save the scoreboards if they were used
        if worldScores is not None:
            worldScores.save()

        # TODO: Would be nice to make saving the world would save the players too
        if "tagPlayers" in config or ("tpToSpawn" in config and config["tpToSpawn"] == True):
            if "tagPlayers" in config:
                print("  Giving scoreboard tags to players...")

            if "tpToSpawn" in config and config["tpToSpawn"] == True:
                print("  Moving players to spawn (" + ",".join(str(e) for e in dstWorld.spawn) + ") ...")

            for a_player in dstWorld.players:
                a_player.full_heal()

                if "tagPlayers" in config:
                    a_player.modify_tags(config["tagPlayers"])

                if "tpToSpawn" in config and config["tpToSpawn"] == True:
                    a_player.spawn = dstWorld.spawn
                    a_player.pos = dstWorld.spawn

                a_player.save()

        # Replace items worldwide if specified
        if "replace_items_globally" in config:
            item_replace_manager = config["replace_items_globally"]
            for item, _, entity_path in dstWorld.items(readonly=False):
                item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=get_debug_string_from_entity_path(entity_path))

        # Replace items on all players if specified
        if "replace_items_on_players" in config:
            item_replace_manager = config["replace_items_on_players"]
            for item, _, entity_path in dstWorld.items(readonly=False, players_only=True):
                item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=get_debug_string_from_entity_path(entity_path))

        dstWorld.save()
        time_end = datetime.datetime.utcnow()
        print("Total time: {}".format(str(time_end - time_start)))
        ##################################################################################

        if statusQueue is not None:
            statusQueue.put({"server":shard_name, "done":True, "replacements_log":replacements_log})

    except:
        e = traceback.format_exc()
        print("Total time: {} :(".format(str(time_end - time_start)))
        if statusQueue is not None:
            statusQueue.put({"server":shard_name, "done":True, "replacements_log":replacements_log, "error":e})
