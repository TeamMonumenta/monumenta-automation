#!/usr/bin/env python3
"""A library for common Minecraft recursive iteration.

Note that this class has some odd import requirements. It is the base class for BlockEntity, Entity, and Item,
but needs to internally handle those classes as they are part of a recursive data structure.

Java is good at this. Python, not so much.
In order to avoid any weird import issues, they would all need to be defined in one file, which would be really ugly.
"""

import math
import os
import sys

class TypeMultipathMap(dict):
    """A map of multipaths for each class and its superclasses."""
    def __getitem__(self, key):
        result = set()
        for superclass_, multipaths in super().items():
            if issubclass(key, superclass_):
                result |= multipaths
        return result

class RecursiveMinecraftIterator():
    """A class that may contain BlockEntity, Entity, and Item objects recursively."""
    # Python renames variables starting with __ and not ending with __ to include the class name.
    __CLASS_UNINITIALIZED = True
    __MULTIPATHS = TypeMultipathMap()

    def __init__(self):
        if type(self).__CLASS_UNINITIALIZED:
            self._init_multipaths(type(self).__MULTIPATHS)
            type(self).__CLASS_UNINITIALIZED = False
        self._multipaths = type(self).__MULTIPATHS

    def _init_multipaths(self, multipaths):
        """Add a set of multipaths for each type that may be contained within this type.

        multipaths[BlockEntity] = frozenset()
        multipaths[Entity] = frozenset()
        multipaths[Item] = frozenset()
        """

    def _local_iterator(self, class_, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        """Iterates over class_ objects directly in this object."""
        from minecraft.player_dat_format.item import Item

        check_coords = not (
            min_x == -math.inf and max_x == math.inf and
            min_y == -math.inf and max_y == math.inf and
            min_z == -math.inf and max_z == math.inf)
        root = self.root if hasattr(self, 'root') else None

        for superclass_, multipaths in self._multipaths.items():
            if issubclass(class_, superclass_):
                for multipath in multipaths:
                    for path, tag in self.nbt.iter_multipath_pair(multipath):
                        if not issubclass(class_, Item):
                            # Items never have a position, so position only needs to be checked for non-items.
                            item_path_debug = self.path_debug.get_child_debug(path, tag, tag)
                            obj = class_(tag, item_path_debug, root)
                            x, y, z = obj.pos if obj.pos is not None else (None, None, None)
                            if not check_coords or (
                                min_x <= x and x < max_x and
                                min_y <= y and y < max_y and
                                min_z <= z and z < max_z
                            ):
                                yield obj
                        elif tag.has_path('id'):
                            # Items without an ID tag are just empty slots, and can be ignored.
                            item_path_debug = self.path_debug.get_child_debug(path, tag, tag)
                            yield class_(tag, item_path_debug, root)

    def iter_all_types(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        """Iterates over all objects directly in this object."""
        from minecraft.player_dat_format.item import Item

        check_coords = not (
            min_x == -math.inf and max_x == math.inf and
            min_y == -math.inf and max_y == math.inf and
            min_z == -math.inf and max_z == math.inf)
        root = self.root if hasattr(self, 'root') else None

        for class_, multipaths in self._multipaths.items():
            for multipath in multipaths:
                for path, tag in self.nbt.iter_multipath_pair(multipath):
                    if not issubclass(class_, Item):
                        # Items never have a position, so position only needs to be checked for non-items.
                        item_path_debug = self.path_debug.get_child_debug(path, tag, tag)
                        obj = class_(tag, item_path_debug, root)
                        x, y, z = obj.pos if obj.pos is not None else (None, None, None)
                        if not check_coords or (
                            min_x <= x and x < max_x and
                            min_y <= y and y < max_y and
                            min_z <= z and z < max_z
                        ):
                            yield obj
                    elif tag.has_path('id'):
                        # Items without an ID tag are just empty slots, and can be ignored.
                        item_path_debug = self.path_debug.get_child_debug(path, tag, tag)
                        yield class_(tag, item_path_debug, root)

    def iter_block_entities(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        """Iterates over block entities directly in this object."""
        from minecraft.chunk_format.block_entity import BlockEntity
        yield from self._local_iterator(BlockEntity, min_x, min_y, min_z, max_x, max_y, max_z)

    def iter_entities(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        """Iterates over entities directly in this object."""
        from minecraft.chunk_format.entity import Entity
        yield from self._local_iterator(Entity, min_x, min_y, min_z, max_x, max_y, max_z)

    def iter_items(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        """Iterates over items directly in this object."""
        from minecraft.player_dat_format.item import Item
        yield from self._local_iterator(Item, min_x, min_y, min_z, max_x, max_y, max_z)

    def _recursive_iterator(self, class_, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        """Recursively iterates over class_ in this object."""
        if isinstance(self, class_):
            yield self

        for child in self.iter_block_entities():
            yield from child._recursive_iterator(class_, min_x, min_y, min_z, max_x, max_y, max_z)

        for child in self.iter_entities():
            yield from child._recursive_iterator(class_, min_x, min_y, min_z, max_x, max_y, max_z)

        for child in self.iter_items():
            yield from child._recursive_iterator(class_, min_x, min_y, min_z, max_x, max_y, max_z)

    def recursive_iter_all_types(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        """Recursively iterates all objects in this object."""
        yield self
        for child in self.iter_all_types():
            yield from child.recursive_iter_all_types(min_x, min_y, min_z, max_x, max_y, max_z)

    def recursive_iter_block_entities(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        """Recursively iterates over block entities in this object."""
        from minecraft.chunk_format.block_entity import BlockEntity
        yield from self._recursive_iterator(BlockEntity, min_x, min_y, min_z, max_x, max_y, max_z)

    def recursive_iter_entities(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        """Recursively iterates over entities in this object."""
        from minecraft.chunk_format.entity import Entity
        yield from self._recursive_iterator(Entity, min_x, min_y, min_z, max_x, max_y, max_z)

    def recursive_iter_items(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        """Recursively iterates over items in this object."""
        from minecraft.player_dat_format.item import Item
        yield from self._recursive_iterator(Item, min_x, min_y, min_z, max_x, max_y, max_z)

