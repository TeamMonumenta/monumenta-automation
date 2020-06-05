#!/usr/bin/env python3

from lib_py3.loot_table_manager import LootTableManager

mgr = LootTableManager()

# AUTOFORMAT
mgr.load_loot_tables_directory("base/data/epic/loot_tables/index")
mgr.autoformat_json_files_in_directory("/home/epic/MCEdit-And-Automation/utility_code/base", indent=2)
