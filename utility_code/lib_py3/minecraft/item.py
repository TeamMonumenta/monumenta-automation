#!/usr/bin/env python3

"""A library to process item stacks"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "."))
from datapack.tags import ItemTag

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt
from brigadier.string_reader import StringReader


class ItemStack(Item):
    """An object to represent an item stack."""
    def __init__(self, other=None):
        """Load an item from another item, or create a new one."""
        super().__init__(other)
        if other is None:
            self._count = 1
            self._slot = None

        else:
            self._count = other._count
            self._slot = other._slot

    @classmethod
    def from_command(cls, string_reader):
        """Load an item from a StringReader with the standard command format."""
        if not isinstance(string_reader, StringReader):
            string_reader = StringReader(string_reader)

        result = cls()

        if string_reader.canRead() and string_reader.peek() == "#":
            raise TypeError("Found an item tag while expecting an item.")

        new_id = ""
        while string_reader.canRead() and string_reader.peek() not in " {":
            new_id += string_reader.read()

        if not new_id:
            raise SyntaxError('Expected item in the format "[namespace:]id{tag} [Count]"')

        result.id = new_id

        if string_reader.canRead() and string_reader.peek() == "{":
            result.tag = nbt.TagCompound.from_mojangson(string_reader)

        count_cursor = string_reader.getCursor()
        if string_reader.canRead(2) and string_reader.peek() == " ":
            string_reader.read()

            try:
                result.count = string_reader.readLong()

            except:
                string_reader.setCursor(count_cursor)

        return result

    def to_command(self):
        result = super().to_command()
        result += " {}".format(self.count)

        return result

    @classmethod
    def from_mojangson(cls, mojangson):
        """Load an item stack from mojangson."""
        tag = nbt.TagCompound.from_mojangson(mojangson)
        return cls.from_nbt(tag)

    def to_mojangson(self):
        return self.to_nbt().to_mojangson()

    @classmethod
    def from_nbt(cls, tag):
        """Load an item stack from the stack NBT."""
        result = cls()

        if not tag.has_path("id"):
            raise KeyError("Item stack has no ID.")
        result.id = tag.at_path("id").value

        if tag.has_path("Count"):
            result.count = tag.at_path("Count").value

        if tag.has_path("Slot"):
            result.slot = tag.at_path("Slot").value

        if tag.has_path("tag"):
            result.tag = tag.at_path("tag")

        return result

    def to_nbt(self):
        result = super().to_nbt()

        result.value["Count"] = nbt.TagByte(self.count)

        if self.slot is not None:
            result["Slot"] = nbt.TagByte(self.slot)

        return nbt.TagCompound(result)

    def tree(self):
        self.to_nbt().tree()

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        if not isinstance(value, int):
            raise TypeError("Item count must be an integer.")

        if value < 0:
            raise ValueError("Item count must not be negative.")

        self._count = value

    @property
    def max_count(self):
        return 64 # TODO

    @property
    def slot(self):
        return self._slot

    @slot.setter
    def slot(self, value):
        if not isinstance(value, int) and value is not None:
            raise TypeError("Item slot must be an integer or None.")

        self._slot = value

    def __repr__(self):
        return "ItemStack.from_mojangson({!r})".format(self.to_mojangson())

class Item(object):
    """An object to represent an item stack."""
    def __init__(self, other=None):
        """Load an item from another item, or create a new one."""
        if other is None:
            self._id = "minecraft:stone"
            self.tag = None

        else:
            self._id = other._id
            if other.tag is None:
                self.tag = None
            else:
                self.tag = other.tag.deep_copy()

    @classmethod
    def from_command(cls, string_reader):
        """Load an item from a StringReader with the standard command format."""
        if not isinstance(string_reader, StringReader):
            string_reader = StringReader(string_reader)

        result = cls()

        if string_reader.canRead() and string_reader.peek() == "#":
            raise TypeError("Found an item tag while expecting an item.")

        new_id = ""
        while string_reader.canRead() and string_reader.peek() not in " {":
            new_id += string_reader.read()

        if not new_id:
            raise SyntaxError('Expected item in the format "[namespace:]id{tag}"')

        result.id = new_id

        if string_reader.canRead() and string_reader.peek() == "{":
            result.tag = nbt.TagCompound.from_mojangson(string_reader)

        return result

    def to_command(self):
        result = self._id

        if self.tag:
            result += self.tag.to_mojangson()

        return result

    def to_loot_table_entry(self):
        result = {}
        result["type"] = "item"
        result["name"] = self._id

        if self.nbt is not None:
            if "functions" not in result:
                result["functions"] = []

            function = {}
            function["function"] = "set_nbt"
            function["tag"] = self.tag.to_mojangson()

            result["functions"].append(function)

        return result

    @classmethod
    def from_mojangson(cls, mojangson):
        """Load an item stack from mojangson."""
        tag = nbt.TagCompound.from_mojangson(mojangson)
        return cls.from_nbt(tag)

    def to_mojangson(self):
        return self.to_nbt().to_mojangson()

    @classmethod
    def from_nbt(cls, tag):
        """Load an item from the stack NBT."""
        result = cls()

        if not tag.has_path("id"):
            raise KeyError("Item has no ID.")
        result.id = tag.at_path("id").value

        if tag.has_path("tag"):
            result.tag = tag.at_path("tag")

        return result

    def to_nbt(self):
        result = {}

        result["id"] = nbt.TagString(self._id)

        if self.tag:
            result["tag"] = self.tag

        return nbt.TagCompound(result)

    def tree(self):
        self.to_nbt().tree()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, str):
            raise TypeError("Item id must be a string.")

        if ":" not in value:
            value = "minecraft:" + value

        self._id = value

    def __repr__(self):
        return "Item.from_mojangson({!r})".format(self.to_mojangson())

