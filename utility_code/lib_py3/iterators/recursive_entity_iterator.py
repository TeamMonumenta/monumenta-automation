#
# Recursive iterator for entities / tile entities everywhere in the world
#

from lib_py3.iterators.base_chunk_entity_iterator import BaseChunkEntityIterator
from lib_py3.iterators.item_iterator import ItemIterator

class RecursiveEntityIterator(object):
    """
    This iterator uses BaseChunkEntityIterator to get entities and tile entities in the world
    Then it recursively iterates over them to find additional entities / tile entities

    Same arguments as BaseChunkEntityIterator:

    If readonly=False, it will save each chunk it visits that contain entities

    If coordinates are specified, it will only load region files that contain those coordinates
    Otherwise it will iterate over everything world wide

    Only iterates over chunks in regions that could plausibly contain the specified coordinates
    """

    def __init__(self, world, pos1=None, pos2=None, readonly=True):
        self._baseiterator = BaseChunkEntityIterator(world, pos1, pos2, readonly)

    def __iter__(self):
        """
        Initialize the iterator for use.

        Doing this here instead of in __init__ allows the iterator to potentially be re-used
        """

        # Initialize the base iterator
        self._baseiterator.__iter__()

        # Use a stack to keep track of what items still need to be processed
        self._work_stack = []

        return self

    def _scan_item_for_work(self, item):
        """
        Looks at an item and if it contains more tile or block entities,
        add them to the _work_stack
        """
        if item.has_path("tag.BlockEntityTag"):
            self._work_stack.append((item.at_path("tag.BlockEntityTag"), True))

        if item.has_path("tag.EntityTag"):
            self._work_stack.append((item.at_path("tag.EntityTag"), False))

    def __next__(self):
        """
        Iterates over entities embedded in an entity.

        Iteration order is depth-first, returning the higher-level object first then using
        a depth-first iterator into nested sub elements

        Return value is two things!
            entity - the entity OR tile entity TagCompound
            is_tile_entity - True if tile entity, False if entity
            source_pos - an (x, y, z) tuple of the original entity's position
        """

        if len(self._work_stack) == 0:
            # No work left to do - get another entity
            entity, is_tile_entity = self._baseiterator.__next__()
            self._work_stack.append((entity, is_tile_entity))

            # Keep track of where the original entity was. This is useful because nested
            # items mostly don't have position tags
            if is_tile_entity:
                if entity.has_path('x') and entity.has_path('y') and entity.has_path('z'):
                    x = entity.at_path('x').value
                    y = entity.at_path('y').value
                    z = entity.at_path('z').value
                    self._source_pos = (x, y, z)
                else:
                    self._source_pos = None
            else:
                if entity.has_path('Pos'):
                    pos = entity.at_path('Pos').value
                    x = pos[0].value
                    y = pos[1].value
                    z = pos[2].value
                    self._source_pos = (x, y, z)
                else:
                    self._source_pos = None


        # Process the next work element on the stack
        current_entity, is_tile_entity = self._work_stack.pop()

        # Add more work to the stack for next time
        if is_tile_entity:
            # Tile entities!
            if current_entity.has_path("SpawnPotentials"):
                for spawn in current_entity.at_path("SpawnPotentials").value:
                    if spawn.has_path("Entity"):
                        self._work_stack.append((spawn.at_path("Entity"), False))

            if current_entity.has_path("SpawnData"):
                self._work_stack.append((current_entity.at_path("SpawnData"), False))

        else:
            # Regular entities!
            if current_entity.has_path("Passengers"):
                for passenger in current_entity.at_path("Passengers").value:
                    self._work_stack.append((passenger, False))

        # Scan items in current entity, and if any are found scan them for nested entities
        ItemIterator.scan_entity_for_items(current_entity, self._scan_item_for_work);

        return current_entity, is_tile_entity, self._source_pos
