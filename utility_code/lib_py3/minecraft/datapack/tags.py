#!/usr/bin/env python3

"""A library to process datapack tags."""

"""TODO

- Load other tags.
- Replace/combine logic
- Subclasses
- Link to target objects
"""

from util import OrderedSet

class BaseTag(object):
    """An object to represent a datapack tag."""
    def __init__(self, other):
        """Load a tag from another tag."""
        if not isinstance(other, BaseTag):
            raise typeError("Tag expected other to be instance of BaseTag.")

        self.namespaced_key = other.namespaced_key
        self.replace = other.replace
        self.local_ids = OrderedSet(other.local_ids)


    def load_from_dict(self, namespaced_key, other):
        """Load a tag from a dict."""
        if not isinstance(other, dict):
            raise typeError("Tag expected other to be type dict.")

        self.namespaced_key = namespaced_key
        self.replace = other.get("replace", False)
        self.local_ids = OrderedSet(other.get("values", ())))


    @property
    def all_ids(self):
        """List all ids for this tag and its child tags."""
        return tuple(self.local_ids)


class BlockTag(BaseTag):
    """A list of blocks."""
    pass


class EntityIdTag(BaseTag):
    """A list of entity IDs."""
    pass


class FunctionTag(BaseTag):
    """A list of functions."""
    pass


class ItemTag(BaseTag):
    """A list of items."""
    pass


