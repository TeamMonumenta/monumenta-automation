#!/usr/bin/env python3

import sys
import os
import json
from pprint import pprint, pformat
from lib_py3.common import parse_name_possibly_json, eprint
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path
from lib_py3.schematic import Schematic

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

from quarry.types import nbt
from quarry.types.nbt import TagCompound
from quarry.types.text_format import unformat_text

class LibraryOfSouls(object):
    def __init__(self, path: str):
        self._path = path
        self._souls = []
        self._index = None

        with open(path, "r") as fp:
            self._souls = json.load(fp)

    def clear_tags(self) -> None:
        for soul_entry in self._souls:
            if "Tags" in soul_entry:
                soul_entry.pop("Tags")

    def refresh_index(self) -> None:
        self._index = {}

        new_souls = []
        for soul_entry in self._souls:
            soul_nbt = nbt.TagCompound.from_mojangson(soul_entry["mojangson"])

            if not soul_nbt.has_path("CustomName"):
                eprint("WARNING: Souls database entry is missing a name: {}".format(pformat(soul_entry)))
                continue
            else:
                name = unformat_text(parse_name_possibly_json(soul_nbt.at_path("CustomName").value))
                self._index[name] = soul_entry

            new_souls.append(soul_entry)

        self._souls = new_souls

    def get_soul(self, name: str) -> dict:
        if self._index is None:
            self.refresh_index()

        if name in self._index:
            return self._index[name]
        return None

    def add_soul(self, soul_nbt: TagCompound) -> None:
        if self._index is None:
            self.refresh_index()

        if not soul_nbt.has_path("CustomName"):
            raise ValueError("Attempted to add souls database entity with no name")

        name = unformat_text(parse_name_possibly_json(soul_nbt.at_path("CustomName").value))

        if not name:
            raise ValueError("Attempted to add souls database entity with no name")

        if name in self._index:
            raise ValueError("Attempted to add souls database entity that already exists")

        soul_entry = {}
        soul_entry["mojangson"] = soul_nbt.to_mojangson()
        self._index[name] = soul_entry
        self._souls.append(soul_entry)

    def save(self):
        with open(self._path, "w") as fp:
            json.dump(self._souls, fp, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': '))
        pass


los = LibraryOfSouls("/home/epic/project_epic/mobs/plugins/LibraryOfSouls/souls_database.json")

los.clear_tags()

not_found_different_mobs = set()
not_found_unique_mobs = {}
not_found_unique_low_count_mobs = set()
mob_counts = {}

for basedir in ["/home/epic/project_epic/server_config/data/structures/region_1", "/home/epic/project_epic/server_config/data/structures/region_2"]:
    for root, subdirs, files in os.walk(basedir):
        for fname in files:
            if fname.endswith(".schematic"):
                schem = Schematic(os.path.join(root, fname))

                armor_stand_count = 0

                print("Processing schematic: {}".format(schem.name))

                for entity, source_pos, entity_path in schem.entity_iterator(readonly=True):
                    if entity.has_path("CustomName"):
                        if not entity.has_path("id"):
                            continue
                        if "armor_stand" in entity.at_path("id").value:
                            armor_stand_count += 1
                            continue

                        name = unformat_text(parse_name_possibly_json(entity.at_path("CustomName").value))

                        # Keep track of how many times each mob is seen
                        if name not in mob_counts:
                            mob_counts[name] = 0
                        mob_counts[name] += 1

                        # Check if this mob is already in the library of souls
                        soul = los.get_soul(name)
                        if soul is not None:
                            # Already in the library - tag it with the name of the structure for searching
                            if "tags" not in soul:
                                soul["tags"] = []
                            if schem.name not in soul["tags"]:
                                soul["tags"].append(schem.name)
                        else:
                            # Not in the library - check if its NBT is unique
                            if name not in not_found_different_mobs:
                                if name in not_found_unique_mobs:
                                    if not_found_unique_mobs[name] != entity:
                                        #print("Diff at mob {}".format(name))
                                        #not_found_unique_mobs[name].diff(entity, order_matters=False, show_values=True)
                                        not_found_different_mobs.add(name)
                                        not_found_unique_mobs.pop(name)
                                else:
                                    not_found_unique_mobs[name] = entity

                if armor_stand_count > 0:
                    eprint("Warning: Structure {} contains {} armor stands!".format(schem.name, armor_stand_count))

#print("\n\n\n\n\n\nNot found unique mobs:")
#pprint(not_found_unique_mobs)

added = 0
for name in not_found_unique_mobs:
    if mob_counts[name] < 5:
        not_found_unique_low_count_mobs.add(name)
    else:
        los.add_soul(not_found_unique_mobs[name])
        added += 1

print("\n\n\n\n\n\nAdded {} mobs to souls index".format(added))

print("\n\n\n\n\n\nNot found unique low-count mobs:")
pprint(not_found_unique_low_count_mobs)

print("\n\n\n\n\n\nNot found different mobs:")
pprint(not_found_different_mobs)

los.save()
