#!/usr/bin/env python3

import os
import sys
import json
import re
from collections import OrderedDict

from lib_py3.json_file import jsonFile
from lib_py3.common import eprint
from lib_py3.common import remove_formatting

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

def make_single_loot_table(loot_table_path, entries):
    pool = OrderedDict()
    pool["rolls"] = 1
    pool["entries"] = entries
    table_dict = OrderedDict()
    table_dict["pools"] = [pool]

    loot_table_string = json.dumps(table_dict, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': '))

    # Make directories if they don't exist
    if not os.path.isdir(os.path.dirname(loot_table_path)):
        os.makedirs(os.path.dirname(loot_table_path))

    with open(loot_table_path, "w", encoding="utf-8") as f:
        f.write(loot_table_string)

def make_loot_table(loot_table_base_path, container_nbt_list, loot_table_name=None):
    entries = None
    for container_nbt in container_nbt_list:
        if "Items" not in container_nbt.value:
            raise KeyError("NBT does not contain Items!")

        for item_nbt in container_nbt.value["Items"].value:
            #item_nbt.tree()
            if not entries or not loot_table_name:
                entries = []

            # Fix minecraft annoyingly escaping apostraphes in item name
            item_nbt.at_path("tag.display.Name").value = re.sub(r"\\u0027", "'", item_nbt.at_path("tag.display.Name").value)

            entry_json = OrderedDict()
            entry_json["type"] = "item"
            entry_json["weight"] = 10
            entry_json["name"] = item_nbt.value["id"].value
            entry_json["functions"] = [{
                "function": "set_nbt",
                "tag": item_nbt.value["tag"].to_mojangson()
            }]

            item_name = item_nbt.at_path("tag.display.Name").value
            item_name = remove_formatting(item_name)
            # If the item name is JSON, parse it down to just the name text
            try:
                name_json = json.loads(item_name)
                if "text" in name_json:
                    item_name = name_json["text"]
            except:
                raise ValueError("WARNING: Item '" + item_name + "isn't json!")

            entries.append(entry_json)

            if not loot_table_name:
                filename = item_name.lower()
                filename = re.sub(" +", "_", filename)
                filename = "".join([i if re.match('[a-z0-9-_]', i) else '' for i in filename])
                filename = filename + ".json"
                make_single_loot_table(os.path.join(loot_table_base_path, filename), entries)

    if loot_table_name:
        make_single_loot_table(os.path.join(loot_table_base_path, loot_table_name), entries)

def usage():
    sys.exit("Usage: " + sys.argv[0] + " [-v, --verbose] <text_file_with_setblock_chest.txt> <output_directory> [loot_table_file_name]")

filename = None
outputdir = None
loot_table_name = None
for arg in sys.argv[1:]:
    if (arg == "--verbose"):
        gverbose = True
    elif (arg == "-v"):
        gverbose = True
    elif filename is None:
        filename = arg
    elif outputdir is None:
        outputdir = arg
    elif loot_table_name is None:
        loot_table_name = arg
        if not loot_table_name.endswith(".json"):
            loot_table_name += ".json"
    else:
        usage()

if filename is None or outputdir is None:
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

    make_loot_table(outputdir, container_nbt_list, loot_table_name)
