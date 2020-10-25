#!/usr/bin/env python3

import os
import sys

from enum import IntEnum

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

class ModifierOperation(IntEnum):
    ADD = 0
    MULTIPLY_BASE = 1
    MULTIPLY = 2

class AttributeModifiers():
    """Item attribute modifiers."""
    def __init__(self, item_tag: nbt.TagCompound):
        """Load an item's attribute modifiers from its tag.

        This is a reference to the original. Make sure to save parent tag when done.
        """
        if not isinstance(item_tag, nbt.TagCompound):
            raise TypeError("Expected item_tag to be an instance of nbt.TagCompound.")

        self.item_tag = item_tag

    @property
    def modifiers(self):
        attributes = []
        for modifier_tag in item_tag.iter_multipath("AttributeModifiers[]"):
            # Add attribute classes to list
            attributes.append(AttributeModifier(modifier_tag))
        return attributes

    @modifiers.setter
    def modifiers(self, value):
        if len(value) == 0:
            if self.item_tag.has_path("AttributeModifiers"):
                self.item_tag.value.pop("AttributeModifiers")
        else:
            attributes = [modifier.tag for modifier in value]
            self.item_tag.value["AttributeModifiers"] = nbt.TagList(attributes)


class AttributeModifier():
    """An item attribute modifier."""
    def __init__(self, modifier_tag: nbt.TagCompound):
        """Load an item's attribute modifier from an attribute modifier tag.

        This is a reference to the original. Make sure to save parent tag when done.
        """
        if not isinstance(modifier_tag, nbt.TagCompound):
            raise TypeError("Expected modifier_tag to be an instance of nbt.TagCompound.")

        for required_tag in ("AttributeName", "Name", "Slot", "Operation", "Amount"):
            if not modifier_tag.has_path(required_tag):
                raise KeyError(f"Missing required tag {required_tag}.")

        self.tag = modifier_tag

        if self.tag.has_path("UUID"):
            self._uuid = uuid_util.from_tag_int_array(self.tag.at_path("UUID"))
        elif self.tag.has_path("UUIDMost") and self.tag.has_path("UUIDLeast"):
            most = self.tag.at_path("UUIDMost")
            least = self.tag.at_path("UUIDLeast")
            self._uuid = uuid_util.from_tag_int_array(most, least)
        if self._uuid is None:
            raise KeyError("Expected a UUID for this attribute modifier.")

    @property
    def attribute_name(self):
        return self.tag.at_path("AttributeName").value

    @attribute_name.setter
    def attribute_name(self, value):
        self.tag.at_path("AttributeName").value = value

    @property
    def name(self):
        return self.tag.at_path("Name").value

    @attribute_name.setter
    def name(self, value):
        self.tag.at_path("Name").value = value

    @property
    def slot(self):
        return self.tag.at_path("Slot").value

    @slot.setter
    def slot(self, value):
        self.tag.at_path("Slot").value = value

    @property
    def operation(self):
        op_id = self.tag.at_path("Operation").value
        for op in ModifierOperation:
            if op == op_id:
                return op
        raise ValueError(f"Unknown operation {op_id}")

    @slot.setter
    def operation(self, value):
        self.tag.at_path("Operation").value = int(value)

    @property
    def amount(self):
        return self.tag.at_path("Amount").value

    @slot.setter
    def amount(self, value):
        self.tag.at_path("Amount").value = value

    @property
    def uuid(self):
        return self._uuid

    @slot.setter
    def uuid(self, value, data_version=2230):
        self._uuid = value

        if data_version >= 2515:
            # Use int array tag, 1.16
            self.tag.value["UUID"] = uuid_util.to_tag_int_array(value)
        elif self.tag.has_path("UUID"):
            # Use int array tag, 1.16
            eprint(f"WARNING! Version incorrectly set in {os.path.realpath(__file__)}. Assuming 1.16+!")
            self.tag.value["UUID"] = uuid_util.to_tag_int_array(value)
        else:
            # Use most/least tags, 1.15.2 or earlier
            tags = uuid_util.to_tag_most_least(value)
            self.tag.value["UUIDMost"] = tags["most"]
            self.tag.value["UUIDLeast"] = tags["least"]

    def new_uuid(self):
        """Give this entity a new random UUID."""
        self.uuid = uuid_util.generate()


from minecraft.util import uuid_util

