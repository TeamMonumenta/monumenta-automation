#!/usr/bin/env python3

import os
import sys
import json
import re
from collections import OrderedDict
from pprint import pprint

from lib_py3.loot_table_manager import LootTableManager
from lib_py3.upgrade import upgrade_entity
from lib_py3.common import parse_name_possibly_json

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt
from quarry.types.text_format import unformat_text

mgr = LootTableManager()
mgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")

containerlist = []
chestcount = 0
for item_id in mgr.item_map:
    for item in mgr.item_map[item_id]:
        if type(mgr.item_map[item_id][item]) is list:
            item_nbt = mgr.item_map[item_id][item][0]["nbt"]
        else:
            item_nbt = mgr.item_map[item_id][item]["nbt"]

        item_slot = nbt.TagCompound({"Slot": nbt.TagByte(len(containerlist)), "Count": nbt.TagByte(1), "id": nbt.TagString(item_id), "tag": item_nbt})
        containerlist.append(item_slot)
        if len(containerlist) == 27:
            chestcount += 1
            print(r'''give @s chest{display:{Name:"\"''' + str(chestcount) + r'''\""},''' + nbt.TagCompound({"id": nbt.TagString("minecraft:chest"), "BlockEntityTag": nbt.TagCompound({"Items": nbt.TagList(containerlist)})}).to_mojangson()[1:])
            containerlist = []

chestcount += 1
print(r'''give @s chest{display:{Name:"\"''' + str(chestcount) + r'''\""},''' + nbt.TagCompound({"id": nbt.TagString("minecraft:chest"), "BlockEntityTag": nbt.TagCompound({"Items": nbt.TagList(containerlist)})}).to_mojangson()[1:])
containerlist = []

