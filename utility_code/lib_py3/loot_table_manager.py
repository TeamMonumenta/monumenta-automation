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
    def fixup_loot_table(cls, loot_table):
        """
        Autoformats a single json file
        """
        if not type(loot_table) is OrderedDict:
            raise TypeError('loot_table is type {}, not type dict'.format(type(loot_table)))
        if "pools" not in loot_table:
            raise ValueError("loot table does not contain 'pools'")
        if not type(loot_table["pools"]) is list:
            raise TypeError('loot_table["pools"] is type {}, not type list'.format(type(loot_table["pools"])))
        for pool in loot_table["pools"]:
            if not type(pool) is OrderedDict:
                raise TypeError('pool is type {}, not type dict'.format(type(pool)))
            if "entries" not in pool:
                continue
            if not type(pool["entries"]) is list:
                raise TypeError('pool["entries"] is type {}, not type list'.format(type(pool["entries"])))
            for entry in pool["entries"]:
                if not type(entry) is OrderedDict:
                    raise TypeError('entry is type {}, not type dict'.format(type(entry)))
                if "type" not in entry:
                    continue
                if entry["type"] == "item":
                    if "name" not in entry:
                        raise KeyError("item loot table entry does not contain 'name'")
                    item_id = entry["name"]

                    # Add the minecraft: namespace to items that don't have ti
                    if not ":" in item_id:
                        entry["name"] = "minecraft:" + item_id
                        item_id = entry["name"]

                    # Convert type=item tables that give air to type=empty
                    if item_id == "minecraft:air" or item_id == "minecraft:empty":
                        entry["type"] = "empty"
                        entry.pop("name")
                        continue

                    if "functions" not in entry:
                        continue
                    if not type(entry["functions"]) is list:
                        raise TypeError('entry["functions"] is type {}, not type list'.format(type(entry["functions"])))
                    for function in entry["functions"]:
                        if not type(function) is OrderedDict:
                            raise TypeError('function is type {}, not type dict'.format(type(function)))
                        if "function" not in function:
                            continue
                        function_type = function["function"]
                        if function_type == "set_nbt":
                            if "tag" not in function:
                                raise KeyError('set_nbt function is missing nbt field!')
                            item_nbt = nbt.TagCompound.from_mojangson(function["tag"])
                            function["tag"] = cls.autoformat_item(item_id, item_nbt).to_mojangson()

                if entry["type"] == "loot_table":
                    if "name" not in entry:
                        raise KeyError("loot_table loot table entry does not contain 'name'")
                    # Convert type=item tables that give air to type=empty
                    if entry["name"] == "minecraft:empty":
                        entry["type"] = "empty"
                        entry.pop("name")
                        continue

    @classmethod
    def autoformat_json_files_in_directory(cls, directory, indent=4):
        """
        Autoformats all json files in a directory
        """
        for root, dirs, files in os.walk(directory):
            for aFile in files:
                if aFile.endswith(".json"):
                    filename = os.path.join(root, aFile)
                    json_file = jsonFile(filename)
                    if type(json_file.dict) is OrderedDict and "pools" in json_file.dict:
                        # This is probably a loot table - no other json files have "pools" at the top level
                        cls.fixup_loot_table(json_file.dict)

                    json_file.save(filename, indent=indent)

    #
    # Loot table autoformatting class methods
    ####################################################################################################

    def __init__(self):
        self.item_map = {}
        self.table_map = {}

    ####################################################################################################
    # Loot table loading
    #

    def load_loot_tables_item(self, filename, entry):
        if "name" not in entry:
            raise KeyError("item loot table entry does not contain 'name'")
        item_id = entry["name"]
        if "functions" not in entry:
            return
        if not type(entry["functions"]) is list:
            raise TypeError('entry["functions"] is type {}, not type list'.format(type(entry["functions"])))
        item_name = None
        for function in entry["functions"]:
            if not type(function) is OrderedDict:
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

    def add_loot_table_path_reference(self, table_path, location_type, filename):
        """
        Adds a reference to the table_map indicating where a reference to the table is
        """
        if location_type is None:
            # Not a reference, just making a note that this path exists / is valid
            if table_path in self.table_map:
                self.table_map[table_path]["valid"] = True
            else:
                self.table_map[table_path] = {"valid":True}

            return

        if table_path in self.table_map:
            if location_type in self.table_map[table_path]:
                # This table name already exists somewhere in the loot tables
                if type(self.table_map[table_path][location_type]) is list:
                    # If already a list, add this to that list
                    self.table_map[table_path][location_type].append(filename)
                else:
                    # If not a list, make a list
                    self.table_map[table_path][location_type] = [self.table_map[table_path][location_type], filename]

            else:
                # Not a duplicate - same name but different ID
                self.table_map[table_path][location_type] = filename

        else:
            # Table name does not exist in loot tables - add it
            self.table_map[table_path] = {}
            self.table_map[table_path][location_type] = filename


    def load_loot_tables_file(self, filename):
        """
        Loads a single file into the manager
        """
        loot_table = jsonFile(filename).dict
        if not type(loot_table) is OrderedDict:
            raise TypeError('loot_table is type {}, not type dict'.format(type(loot_table)))
        if "pools" not in loot_table:
            raise ValueError("loot table does not contain 'pools'")
        if not type(loot_table["pools"]) is list:
            raise TypeError('loot_table["pools"] is type {}, not type list'.format(type(loot_table["pools"])))

        # Add a reference to the loot table to later test that references to it are valid
        self.add_loot_table_path_reference(self.to_namespaced_path(filename), None, filename)

        for pool in loot_table["pools"]:
            if not type(pool) is OrderedDict:
                raise TypeError('pool is type {}, not type dict'.format(type(pool)))
            if "entries" not in pool:
                continue
            if not type(pool["entries"]) is list:
                raise TypeError('pool["entries"] is type {}, not type list'.format(type(pool["entries"])))
            for entry in pool["entries"]:
                if not type(entry) is OrderedDict:
                    raise TypeError('entry is type {}, not type dict'.format(type(entry)))
                if "type" not in entry:
                    continue
                if entry["type"] == "item":
                    self.load_loot_tables_item(filename, entry)
                if entry["type"] == "loot_table":
                    if "name" not in entry:
                        raise KeyError("table loot table entry does not contain 'name'")

                    self.add_loot_table_path_reference(entry["name"], "loot_table", filename)


    def load_loot_tables_directory(self, directory):
        """
        Loads all json files in a directory into the manager
        """
        for root, dirs, files in os.walk(directory):
            for aFile in files:
                if aFile.endswith(".json"):
                    filename = os.path.join(root, aFile)
                    try:
                        self.load_loot_tables_file(filename)
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
                    self.load_loot_tables_directory(os.path.join(root, dirname))


    def check_for_invalid_loot_table_references(self):
        for item in self.table_map:
            if not "valid" in self.table_map[item]:
                eprint("\033[1;31m", end="")
                if "loot_table" in self.table_map[item]:
                    eprint("ERROR: Reference to nonexistent loot table '{}' in loot table '{}'".format(item, self.table_map[item]["loot_table"]), end="")
                if "scripted_quests" in self.table_map[item]:
                    eprint("ERROR: Reference to nonexistent loot table '{}' in quest file '{}'".format(item, self.table_map[item]["scripted_quests"]), end="")
                if "advancements" in self.table_map[item]:
                    eprint("ERROR: Reference to nonexistent loot table '{}' in advancement file '{}'".format(item, self.table_map[item]["advancements"]), end="")
                if "functions" in self.table_map[item]:
                    eprint("ERROR: Reference to nonexistent loot table '{}' in function file '{}'".format(item, self.table_map[item]["functions"]), end="")
                eprint("\033[0;0m")

    #
    # Loot table loading
    ####################################################################################################

    ####################################################################################################
    # Scripted Quests File Loading
    #

    def load_scripted_quests_recursive(self, filename, element):
        if type(element) is list:
            for el in element:
                self.load_scripted_quests_recursive(filename, el)
        elif type(element) is OrderedDict:
            for el in element:
                if el == "command":
                    if "giveloottable" in element[el]:
                        path = element[el]
                        if path[-1] != '"':
                            raise ValueError('giveloottable command in {} does not end with a "'.format(filename))
                        path = path[:-1]
                        if not path.rfind('"'):
                            raise ValueError('giveloottable command in {} missing first "'.format(filename))
                        path = path[path.rfind('"') + 1:]
                        self.add_loot_table_path_reference(path, "scripted_quests", filename)

                elif el == "give_loot":
                    self.add_loot_table_path_reference(element[el], "scripted_quests", filename)
                else:
                    self.load_scripted_quests_recursive(filename, element[el])
        else:
            # Nothing interesting to do for fundamental type objects
            pass


    def load_scripted_quests_file(self, filename):
        """
        Loads a single scripted quests file into the manager looking for references to loot tables
        """
        scripted_quests_file = jsonFile(filename)

        self.load_scripted_quests_recursive(filename, scripted_quests_file.dict)


    def load_scripted_quests_directory(self, directory):
        """
        Loads all json files in all subdirectories - specifically looking for references to loot tables
        """
        for root, dirs, files in os.walk(directory):
            for aFile in files:
                if aFile.endswith(".json"):
                    filename = os.path.join(root, aFile)
                    try:
                        self.load_scripted_quests_file(filename)
                    except:
                        eprint("Error parsing '" + filename + "'")
                        eprint(str(traceback.format_exc()))

    def update_table_link_in_quest_recursive(self, filename, element, old_namespaced_path, new_namespaced_path):
        """
        Recursively processes quests json replacing loot table path if appropriate
        """
        if type(element) is list:
            for el in element:
                self.update_table_link_in_quest_recursive(filename, el, old_namespaced_path, new_namespaced_path)
        elif type(element) is OrderedDict:
            for el in element:
                if el == "command" or el == "give_loot":
                    element[el] = self.update_table_link_in_command(element[el], old_namespaced_path, new_namespaced_path)
                else:
                    self.update_table_link_in_quest_recursive(filename, element[el], old_namespaced_path, new_namespaced_path)
        else:
            # Nothing interesting to do for fundamental type objects
            pass

    def update_table_link_in_single_quests_file(self, filename, old_namespaced_path, new_namespaced_path):
        """
        Updates a reference to a table within a single quests file
        """
        json_file = jsonFile(filename)

        self.update_table_link_in_quest_recursive(filename, json_file.dict, old_namespaced_path, new_namespaced_path)

        json_file.save(filename, indent=2)

    #
    # Scripted Quests File Loading
    ####################################################################################################

    ####################################################################################################
    # Advancements File Loading
    #

    def load_advancements_file(self, filename):
        """
        Loads a single scripted quests file into the manager looking for references to loot tables
        """
        advancements = jsonFile(filename).dict

        if not type(advancements) is OrderedDict:
            raise TypeError('advancements is type {}, not type dict'.format(type(advancements)))
        if "rewards" not in advancements:
            return
        if not type(advancements["rewards"]) is OrderedDict:
            raise TypeError('advancements["rewards"] is type {}, not a dictionary'.format(type(advancements["rewards"])))

        if "loot" not in advancements["rewards"]:
            return
        if not type(advancements["rewards"]["loot"]) is list:
            raise TypeError('advancements["rewards"]["loot"] is type {}, not list'.format(type(advancements["rewards"]["loot"])))

        for loot_table in advancements["rewards"]["loot"]:
            self.add_loot_table_path_reference(loot_table, "advancements", filename)

    def load_advancements_directory(self, directory):
        """
        Loads all json files in all subdirectories - specifically looking for references to loot tables
        """
        for root, dirs, files in os.walk(directory):
            for aFile in files:
                if aFile.endswith(".json"):
                    filename = os.path.join(root, aFile)
                    try:
                        self.load_advancements_file(filename)
                    except:
                        eprint("Error parsing '" + filename + "'")
                        eprint(str(traceback.format_exc()))

    def load_advancements_subdirectories(self, directory):
        """
        Loads all json files in all subdirectories named "advancements"
        """
        for root, dirs, files in os.walk(directory):
            for dirname in dirs:
                if dirname == "advancements":
                    self.load_advancements_directory(os.path.join(root, dirname))

    def update_table_link_in_single_advancement(self, filename, old_namespaced_path, new_namespaced_path):
        json_file = jsonFile(filename)
        advancements = json_file.dict

        for i in range(advancements["rewards"]["loot"]):
            if advancements["rewards"]["loot"][i] == old_namespaced_path:
                advancements["rewards"]["loot"][i] = new_namespaced_path

        json_file.save(filename)

    #
    # Advancements File Loading
    ####################################################################################################

    ####################################################################################################
    # Functions File Loading
    #

    def load_functions_file(self, filename):
        """
        Loads a single function file into the manager looking for references to loot tables
        """
        with open(filename, 'r') as fp:
            for line in fp.readlines():
                if "giveloottable" in line:
                    line = line.strip()
                    if line[-1] != '"':
                        raise ValueError('giveloottable command in {} does not end with a "'.format(filename))
                    line = line[:-1]
                    if not line.rfind('"'):
                        raise ValueError('giveloottable command in {} missing first "'.format(filename))
                    line = line[line.rfind('"') + 1:]
                    self.add_loot_table_path_reference(line, "functions", filename)

                # TODO: summon
                # TODO: setblock
                # TODO: data merge block
                # TODO: data merge entity

    def load_functions_directory(self, directory):
        """
        Loads all mcfunction files in all subdirectories - specifically looking for references to loot tables
        """
        for root, dirs, files in os.walk(directory):
            for aFile in files:
                if aFile.endswith(".mcfunction"):
                    filename = os.path.join(root, aFile)
                    try:
                        self.load_functions_file(filename)
                    except:
                        eprint("Error parsing '" + filename + "'")
                        eprint(str(traceback.format_exc()))

    def load_functions_subdirectories(self, directory):
        """
        Loads all mcfunction files in all subdirectories named "functions"
        """
        for root, dirs, files in os.walk(directory):
            for dirname in dirs:
                if dirname == "functions":
                    self.load_functions_directory(os.path.join(root, dirname))

    @classmethod
    def update_table_link_in_command(cls, line, old_namespaced_path, new_namespaced_path):
        """
        Replaces a loot table path in a command
        """
        return line.replace(old_namespaced_path, new_namespaced_path)

    @classmethod
    def update_table_link_in_single_function(self, filename, old_namespaced_path, new_namespaced_path):
        output_lines = []
        with open(filename, 'r') as fp:
            for line in fp.readlines():
                line = self.update_table_link_in_command(line, old_namespaced_path, new_namespaced_path)

                # Write this line to the output list
                output_lines.append(line)

        with open(filename, 'w') as fp:
            fp.writelines(output_lines)

    #
    # Functions File Loading
    ####################################################################################################

    ####################################################################################################
    # Loot table manipulation
    #

    def update_item_in_single_loot_table(self, filename, search_item_name, search_item_id, replace_item_nbt):
        """
        Updates an item within a single loot table
        """
        json_file = jsonFile(filename)
        loot_table = json_file.dict

        if not type(loot_table) is OrderedDict:
            raise TypeError('loot_table is type {}, not type dict'.format(type(loot_table)))
        if "pools" not in loot_table:
            raise ValueError("loot table does not contain 'pools'")
        if not type(loot_table["pools"]) is list:
            raise TypeError('loot_table["pools"] is type {}, not type list'.format(type(loot_table["pools"])))
        for pool in loot_table["pools"]:
            if not type(pool) is OrderedDict:
                raise TypeError('pool is type {}, not type dict'.format(type(pool)))
            if "entries" not in pool:
                continue
            if not type(pool["entries"]) is list:
                raise TypeError('pool["entries"] is type {}, not type list'.format(type(pool["entries"])))
            for entry in pool["entries"]:
                if not type(entry) is OrderedDict:
                    raise TypeError('entry is type {}, not type dict'.format(type(entry)))
                if "type" not in entry:
                    continue
                if entry["type"] == "item":
                    if "name" not in entry:
                        raise KeyError("item loot table entry does not contain 'name'")
                    item_id = entry["name"]
                    if "functions" not in entry:
                        continue
                    if not type(entry["functions"]) is list:
                        raise TypeError('entry["functions"] is type {}, not type list'.format(type(entry["functions"])))
                    item_name = None
                    for function in entry["functions"]:
                        if not type(function) is OrderedDict:
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
            self.update_item_in_single_loot_table(filename, item_name, item_id, item_nbt)

    def update_table_link_in_single_loot_table(self, filename, old_namespaced_path, new_namespaced_path):
        """
        Updates a reference to a table within a single loot table
        """
        json_file = jsonFile(filename)
        loot_table = json_file.dict

        if not type(loot_table) is OrderedDict:
            raise TypeError('loot_table is type {}, not type dict'.format(type(loot_table)))
        if "pools" not in loot_table:
            raise ValueError("loot table does not contain 'pools'")
        if not type(loot_table["pools"]) is list:
            raise TypeError('loot_table["pools"] is type {}, not type list'.format(type(loot_table["pools"])))
        for pool in loot_table["pools"]:
            if not type(pool) is OrderedDict:
                raise TypeError('pool is type {}, not type dict'.format(type(pool)))
            if "entries" not in pool:
                continue
            if not type(pool["entries"]) is list:
                raise TypeError('pool["entries"] is type {}, not type list'.format(type(pool["entries"])))
            for entry in pool["entries"]:
                if not type(entry) is OrderedDict:
                    raise TypeError('entry is type {}, not type dict'.format(type(entry)))
                if "type" not in entry:
                    continue
                if entry["type"] == "loot_table":
                    if "name" not in entry:
                        raise KeyError("table loot table entry does not contain 'name'")
                    if entry["name"] == old_namespaced_path:
                        entry["name"] = new_namespaced_path

        json_file.save(filename)

    def update_table_link_in_all_of_type(self, old_namespaced_path, new_namespaced_path, label, update_function):
        """
        Updates all references to a table of the given label using the provided update_function
        """

        if not label in self.table_map[old_namespaced_path]:
            # Not referenced in the loot tables
            return

        # Get a list of files where this needs updating
        update_file_list = []
        if type(self.table_map[old_namespaced_path][label]) is list:
            update_file_list = self.table_map[old_namespaced_path][label]
        else:
            update_file_list.append(self.table_map[old_namespaced_path][label])

        for filename in update_file_list:
            update_function(filename, old_namespaced_path, new_namespaced_path)

    def update_table_link_everywhere(self, old_path, new_path):
        """
        Updates all references to a table everywhere loaded into this class
        """

        old_namespaced_path = self.to_namespaced_path(old_path)
        new_namespaced_path = self.to_namespaced_path(new_path)

        if not old_namespaced_path in self.table_map:
            # Not referenced anywhere
            return

        self.update_table_link_in_all_of_type(old_namespaced_path, new_namespaced_path, "loot_table", self.update_table_link_in_single_loot_table)
        self.update_table_link_in_all_of_type(old_namespaced_path, new_namespaced_path, "advancements", self.update_table_link_in_single_advancement)
        self.update_table_link_in_all_of_type(old_namespaced_path, new_namespaced_path, "functions", self.update_table_link_in_single_function)
        self.update_table_link_in_all_of_type(old_namespaced_path, new_namespaced_path, "scripted_quests", self.update_table_link_in_single_quests_file)

    #
    # Loot table manipulation
    ####################################################################################################

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



