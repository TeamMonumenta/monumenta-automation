#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

class EntityTag():
    """The block entity tag to be placed/displayed by this item."""
    def __init__(self, item: Item):
        """Load the entity in this item from its tag.

        This is a reference to the original. Make sure to save parent tag when done.
        """
        if not isinstance(item, Item):
            raise TypeError("Expected item to be an instance of Item.")

        self.item = item
        self.item_tag = item.tag

    @property
    def entity(self):
        """"Get the entity tag of this item, or None."""
        if not self.item_tag.has_path("EntityTag"):
            return None
        return Entity(self.item_tag.at_path("EntityTag"), self.item, self.item.root)

    @entity.setter
    def entity(self, value):
        """Set the entity tag of this item."""
        if value is None:
            if self.item_tag.has_path("EntityTag"):
                self.item_tag.value.pop("EntityTag")
        elif isinstance(value, Entity):
            self.item_tag.value["EntityTag"] = value.nbt
        else:
            self.item_tag.value["EntityTag"] = value


from minecraft.chunk_format.entity import Entity

