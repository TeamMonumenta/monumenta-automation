#!/usr/bin/env python3

class BaseContainer(object):
    """An item container."""
    _slots = 0

    def __init__(self):
        """Initialize the container."""
        pass

    def slot_ids(self, side=None):
        """Returns a tuple of available slot IDs"""
        return tuple()

    def available_slots(self, item=None):
        """How many items can fit in each slot.

        If no item is provided, counts only empty spaces.
        """
        return {}

    def add_to_slot(self, slot, item_stack):
        """Insert items into a slot, returning an item stack for remaining items."""
        pass
