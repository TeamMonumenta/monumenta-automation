#!/usr/bin/env python3
"""Dumps items from loot tables to give chest commands on stdout."""

import argparse
import os
import sys
import json

from lib_py3.loot_table_manager import LootTableManager

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt


def is_up_to_date(item_tag):
    """Returns true if an item is up to date."""
    if item_tag.has_path("Monumenta"):
        return True
    return False


def print_give_chest(chest_count, container_list):
    chest_name_json = json.dumps({"text":str(chest_count)})
    chest_tag = nbt.TagCompound({
        "BlockEntityTag": nbt.TagCompound({
            "Items": nbt.TagList(container_list),
            "id": nbt.TagString("minecraft:chest")
        }),
        "display": nbt.TagCompound({
            "Name": nbt.TagString(chest_name_json)
        })
    })
    print('give @s chest' + chest_tag.to_mojangson())


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
            if isinstance(mgr.item_map[item_id][item], list):
                entry = mgr.item_map[item_id][item][0]
            else:
                entry = mgr.item_map[item_id][item]
            if entry["generated"]:
                # Skip generated entries
                continue
            item_nbt = entry["nbt"]
            if args.unupdated and is_up_to_date(item_nbt):
                continue

            item_slot = nbt.TagCompound({
                "Slot": nbt.TagByte(len(containerlist)),
                "Count": nbt.TagByte(1),
                "id": nbt.TagString(item_id),
                "tag": item_nbt
            })
            containerlist.append(item_slot)
            if len(containerlist) == 27:
                chestcount += 1
                print_give_chest(chestcount, containerlist)
                containerlist = []

    chestcount += 1
    print_give_chest(chestcount, containerlist)
    containerlist = []


if __name__ == '__main__':
    main()
