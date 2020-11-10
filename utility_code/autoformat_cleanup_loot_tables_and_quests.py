#!/usr/bin/env python3

import os

from lib_py3.loot_table_manager import LootTableManager
from lib_py3.upgrade import upgrade_text_containing_mojangson, upgrade_json_file, upgrade_mcfunction_file

mgr = LootTableManager()

# AUTOFORMAT
#mgr.load_loot_tables_directory("/home/epic/project_epic/server_config/data/datapacks/base/data/epic/loot_tables/index")

upgrade_path = '/home/epic/project_epic/server_config/data'
#upgrade_path = '../data/datapacks/base/data/monumenta/functions/mechanisms/buyback/'
mgr.autoformat_json_files_in_directory(upgrade_path, indent=2)

for root, subdirs, files in os.walk(upgrade_path):
    for fname in files:
        path = os.path.join(root, fname)
        if fname.endswith(".json"):
            if not "loot_tables" in path: # Loot tables are upgraded by the loot table manager
                upgrade_json_file(path, convert_checks_to_plain="auto")
                pass
        elif fname.endswith(".mcfunction"):
            upgrade_mcfunction_file(path, convert_checks_to_plain="auto")
            pass

