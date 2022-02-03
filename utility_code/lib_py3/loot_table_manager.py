"""A library for managing loot tables and their items."""
import os
import sys
import traceback
import re

from lib_py3.json_file import jsonFile
from lib_py3.common import eprint
from lib_py3.common import get_item_name_from_nbt
from lib_py3.upgrade import upgrade_entity

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt


class LootTableManager():
    """A tool to manipulate loot tables."""
    INTERCHANGEABLE_ITEM_IDS = (
        ( # Shulker boxes
            "minecraft:shulker_box",
            "minecraft:white_shulker_box",
            "minecraft:orange_shulker_box",
            "minecraft:magenta_shulker_box",
            "minecraft:light_blue_shulker_box",
            "minecraft:yellow_shulker_box",
            "minecraft:lime_shulker_box",
            "minecraft:pink_shulker_box",
            "minecraft:gray_shulker_box",
            "minecraft:light_gray_shulker_box",
            "minecraft:cyan_shulker_box",
            "minecraft:purple_shulker_box",
            "minecraft:blue_shulker_box",
            "minecraft:brown_shulker_box",
            "minecraft:green_shulker_box",
            "minecraft:red_shulker_box",
            "minecraft:black_shulker_box",
        ),
    )

    ####################################################################################################
    # Utility Functions
    #


    @staticmethod
    def _to_namespaced_path(path):
        """Takes a filename and converts it to a loot table namespaced path (i.e. 'epic:loot/blah')."""
        split = path.split('/')
        namespace = None
        for i in range(1, len(split)):
            if split[i] == "loot_tables":
                namespace = split[i - 1]
                key = '/'.join(split[i + 1:])
                break

        if not namespace:
            raise ValueError(f'"loot_tables" not found in path {path!r}')

        if key.lower().endswith('.json'):
            key = key[:-5]
        return namespace + ":" + key

    #
    # Utility Functions
    ####################################################################################################

    ####################################################################################################
    # Loot table autoformatting methods
    #


    def fixup_loot_table(self, filename, loot_table):
        """Autoformats a single json file."""
        if not isinstance(loot_table, dict):
            raise TypeError(f'loot_table is type {type(loot_table)}, not instance of dict')
        if "pools" not in loot_table:
            return
        if not isinstance(loot_table["pools"], list):
            raise TypeError(f'loot_table["pools"] is type {type(loot_table["pools"])}, not instance of list')
        for pool in loot_table["pools"]:
            if not isinstance(pool, dict):
                raise TypeError(f'pool is type {type(pool)}, not instance of dict')
            if "entries" not in pool:
                continue
            if not isinstance(pool["entries"], list):
                raise TypeError(f'pool["entries"] is type {type(pool["entries"])}, not instance of list')
            for entry in pool["entries"]:
                if not isinstance(entry, dict):
                    raise TypeError(f'entry is type {type(entry)}, not instance of dict')
                if "type" not in entry:
                    continue
                if entry["type"] == "item":
                    if "name" not in entry:
                        raise KeyError("item loot table entry does not contain 'name'")
                    item_id = entry["name"]

                    # Add the minecraft: namespace to items that don't have it
                    if not ":" in item_id:
                        entry["name"] = "minecraft:" + item_id
                        item_id = entry["name"]

                    # Convert type=item tables that give air to type=empty
                    if item_id in ("minecraft:air", "minecraft:empty"):
                        entry["type"] = "empty"
                        entry.pop("name")
                        continue

                    if "functions" not in entry:
                        continue
                    if not isinstance(entry["functions"], list):
                        raise TypeError(f'entry["functions"] is type {type(entry["functions"])}, not instance of list')
                    for function in entry["functions"]:
                        if not isinstance(function, dict):
                            raise TypeError(f'function is type {type(function)}, not instance of dict')
                        if "function" not in function:
                            continue
                        function_type = function["function"]
                        if function_type == "set_nbt":
                            if "tag" not in function:
                                raise KeyError('set_nbt function is missing nbt field!')
                            item_nbt = nbt.TagCompound.from_mojangson(function["tag"])
                            upgrade_entity(item_nbt, regenerateUUIDs=False, tagsToRemove=[])
                            function["tag"] = item_nbt.to_mojangson()

                            ################################################################################
                            # Update item entry to use index instead

                            if not "epic/loot_tables/index" in filename and item_nbt.has_path('display.Name'):
                                item_name = get_item_name_from_nbt(item_nbt)

                                item_index_entry = self.item_map.get(item_id, {}).get(item_name, None)
                                if item_index_entry is not None and "epic:index" in item_index_entry["namespaced_key"]:
                                    print(f'Updating item in loot table to point to index: {item_id} - {item_name} - {filename}')

                                    entry["type"] = "loot_table"
                                    entry["name"] = item_index_entry["namespaced_key"]
                                    entry.pop("functions")
                                    break

                            # Update item entry to use index instead
                            ################################################################################

                if entry["type"] == "loot_table":
                    if "name" not in entry:
                        raise KeyError("loot_table loot table entry does not contain 'name'")
                    # Convert type=item tables that give air to type=empty
                    if entry["name"] == "minecraft:empty":
                        entry["type"] = "empty"
                        entry.pop("name")
                        continue


    def autoformat_json_files_in_directory(self, directory, indent=2):
        """Autoformats all json files in a directory."""
        for root, _, files in os.walk(directory):
            for file_ in files:
                if file_.endswith(".json"):
                    filename = os.path.join(root, file_)

                    # Don't update the items index files, they are auto generated
                    if "epic/loot_tables/index" in filename:
                        continue
                    # Don't update the LoS database
                    if "LibraryOfSouls/souls_database" in filename:
                        continue

                    try:
                        json_file = jsonFile(filename)
                        if isinstance(json_file.dict, dict) and "pools" in json_file.dict:
                            # This is probably a loot table - no other json files have "pools" at the top level
                            self.fixup_loot_table(filename, json_file.dict)

                        json_file.save(filename, indent=indent)
                    except Exception as exception:
                        print(f'Failed to autoformat {filename!r} : {exception}')

    #
    # Loot table autoformatting methods
    ####################################################################################################


    def __init__(self):
        self.item_map = {}
        self.table_map = {}
        self.skin_map = {}
        self._world = None

    ####################################################################################################
    # Loot table loading
    #


    def load_loot_tables_item(self, filename, entry):
        """Loads a single item from a loot table entry."""
        if "name" not in entry:
            raise KeyError("item loot table entry does not contain 'name'")
        item_id = entry["name"]
        if "functions" not in entry:
            return
        if not isinstance(entry["functions"], list):
            raise TypeError(f'entry["functions"] is type {type(entry["functions"])}, not instance of list')
        item_name = None
        for function in entry["functions"]:
            if not isinstance(function, dict):
                raise TypeError(f'function is type {type(function)}, not instance of dict')
            if "function" not in function:
                raise KeyError("functions entry is missing 'function' key")
            function_type = function["function"]
            if function_type == "set_nbt":
                if "tag" not in function:
                    raise KeyError('set_nbt function is missing nbt field!')
                item_tag_json = function["tag"]
                item_tag_nbt = nbt.TagCompound.from_mojangson(item_tag_json)
                item_name = get_item_name_from_nbt(item_tag_nbt)

        if item_name is None:
            return

        # Item is named - add it to the map
        new_entry = {}
        new_entry["file"] = filename
        new_entry["nbt"] = item_tag_nbt
        new_entry["namespaced_key"] = self._to_namespaced_path(filename)

        found_in_interchangeable_set = False
        for interchangeable_id_set in self.INTERCHANGEABLE_ITEM_IDS:
            if item_id in interchangeable_id_set:
                found_in_interchangeable_set = True
                for interchangeable_id in interchangeable_id_set:
                    self._register_loot_table_item(interchangeable_id, item_name, new_entry, generated=True)
        if not found_in_interchangeable_set:
            self._register_loot_table_item(item_id, item_name, new_entry)

    def _register_loot_table_item(self, item_id, item_name, new_entry, generated=False, skin_of=None):
        """Registers an item to the item_map

        new_entry = {"file": filename, "nbt": item_tag_nbt, "namespaced_key": namespaced_path}
        generated = True if automatically generated from another item, else False (shulker box colors, etc)
        skin_of = the item_name of the parent item with the same ID, or None if not a skin
        """
        namespaced_path = new_entry["namespaced_key"]
        self._add_loot_table_reference(namespaced_path, "forward_reference_item", {"item_id": item_id, "item_name": item_name})

        new_entry = dict(new_entry)
        new_entry["generated"] = generated
        if skin_of is not None:
            new_entry["skin_of"] = skin_of
        if item_id in self.item_map:
            if item_name in self.item_map[item_id]:
                # DUPLICATE! This name / item id already exists
                if generated:
                    # Generated items take lower priority than existing items
                    pass
                elif isinstance(self.item_map[item_id][item_name], list):
                    # If already a list, add this to that list
                    self.item_map[item_id][item_name].append(new_entry)
                elif self.item_map[item_id][item_name]["generated"]:
                    # Old entry was generated, override
                    self.item_map[item_id][item_name] = new_entry
                else:
                    # If not a list, make a list
                    self.item_map[item_id][item_name] = [self.item_map[item_id][item_name], new_entry]

            else:
                # Not a duplicate - same name but different ID
                self.item_map[item_id][item_name] = new_entry

        else:
            # Item name does not exist - add it
            self.item_map[item_id] = {}
            self.item_map[item_id][item_name] = new_entry


    def _add_loot_table_reference(self, table_path, location_type, ref_obj):
        """Adds a reference to the table_map indicating where a reference to the table is."""
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
                if isinstance(self.table_map[table_path][location_type], list):
                    # If already a list, add this to that list
                    self.table_map[table_path][location_type].append(ref_obj)
                else:
                    # If not a list, make a list
                    self.table_map[table_path][location_type] = [self.table_map[table_path][location_type], ref_obj]

            else:
                # Not a duplicate - same name but different ID
                self.table_map[table_path][location_type] = ref_obj

        else:
            # Table name does not exist in loot tables - add it
            self.table_map[table_path] = {}
            self.table_map[table_path][location_type] = ref_obj


    @staticmethod
    def _invalidate_skin_entry(skin_entry):
        """Marks a skin entry as invalid, freeing up unneeded data in the process"""
        skin_entry.clear()
        skin_entry["valid"] = False


    @staticmethod
    def _mark_skin_entry_valid(skin_entry):
        """Marks a skin entry as valid, freeing up unneeded data in the process"""
        skin_entry["valid"] = True
        del skin_entry["functions"]


    def _handle_skin_entry_from_loot_table(self, original_target_namespaced_path, skin_path, skin_entry, forward_target_namespaced_path):
        """"Validates and loads a single skin from another skin if possible."""
        # TODO HERE Just speeding things along for development
        raise NotImplementedError("Skins of skins are not supported for now.")


    def _handle_skin_entry_from_item(self, target_namespaced_path, skin_path, skin_entry, item_id, source_item_name):
        """"Validates and loads a single skin from an item if possible."""
        base_item = self.item_map.get(item_id, {}).get(source_item_name, None)
        if base_item is None:
            raise TypeError(f'base_item not found')
        elif isinstance(base_item, list):
            # Most likely just a loot table giving more than one item
            self._invalidate_skin_entry(skin_entry)
            return

        # Make sure the original copy isn't modified
        item_new_name = source_item_name
        new_entry = {
            "file": skin_path,
            "nbt": base_item["nbt"].deep_copy(),
            "namespaced_key": self._to_namespaced_path(skin_path),
        }

        functions = skin_entry["functions"]
        if not isinstance(functions, list):
            raise TypeError(f'functions is type {type(functions)}, not instance of list')
        for function in functions:
            if not isinstance(function, dict):
                raise TypeError(f'function is type {type(function)}, not instance of dict')
            if "function" not in function:
                raise KeyError("functions entry is missing 'function' key")
            function_type = function["function"]
            if function_type == "set_nbt":
                if "tag" not in function:
                    raise KeyError('set_nbt function is missing nbt field!')
                item_tag_patch_json = function["tag"]
                item_tag_patch_nbt = nbt.TagCompound.from_mojangson(item_tag_patch_json)
                item_new_name = get_item_name_from_nbt(item_tag_patch_nbt)
                new_entry["nbt"].update(item_tag_patch_nbt)

        if source_item_name == item_new_name:
            # Most likely just a loot table giving more than one item
            self._invalidate_skin_entry(skin_entry)
            return

        self._register_loot_table_item(item_id, item_new_name, new_entry, skin_of=source_item_name)
        self._mark_skin_entry_valid(skin_entry)


    def _handle_skin_entry(self, target_namespaced_path, skin_path, skin_entry):
        """"Validates and loads a single skin if possible."""
        target = self.table_map.get(target_namespaced_path, None)
        if target is None or not target.get("valid", None):
            raise KeyError(f'forward_loot_table {target_namespaced_path!r} not found')

        if "forward_reference_loot_table" not in target and "forward_reference_item" not in target:
            raise KeyError('target has neither "forward_reference_loot_table" nor "forward_reference_item" key')
        if "forward_reference_loot_table" in target and "forward_reference_item" in target:
            self._invalidate_skin_entry(skin_entry)
            return
        if "forward_reference_loot_table" in target:
            forward_loot_table = target["forward_reference_loot_table"]
            if isinstance(forward_loot_table, str):
                self._handle_skin_entry_from_loot_table(target_namespaced_path,
                                                        skin_path,
                                                        skin_entry,
                                                        forward_loot_table)
                return
            else:
                self._invalidate_skin_entry(skin_entry)
                return

        # Forward reference item
        forward_item_id_and_name = target["forward_reference_item"]
        if isinstance(forward_item_id_and_name, dict):
            keys = set(forward_item_id_and_name.keys())
            if keys != {"item_id", "item_name"}:
                raise KeyError('forward_item_id_and_name keys must be exactly {"item_id", "item_name"}, not ' + repr(keys))
            self._handle_skin_entry_from_item(target_namespaced_path,
                                              skin_path,
                                              skin_entry,
                                              forward_item_id_and_name["item_id"],
                                              forward_item_id_and_name["item_name"])
        else:
            self._invalidate_skin_entry(skin_entry)
            return


    def handle_skin_map(self):
        """Validate and load skins that were added to the work queue"""
        while True:
            loaded_last_pass = 0

            for target_namespaced_path, sub_map in dict(self.skin_map).items():
                for skin_path, skin_entry in dict(sub_map).items():
                    if skin_entry["valid"] is not None:
                        continue
                    try:
                        self._handle_skin_entry(target_namespaced_path, skin_path, skin_entry)
                    except Exception:
                        self._invalidate_skin_entry(skin_entry)
                        eprint(f'Error parsing {skin_path!r}')
                        eprint(str(traceback.format_exc()))
                    if skin_entry["valid"]:
                        loaded_last_pass += 1

            if loaded_last_pass == 0:
                break


    def load_loot_tables_file(self, filename):
        """Loads a single file into the manager."""
        loot_table = jsonFile(filename).dict
        if not isinstance(loot_table, dict):
            raise TypeError(f'loot_table is type {type(loot_table)}, not instance of dict')
        if len(loot_table) == 0:
            # Nothing to do
            return
        if "pools" not in loot_table:
            return
        if not isinstance(loot_table["pools"], list):
            raise TypeError(f'loot_table["pools"] is type {type(loot_table["pools"])}, not instance of list')

        # Add a reference to the loot table to later test that references to it are valid
        namespaced_path = self._to_namespaced_path(filename)
        self._add_loot_table_reference(namespaced_path, None, filename)

        for pool in loot_table["pools"]:
            if not isinstance(pool, dict):
                raise TypeError(f'pool is type {type(pool)}, not instance of dict')
            if "entries" not in pool:
                continue
            if not isinstance(pool["entries"], list):
                raise TypeError(f'pool["entries"] is type {type(pool["entries"])}, not instance of list')
            for entry in pool["entries"]:
                if not isinstance(entry, dict):
                    raise TypeError(f'entry is type {type(entry)}, not instance of dict')
                if "type" not in entry:
                    continue
                if entry["type"] == "item":
                    self.load_loot_tables_item(filename, entry)
                if entry["type"] == "loot_table":
                    if "name" not in entry:
                        raise KeyError("table loot table entry does not contain 'name'")
                    target = entry["name"]

                    self._add_loot_table_reference(target, "loot_table", filename)
                    self._add_loot_table_reference(namespaced_path, "forward_reference_loot_table", target)

                    if "functions" in entry:
                        skin_entry = {"valid": None, "functions": entry["functions"]}

                        if target not in self.skin_map:
                            self.skin_map[target] = {}

                        if filename not in self.skin_map[target]:
                            self.skin_map[target][filename] = skin_entry
                        else:
                            # If there's more than one loot table with a function modifying it, it's probably not skins
                            self._invalidate_skin_entry(self.skin_map[target][filename])


    def load_loot_tables_directory(self, directory):
        """Loads all json files in a directory into the manager."""
        for root, _, files in os.walk(directory):
            for file_ in files:
                if file_.endswith(".json"):
                    filename = os.path.join(root, file_)
                    try:
                        self.load_loot_tables_file(filename)
                    except Exception:
                        eprint("Error parsing " + repr(filename))
                        eprint(str(traceback.format_exc()))


    def load_loot_tables_subdirectories(self, directory):
        """Loads all json files in all subdirectories named "loot_tables"."""
        for root, dirs, _ in os.walk(directory):
            for dirname in dirs:
                if dirname == "loot_tables":
                    self.load_loot_tables_directory(os.path.join(root, dirname))


    def get_invalid_loot_table_references(self):
        """Returns a map of loot tables that are referenced, but do not exist."""
        invalid_references = {}
        for item in self.table_map:
            if not "valid" in self.table_map[item] and item != "minecraft:empty":
                is_valid = True
                for key in self.table_map[item]:
                    if key == "valid":
                        continue

                    if is_valid:
                        is_valid = False
                        invalid_references[item] = {}

                    invalid_references[item][key] = self.table_map[item][key]

        return invalid_references

    #
    # Loot table loading
    ####################################################################################################

    ####################################################################################################
    # Scripted Quests File Loading
    #


    def load_scripted_quests_recursive(self, filename, element):
        """Loads a scripted quests file, including child actions such as in clickable dialog."""
        if isinstance(element, list):
            for child_element in element:
                self.load_scripted_quests_recursive(filename, child_element)
        elif isinstance(element, dict):
            for action_key in element:
                if action_key == "command":
                    self.load_command(element[action_key], "scripted_quests", filename)
                elif action_key == "give_loot":
                    self._add_loot_table_reference(element[action_key], "scripted_quests", filename)
                else:
                    self.load_scripted_quests_recursive(filename, element[action_key])
        else:
            # Nothing interesting to do for fundamental type objects
            pass


    def load_scripted_quests_file(self, filename):
        """Loads a single scripted quests file into the manager looking for references to loot tables."""
        scripted_quests_file = jsonFile(filename)

        self.load_scripted_quests_recursive(filename, scripted_quests_file.dict)


    def load_scripted_quests_directory(self, directory):
        """Loads all json files in all subdirectories - specifically looking for references to loot tables."""
        for root, _, files in os.walk(directory):
            for file_ in files:
                if file_.endswith(".json"):
                    filename = os.path.join(root, file_)
                    try:
                        self.load_scripted_quests_file(filename)
                    except Exception:
                        eprint("Error parsing " + repr(filename))
                        eprint(str(traceback.format_exc()))


    def update_table_link_in_quest_recursive(self, filename, element, old_namespaced_path, new_namespaced_path):
        """Recursively processes quests json replacing loot table path if appropriate."""
        if isinstance(element, list):
            for child_element in element:
                self.update_table_link_in_quest_recursive(filename, child_element, old_namespaced_path, new_namespaced_path)
        elif isinstance(element, dict):
            for action_key in element:
                if action_key == "command":
                    element[action_key] = self.update_table_link_in_command(filename,
                                                                            element[action_key],
                                                                            old_namespaced_path,
                                                                            new_namespaced_path)
                elif action_key == "give_loot":
                    if element[action_key] == old_namespaced_path:
                        element[action_key] = new_namespaced_path
                else:
                    self.update_table_link_in_quest_recursive(filename, element[action_key], old_namespaced_path, new_namespaced_path)

        # Nothing interesting to do for fundamental type objects


    def update_table_link_in_single_quests_file(self, filename, old_namespaced_path, new_namespaced_path):
        """Updates a reference to a table within a single quests file."""
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
        """Loads a single scripted quests file into the manager looking for references to loot tables."""
        advancements = jsonFile(filename).dict

        if not isinstance(advancements, dict):
            raise TypeError(f'advancements is type {type(advancements)}, not instance of dict')
        if "rewards" not in advancements:
            return
        if not isinstance(advancements["rewards"], dict):
            raise TypeError(f'advancements["rewards"] is type {type(advancements["rewards"])}, not instance of dict')

        if "loot" not in advancements["rewards"]:
            return
        if not isinstance(advancements["rewards"]["loot"], list):
            raise TypeError(f'advancements["rewards"]["loot"] is type {type(advancements["rewards"]["loot"])}, not instance of list')

        for loot_table in advancements["rewards"]["loot"]:
            self._add_loot_table_reference(loot_table, "advancements", filename)


    def load_advancements_directory(self, directory):
        """Loads all json files in all subdirectories - specifically looking for references to loot tables."""
        for root, _, files in os.walk(directory):
            for file_ in files:
                if file_.endswith(".json"):
                    filename = os.path.join(root, file_)
                    try:
                        self.load_advancements_file(filename)
                    except Exception:
                        eprint("Error parsing " + repr(filename))
                        eprint(str(traceback.format_exc()))


    def load_advancements_subdirectories(self, directory):
        """Loads all json files in all subdirectories named "advancements"."""
        for root, dirs, _ in os.walk(directory):
            for dirname in dirs:
                if dirname == "advancements":
                    self.load_advancements_directory(os.path.join(root, dirname))


    @staticmethod
    def update_table_link_in_single_advancement(filename, old_namespaced_path, new_namespaced_path):
        """Refactors a loot table path in an advancement."""
        json_file = jsonFile(filename)
        advancements = json_file.dict

        for i in range(len(advancements["rewards"]["loot"])):
            if advancements["rewards"]["loot"][i] == old_namespaced_path:
                advancements["rewards"]["loot"][i] = new_namespaced_path

        json_file.save(filename)

    #
    # Advancements File Loading
    ####################################################################################################

    ####################################################################################################
    # Functions File Loading
    #


    def load_command(self, command, source_label, ref_obj):
        """Load a command into the loot table manager."""
        if "giveloottable" in command:
            #pat = re.compile(r'giveloottable (.*) "([^"]+)" *[0-9]*')
            match = re.match(r'.*giveloottable.*"(.*)" *[0-9]*', command)
            if not match:
                raise ValueError(f"Can't identify loot table in command: {command}")
            self._add_loot_table_reference(match.group(1), source_label, ref_obj)

        # This handles both mob DeathLootTable and chest/container LootTable
        line = command
        matchstr = 'LootTable:"'
        while matchstr in line:
            idx = line.find(matchstr)
            line = line[idx + len(matchstr):]
            idx = line.find('"')
            self._add_loot_table_reference(line[:idx], source_label, ref_obj)
            line = line[idx:]


    def load_functions_directory(self, directory):
        """Loads all mcfunction files in all subdirectories - specifically looking for references to loot tables."""
        for root, _, files in os.walk(directory):
            for file_ in files:
                if file_.endswith(".mcfunction"):
                    filename = os.path.join(root, file_)
                    try:
                        with open(filename, 'r') as fp:
                            for line in fp.readlines():
                                self.load_command(line, "functions", filename)
                    except Exception:
                        eprint("Error parsing " + repr(filename))
                        eprint(str(traceback.format_exc()))


    def load_functions_subdirectories(self, directory):
        """Loads all mcfunction files in all subdirectories named "functions"."""
        for root, dirs, _ in os.walk(directory):
            for dirname in dirs:
                if dirname == "functions":
                    self.load_functions_directory(os.path.join(root, dirname))


    @classmethod
    def update_table_link_in_command(cls, ref_obj, command, old_namespaced_path, new_namespaced_path):
        """Replaces a loot table path in a command."""
        if "giveloottable" in command:
            orig_command = command
            command = command.strip()
            if command[-1] != '"':
                raise ValueError(f'giveloottable command in {ref_obj} does not end with a "')
            command = command[:-1]
            if not command.rfind('"'):
                raise ValueError(f'giveloottable command in {ref_obj} missing first "')

            if command[command.rfind('"') + 1:] == old_namespaced_path:
                return command[:command.rfind('"')] + '"' + new_namespaced_path + '"'
            return orig_command

        # This handles both mob DeathLootTable and chest/container LootTable
        return command.replace('LootTable:"' + old_namespaced_path + '"', 'LootTable:"' + new_namespaced_path + '"')


    @classmethod
    def update_table_link_in_single_function(cls, filename, old_namespaced_path, new_namespaced_path):
        """Refactors a loot table path in a function."""
        output_lines = []
        with open(filename, 'r') as fp:
            for line in fp.readlines():
                line = cls.update_table_link_in_command(filename, line, old_namespaced_path, new_namespaced_path)
                if line[-1] != '\n':
                    line += '\n'

                # Write this line to the output list
                output_lines.append(line)

        with open(filename, 'w') as fp:
            fp.writelines(output_lines)

    #
    # Functions File Loading
    ####################################################################################################

    ####################################################################################################
    # World Loading
    #


    def load_entity(self, entity):
        """Loads a single entity into the manager looking for references to loot tables

        If this was from a spawner, set ref_dict to the blockdata that will actually be the record entry
        """

        ref_dict = {
            "path":entity.get_debug_str(),
            "pos": entity.pos,
        }

        if entity.nbt.has_path("CustomName"):
            ref_dict["entity_name"] = entity.nbt.at_path("CustomName").value

        if entity.nbt.has_path("DeathLootTable"):
            self._add_loot_table_reference(entity.nbt.at_path("DeathLootTable").value, "world", ref_dict)

        if entity.nbt.has_path("LootTable"):
            self._add_loot_table_reference(entity.nbt.at_path("LootTable").value, "world", ref_dict)

        if entity.nbt.has_path("Command"):
            self.load_command(entity.nbt.at_path("Command").value, "world", ref_dict)


    def load_world(self, world):
        """Loads all loot table locations in a world

        These locations are loaded so far:
            tile entities
        """
        if not self._world is None:
            raise Exception("Only one world can be loaded into a loot table manager at a time")

        self._world = world
        for region in world.iter_regions(read_only=True):
            for chunk in region.iter_chunks(autosave=False):
                for entity in chunk.recursive_iter_all_types():
                    self.load_entity(entity)


    def update_table_link_in_world_entry(self, tile_entity_ref, old_namespaced_path, new_namespaced_path):
        """Updates a reference to a table in all entities and tile entities in the world that reference the old path."""

        pos = tile_entity_ref["pos"]
        # Ask the world to find this tile entity again
        # Somewhat clunky, but works
        for entity, _, __ in self._world.entity_iterator(pos1=pos, pos2=pos, readonly=False):
            if entity.has_path("LootTable"):
                if entity.at_path("LootTable").value == old_namespaced_path:
                    entity.at_path("LootTable").value = new_namespaced_path

            if entity.has_path("Command"):
                entity.at_path("Command").value = self.update_table_link_in_command(tile_entity_ref,
                                                                                    entity.at_path("Command").value,
                                                                                    old_namespaced_path, new_namespaced_path)
            if entity.has_path("DeathLootTable"):
                if entity.at_path("DeathLootTable").value == old_namespaced_path:
                    entity.at_path("DeathLootTable").value = new_namespaced_path


    #
    # World Loading
    ####################################################################################################

    ####################################################################################################
    # Loot table manipulation
    #


    @staticmethod
    def _update_item_in_single_loot_table(filename, search_item_name, search_item_id, replace_item_nbt):
        """Updates an item within a single loot table."""
        json_file = jsonFile(filename)
        loot_table = json_file.dict

        if not isinstance(loot_table, dict):
            raise TypeError(f'loot_table is type {type(loot_table)}, not instance of dict')
        if "pools" not in loot_table:
            return
        if not isinstance(loot_table["pools"], list):
            raise TypeError(f'loot_table["pools"] is type {type(loot_table["pools"])}, not instance of list')
        for pool in loot_table["pools"]:
            if not isinstance(pool, dict):
                raise TypeError(f'pool is type {type(pool)}, not instance of dict')
            if "entries" not in pool:
                continue
            if not isinstance(pool["entries"], list):
                raise TypeError(f'pool["entries"] is type {type(pool["entries"])}, not instance of list')
            for entry in pool["entries"]:
                if not isinstance(entry, dict):
                    raise TypeError(f'entry is type {type(entry)}, not instance of dict')
                if "type" not in entry:
                    continue
                if entry["type"] == "item":
                    if "name" not in entry:
                        raise KeyError("item loot table entry does not contain 'name'")
                    item_id = entry["name"]
                    if "functions" not in entry:
                        continue
                    if not isinstance(entry["functions"], list):
                        raise TypeError(f'entry["functions"] is type {type(entry["functions"])}, not instance of list')
                    item_name = None
                    for function in entry["functions"]:
                        if not isinstance(function, dict):
                            raise TypeError(f'function is type {type(function)}, not instance of dict')
                        if "function" not in function:
                            continue
                        function_type = function["function"]
                        if function_type == "set_nbt":
                            if "tag" not in function:
                                raise KeyError('set_nbt function is missing nbt field!')
                            item_tag_json = function["tag"]
                            item_tag_nbt = nbt.TagCompound.from_mojangson(item_tag_json)
                            item_name = get_item_name_from_nbt(item_tag_nbt)

                            if item_name == search_item_name and item_id == search_item_id:
                                # Found a match! Update the tag
                                function["tag"] = replace_item_nbt.to_mojangson()

        json_file.save(filename)


    def update_item_in_loot_tables(self, item_id, item_nbt=None, item_nbt_str=None):
        """Updates an item within all loaded loot tables."""
        if item_nbt is None and item_nbt_str is None:
            raise ValueError("Either item_nbt or item_nbt_str must be specified")

        if item_nbt is None:
            item_nbt = nbt.TagCompound.from_mojangson(item_nbt_str)

        item_name = get_item_name_from_nbt(item_nbt)
        if not item_name:
            raise ValueError("Item NBT does not have a name")

        if not item_id in self.item_map:
            raise ValueError(f'Item id {item_id!r} not in loot tables')

        if not item_name in self.item_map[item_id]:
            raise ValueError(f'Item id {item_id!r} name {item_name!r} not in loot tables')

        # Get a list of all the occurrences for iterating
        match_list = []
        if isinstance(self.item_map[item_id][item_name], list):
            match_list = self.item_map[item_id][item_name]
        else:
            match_list.append(self.item_map[item_id][item_name])

        # Get a list of files where this needs updating
        update_file_list = []
        for match in match_list:
            update_file_list.append(match["file"])

        for filename in update_file_list:
            self._update_item_in_single_loot_table(filename, item_name, item_id, item_nbt)

        return update_file_list


    @staticmethod
    def _update_table_link_in_single_loot_table(filename, old_namespaced_path, new_namespaced_path):
        """Updates a reference to a table within a single loot table."""
        json_file = jsonFile(filename)
        loot_table = json_file.dict

        if not isinstance(loot_table, dict):
            raise TypeError(f'loot_table is type {type(loot_table)}, not instance of dict')
        if "pools" not in loot_table:
            return
        if not isinstance(loot_table["pools"], list):
            raise TypeError(f'loot_table["pools"] is type {type(loot_table["pools"])}, not instance of list')
        for pool in loot_table["pools"]:
            if not isinstance(pool, dict):
                raise TypeError(f'pool is type {type(pool)}, not instance of dict')
            if "entries" not in pool:
                continue
            if not isinstance(pool["entries"], list):
                raise TypeError(f'pool["entries"] is type {type(pool["entries"])}, not instance of list')
            for entry in pool["entries"]:
                if not isinstance(entry, dict):
                    raise TypeError(f'entry is type {type(entry)}, not instance of dict')
                if "type" not in entry:
                    continue
                if entry["type"] == "loot_table":
                    if "name" not in entry:
                        raise KeyError("table loot table entry does not contain 'name'")
                    if entry["name"] == old_namespaced_path:
                        entry["name"] = new_namespaced_path

        json_file.save(filename)


    def update_table_link_in_all_of_type(self, old_namespaced_path, new_namespaced_path, label, update_function):
        """Updates all references to a table of the given label using the provided update_function."""

        if not label in self.table_map[old_namespaced_path]:
            # Not referenced in the loot tables
            return

        # Get a list of files where this needs updating
        update_file_list = []
        if isinstance(self.table_map[old_namespaced_path][label], list):
            update_file_list = self.table_map[old_namespaced_path][label]
        else:
            update_file_list.append(self.table_map[old_namespaced_path][label])

        for filename in update_file_list:
            update_function(filename, old_namespaced_path, new_namespaced_path)


    def update_table_link_everywhere(self, old_namespaced_path, new_namespaced_path):
        """Updates all references to a table everywhere loaded into this class."""

        if not old_namespaced_path in self.table_map:
            # Not referenced anywhere
            return

        self.update_table_link_in_all_of_type(old_namespaced_path, new_namespaced_path, "loot_table", self._update_table_link_in_single_loot_table)
        self.update_table_link_in_all_of_type(old_namespaced_path, new_namespaced_path, "advancements", self.update_table_link_in_single_advancement)
        self.update_table_link_in_all_of_type(old_namespaced_path, new_namespaced_path, "functions", self.update_table_link_in_single_function)
        self.update_table_link_in_all_of_type(old_namespaced_path, new_namespaced_path, "scripted_quests", self.update_table_link_in_single_quests_file)
        self.update_table_link_in_all_of_type(old_namespaced_path, new_namespaced_path, "world", self.update_table_link_in_world_entry)

    #
    # Loot table manipulation
    ####################################################################################################


    def get_unique_item_map(self, show_errors=True):
        """Returns item_map[item_id][item_name] = entry without alternate versions."""
        unique_item_map = {}

        for item_id in self.item_map:
            for item_name in dict(sorted(self.item_map[item_id].items())):
                if isinstance(self.item_map[item_id][item_name], list):
                    # DUPLICATE!

                    # First check if every duplicate is identical
                    different = False
                    for loc in self.item_map[item_id][item_name]:
                        if loc["nbt"].to_bytes() != self.item_map[item_id][item_name][0]["nbt"].to_bytes():
                            # This is really bad - different loot table entries with different contents
                            different = True

                    if show_errors and different:
                        eprint("\033[1;31m", end="")
                        eprint(f'ERROR: Item {item_name!r} type {item_id!r} is different and duplicated in the loot tables!')

                        count = 1
                        for loc in self.item_map[item_id][item_name]:
                            eprint(f' {count}: {loc["namespaced_key"]} - {loc["file"]}')
                            eprint(f'    {loc["nbt"].to_mojangson()}')

                            count += 1

                        eprint("\033[0;0m", end="")
                        eprint()

                    if not item_id in unique_item_map:
                        unique_item_map[item_id] = {}
                    unique_item_map[item_id][item_name] = self.item_map[item_id][item_name][0]
                else:
                    if not item_id in unique_item_map:
                        unique_item_map[item_id] = {}
                    unique_item_map[item_id][item_name] = self.item_map[item_id][item_name]

        return unique_item_map
