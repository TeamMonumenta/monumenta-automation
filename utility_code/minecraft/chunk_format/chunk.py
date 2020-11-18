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

class Chunk(RecursiveMinecraftIterator):
    """A chunk, loaded from a tag."""
    __CLASS_UNINITIALIZED = True
    __MULTIPATHS = TypeMultipathMap()

    def __init__(self, nbt, path_debug):
        """Load an entity from an NBT tag.

        Must be saved from wherever the tag was loaded from to apply.
        path_debug is the new NbtPathDebug object for this object, missing its references to this.
        """
        if type(self).__CLASS_UNINITIALIZED:
            self._init_multipaths(type(self).__MULTIPATHS)
            type(self).__CLASS_UNINITIALIZED = False
        self._multipaths = type(self).__MULTIPATHS

        self.nbt = nbt
        self.path_debug = path_debug
        self.path_debug.obj = self
        self.path_debug.data_version = self.nbt.at_path('DataVersion')

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

    def __str__(self):
        return f'Chunk ({self.cx}, {self.cz})'

    def __repr__(self):
        return f'Chunk(nbt.TagCompound.from_mojangson({self.nbt.to_mojangson()!r}))'
