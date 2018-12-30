#!/usr/bin/env python3

import os
import sys
import traceback
import json
from collections import OrderedDict

from lib_py3.json_file import jsonFile
from lib_py3.common import eprint
from lib_py3.common import remove_formatting

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

class LootTableManager(object):
    """
    A tool to manipulate loot tables
    """

    def __init__(self):
        self.map = {}

    def load_file(self, filename):
        """
        Loads a single file into the manager
        """
        loot_table = jsonFile(filename).dict
        if not type(loot_table) is dict:
            raise TypeError('loot_table is type {}, not type dict'.format(type(loot_table)))
        if "pools" not in loot_table:
            raise ValueError("loot table does not contain 'pools'")
        if not type(loot_table["pools"]) is list:
            raise TypeError('loot_table["pools"] is type {}, not type list'.format(type(loot_table["pools"])))
        for pool in loot_table["pools"]:
            if not type(pool) is dict:
                raise TypeError('pool is type {}, not type dict'.format(type(pool)))
            if "entries" not in pool:
                continue
            if not type(pool["entries"]) is list:
                raise TypeError('pool["entries"] is type {}, not type list'.format(type(pool["entries"])))
            for entry in pool["entries"]:
                if not type(entry) is dict:
                    raise TypeError('entry is type {}, not type dict'.format(type(entry)))
                if "type" not in entry:
                    continue
                if entry["type"] != "item":
                    continue
                if "name" not in entry:
                    continue
                item_id = entry["name"]
                if "functions" not in entry:
                    continue
                if not type(entry["functions"]) is list:
                    raise TypeError('entry["functions"] is type {}, not type list'.format(type(entry["functions"])))
                item_tag_json = None
                item_name = None
                for function in entry["functions"]:
                    if not type(function) is dict:
                        raise TypeError('function is type {}, not type dict'.format(type(function)))
                    if "function" not in function:
                        continue
                    function_type = function["function"]
                    if function_type == "set_nbt":
                        if "tag" not in function:
                            continue
                        item_tag_json = function["tag"]
                        item_tag_nbt = nbt.TagCompound.from_mojangson(item_tag_json)
                        #item_tag_nbt.tree()
                        if (
                            "display" not in item_tag_nbt.value or
                            "Name" not in item_tag_nbt.value["display"].value
                        ):
                            continue
                        item_name = item_tag_nbt.value["display"].value["Name"].value
                        item_name = remove_formatting(item_name)
                        # If the item name is JSON, parse it down to just the name text
                        try:
                            name_json = json.loads(item_name)
                            if "text" in name_json:
                                item_name = name_json["text"]
                        except:
                            eprint("WARNING: Item '" + item_name + "' isn't json!")


                if item_tag_json is None:
                    continue
                if item_name is None:
                    continue

                # Item is named - add it to the map
                new_entry = {}
                new_entry["file"] = filename
                new_entry["nbt"] = item_tag_nbt
                if item_name in self.map:
                    if item_id in self.map[item_name]:
                        # DUPLICATE! This name / item id already exists
                        if type(self.map[item_name][item_id]) is list:
                            # If already a list, add this to that list
                            self.map[item_name][item_id].append(new_entry)
                        else:
                            # If not a list, make a list
                            self.map[item_name][item_id] = [self.map[item_name][item_id], new_entry]

                    else:
                        # Not a duplicate - same name but different ID
                        self.map[item_name] = {}
                        self.map[item_name][item_id] = new_entry

                else:
                    # Item name does not exist - add it
                    self.map[item_name] = {}
                    self.map[item_name][item_id] = new_entry


    def load_directory(self, directory):
        """
        Loads all json files in a directory into the manager
        """
        for root, dirs, files in os.walk(directory):
            for aFile in files:
                if aFile.endswith(".json"):
                    filename = os.path.join(root, aFile)
                    try:
                        self.load_file(filename)
                    except:
                        eprint("Error parsing '" + filename + "'")
                        eprint(str(traceback.format_exc()))

    def load_loot_tables_subdirectories(self, directory):
        """
        Loads all json files in a directory into the manager
        """
        for root, dirs, files in os.walk(directory):
            for dirname in dirs:
                if dirname == "loot_tables":
                    self.load_directory(os.path.join(root, dirname))

    def get_as_replacements(self):
        replacements = []
        for item_name in OrderedDict(sorted(self.map.items())):
            for item_id in self.map[item_name]:
                if type(self.map[item_name][item_id]) is list:
                    # DUPLICATE!
                    eprint("WARNING: Item '{}' type '{}' is duplicated in the loot tables!".format(item_name, item_id))
                    count = 1;
                    for loc in self.map[item_name][item_id]:
                        eprint(" {}: {}".format(count, loc["file"]))
                        count += 1
                    # Take the first entry and use that for the replacements
                    entry = self.map[item_name][item_id][0]
                else:
                    # Not a duplicate - use the entry
                    entry = self.map[item_name][item_id]

                replacements.append([
                    {
                        'id': item_id,
                        'name': item_name,
                    },
                    [
                        'nbt',
                        'replace',
                        entry['nbt'].to_mojangson(),
                    ]
                ])

        return replacements



