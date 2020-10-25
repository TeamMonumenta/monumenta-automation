#!/usr/bin/env python3

import os
import sys

from minecraft.util.iter_util import RecursiveMinecraftIterator, TypeMultipathMap

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

class BlockEntity(RecursiveMinecraftIterator):
    """An object for editing a block entity (1.13+)."""
    __CLASS_UNINITIALIZED = True
    __MULTIPATHS = TypeMultipathMap()

    def __init__(self, nbt, path_debug=None, root=None):
        """Load a block entity from an NBT tag.

        Must be saved from wherever the tag was loaded from to apply.
        path_debug is the new NbtPathDebug object for this object, missing its references to this.
        root is the base Entity, BlockEntity, or Item of this BlockEntity, which may be itself.
        """
        if type(self).__CLASS_UNINITIALIZED:
            self._init_multipaths(type(self).__MULTIPATHS)
            type(self).__CLASS_UNINITIALIZED = False
        self._multipaths = type(self).__MULTIPATHS

        self.nbt = nbt
        self.path_debug = path_debug
        if self.path_debug is not None:
            self.path_debug.obj = self
        self.root = root if root is not None else self
        self.root_entity = self
        parent = self.path_debug.parent.obj
        if isinstance(parent, (BlockEntity, Entity, Item)):
            self.root_entity = parent.root_entity

    def _init_multipaths(self, multipaths):
        super()._init_multipaths(multipaths)
        multipaths[Entity] |= frozenset({
            'Bees[]',
            'SpawnData',
            'SpawnPotentials[]',
        })
        multipaths[Item] |= frozenset({
            'Book',
            'Items[]',
            'RecordItem',
        })

    def get_legacy_debug(self):
        result = [self.nbt]
        parent = self.path_debug.parent.obj
        if isinstance(parent, (BlockEntity, Entity, Item)):
            result = parent.get_legacy_debug() + result
        return result

    @property
    def pos(self):
        """Returns the block entity's coordinates as (x, y, z).

        >>> print(self.pos)
        (2, 63, 3)
        """
        if self.root_entity is not self:
            return self.root_entity.pos

        elif self.nbt.has_path('x') and self.nbt.has_path('y') and self.nbt.has_path('z'):
            x = self.nbt.at_path('x').value
            y = self.nbt.at_path('y').value
            z = self.nbt.at_path('z').value

            return (x, y, z)

        else:
            return None

    @pos.setter
    def pos(self, pos):
        """Set the block entity's coordinates to pos=[x, y, z].

        If this is not a root block entity, this method does nothing.

        >>> self.pos = [2, 63, 3]
        """
        if self.root_entity is not self:
            return
        elif len(pos) != 3:
            raise IndexError('pos must have 3 entries; x, y, z')

        elif self.nbt.has_path('x') and self.nbt.has_path('y') and self.nbt.has_path('z'):
            self.nbt.at_path('x').value = pos[0]
            self.nbt.at_path('y').value = pos[1]
            self.nbt.at_path('z').value = pos[2]

        else:
            return

    def __repr__(self):
        return f'Entity(nbt.TagCompound.from_mojangson({self.nbt.to_mojangson()}))'


from minecraft.chunk_format.entity import Entity
from minecraft.player_dat_format.item import Item

