#
# Iterator for entities / tile entities stored in region files (without recursion)
#

import math
import os

from quarry.types import nbt

from lib_py3.common import bounded_range

from lib_py3.iterators.iterator_interface import base_chunk_entity_iterator

class BaseChunkEntityIterator(object):
    """
    This is an iterator over basic (non-recursive) entities AND tile entities in the world

    If readonly=False, it will save each chunk it visits that contain entities

    If coordinates are specified, it will only load region files that contain those coordinates
    Otherwise it will iterate over everything world wide

    Only iterates over chunks in regions that could plausibly contain the specified coordinates
    """

    def __init__(self, world, pos1=None, pos2=None, readonly=True):
        self._world = world
        self._pos1 = pos1
        self._pos2 = pos2
        self._readonly = readonly

        self._iter = base_chunk_entity_iterator(self._world, self._pos1, self._pos2, self._readonly)

    def __iter__(self):
        """
        Initialize the iterator for use.

        Doing this here instead of in __init__ allows the iterator to potentially be re-used
        """
        self._iter = base_chunk_entity_iterator(self._world, self._pos1, self._pos2, self._readonly)

        return self

    def __next__(self):
        """
        Iteratively identifies the next valid tile entity or regular entity and returns it.

        Return value:
            entity - the entity OR tile entity TagCompound

        This does the final check to make sure returned entities are in the bounding box
        """
        return self._iter.__next__()
