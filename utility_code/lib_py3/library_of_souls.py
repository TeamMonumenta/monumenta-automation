import sys
import os
import json
from pprint import pformat
from lib_py3.common import parse_name_possibly_json, eprint

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
            if "tags" in soul_entry:
                soul_entry.pop("tags")
            if "location_names" in soul_entry:
                soul_entry.pop("location_names")

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
