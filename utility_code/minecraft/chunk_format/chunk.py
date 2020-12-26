#!/usr/bin/env python3

import os
import sys

from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.entity import Entity
from minecraft.util.debug_util import NbtPathDebug
from minecraft.util.iter_util import RecursiveMinecraftIterator, TypeMultipathMap

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt
# TODO Add methods for dealing with blocks, lighting, etc.
#from quarry.types.buffer import BufferUnderrun
#from quarry.types.chunk import BlockArray

class Chunk(RecursiveMinecraftIterator, NbtPathDebug):
    """A chunk, loaded from a tag."""
    __CLASS_UNINITIALIZED = True
    __MULTIPATHS = TypeMultipathMap()

    def __init__(self, nbt):
        """Load an entity from an NBT tag.

        Must be saved from wherever the tag was loaded from for changes to apply.
        """
        if type(self).__CLASS_UNINITIALIZED:
            self._init_multipaths(type(self).__MULTIPATHS)
            type(self).__CLASS_UNINITIALIZED = False
        self._multipaths = type(self).__MULTIPATHS

        self.__init__(nbt, None, self, self.nbt.at_path('DataVersion').value)

    def _init_multipaths(self, multipaths):
        super()._init_multipaths(multipaths)
        multipaths[BlockEntity] |= frozenset({
            'Level.TileEntities[]',
        })
        multipaths[Entity] |= frozenset({
            'Level.Entities[]',
        })

    @property
    def cx(self):
        return self.nbt.at_path('Level.xPos').value

    @property
    def cz(self):
        return self.nbt.at_path('Level.zPos').value

    @property
    def pos(self):
        """Chunks don't return a position, even though they have one,
        because everything inside a chunk should have a position
        """
        return None

    def __str__(self):
        return f'Chunk ({self.cx}, {self.cz})'

    def __repr__(self):
        return f'Chunk(nbt.TagCompound.from_mojangson({self.nbt.to_mojangson()!r}))'
