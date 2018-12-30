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

    ####################################################################################################
    # Utility Functions
    #

    @classmethod
    def to_namespaced_path(cls, path):
        """
        Takes a filename and converts it to a loot table namespaced path (i.e. 'epic:loot/blah')
        """
        split = path.split('/')
        namespace = None
        for i in range(1, len(split)):
            if split[i] == "loot_tables":
                namespace = split[i - 1]
                key = '/'.join(split[i + 1:])
                break

        if not namespace:
            raise ValueError("'loot_tables' not found in path '{}'".format(path))

        if key.lower().endswith('.json'):
            key = key[:-5]
        return namespace + ":" + key

    @classmethod
    def get_item_name_from_nbt(cls, item_nbt):
        """
        Parses a color-removed name out of an item's NBT. Returns a string or None if no name exists
        """
        if "display" not in item_nbt.value or "Name" not in item_nbt.value["display"].value:
            return None

        item_name = item_nbt.value["display"].value["Name"].value
        item_name = remove_formatting(item_name)
        # If the item name is JSON, parse it down to just the name text
        try:
            name_json = json.loads(item_name)
            if "text" in name_json:
                item_name = name_json["text"]
        except:
            eprint("WARNING: Item '" + item_name + "' isn't json!")

        return item_name

    #
    # Utility Functions
    ####################################################################################################

    ####################################################################################################
    # Loot table autoformatting class methods
    #

    @classmethod
    def autoformat_item(cls, item_id, item_nbt):
        """
        Autoformats / reorders / fixes types for a single item's NBT
        """
        item_name = cls.get_item_name_from_nbt(item_nbt)

        # Rename "ench" -> "Enchantments"
        if "ench" in item_nbt.value:
            item_nbt.value["Enchantments"] = item_nbt.value["ench"]
            item_nbt.value.pop("ench")

        if "Enchantments" in item_nbt.value:
            ench_list = item_nbt.value["Enchantments"]
            for enchant in ench_list.value:
                if not "lvl" in enchant.value:
                    raise KeyError("Item '{}' enchantment does not contain 'lvl'".format(item_name))
                if not "id" in enchant.value:
                    raise KeyError("Item '{}' enchantment does not contain 'id'".format(item_name))

                # Make sure the enchantment is namespaced
                if not ":" in enchant.value["id"].value:
                    enchant.value["id"].value = "minecraft:" + enchant.value["id"].value

                # Make sure the tags are in the correct order and of the correct type
                enchant_id = enchant.value["id"].value
                enchant_lvl = enchant.value["lvl"].value
                enchant.value.pop("id")
                enchant.value.pop("lvl")
                enchant.value["lvl"] = nbt.TagShort(enchant_lvl)
                enchant.value["id"] = nbt.TagString(enchant_id)

        return item_nbt

    @classmethod
    def autoformat_file(cls, filename):
        """
        Autoformats a single json file
        """
        json_file = jsonFile(filename)
        loot_table = json_file.dict
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
                    raise KeyError("item loot table entry does not contain 'name'")
                item_id = entry["name"]

                # Add the minecraft: namespace to items that don't have ti
                if not ":" in item_id:
                    entry["name"] = "minecraft:" + item_id
                    item_id = entry["name"]

                # Convert type=item tables that give air to type=empty
                if item_id == "minecraft:air":
                    entry["type"] = "empty"
                    entry.pop("name")
                    continue

                if "functions" not in entry:
                    continue
                if not type(entry["functions"]) is list:
                    raise TypeError('entry["functions"] is type {}, not type list'.format(type(entry["functions"])))
                for function in entry["functions"]:
                    if not type(function) is dict:
                        raise TypeError('function is type {}, not type dict'.format(type(function)))
                    if "function" not in function:
                        continue
                    function_type = function["function"]
                    if function_type == "set_nbt":
                        if "tag" not in function:
                            raise KeyError('set_nbt function is missing nbt field!')
                        item_nbt = nbt.TagCompound.from_mojangson(function["tag"])
                        function["tag"] = cls.autoformat_item(item_id, item_nbt).to_mojangson()

        json_file.save(filename)

    @classmethod
    def autoformat_directory(cls, directory):
        """
        Autoformats all json files in a directory
        """
        for root, dirs, files in os.walk(directory):
            for aFile in files:
                if aFile.endswith(".json"):
                    cls.autoformat_file(os.path.join(root, aFile))

    @classmethod
    def autoformat_loot_tables_subdirectories(cls, directory):
        """
        Autoformats all json files in all subdirectories named "loot_tables"
        """
        for root, dirs, files in os.walk(directory):
            for dirname in dirs:
                if dirname == "loot_tables":
                    cls.autoformat_directory(os.path.join(root, dirname))

    #
    # Loot table autoformatting class methods
    ####################################################################################################

    ####################################################################################################
    # Loot table loading and management
    #

    def __init__(self):
        self.item_map = {}
        self.table_map = {}

    def load_item(self, filename, entry):
        if "name" not in entry:
            raise KeyError("item loot table entry does not contain 'name'")
        item_id = entry["name"]
        if "functions" not in entry:
            return
        if not type(entry["functions"]) is list:
            raise TypeError('entry["functions"] is type {}, not type list'.format(type(entry["functions"])))
        item_name = None
        for function in entry["functions"]:
            if not type(function) is dict:
                raise TypeError('function is type {}, not type dict'.format(type(function)))
            if "function" not in function:
                raise KeyError("functions entry is missing 'function' key")
            function_type = function["function"]
            if function_type == "set_nbt":
                if "tag" not in function:
                    raise KeyError('set_nbt function is missing nbt field!')
                item_tag_json = function["tag"]
                item_tag_nbt = nbt.TagCompound.from_mojangson(item_tag_json)
                item_name = self.get_item_name_from_nbt(item_tag_nbt)

        if item_name is None:
            return

        # Item is named - add it to the map
        new_entry = {}
        new_entry["file"] = filename
        new_entry["nbt"] = item_tag_nbt
        new_entry["namespaced_key"] = self.to_namespaced_path(filename)

        if item_name in self.item_map:
            if item_id in self.item_map[item_name]:
                # DUPLICATE! This name / item id already exists
                if type(self.item_map[item_name][item_id]) is list:
                    # If already a list, add this to that list
                    self.item_map[item_name][item_id].append(new_entry)
                else:
                    # If not a list, make a list
                    self.item_map[item_name][item_id] = [self.item_map[item_name][item_id], new_entry]

            else:
                # Not a duplicate - same name but different ID
                self.item_map[item_name] = {}
                self.item_map[item_name][item_id] = new_entry

        else:
            # Item name does not exist - add it
            self.item_map[item_name] = {}
            self.item_map[item_name][item_id] = new_entry

    def load_table(self, filename, entry):
        if "name" not in entry:
            raise KeyError("table loot table entry does not contain 'name'")

        table_path = entry["name"]

        # Add a reference to the map indicating where this table name is used

        if table_path in self.table_map:
            if "loot_table" in self.table_map[table_path]:
                # This table name already exists somewhere in the loot tables
                if type(self.table_map[table_path]["loot_table"]) is list:
                    # If already a list, add this to that list
                    self.table_map[table_path]["loot_table"].append(filename)
                else:
                    # If not a list, make a list
                    self.table_map[table_path]["loot_table"] = [self.table_map[table_path]["loot_table"], filename]

            else:
                # Not a duplicate - same name but different ID
                self.table_map[table_path] = {}
                self.table_map[table_path]["loot_table"] = filename

        else:
            # Table name does not exist in loot tables - add it
            self.table_map[table_path] = {}
            self.table_map[table_path]["loot_table"] = filename

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
                if entry["type"] == "item":
                    self.load_item(filename, entry)
                if entry["type"] == "loot_table":
                    self.load_table(filename, entry)


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
        Loads all json files in all subdirectories named "loot_tables"
        """
        for root, dirs, files in os.walk(directory):
            for dirname in dirs:
                if dirname == "loot_tables":
                    self.load_directory(os.path.join(root, dirname))

    def update_item_in_loot_table(self, filename, search_item_name, search_item_id, replace_item_nbt):
        """
        Updates an item within a single loot table
        """
        json_file = jsonFile(filename)
        loot_table = json_file.dict

        # Keep track of whether a match was found - don't save the file if not
        found = False

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
                    raise KeyError("item loot table entry does not contain 'name'")
                item_id = entry["name"]
                if "functions" not in entry:
                    continue
                if not type(entry["functions"]) is list:
                    raise TypeError('entry["functions"] is type {}, not type list'.format(type(entry["functions"])))
                item_name = None
                for function in entry["functions"]:
                    if not type(function) is dict:
                        raise TypeError('function is type {}, not type dict'.format(type(function)))
                    if "function" not in function:
                        continue
                    function_type = function["function"]
                    if function_type == "set_nbt":
                        if "tag" not in function:
                            raise KeyError('set_nbt function is missing nbt field!')
                        item_tag_json = function["tag"]
                        item_tag_nbt = nbt.TagCompound.from_mojangson(item_tag_json)
                        item_name = self.get_item_name_from_nbt(item_tag_nbt)

                        if item_name == search_item_name and item_id == search_item_id:
                            # Found a match! Update the tag
                            function["tag"] = replace_item_nbt.to_mojangson()
                            found = True

        if found:
            json_file.save(filename)


    def update_item_in_loot_tables(self, item_id, item_nbt):
        """
        Updates an item within all loaded loot tables
        """
        item_name = self.get_item_name_from_nbt(item_nbt)
        if not item_name:
            raise ValueError("Item NBT does not have a name")

        if not item_name in self.item_map:
            raise ValueError("Item '{}' not in loot tables".format(item_name))

        if not item_id in self.item_map[item_name]:
            raise ValueError("Item '{}' id '{}' not in loot tables".format(item_name, item_id))

        # Get a list of all the occurrences for iterating
        match_list = []
        if type(self.item_map[item_name][item_id]) is list:
            match_list = self.item_map[item_name][item_id]
        else:
            match_list.append(self.item_map[item_name][item_id])

        # Get a list of files where this needs updating
        update_file_list = []
        for match in match_list:
            update_file_list.append(match["file"])

        for filename in update_file_list:
            self.update_item_in_loot_table(filename, item_name, item_id, item_nbt)

    def get_as_replacements(self):
        replacements = []
        for item_name in OrderedDict(sorted(self.item_map.items())):
            for item_id in self.item_map[item_name]:
                if type(self.item_map[item_name][item_id]) is list:
                    # DUPLICATE!

                    # First check if every duplicate is identical
                    different = False
                    for loc in self.item_map[item_name][item_id]:
                        if loc["nbt"].to_bytes() != self.item_map[item_name][item_id][0]["nbt"].to_bytes():
                            # This is really bad - different loot table entries with different contents
                            different = True

                    if not different:
                        eprint("WARNING: Item '{}' type '{}' is duplicated in the loot tables!".format(item_name, item_id))
                    else:
                        eprint("\033[1;31m", end="")
                        eprint("ERROR: Item '{}' type '{}' is different and duplicated in the loot tables!".format(item_name, item_id))

                    count = 1
                    for loc in self.item_map[item_name][item_id]:
                        eprint(" {}: {} - {}".format(count, loc["namespaced_key"], loc["file"]))
                        if different:
                            eprint("    {}".format(loc["nbt"].to_mojangson()))

                        count += 1

                    if different:
                        eprint("\033[0;0m", end="")
                    eprint()

                    # Take the first entry and use that for the replacements
                    entry = self.item_map[item_name][item_id][0]
                else:
                    # Not a duplicate - use the entry
                    entry = self.item_map[item_name][item_id]

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



