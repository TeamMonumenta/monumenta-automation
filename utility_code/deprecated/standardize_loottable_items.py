#!/usr/bin/env python3

import os
import sys

from lib_py3.loot_table_manager import LootTableManager

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

mgr = LootTableManager()
mgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")

container_nbt = []
chestcount = 0
for item_id in mgr.item_map:
    for item in mgr.item_map[item_id]:
        if type(mgr.item_map[item_id][item]) is list:
            item_nbt = mgr.item_map[item_id][item][0]["nbt"]
        else:
            item_nbt = mgr.item_map[item_id][item]["nbt"]

        item_nbt_str = item_nbt.to_mojangson()
        if "Lantern" not in item_nbt_str:
            mgr.update_item_in_loot_tables(item_id, item_nbt_str=item_nbt_str)

