#
# Recursive iterator for items everywhere in the world
#

from lib_py3.iterators.recursive_entity_iterator import RecursiveEntityIterator
from lib_py3.iterators.recursive_entity_iterator import scan_entity_for_items

class ItemIterator(object):
    def __init__(self, world, pos1=None, pos2=None, readonly=True, players_only=False):
        self._entity_iterator = RecursiveEntityIterator(world, pos1, pos2, readonly, players_only)

    def __iter__(self):
        """
        Initialize the iterator for use.

        Doing this here instead of in __init__ allows the iterator to potentially be re-used
        """

        # Initialize the base iterator
        self._entity_iterator.__iter__()

        # Use a stack to keep track of what items still need to be processed
        self._work_stack = []

        return self

    def _scan_item_for_work(self, item, arg):
        """
        Adds a found item to the work queue
        """
        # Don't bother returning empty items
        if len(item.value) != 0:
            self._work_stack.append((item, arg[0], arg[1]))

    def __next__(self):
        """
        Iterates over items in the world

        Iteration order is depth-first, returning the higher-level object first then using
        a depth-first iterator into nested sub elements

        Return value is:
            item - the item TagCompound
        """

        while len(self._work_stack) == 0:
            # No work left to do - search for another entity containing items
            entity, source_pos, entity_path = self._entity_iterator.__next__()

            # Add more work to the stack for items contained in this entity, if any
            scan_entity_for_items(entity, self._scan_item_for_work, (source_pos, entity_path));

        # Process the next work element on the stack
        current_item, source_pos, entity_path = self._work_stack.pop()

        return current_item, source_pos, entity_path + [current_item,]
