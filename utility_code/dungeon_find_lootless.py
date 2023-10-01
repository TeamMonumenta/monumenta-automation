#!/usr/bin/env python3

import argparse
import os
import sys
import multiprocessing
import concurrent
from minecraft.world import World
from minecraft.region import Region

def process_world(arg):
    """Process a world, intended to be called with multiprocessing pool"""
    verbose, dungeons, dungeon_path, world_name = arg

    # Get dungeon config, default to no config
    dungeon = dungeons.get(world_name, {})
    container_entity_ids = dungeon.get("container_entity_ids", ["minecraft:chest"])
    whitelisted_lore_lines = dungeon.get("whitelisted_lore_lines", [])

    container_whitelist = []
    for old_coords in dungeon.get("container_whitelist", []):
        if isinstance(old_coords, str):
            new_coords = []
            old_coords = old_coords.replace(",", " ")
            for coord in old_coords.split(" "):
                if len(coord) == 0:
                    continue
                new_coords.append(int(coord))
            container_whitelist.append(tuple(new_coords))
        elif isinstance(old_coords, tuple):
            container_whitelist.append(old_coords)
        else:
            sys.exit(f"container_whitelist entry '{old_coords}' is neither string nor tuple")

    non_loot_table_containers = []

    ok_loottable = 0
    ok_ids = set()
    ok_pos = []
    ok_lore = set()

    world = World(os.path.join(dungeon_path, world_name))
    for region in world.iter_regions(region_types=(Region,)):
        for chunk in region.iter_chunks(autosave=False):
            for block_entity in chunk.recursive_iter_block_entities():
                nbt = block_entity.nbt

                if nbt.has_path('LootTable'):
                    # This container is all set
                    ok_loottable += 1
                    continue

                if not nbt.has_path('id'):
                    # No container ID, this is nested.
                    continue

                entity_id = nbt.at_path('id').value
                if entity_id not in container_entity_ids:
                    # Not a container ID we care about
                    ok_ids.add(entity_id)
                    continue

                if block_entity.pos in container_whitelist:
                    # Whitelisted position
                    ok_pos.append(block_entity.pos)
                    continue

                if nbt.has_path('Items'):
                    found_whitelisted_item = False

                    for item in nbt.iter_multipath('Items[]'):
                        # Ignore BoS:
                        if item.has_path('tag.author') and item.at_path('tag.author').value == "§6The Creator":
                            continue

                        if not item.has_path('tag.display.Lore'):
                            continue

                        for lore_line in item.iter_multipath('tag.plain.display.Lore[]'):
                            for whitelisted_lore_line in whitelisted_lore_lines:
                                if whitelisted_lore_line in lore_line.value:
                                    found_whitelisted_item = True
                                    ok_lore.add(lore_line.value)
                                    break

                            if found_whitelisted_item:
                                break

                        if found_whitelisted_item:
                            break

                    if found_whitelisted_item:
                        continue

                # Now we're sure this chest isn't allowed here.
                non_loot_table_containers.append(block_entity)


    # This is the text returned to the user
    out_text = ""

    out_text += "\n" + f"{world_name}:"

    out_text += "\n" + f"- Containers with loot tables: {ok_loottable}"

    if verbose:
        if ok_ids:
            out_text += "\n" + "- Other ids found:"
            for thing in sorted(ok_ids):
                out_text += "\n" + f"  - {thing}"

        if ok_pos:
            out_text += "\n" + "- Whitelisted positions found:"
            for thing in sorted(ok_pos):
                out_text += "\n" + f"  - {thing}"

        if ok_lore:
            out_text += "\n" + "- Lore that matched whitelist:"
            for thing in sorted(ok_lore):
                out_text += "\n" + f"  - {thing}"

    if non_loot_table_containers:
        out_text += "\n" + f"- Lootless containers: {len(non_loot_table_containers)}. Top line teleports your face into the block, bottom line is a whitelist entry if it's allowed:"

        for block_entity in non_loot_table_containers:
            pos = block_entity.pos
            out_text += "\n" + f"/tp @s {pos[0]} {pos[1] - 1.2} {pos[2]}"
            out_text += "\n" + f'"{pos[0]} {pos[1]} {pos[2]}",'


    if not (ok_loottable or ok_ids or ok_pos or ok_lore or non_loot_table_containers):
        out_text += "\n" + "- No containers detected at all...wait, what?"

    return (len(non_loot_table_containers), out_text)



dungeon_path = '/home/epic/project_epic/dungeon'

dungeons = {
    #################### R1 ####################
    "white": {
        "whitelisted_lore_lines":["King's Valley : Trophy",],
        "container_whitelist":[
            "-1517 32 -782",
            "-1458 30 -816",
            "-1442 42 -828",
            "-1443 42 -828",
        ],
    },
    "orange": {
        "whitelisted_lore_lines":["King's Valley : Trophy",],
    },
    "magenta": {
        "whitelisted_lore_lines":["King's Valley : Trophy",],
        "container_whitelist":[
            "-1502 77 78",
            "-1502 45 78",
            "-1381 88 91",
            "-1379 88 92",
            "-1502 77 114",
            "-1502 45 114",
            "-1502 77 150",
            "-1502 45 150",
            "-1502 77 186",
            "-1502 45 186",
        ],
    },
    "lightblue": {
        "whitelisted_lore_lines":["King's Valley : Trophy",],
        "container_whitelist":[
            "-1495 181 551",
            "-1419 177 600",
            "-1390 210 597",
            "-1371 175 598",
            "-1368 209 599",
            "-1265 181 598",
            "-1381 180 645",
            "-1456 170 694",
            "-1336 168 708",
        ],
    },
    "yellow": {
        "whitelisted_lore_lines":["King's Valley : Trophy",],
        "container_whitelist":[
            "-1489 65 1087",
            "-1488 65 1086",
            "-1493 65 1095",
            "-1493 65 1096",
            "-1493 63 1094",
            "-1491 65 1089",
            "-1490 65 1088",
            "-1490 65 1098",
            "-1490 63 1098",
            "-1493 40 1094",
            "-1490 42 1098",
            "-1488 65 1098",
            "-1487 65 1098",
            "-1486 63 1098",
            "-1488 71 1092",
            "-1372 147 1091",
            "-1513 40 1150",
            "-1506 103 1165",
            "-1497 5 1155",
            "-1373 57 1210",
            "-1460 90 1239",
        ],
    },
    "reverie": {
        "whitelisted_lore_lines":["King's Valley : Key",],
        "container_whitelist":[
            "-1280 77 2177",
            "-1280 77 2176",
            "-1304 59 2246",
            "-1265 90 2337",
        ],
    },
    "tutorial": {
        "container_whitelist":[
            "-814 78 623",
            "-809 66 621",
            "-792 55 616",
            "-761 66 644",
            "-761 66 645",
            "-801 71 657",
            "-755 74 668",
            "-916 15 672",
            "-910 44 674",
            "-910 44 673",
            "-808 47 672",
            "-749 67 672",
            "-791 68 688",
        ],
    },
    "corridors": {
        "container_whitelist":[
            "-695 9 -187",
        ],
    },
    "labs": {
        "whitelisted_lore_lines":["King's Valley : Trophy",],
        "container_whitelist":[
            "-746 102 1172",
            "-883 102 1185",
            "-883 107 1269",
        ],
    },

    #################### R2 ####################

    "lime": {
        "whitelisted_lore_lines":["Celsian Isles : Trophy",],
        "container_whitelist":[
            "-1435 120 2586",
            "-1395 67 2597",
            "-1468 123 2617",
            "-1336 124 2609",
            "-1501 22 2647",
            "-1475 121 2645",
            "-1353 86 2657",
            "-1450 46 2680",
            "-1370 129 2762",
            "-1529 39 2780",
            "-1472 129 2771",
        ],
    },
    "pink": {
        "whitelisted_lore_lines":["Celsian Isles : Trophy",],
        "container_whitelist":[
            "-1403 11 3678",
            "-1477 72 3690",
            "-1409 23 3717",
            "-1354 21 3759",
            "-1374 98 3763",
            "-1495 14 3801",
            "-1321 16 3792",
            "-1486 89 3824",
            "-1406 19 3827",
        ],
    },
    "gray": {
        "whitelisted_lore_lines":["Celsian Isles : Trophy",],
        "container_whitelist":[
            "-1387 58 3118",
            "-1344 140 3118",
            "-1357 32 3185",
        ],
    },
    "cyan": {
        "whitelisted_lore_lines":["Celsian Isles : Trophy",],
        "container_whitelist":[
            "-1509 234 4630",
            "-1509 234 4632",
            "-1509 234 4633",
            "-1372 42 4756",
            "-1284 123 4817",
        ],
    },
    "lightgray": {
        "whitelisted_lore_lines":["Celsian Isles : Trophy",],
        "container_whitelist":[
            "-1366 200 4233",
        ],
    },
    "depths": {
        "container_whitelist":[
            "-995 128 2299",
        ],
    },
    "depthsrooms": {
        "container_whitelist":[
            "-328 10 9143",
            "-328 11 9366",
        ],
    },
    "purple": {
        "whitelisted_lore_lines":["Celsian Isles : Trophy",],
        "container_whitelist":[
            "-1402 222 6720",
            "-1402 216 6720",
            "-1325 39 6722",
            "-1459 195 6749",
            "-1459 195 6748",
            "-1323 116 6774",
            "-1307 46 6791",
            "-1321 181 6803",
            "-1414 72 6863",
            "-1436 181 6933",
        ],
    },
    "shiftingcity": {
        "whitelisted_lore_lines":["Celsian Isles : Trophy",],
        "container_whitelist":[
            "-773 207 4863",
            "-768 207 4863",
            "-770 207 4865",
            "-771 207 4865",
            "-757 95 4865",
        ],
    },
    "shiftingrooms": {
        "container_whitelist":[
            "-2156 240 -2094",
            "-2067 235 -2090",
            "-2104 241 -2070",
            "-2086 193 -2078",
            "-2016 37 -2072",
            "-2000 157 -2026",
        ],
    },
    "teal": {
        "whitelisted_lore_lines":["Celsian Isles : Trophy", "Celsian Isles : Key"],
        "container_whitelist":[
            "-617 148 6277",
            "-859 158 6514",
        ],
    },
    "forum": {
        "whitelisted_lore_lines":["Celsian Isles : Trophy",],
        "container_whitelist":[
            "-1466 36 8301",
            "-1243 137 8348",
            "-1300 46 8415",
            "-1235 166 8434",
            "-1237 171 8468",
            "-1238 172 8466",
            "-1155 54 8477",
            "-1150 133 8468",
            "-1272 152 8532",
            "-1291 145 8557",
            "-1413 142 8574",
        ],
    },

    #################### R3 ####################

    "blue": {
        "whitelisted_lore_lines":["Architect's Ring : Trophy",],
        "container_whitelist":[
            "400 499 -1069",
            "3415 349 517",
            "3815 349 517",
            "4215 349 517",
            "2215 349 517",
            "4615 349 517",
            "2615 349 517",
            "3015 349 517",
            "1815 349 517",
        ],
    },
    "brown": {
        "whitelisted_lore_lines":["Architect's Ring : Trophy",],
        "container_whitelist":[
            "-201 226 7422",
            "-277 72 7579",
            "-275 72 7582",
            "-275 72 7581",
            "-277 72 7584",
            "-282 73 7589",
        ],
    },
    "zenith": {
        "container_whitelist":[],
    },
}

if __name__ == '__main__':
    multiprocessing.set_start_method("fork")

    cpu_count = os.cpu_count()
    if cpu_count is None:
        cpu_count = 1
    default_thread_count = cpu_count // 4
    if default_thread_count < 1:
        default_thread_count = 1

    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('worlds', type=str, nargs='*')
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('-j', '--num-threads', type=int, default=default_thread_count)
    args = arg_parser.parse_args()

    missing_loot_tables = 0

    worlds_to_process = []
    available_worlds = World.enumerate_worlds(dungeon_path)
    for world_name in available_worlds:
        # If provided command line arguments, filter down to just those worlds
        if len(args.worlds) > 0 and world_name not in args.worlds:
            continue

        # If no worlds specified manually, skip the overworld and any world name that ends with assets
        if len(args.worlds) == 0 and (world_name == "Project_Epic-dungeon" or world_name.endswith("assets")):
            continue

        worlds_to_process.append((args.verbose, dungeons, dungeon_path, world_name))

    for world_name in args.worlds:
        if world_name not in available_worlds:
            sys.exit(f"Unable to process nonexistent world '{world_name}'")

    print(f"Processing worlds with {args.num_threads} threads : {[item[3] for item in worlds_to_process]}")

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.num_threads) as pool:
        results = pool.map(process_world, worlds_to_process)

    for num_non_loot_table_containers, text  in results:
        missing_loot_tables += num_non_loot_table_containers
        print(text)

    if missing_loot_tables == 0:
        print("No loot tables missing.")
    print("Done.")

    sys.exit(min(missing_loot_tables, (2**31)-1))
