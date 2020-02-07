#!/usr/bin/env python3

from pprint import pprint

from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager

lootmgr = LootTableManager()
lootmgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")
mgr = ItemReplacementManager(lootmgr.get_unique_item_map())
