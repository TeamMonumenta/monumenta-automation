#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

# TODO: This get name thing should be built into the item / entity objects
import re
from quarry.types.text_format import unformat_text
def get_name(name):
    name = re.sub(r"\\u0027", "'", name)
    name = re.sub(r"\\u00a7", "§", name)

    # If the name is JSON, parse it down to just the name text
    try:
        name_json = json.loads(name)
        if "text" in name_json:
            name = name_json["text"]
    except:
        pass

    name = unformat_text(name)

    return name

class NbtPathDebug():
    """
        A subclass of entities to help understand where they are and
        their relationship to other entities they are stored inside of.

        Subclasses that extend this should call __init__() with appropriate data
    """

    def nbt_path_init(self, nbt, parent, root, data_version):
        self.nbt = nbt
        self.parent = parent
        self.root = root
        self.data_version = data_version

    @property
    def full_nbt_path(self):
        """Get the full NBT path from the original file."""
        if self.parent is None:
            return self.nbt_path_from_parent

        return nbt.nbt_path_join(self.parent.full_nbt_path, self.nbt_path_from_parent)

    def get_legacy_debug(self):
        result = [self.nbt]
        node = self
        while node.parent is not None:
            result.append(node.parent.nbt)
            node = node.parent

        return result

    def print(self):
        """Print the debug path from file root to here."""
        if self.parent is None:
            print(f'NBT debug path for {type(self.obj)} {self.file_uri}')
            return

        self.parent.print()
        print(f'- go into {type(self.obj)} at {self.nbt_path_from_parent}')

    def get_path_repr_str(self):
        """Return the text to be entered in a script or interpretter."""
        if self.parent is None:
            return repr(self)
        return f'{repr(self.parent)} \\\n    {repr(self)}'

    # TODO: This should be a property of the entities themselves
    def get_debug_str(self):
        if self.nbt.has_path("playerGameType"):
            # This is a player
            return f"player {get_entity_uuid(self.nbt)}"
        elif self.nbt.has_path("SpawnPotentials"):
            return f"spawner {self.pos}"
        elif self.nbt.has_path("id"):
            name = ""
            if self.nbt.has_path("CustomName"):
                name = get_name(self.nbt.at_path("CustomName").value)

                # Don't print names of things that are just "@" (commands do this a lot apparently)
                if name == "@":
                    name = ""

            if self.nbt.has_path("tag.display.Name"):
                name = get_name(self.nbt.at_path("tag.display.Name").value)

            return f"""{self.nbt.at_path("id").value.replace("minecraft:","")} {self.pos} {name}"""
        return str(self)

    def get_path_str(self):
        if self.parent is None:
            return self.get_debug_str()
        return f'{self.parent.get_path_str()} -> {self.get_debug_str()}'

    def get_path_pretty_str(self):
        """Return the text to be entered in a script or interpretter."""
        if self.parent is None:
            return repr(self)
        return f'{repr(self.parent)} \\\n    {repr(self)}'
