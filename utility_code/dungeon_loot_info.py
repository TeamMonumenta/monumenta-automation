#!/usr/bin/env python3

import copy
import math
import os
import statistics
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../"))

from lib_py3.world import World
from lib_py3.common import DictWithDefault
from lib_py3.common import get_item_name_from_nbt

world = World('/home/epic/project_epic/dungeon/Project_Epic-dungeon')

dungeons = (
    {
        "name":"white",
        "region":{"x":-3, "z":-2},
    },{
        "name":"orange",
        "region":{"x":-3, "z":-1},
    },{
        "name":"magenta",
        "region":{"x":-3, "z":0},
    },{
        "name":"lightblue",
        "region":{"x":-3, "z":1},
    },{
        "name":"yellow",
        "region":{"x":-3, "z":2},
    },{
        "name":"willows",
        "region":{"x":-3, "z":3},
    },{
        "name":"roguelike",
        "region":{"x":-2, "z":-1},
    },{
        "name":"reverie",
        "region":{"x":-3, "z":4},
    },{
        "name":"tutorial",
        "region":{"x":-2, "z":0},
    },{
        "name":"sanctum",
        "region":{"x":-3, "z":12},
    },{
        "name":"labs",
        "region":{"x":-2, "z":2},
    },{
        "name":"lime",
        "region":{"x":-3, "z":5},
    },{
        "name":"pink",
        "region":{"x":-3, "z":7},
    },{
        "name":"gray",
        "region":{"x":-3, "z":6},
    },{
        "name":"cyan",
        "region":{"x":-3, "z":9},
    },{
        "name":"light_gray",
        "region":{"x":-3, "z":8},
    },{
        "name":"purple",
        "region":{"x":-3, "z":13},
    },{
        "name":"shiftingcity",
        "region":{"x":-2, "z":9},
    },{
        "name":"teal",
        "region":{"x":-2, "z":12},
    },{
        "name":"forum",
        "region":{"x":-3, "z":16},
    },{
        "name":"rush",
        "region":{"x":-3, "z":15},
    },
)

def out_of_bounds(pos1, source_pos, pos2):
    if type(source_pos) is not tuple:
        return True
    for axis in range(3):
        if pos1[axis] > source_pos[axis] or source_pos[axis] > pos2[axis]:
            return True
    return False

for dungeon in dungeons:
    rx = dungeon["region"]["x"]
    rz = dungeon["region"]["z"]

    pos1 = (512*rx      ,   0, 512*rz      )
    pos2 = (512*rx + 511, 255, 512*rz + 511)

    items = DictWithDefault(
        # Key is "item_id item_name"
        default=0
    )
    loottables = DictWithDefault(
        # Key is loottable
        default=0
    )

    """
    Find loot tables
    """
    for entity, source_pos, entity_path in world.entity_iterator():
        # Why doesn't the items iterator take pos1, pos2 properly?
        if out_of_bounds(pos1, source_pos, pos2):
            continue

        if not entity.has_path('LootTable'):
            continue
        loottable = entity.at_path('LootTable').value
        loottables[loottable] += 1

    """
    Find items
    """
    for item, source_pos, entity_path in world.items(pos1=pos1, pos2=pos2, readonly=True):
        # Why doesn't the items iterator take pos1, pos2 properly?
        if out_of_bounds(pos1, source_pos, pos2):
            continue

        # Ignore entities, we only care about tile entities
        if type(source_pos[0]) == float:
            continue

        # Ignore mob spawners
        if len(entity_path) >= 1 and entity_path[0].has_path("id"):
            if entity_path[0].at_path("id").value == "minecraft:mob_spawner":
                continue

        # Ignore BoS:
        if item.has_path('tag.author') and item.at_path('tag.author').value == "§6The Creator":
            continue

        if not item.has_path('id'):
            continue
        item_id = item.at_path('id').value

        item_name = None
        if item.has_path('tag.display.Name'):
            item_name = get_item_name_from_nbt(item.at_path('tag'))

        if item_name is None:
            item_name = "with no name"
        else:
            item_name = "named {}".format(item_name)

        item_count = 1
        if item.has_path('Count'):
            item_count = item.at_path('Count').value

        items[item_id + " " + item_name] += item_count

    """
    Print findings
    """
    print(dungeon["name"] + ":")
    print("  - Loose items:")
    for item_details, count in items.items():
        print("    - x{0:3d} {1}".format(count, item_details))
    print("  - Loot tables:")
    for loottable, count in loottables.items():
        print("    - x{0:3d} {1}".format(count, loottable))

