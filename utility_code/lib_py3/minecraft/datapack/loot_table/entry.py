#!/usr/bin/env python3

import copy
import os
import random
import sys

this_folder = os.path.dirname(os.path.realpath(__file__))

sys.path.append(this_folder)
from condition import BaseConditionList
from function import BaseFunctionList

sys.path.append(os.path.join(this_folder, "../.."))
from item import Item, ItemStack

class BaseEntry(object):
    """A loot table entry.

    This is the base class, and is not intended to be used directly, except to get subclasses.
    Subclass names are CaseSensitive, and must match the IDs used by Minecraft itself.
    """
    def __init__(self, entry):
        """Load the entry from a dict.

        A description of the arguements goes here.
        """
        if isinstance(entry, type(self)):
            self._dict = copy.deepcopy(entry._dict)

        elif isinstance(entry, dict):
            self._dict = copy.deepcopy(entry)

        else:
            raise TypeError("Expected entry to be type dict.")

        self.weight = self._dict.get('weight', 1)
        self.quality = self._dict.get('quality', 0)

        self.conditions = BaseConditionList(self._dict.get('conditions', []))

    def generate(self, generation_state):
        """Generate the entry as part of generating loot from a loot table."""
        if self.conditions.test(generation_state):
            self._generate(generation_state)

    def _generate(self, generation_state):
        """Generate the entry after confirming the conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this entry does"""
        NotImplemented

    def __repr__(self):
        return "{name}({entry})".format(name=self.__class__.__name__, entry=self._dict)

    def get_weight(self, generate_state):
        """Get this entry's weight for the generation state."""
        # TODO Improperly implemented - does not account for luck or looting.
        return self.weight

    @classmethod
    def recursive_public_subclasses(cls):
        """Return a dict of subclasses by name, not listing subclasses starting with '_'.

        Should multiple subclasses need to be derived from another subclass,
        a base subclass whose name starts with '_' should be created so
        its children are returned, but not the base subclass itself.
        """
        result = {}

        for subclass in cls.__subclasses__():
            name = subclass.__name__

            # Ignore subclasses that exist only as a parent to other subclasses
            if not name.startswith("_") and not name.startswith("Base"):
                if name in result:
                    raise KeyError("Subclass with the name {!r} appears more than once.".format(name))

                result[name] = subclass

            subsubclasses = subclass.recursive_public_subclasses()

            for name, subsubclass in subsubclasses.items():
                if name in result:
                    raise KeyError("Subclass with the name {!r} appears more than once.".format(name))

                result[name] = subclass

        return result


class BaseEntryList(BaseEntry):
    """A list of loot table entries.

    Generates all in sequence. (TODO)
    """
    def __init__(self, entry):
        """Load the entry from a ~~dict~~ list of dicts."""
        if isinstance(entry, type(self)):
            self._list = copy.deepcopy(entry._list)

        elif isinstance(entry, list):
            self._list = copy.deepcopy(entry)

        else:
            raise TypeError("Expected entry list to be type list.")

        self.entries = [Entry(entry) for entry in self._list]

    def _generate(self, generation_state):
        """Generate the entries; does not check conditions."""
        NotImplemented
        # TODO lots

    def description(self):
        """A description of what these entries do."""
        result = []

        for entry in self._list:
            result += entry.description()

        return result

    def __len__(self):
        return len(self._list)

    def __getitem__(self, index):
        return self._list.__get__(index)

    def __repr__(self):
        return "{name}({entry})".format(name=self.__class__.__name__, entry=self._dict)


class alternatives(BaseEntry):
    """An alternatives loot table entry.

    Generates one child entry.
    """
    def __init__(self, entry):
        """Load the entry from a dict.

        type(entry["children"]) == list: List of entries
        """
        super().__init__(entry)
        self.alternatives = BaseEntryList(entry["children"])

    def _generate(self, generation_state):
        """Generate the entry after confirming the conditions are met."""
        # TODO Create list that can generate with the current conditions,
        # check if that list is empty, and try to generate until one works.
        NotImplemented

    def description(self):
        """A description of what this entry does"""
        NotImplemented

    def __repr__(self):
        return "{name}({entry})".format(name=self.__class__.__name__, entry=self._dict)


class dynamic(BaseEntry):
    """A dynamic loot table entry.

    Generates block specific drops.
    """
    def __init__(self, entry):
        """Load the entry from a dict.

        self._dict["name"] == "contents": For containers.
        self._dict["name"] == "self": For skulls and banners.
        """
        super().__init__(entry)
        NotImplemented

    def _generate(self, generation_state):
        """Generate the entry after confirming the conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this entry does"""
        NotImplemented

    def __repr__(self):
        return "{name}({entry})".format(name=self.__class__.__name__, entry=self._dict)


class empty(BaseEntry):
    """An empty loot table entry.

    Generates nothing.
    """
    def __init__(self, entry):
        """Load the entry from a dict."""
        super().__init__(entry)

    def _generate(self, generation_state):
        """Generate the entry after confirming the conditions are met."""
        return

    def description(self):
        """A description of what this entry does"""
        return ["Generate no items."]

    def __repr__(self):
        return "{name}({entry})".format(name=self.__class__.__name__, entry=self._dict)


class group(BaseEntry):
    """A group loot table entry.

    Generates all child entries.
    Allows one set of conditions to apply to a group of entries without being repeated.
    """
    def __init__(self, entry):
        """Load the entry from a dict.

        type(entry["children"]) == list: List of entries
        """
        super().__init__(entry)
        self.group = BaseEntryList(entry["children"])
        NotImplemented

    def _generate(self, generation_state):
        """Generate the entry after confirming the conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this entry does"""
        NotImplemented

    def __repr__(self):
        return "{name}({entry})".format(name=self.__class__.__name__, entry=self._dict)


class item(BaseEntry):
    """An item loot table entry.

    Generates a single item.
    """
    def __init__(self, entry):
        """Load the entry from a dict.

        type(self._dict["name"]) == str: A namedpsaced item ID. Namespace defaults to minecraft.
        type(self._dict["functions"]) == list: A list of loot table functions.
        """
        super().__init__(entry)
        self.item_id = self._dict["name"]
        self.functions = BaseFunctionList(self._dict.get("functions", []))

    def _generate(self, generation_state):
        """Generate the entry after confirming the conditions are met."""
        item = ItemStack()
        item.id = self.item_id
        self.functions(item, generation_state)
        NotImplemented # Put the item in the container

    def description(self):
        """A description of what this entry does"""
        NotImplemented

    def __repr__(self):
        return "{name}({entry})".format(name=self.__class__.__name__, entry=self._dict)


class loot_table(BaseEntry):
    """An loot table loot table entry.

    Yes.
    Ok, more helpful description:
    Generates items from another loot table.

    This can be used to give entire loot tables different weights, or just for organization.
    """
    def __init__(self, entry):
        """Load the entry from a dict.

        type(self._dict["name"]) == str: A namedpsaced loot table ID. Namespace defaults to minecraft.
        """
        super().__init__(entry)
        NotImplemented

    def _generate(self, generation_state):
        """Generate the entry after confirming the conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this entry does"""
        NotImplemented

    def __repr__(self):
        return "{name}({entry})".format(name=self.__class__.__name__, entry=self._dict)


class sequence(BaseEntry):
    """A sequence loot table entry.

    Generates random child entries until one entry cannot be granted.
    """
    def __init__(self, entry):
        """Load the entry from a dict.

        type(entry["children"]) == list: List of entries
        """
        super().__init__(entry)
        self.sequence = BaseEntryList(entry["children"])
        NotImplemented

    def _generate(self, generation_state):
        """Generate the entry after confirming the conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this entry does"""
        NotImplemented

    def __repr__(self):
        return "{name}({entry})".format(name=self.__class__.__name__, entry=self._dict)


class tag(BaseEntry):
    """An item tag loot table entry.

    Generates items based on an item tag.
    TODO Not sure if this generates one or all tag entries.
    """
    def __init__(self, entry):
        """Load the entry from a dict.

        type(self._dict["name"]) == str: A namedpsaced item tag ID. Namespace defaults to minecraft.
        self._dict["expand"] is True: (TODO Split/Share) the weight and quality of this entry among each item in the tag.
        self._dict["expand"] is False: Generate one of each item in the tag.
        """
        super().__init__(entry)
        NotImplemented

    def _generate(self, generation_state):
        """Generate the entry after confirming the conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this entry does"""
        NotImplemented

    def __repr__(self):
        return "{name}({entry})".format(name=self.__class__.__name__, entry=self._dict)


entry_types = BaseFunction.recursive_public_subclasses()

def load_entry(entry):
    """Loads a function, determining the appropriate type automatically."""
    entry_type = entry['type']
    entry_class = entry_types[entry_type]
    return entry_class(entry)

