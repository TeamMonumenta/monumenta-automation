import sys
import os
import json
import time
from pprint import pformat
from lib_py3.common import parse_name_possibly_json, eprint
from lib_py3.mob_replacement_manager import MobReplacementManager

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

from quarry.types import nbt
from quarry.types.nbt import TagCompound
from quarry.types.text_format import unformat_text


class LibraryOfSouls(object):
    def __init__(self, path: str, readonly=False):
        self._path = path
        self._souls = []
        self._index = None
        self._readonly = readonly

        with open(path, "r") as fp:
            self._souls = json.load(fp)

        self.upgrade()

    def upgrade(self):
        for soul_entry in self._souls:
            if "mojangson" in soul_entry:
                hist_element = {}
                hist_element["mojangson"] = soul_entry["mojangson"]
                hist_element["modified_on"] = int(time.time())
                soul_entry["history"] = [hist_element, ]
                soul_entry.pop("mojangson")

    def clear_tags(self) -> None:
        for soul_entry in self._souls:
            if "tags" in soul_entry:
                soul_entry.pop("tags")
            if "location_names" in soul_entry:
                soul_entry.pop("location_names")

    def refresh_index(self) -> None:
        self._index = {}

        new_souls = []
        for soul_entry in self._souls:
            soul_nbt = nbt.TagCompound.from_mojangson(soul_entry["history"][0]["mojangson"])

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

    def get_soul_current_nbt(self, name: str) -> TagCompound:
        if self._index is None:
            self.refresh_index()

        if name in self._index:
            return nbt.TagCompound.from_mojangson(self._index[name]["history"][0]["mojangson"])
        return None

    def add_soul(self, soul_nbt: TagCompound) -> None:
        if self._readonly:
            raise Exception("Attempted to save read-only Library of Souls")
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

    def load_replacements(self, mgr: MobReplacementManager) -> None:
        if self._index is None:
            self.refresh_index()

        current_nbt = []
        for name in self._index:
            current_nbt.append(self.get_soul_current_nbt(name))

        mgr.add_replacements(current_nbt)

    def save(self) -> None:
        if self._readonly:
            raise Exception("Attempted to save read-only Library of Souls")
        with open(self._path, "w") as fp:
            json.dump(self._souls, fp, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': '))