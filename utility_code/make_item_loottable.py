#!/usr/bin/env python3

import os
import sys
import json
import re
from collections import OrderedDict
from pprint import pprint

from lib_py3.json_file import jsonFile
from lib_py3.common import eprint

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt
from quarry.types.text_format import unformat_text

def make_single_loot_table(loot_table_path, pools):
    table_dict = OrderedDict()
    table_dict["pools"] = pools

    loot_table_string = json.dumps(table_dict, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': '))

    # Make directories if they don't exist
    if not os.path.isdir(os.path.dirname(loot_table_path)):
        os.makedirs(os.path.dirname(loot_table_path), mode=0o775)

    with open(loot_table_path, "w", encoding="utf-8") as f:
        f.write(loot_table_string)

def make_loot_table(loot_table_base_path, container_nbt_list, loot_table_name=None, multi_pool=False):
    entries = None
    for container_nbt in container_nbt_list:
        if "Items" not in container_nbt.value:
            raise KeyError("NBT does not contain Items!")

        for item_nbt in container_nbt.at_path("Items").value:
            #item_nbt.tree()
            if not entries or not loot_table_name:
                entries = []

            entry_json = OrderedDict()
            entry_json["type"] = "item"
            entry_json["weight"] = 10
            entry_json["name"] = item_nbt.at_path("id").value
            entry_json["functions"] = []

            # If item has a data tag, include it
            if item_nbt.has_path('tag'):
                func = OrderedDict()
                func["function"] = "set_nbt"
                func["tag"] = item_nbt.at_path("tag").to_mojangson()
                entry_json["functions"].append(func)

            # If count > 1 include it
            if item_nbt.at_path('Count').value > 1:
                func = OrderedDict()
                func["function"] = "set_count"
                func["count"] = item_nbt.at_path("Count").value
                entry_json["functions"].append(func)

            # If functions is empty, don't bother with it
            if len(entry_json["functions"]) == 0:
                entry_json.pop("functions")

            entries.append(entry_json)

            if not loot_table_name:
                # If the item has a display name, grab it
                if not item_nbt.has_path("tag.display.Name"):
                    ValueError("ERROR: Single item loot table specified but item has no display name")

                item_name = item_nbt.at_path("tag.display.Name").value
                # Fix minecraft annoyingly escaping apostraphes in item name
                item_name = re.sub(r"\\u0027", "'", item_name)
                item_name = unformat_text(item_name)
                # If the item name is JSON, parse it down to just the name text
                try:
                    name_json = json.loads(item_name)
                    if "text" in name_json:
                        item_name = name_json["text"]
                except:
                    raise ValueError("WARNING: Item " + repr(item_name) + " isn't json!")
                filename = item_name.lower()
                filename = re.sub(" +", "_", filename)
                filename = "".join([i if re.match('[a-z0-9-_]', i) else '' for i in filename])
                filename = filename + ".json"

                pool = OrderedDict()
                pool["rolls"] = 1
                pool["entries"] = entries
                make_single_loot_table(os.path.join(loot_table_base_path, filename), [pool,])

    if loot_table_name:
        if multi_pool:
            pools = []
            for entry in entries:
                pool = OrderedDict()
                pool["rolls"] = 1
                pool["entries"] = [entry]
                pools.append(pool)
            make_single_loot_table(os.path.join(loot_table_base_path, loot_table_name), pools)

        else:
            pool = OrderedDict()
            pool["rolls"] = 1
            pool["entries"] = entries
            make_single_loot_table(os.path.join(loot_table_base_path, loot_table_name), [pool])

def usage():
    sys.exit("Usage: " + sys.argv[0] + " [-v, --verbose] <text_file_with_setblock_chest.txt> <output_directory> [loot_table_file_name] [--multi-pool]")

filename = None
outputdir = None
loot_table_name = None
multi_pool = False
for arg in sys.argv[1:]:
    if (arg == "--verbose"):
        gverbose = True
    elif (arg == "-v"):
        gverbose = True
    elif (arg == "--multi-pool"):
        multi_pool = True
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

    make_loot_table(outputdir, container_nbt_list, loot_table_name=loot_table_name, multi_pool=multi_pool)
