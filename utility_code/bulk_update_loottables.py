#!/usr/bin/env python3

import os
import sys
import json
import re
from pprint import pprint

from lib_py3.loot_table_manager import LootTableManager
from lib_py3.common import parse_name_possibly_json

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt
from quarry.types.text_format import unformat_text

def update_items(container_nbt_list):
    mgr = LootTableManager()
    mgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")

    for container_nbt in container_nbt_list:
        if "Items" not in container_nbt.value:
            raise KeyError("NBT does not contain Items!")

        for item_nbt in container_nbt.at_path("Items").value:
            if not item_nbt.has_path("id"):
                raise KeyError("Item does not contain id!")
            if not item_nbt.has_path("tag"):
                raise KeyError("Item does not contain tag!")
            if not item_nbt.has_path("tag.display.Name"):
                raise KeyError("Item does not contain tag.display.Name!")

            item_id = item_nbt.at_path("id").value
            item_nbt_str = item_nbt.at_path("tag").to_mojangson()
            item_name = parse_name_possibly_json(item_nbt.at_path('tag.display.Name').value)

            locations = mgr.update_item_in_loot_tables(item_id, item_nbt_str=item_nbt_str)
            print("Updated '{}' in loot tables: \n{}".format(item_name, "\n".join(locations)))

def usage():
    sys.exit("Usage: " + sys.argv[0] + " <text_file_with_setblock_chest.txt>")

filename = None
for arg in sys.argv[1:]:
    if filename is None:
        filename = arg
    else:
        usage()

if filename is None:
    usage()

with open(filename,'r') if filename != "-" else sys.stdin as f:
    container_nbt_list = []
    while True:
        raw = f.readline().strip()
        if not raw:
            break

        # Strip everything before the item/block type
        raw = re.sub('^[^{]*( [^ {]*{)', r'\1', raw.strip())

        # Strip the count
        raw = re.sub('}[^}]*$', '}', raw.strip())

        item_type = re.sub('{.*$', '', raw)
        nbt_str = re.sub('^[^{]*{', '{', raw)

        item_nbt = nbt.TagCompound.from_mojangson(nbt_str)
        container_nbt_list.append(item_nbt)

    update_items(container_nbt_list)
