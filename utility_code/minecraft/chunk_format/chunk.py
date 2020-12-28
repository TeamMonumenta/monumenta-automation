#!/usr/bin/env python3

import os
import sys

from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.entity import Entity
from minecraft.util.debug_util import NbtPathDebug
from minecraft.util.iter_util import RecursiveMinecraftIterator, TypeMultipathMap
# TODO: This needs to get moved into this library
from lib_py3.block_map import block_map

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt
from quarry.types.chunk import BlockArray
# TODO Add methods for dealing with blocks, lighting, etc.
#from quarry.types.buffer import BufferUnderrun

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

        self.nbt_path_init(nbt, None, self, nbt.at_path('DataVersion').value)

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

    def get_block(self, pos: [int, int, int]):
        """
        Get the block at position (x, y, z).
        Example block:
        {'facing': 'north', 'waterlogged': 'false', 'name': 'minecraft:wall_sign'}

        Liquids are not yet supported
        """
        x, y, z = (int(pos[0]), int(pos[1]), int(pos[2]))
        # bx, by, bz are block coordinates within the chunk section
        rx, bx = divmod(x, 512)
        by = y
        rz, bz = divmod(z, 512)
        cx, bx = divmod(bx, 16)
        cy, by = divmod(by, 16)
        cz, bz = divmod(bz, 16)

        if self.cx != x // 16 or self.cz != z // 16:
            raise Exception("Coordinates don't match this chunk!")

        section_not_found = True
        for section in self.nbt.iter_multipath('Level.Sections[]'):
            if section.at_path('Y').value == cy:
                section_not_found = False
                blocks = BlockArray.from_nbt(section, block_map)
                return blocks[256 * by + 16 * bz + bx]

        if section_not_found:
            raise Exception("Chunk section not found")

    def set_block(self, pos: [int, int, int], block):
        """
        Set a block at position (x, y, z).
        Example block:
        {'snowy': 'false', 'name': 'minecraft:grass_block'}

        In this version:
        - All block properties are mandatory (no defaults are filled in for you)
        - Block NBT cannot be set, but can be read.
        - Existing block NBT for the specified coordinate is cleared.
        - Liquids are not yet supported
        """
        x, y, z = (int(pos[0]), int(pos[1]), int(pos[2]))
        # bx, by, bz are block coordinates within the chunk section
        rx, bx = divmod(x, 512)
        by = y
        rz, bz = divmod(z, 512)
        cx, bx = divmod(bx, 16)
        cy, by = divmod(by, 16)
        cz, bz = divmod(bz, 16)

        if self.cx != x // 16 or self.cz != z // 16:
            raise Exception("Coordinates don't match this chunk!")

        section_not_found = True
        for section in self.nbt.iter_multipath('Level.Sections[]'):
            if section.at_path('Y').value == cy:
                section_not_found = False
                blocks = BlockArray.from_nbt(section, block_map)
                blocks[256 * by + 16 * bz + bx] = block
                break

        if section_not_found:
            raise Exception("Chunk section not found")

