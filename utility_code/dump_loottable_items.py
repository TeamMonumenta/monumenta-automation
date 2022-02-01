#!/usr/bin/env python3
"""Dumps items from loot tables to give chest commands on stdout."""

import argparse
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


def is_up_to_date(item_id, plain_name, item_tag):
    if item_tag.has_path("Monumenta"):
        return True
    return False


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('--unupdated', action='store_true')
    args = arg_parser.parse_args()

    mgr = LootTableManager()
    mgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")

    containerlist = []
    chestcount = 0
    for item_id in mgr.item_map:
        for item in mgr.item_map[item_id]:
            if type(mgr.item_map[item_id][item]) is list:
                entry = mgr.item_map[item_id][item][0]
            else:
                entry = mgr.item_map[item_id][item]
            if entry["generated"]:
                # Skip generated entries
                continue
            item_nbt = entry["nbt"]
            if args.unupdated and is_up_to_date(item_id, item, item_nbt):
                continue

            item_slot = nbt.TagCompound({"Slot": nbt.TagByte(len(containerlist)), "Count": nbt.TagByte(1), "id": nbt.TagString(item_id), "tag": item_nbt})
            containerlist.append(item_slot)
            if len(containerlist) == 27:
                chestcount += 1
                print(r'''give @s chest{display:{Name:"\"''' + str(chestcount) + r'''\""},''' + nbt.TagCompound({"id": nbt.TagString("minecraft:chest"), "BlockEntityTag": nbt.TagCompound({"Items": nbt.TagList(containerlist)})}).to_mojangson()[1:])
                containerlist = []

    chestcount += 1
    print(r'''give @s chest{display:{Name:"\"''' + str(chestcount) + r'''\""},''' + nbt.TagCompound({"id": nbt.TagString("minecraft:chest"), "BlockEntityTag": nbt.TagCompound({"Items": nbt.TagList(containerlist)})}).to_mojangson()[1:])
    containerlist = []


if __name__ == '__main__':
    main()
