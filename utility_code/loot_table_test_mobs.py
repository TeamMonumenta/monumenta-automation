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

world = World('/home/rock/project_epic/mobs/Project_Epic-mobs')
# pos1 must be less than pos2 on every axis
pos1 = (-1024, 16, -1584)
pos2 = (-1009, 30, -1569)

total_chests = 1024
print("""Items found in the {} chests at "/warp loottest" on the mobs shard:""".format(total_chests))

def out_of_bounds(pos1, source_pos, pos2):
    if type(source_pos) is not tuple:
        return True
    for axis in range(3):
        if pos1[axis] > source_pos[axis] or source_pos[axis] > pos2[axis]:
            return True
    return False

"""
First, group together stacks of items that Minecraft spreads out by default,
getting a count of each ID/Name pair in that chest.

This is handled per-chest, where each chest is a roll of the loot table.
"""
despread_items = DictWithDefault(
    # key = source_pos
    default=DictWithDefault(
        # key = ID
        default=DictWithDefault(
            # key = Name
            # value = Count
            default=0
        )
    )
)
for item, source_pos, entity_path in world.items(pos1=pos1, pos2=pos2, readonly=True):
    # Why doesn't the items iterator take pos1, pos2 properly?
    if out_of_bounds(pos1, source_pos, pos2):
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

    despread_items[source_pos][item_id][item_name] += item_count

"""
Next, combine the stats of all the chests to get the stats of a typical roll.
"""
item_count_map = DictWithDefault(
    # key = ID
    default=DictWithDefault(
        # key = Name
        default={
            "total":0,
            "stacks":0,
            "by_count":DictWithDefault(
                # Key = Count in stack
                # Value = stacks with that count
                default=0
            )
        }
    )
)
total_stacks = 0
total_items = 0
max_item_id_chars = 0
max_item_count_chars = 0

for chest_contents in despread_items.values():
    for item_id in chest_contents.keys():
        for item_name, item_count in chest_contents[item_id].items():
            item_count_map[item_id][item_name]["stacks"] += 1
            item_count_map[item_id][item_name]["total"] += item_count

            item_count_map[item_id][item_name]["by_count"][item_count] += 1

            total_stacks += 1
            total_items += item_count
            max_item_id_chars = max(max_item_id_chars, len(item_id))
            max_item_count_chars = max(max_item_count_chars, 1 + int(math.log10(max(1, item_count))))

"""
Now we've got our data, we sort it to print in whatever order we want,
getting the number of characters for text fields that can get rather long.
"""
items_by_odds = DictWithDefault(default=[])
for item_id in item_count_map.keys():
    for item_name in item_count_map[item_id].keys():
        item_count = item_count_map[item_id][item_name]["total"]

        #odds = item_count / total_items
        odds = item_count / total_chests
        item_details = (item_id, item_name)

        items_by_odds[odds].append(item_details)

item_probability_format  = "+ {0:9.5f} x {1:<" + str(max_item_id_chars) + "} {2}"
# 0 is odds
# 1 is item_id
# 2 is item_name

count_average_format     = "    - Count Mean:  {0:9.5f}"
# 0 is average

count_stdev_format       = "    - Count Stdev: {0:9.5f}"
# 0 is stdev

count_probability_format = "    - x{0:>" + str(max_item_count_chars) + "} {1:9.5f} x of the time"
# 0 is item_count
# 1 is odds_count

"""
Finally, we pretty print the results.
"""
print("Total stacks: {}".format(total_stacks))
print("Total items:  {}".format(total_items))

for odds in sorted(items_by_odds.keys(),reverse=True):
    for item_id, item_name in sorted(items_by_odds[odds]):
        print(item_probability_format.format(odds, item_id, item_name))

