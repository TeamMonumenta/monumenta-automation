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
    return False
    # Old pre 1.18 stuff? Maybe a useful example
    # if item_tag.has_path("Monumenta"):
    #     return True
    # if (
    #     not item_tag.has_path("display.Lore")
    #     and not item_tag.has_path("AttributeModifiers")
    #     and not item_tag.has_path("Enchantments")
    # ):
    #     return True
    # return False

def return_chest(chest_count, container_list) -> str:
    chest_name_json = json.dumps({"text":str(chest_count)})
    chest_tag = nbt.TagCompound({
        "Items": nbt.TagList(container_list),
        "CustomName": nbt.TagString(chest_name_json)
    })
    return str('minecraft:chest' + chest_tag.to_mojangson())

def create_mcfunction(chestlist: [str]):
    lengthx = len(chestlist)//10 + 1
    lengthz = 10
    with open("placechests.mcfunction", "w") as fp:
        # prep
        x = 1
        z = 0
        fp.write(f'forceload add ~ ~ ~{lengthx} ~{lengthz}\n')
        fp.write('\n')

        for chest in chestlist:
            fp.write(f'setblock ~{x} ~ ~{z} {chest}\n')
            z += 1
            if z >= 10:
                z = 0
                x += 1

        fp.write('\n')
        fp.write(f'forceload remove ~ ~ ~{lengthx} ~{lengthz}\n')
        fp.close()
    with open("updatechests.mcfunction", "w") as fp:
        # prep
        x = 1
        z = 0
        fp.write(f'forceload add ~ ~ ~{lengthx} ~{lengthz}\n')
        fp.write('\n')

        for chest in chestlist:
            fp.write(f'updatechestitems ~{x} ~ ~{z}\n')
            z += 1
            if z >= 10:
                z = 0
                x += 1

        fp.write('\n')
        fp.write(f'forceload remove ~ ~ ~{lengthx} ~{lengthz}\n')
        fp.close()
    with open("resetchests.mcfunction", "w") as fp:
        fp.write(f'forceload add ~ ~ ~{lengthx} ~{lengthz}\n')
        fp.write(f'fill ~ ~ ~ ~{lengthx} ~ ~{lengthz} air\n')
        fp.write(f'forceload remove ~ ~ ~{lengthx} ~{lengthz}\n')
        fp.close()



def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('--unupdated', action='store_true')
    arg_parser.add_argument('--only_masterworked', action='store_true')
    args = arg_parser.parse_args()

    mgr = LootTableManager()
    mgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")

    containerlist = []
    chestlist = []
    chestcount = 0
    totalitems = 0
    for item_id, sub_map in mgr.item_map.items():
        for item_name, entry in sub_map.items():
            if isinstance(entry, list):
                entry = entry[0]
            if entry["generated"]:
                # Skip generated entries
                continue
            item_nbt = entry["nbt"]
            if args.unupdated and is_up_to_date(item_nbt):
                continue
            if args.only_masterworked and "masterwork" not in entry:
                continue

            item_slot = nbt.TagCompound({
                "Slot": nbt.TagByte(len(containerlist)),
                "Count": nbt.TagByte(1),
                "id": nbt.TagString(item_id),
                "tag": item_nbt
            })
            totalitems += 1
            containerlist.append(item_slot)
            if len(containerlist) == 27:
                chestcount += 1
                chestlist.append(return_chest(chestcount, containerlist))
                containerlist = []
    if len(containerlist) != 27: # don't add extra chest if last chest has 27 exactly
        chestcount += 1
        chestlist.append(return_chest(chestcount, containerlist))
        containerlist = []

    print(f"Generated functions to setblock chests containing {totalitems} total items")

    create_mcfunction(chestlist)



if __name__ == '__main__':
    main()
