#!/usr/bin/env python3

import json

import os
import sys
import getopt
from pprint import pprint

from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path
from lib_py3.common import eprint, get_item_name_from_nbt
from lib_py3.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

def get_item_location_key(debug_path: [nbt.TagCompound]) -> str:
    """
    Takes an item path and returns a unique-ish string like this to use as a hash key:
    x_y_z_topContainerId_itemDepth
    """

    x = None
    y = None
    z = None
    if debug_path[0].has_path("Pos"):
        x = debug_path[0].at_path('Pos').value[0].value
        y = debug_path[0].at_path('Pos').value[1].value
        z = debug_path[0].at_path('Pos').value[2].value

    if debug_path[0].has_path("x"):
        x = debug_path[0].at_path('x').value
        y = debug_path[0].at_path('y').value
        z = debug_path[0].at_path('z').value

    x = int(round(x))
    y = int(round(y))
    z = int(round(z))

    if x is None or y is None or z is None:
        raise Exception("Damaged item with no debug path location")

    return f"{x}_{y}_{z}_{debug_path[0].at_path('id').value.lower().replace('minecraft:','')}_{len(debug_path)}"

repair_map = {}

broken_items = []
with open("REPAIR/all_plots_infusions_pre_116_upgrade.json", "r") as fin:
    broken_items = json.load(fin)

num_broken = 0
num_skipped = 0

for broken_item in broken_items:
    num_broken += 1

    debug_path = []
    for debug_path_entry_str in broken_item["path"]:
        debug_path.append(nbt.TagCompound.from_mojangson(debug_path_entry_str))

    fullitem = nbt.TagCompound.from_mojangson(broken_item["from"])
    nbttag = fullitem.at_path("tag")
    broken_item['from'] = nbttag.to_mojangson()
    broken_item['name'] = get_item_name_from_nbt(nbttag, remove_color=True)

    location_key = get_item_location_key(debug_path)
    if location_key in repair_map:
        repair_map[location_key].append(broken_item)
    else:
        repair_map[location_key] = [broken_item,]

    #print(json.dumps(repair_map, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': ')))
    #crash


with open("REPAIR/repair_map.json", "w") as fout:
    json.dump(repair_map, fout, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

print("Broken items added to map:", num_broken)
print("Not broken items skipped:", num_skipped)
