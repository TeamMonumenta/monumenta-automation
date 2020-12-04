#!/usr/bin/env python3

import json
from pprint import pprint
from lib_py3.loot_table_manager import LootTableManager

repair_map = {}
with open("REPAIR/repair_map_pre_filter_previous_repairs.json", "r") as fin:
    repair_map = json.load(fin)

repair_map_previous = {}
with open("REPAIR/actual_repair_map_nov_26_out.json", "r") as fin:
    repair_map_previous = json.load(fin)

loot_table_manager = LootTableManager()
loot_table_manager.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")
unique_item_map = loot_table_manager.get_unique_item_map(show_errors=True)
unique_item_names = set()
for item_id in unique_item_map:
    unique_item_names.update(unique_item_map[item_id].keys())
#pprint(unique_item_names)

num_repaired_before = 0
num_remaining = 0
num_remaining_new = 0
num_not_in_loot_tables = 0

to_pop_locations = []
repair_map_not_in_tables = []
for location in repair_map:
    repair_map_loc = repair_map[location]
    new_repair_map_loc = []

    for current_entry in repair_map_loc:
        if location in repair_map_previous:
            # This location WAS in the last attempt

            notexists = True
            for previous_entry in repair_map_previous[location]:
                if previous_entry["name"] == current_entry["name"] and "repaired" in previous_entry:
                    num_repaired_before += 1
                    notexists = False
                    break

            if notexists:
                if current_entry["name"] in unique_item_names:
                    if "Items:[" in current_entry["from"]:
                        print("Warn: Skipping for items: ", current_entry["name"])
                    else:
                        new_repair_map_loc.append(current_entry)
                        num_remaining += 1
                else:
                    num_not_in_loot_tables += 1
                    repair_map_not_in_tables.append(current_entry)

        else:
            # This location was NOT in the last attempt

            if current_entry["name"] in unique_item_names:
                if "Items:[" in current_entry["from"]:
                    print("Warn: Skipping for items: ", current_entry["name"])
                else:
                    new_repair_map_loc.append(current_entry)
                    num_remaining_new += 1
            else:
                num_not_in_loot_tables += 1
                repair_map_not_in_tables.append(current_entry)

    if len(new_repair_map_loc) == 0:
        to_pop_locations.append(location)
    else:
        repair_map[location] = new_repair_map_loc

for location in to_pop_locations:
    repair_map.pop(location)

with open("REPAIR/repair_map_filtered.json", "w") as fout:
    json.dump(repair_map, fout, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))
with open("REPAIR/repair_map_ignored_not_in_tables.json", "w") as fout:
    json.dump(repair_map_not_in_tables, fout, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

print(f"Removed {num_repaired_before} items that had been repaired before")
print(f"{num_remaining} items remain to be repaired in locations previously known")
print(f"{num_remaining_new} items remain to be repaired in locations that were not previously in the map")
print(f"{num_not_in_loot_tables} items had infusions but are not in loot tables so will not be fixed")
