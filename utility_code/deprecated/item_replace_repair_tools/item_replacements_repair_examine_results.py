#!/usr/bin/env python3

import json

import os
import sys
import getopt
from pprint import pprint

from lib_py3.loot_table_manager import LootTableManager
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path
from lib_py3.common import eprint, get_item_name_from_nbt
from lib_py3.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

loot_table_manager = LootTableManager()
loot_table_manager.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")
unique_item_map = loot_table_manager.get_unique_item_map(show_errors=False)

lost_enchants = [
    (' SHATTERED ', False),
    ('Soulbound to', False),
    ('Hope', False),
    ('Gilded', False),
    ('Festive', False),
    ('Acumen', True),
    ('Focus', True),
    ('Perspicacity', True),
    ('Tenacity', True),
    ('Vigor', True),
    ('Vitality', True),
    ('Barking', True),
    ('Debarking', True),
]
def contains_infusions(from_mojangson: str) -> [str]:
    global lost_enchants

    count_before = 0
    count_after = 0
    infusions = []
    for enchant, uses_levels in lost_enchants:
        if from_mojangson.count(enchant) > 0:
            if uses_levels:
                nextblock = from_mojangson[from_mojangson.index(enchant) + len(enchant):]
                if nextblock.startswith(" V"):
                    enchant += " V"
                elif nextblock.startswith(" IV"):
                    enchant += " IV"
                elif nextblock.startswith(" III"):
                    enchant += " III"
                elif nextblock.startswith(" II"):
                    enchant += " II"
                elif nextblock.startswith(" I"):
                    enchant += " I"
            infusions.append(enchant.strip())

    return infusions

def get_from_unique_item_map(name: str) -> [str]:
    global unique_item_map
    for item_id in unique_item_map:
        if name in unique_item_map[item_id]:
            return contains_infusions(unique_item_map[item_id][name]["nbt"].to_mojangson())
    return "NOPE"




repair_map = {}

broken_items = []
with open("REPAIR/2nd_try_repair_map_out.json", "r") as fin:
    broken_items = json.load(fin)

num_shattered = 0
num_unfixed_not_shattered = 0
for broken_item_location in broken_items:
    for broken_item in broken_items[broken_item_location]:
        if "repaired" not in broken_item:
            base_item_stats = get_from_unique_item_map(broken_item['name'])
            stats = contains_infusions(broken_item["from"])
            for stat in base_item_stats:
                stats.remove(stat)

            if len(stats) > 0 and (len(stats) > 1 or stats[0] != "SHATTERED"):
                print("{:30} {:30} {}".format(broken_item_location, broken_item['name'], ", ".join(stats)))

