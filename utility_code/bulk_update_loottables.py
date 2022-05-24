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

def update_items(container_nbt_list, output_dir=None):
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
            if not item_nbt.has_path("tag.display.Name") and not item_nbt.has_path("tag.title"):
                raise KeyError("Item does not contain tag.display.Name or tag.title!")

            upgrade_entity(item_nbt)

            item_id = item_nbt.at_path("id").value
            item_nbt_str = item_nbt.at_path("tag").to_mojangson()
            if item_nbt.has_path("tag.display.Name"):
                item_name = parse_name_possibly_json(item_nbt.at_path('tag.display.Name').value)
                if item_nbt.has_path('tag.Monumenta.Masterwork') and item_nbt.at_path('tag.Monumenta.Masterwork').value in ['1', '2', '3', '4', '5', '6', '7']:
                    item_name = item_name + '~m' + item_nbt.at_path('tag.Monumenta.Masterwork').value
            else:
                item_name = parse_name_possibly_json(item_nbt.at_path('tag.title').value)

            if "Book of Souls" in item_name:
                raise KeyError("No books of souls!")

            try:
                locations = mgr.update_item_in_loot_tables(item_id, item_nbt_str=item_nbt_str)
                print("Updated '{}' in loot tables: \n{}".format(item_name, "\n".join(locations)))
            except ValueError as e:
                print("WARNING: Failed to update '{}' in loot tables: {}".format(item_name, e))

                filename = item_name.lower()
                filename = re.sub(" +", "_", filename)
                filename = "".join([i if re.match('[a-z0-9-_~]', i) else '' for i in filename])
                filename = filename + ".json"

                entry_json = OrderedDict()
                entry_json["type"] = "item"
                entry_json["weight"] = 10
                entry_json["name"] = item_id
                entry_json["functions"] = []

                func = OrderedDict()
                func["function"] = "set_nbt"
                func["tag"] = item_nbt_str
                entry_json["functions"].append(func)

                pool = OrderedDict()
                pool["rolls"] = 1
                pool["entries"] = [entry_json, ]

                table_dict = OrderedDict()
                table_dict["pools"] = [pool,]

                loot_table_string = json.dumps(table_dict, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

                print(f"Here is a basic loot table for this item:\n\n" +
                      f"Name: {filename}\n" +
                      f"{loot_table_string}\n")
                if output_dir is not None:
                    with open(os.path.join(output_dir, filename), "w") as fp:
                        fp.write(loot_table_string)
                        fp.write("\n")

def usage():
    sys.exit("Usage: " + sys.argv[0] + " [--output-dir dir] <text_file_with_setblock_chest.txt>")

if __name__ == '__main__':
    output_dir = None
    filename = None
    if len(sys.argv) < 2:
        usage()
    args = sys.argv[1:]
    if args[0] == "--output-dir":
        output_dir = args[1]
        args = args[2:]
    for arg in args:
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

        update_items(container_nbt_list, output_dir=output_dir)
