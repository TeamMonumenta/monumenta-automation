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


repair_map = {}

broken_items = []
with open("REPAIR/repair_map_out.json", "r") as fin:
    broken_items = json.load(fin)

num_shattered = 0
num_unfixed_not_shattered = 0
for broken_item_location in broken_items:
    for broken_item in broken_items[broken_item_location]:
        if "repaired" not in broken_item:
            if "SHATTERED" in broken_item["changed"]:
                num_shattered += 1
            else:
                print(f"{broken_item_location} | {broken_item['name']} | {broken_item['changed']}")
                num_unfixed_not_shattered += 1



print("Number of shattered items not fixed:", num_shattered)
print("Number of broken items that were not shattered and not fixed:", num_unfixed_not_shattered)
