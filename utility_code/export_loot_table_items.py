#!/usr/bin/env python3

import os
import sys
import json

from lib_py3.loot_table_manager import LootTableManager

out_name = sys.argv[1]
out_map = {}

mgr = LootTableManager()
mgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")

for item_type in mgr.item_map:
    next_map = mgr.item_map[item_type]
    items = {}
    for item_name in next_map:
        item = next_map[item_name]
        locs = []
        nbt = None
        if type(item) is list:
            for elem in item:
                if not elem.get("generated", False):
                    locs.append(elem["file"].replace("/home/epic/project_epic/server_config/", ""))
                    nbt = elem["nbt"]
        else:
            if not elem.get("generated", False):
                locs.append(item["file"].replace("/home/epic/project_epic/server_config/", ""))
                nbt = item["nbt"]

        if nbt is not None:
            items[item_name] = {"files": locs, "nbt": nbt.to_mojangson()}
    if len(items) > 0:
        out_map[item_type] = items


with open(out_name, 'w') as outfile:
    json.dump(out_map, outfile, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))
