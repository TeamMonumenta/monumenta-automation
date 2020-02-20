#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../"))

from lib_py3.world import World

world = World('/home/epic/project_epic/dungeon/Project_Epic-dungeon')
debug = False

dungeons = (
    {
        "name":"white",
        "region":{"x":-3, "z":-2},
        "whitelisted_lore_lines":("Monument Block",),
        "container_whitelist":(
            "-1409 37 -776",
            "-1409 37 -775",
            "-1443 42 -828",
            "-1442 42 -828",
            "-1458 30 -816",
            "-1487 71 -920",
            "-1529 120 -975",
            "-1517 32 -782",
            "-1387 24 -756",
            "-1420 42 -877",
        ),
    },{
        "name":"orange",
        "region":{"x":-3, "z":-1},
        "whitelisted_lore_lines":("Monument Block",),
    },{
        "name":"magenta",
        "region":{"x":-3, "z":0},
        "whitelisted_lore_lines":("Monument Block",),
        "container_whitelist":(
            "-1381 88 91",
            "-1379 88 92",
        ),
    },{
        "name":"lightblue",
        "region":{"x":-3, "z":1},
        "whitelisted_lore_lines":("Monument Block",),
        "container_whitelist":(
            "-1381 180 645",
            "-1456 170 694",
            "-1371 175 598",
            "-1423 178 593",
            "-1265 181 598",
        ),
    },{
        "name":"yellow",
        "region":{"x":-3, "z":2},
        "whitelisted_lore_lines":("Monument Block",),
        "container_whitelist":(
            "-1488 65 1086",
            "-1460 90 1239",
            "-1489 65 1087",
            "-1506 103 1165",
            "-1513 40 1152",
            "-1493 65 1095",
            "-1493 65 1096",
            "-1493 63 1094",
            "-1491 65 1089",
            "-1490 65 1088",
            "-1490 65 1098",
            "-1490 63 1098",
            "-1493 40 1094",
            "-1490 42 1098",
            "-1462 140 1104",
            "-1488 65 1098",
            "-1487 65 1098",
            "-1486 63 1098",
            "-1455 104 1178",
            "-1513 40 1150",
        ),
    },{
        "name":"willows",
        "region":{"x":-3, "z":3},
    },{
        "name":"roguelike",
        "region":{"x":-2, "z":-1},
    },{
        "name":"nightmare",
        "region":{"x":-3, "z":4},
        "container_whitelist":(
            "-1341 128 2154",
            "-1358 59 2306",
            "-1453 51 2295",
            "-1261 49 2416",
            "-1450 103 2318",
            "-1393 41 2312",
            "-1265 90 2337",
            "-1358 59 2329",
            "-1307 3 2170",
            "-1332 120 2411",
            "-1304 59 2246",
            "-1280 77 2177",
            "-1280 77 2176",
        ),
    },{
        "name":"tutorial",
        "region":{"x":-2, "z":0},
        "container_whitelist":(
            "-972 43 35",
            "-1010 48 27",
            "-986 20 71",
            "-987 20 71",
            "-987 13 22",
            "-986 13 22",
            "-991 5 27",
            "-970 52 60",
            "-957 49 71",
            "-997 20 82",
        ),
    },{
        "name":"labs",
        "region":{"x":-2, "z":1},
    },{
        "name":"lime",
        "region":{"x":-3, "z":5},
        "whitelisted_lore_lines":("Monument Block",),
    },{
        "name":"pink",
        "region":{"x":-3, "z":7},
        "whitelisted_lore_lines":("Monument Block",),
    },{
        "name":"gray",
        "region":{"x":-3, "z":6},
        "whitelisted_lore_lines":("Monument Block",),
    },{
        "name":"cyan",
        "region":{"x":-3, "z":9},
        "whitelisted_lore_lines":("Monument Block",),
    },{
        "name":"lightgray",
        "region":{"x":-3, "z":8},
        "whitelisted_lore_lines":("Monument Block",),
    },{
        "name":"purple",
        "region":{"x":-3, "z":13},
        "whitelisted_lore_lines":("Monument Block",),
    },{
        "name":"lime",
        "region":{"x":-3, "z":5},
        "whitelisted_lore_lines":("Monument Block",),
    },{
        "name":"shiftingcity",
        "region":{"x":-2, "z":9},
        "whitelisted_lore_lines":("Monument Block",),
    },
)

missing_loot_tables = 0

for dungeon in dungeons:
    name = dungeon["name"]
    rx = dungeon["region"]["x"]
    rz = dungeon["region"]["z"]

    container_entity_ids = dungeon.get("container_entity_ids", ["minecraft:chest"])
    whitelisted_lore_lines = dungeon.get("whitelisted_lore_lines", [])
    container_whitelist = list(dungeon.get("container_whitelist", []))

    for i in range(len(container_whitelist)):
        old_coords = container_whitelist[i]
        if isinstance(old_coords, str):
            new_coords = []
            old_coords = old_coords.replace(",", " ")
            for coord in old_coords.split(" "):
                if len(coord) == 0:
                    continue
                new_coords.append(coord)
            container_whitelist[i] = tuple(new_coords)

    pos1 = (512*rx      ,   0, 512*rz      )
    pos2 = (512*rx + 511, 255, 512*rz + 511)

    lootless_containers = []

    ok_loottable = 0
    ok_ids = set()
    ok_pos = []
    ok_lore = set()

    """
    Find missing loot tables
    """
    for entity, source_pos, entity_path in world.entity_iterator(pos1, pos2, readonly=True):
        if entity.has_path('LootTable'):
            # This container is all set
            ok_loottable += 1
            continue

        if not entity.has_path('id'):
            # No container ID, this is nested.
            continue

        entity_id = entity.at_path('id').value
        if entity_id not in container_entity_ids:
            # Not a container ID we care about
            ok_ids.add(entity_id)
            continue

        if (
            not entity.has_path('x')
            or not entity.has_path('y')
            or not entity.has_path('z')
        ):
            # Has no position
            continue

        pos = (
            entity.at_path('x').value,
            entity.at_path('y').value,
            entity.at_path('z').value
        )

        if pos in container_whitelist:
            # Whitelisted position
            ok_pos.append(pos)
            continue

        if entity.has_path('Items'):
            found_whitelisted_item = False

            items = entity.at_path('Items').value
            for item in items:
                if not item.has_path('tag.display.Lore'):
                    continue

                lore_lines = item.at_path('tag.display.Lore').value
                for lore_line in lore_lines:
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
        lootless_containers.append(entity)

    print("{}:".format(name))

    print("- Containers with loot tables: {}".format(ok_loottable))

    if debug:
        if ok_ids:
            print("- Other ids found:")
            for thing in sorted(ok_ids):
                print("  - {}".format(thing))

        if ok_pos:
            print("- Whitelisted positions found:")
            for thing in sorted(ok_pos):
                print("  - {}".format(thing))

        if ok_lore:
            print("- Lore that matched whitelist:")
            for thing in sorted(ok_lore):
                print("  - {}".format(thing))

    if lootless_containers:
        print("- Lootless containers: {}. Top line teleports your face into the block, bottom line is a whitelist entry if it's allowed:".format(len(lootless_containers)))

        for entity in lootless_containers:
            pos = (
                entity.at_path('x').value,
                entity.at_path('y').value,
                entity.at_path('z').value,
            )

            print("-"*80)
            print("/tp @s {} {} {}".format(
                pos[0],
                pos[1] - 1.2,
                pos[2],
            ))
            print('            "{} {} {}",'.format(
                pos[0],
                pos[1],
                pos[2]
            ))

        print("-"*80)

    if not (
        ok_loottable
        or ok_ids
        or ok_pos
        or ok_lore
        or lootless_containers
    ):
        print("- No containers detected at all...wait, what?")

    print("="*80)

    missing_loot_tables += len(lootless_containers)

if missing_loot_tables == 0:
    print("No loot tables missing.")
print("Done.")

sys.exit(min(missing_loot_tables, (2**31)-1))

