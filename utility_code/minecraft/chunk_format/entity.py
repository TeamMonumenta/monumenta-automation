#!/usr/bin/env python3

import os
import sys

from lib_py3.common import eprint

from minecraft.util.iter_util import RecursiveMinecraftIterator, TypeMultipathMap

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

class Entity(RecursiveMinecraftIterator):
    """An object for editing an entity (1.13+)."""
    __CLASS_UNINITIALIZED = True
    __MULTIPATHS = TypeMultipathMap()

    def __init__(self, nbt, path_debug=None, root=None):
        """Load an entity from an NBT tag.

        Must be saved from wherever the tag was loaded from to apply.
        path_debug is the new NbtPathDebug object for this object, missing its references to this.
        root is the base Entity, BlockEntity, or Item of this Entity, which may be itself.
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
            # Entities
            'Passengers[]',

            # Spawner minecarts
            'SpawnData',
            'SpawnPotentials[].Entity',
        })
        multipaths[Item] |= frozenset({
            # Mobs (common)
            'ArmorItems[]',
            'HandItems[]',

            # Horses and similar
            'ArmorItem',
            'SaddleItem',

            # Llamas
            'DecorItem',

            # Villagers
            'Offers.Recipes[].buy',
            'Offers.Recipes[].buyB',
            'Offers.Recipes[].sell',

            # Misc Entities
            'Item',
            'Items[]',
            'Inventory[]',
            'Trident',
            'FireworksItem',
        })

    def get_legacy_debug(self):
        result = [self.nbt]
        if self.path_debug.parent is not None:
            parent = self.path_debug.parent.obj
            if isinstance(parent, (BlockEntity, Entity, Item)):
                result = parent.get_legacy_debug() + result

        return result

    @property
    def uuid(self):
        """Returns UUID or None for any entity with a UUID, including 1.16"""
        if self.nbt.has_path("UUIDMost") and self.nbt.has_path("UUIDLeast"):
            result = uuid_util.from_tag_most_least(self.nbt.at_path("UUIDMost"), self.nbt.at_path("UUIDLeast"))
            if result is not None:
                return result

        if self.nbt.has_path("UUID"):
            result = uuid_util.from_tag_int_array(self.nbt.at_path("UUID"))
            if result is not None:
                return result

        return None

    @uuid.setter
    def uuid(self, value, data_version=2230):
        """Sets the UUID of this entity.

        data_version is the version ID for data files from vanilla.
        """
        if value is None:
            if self.nbt.has_path("UUID"):
                self.nbt.value.pop("UUID")
            if self.nbt.has_path("UUIDMost"):
                self.nbt.value.pop("UUIDMost")
            if self.nbt.has_path("UUIDLeast"):
                self.nbt.value.pop("UUIDLeast")
            return

        if data_version >= 2515:
            # Use int array tag, 1.16
            self.nbt.value["UUID"] = uuid_util.to_tag_int_array(value)
        elif self.nbt.has_path("UUID"):
            # Use int array tag, 1.16
            eprint(f"WARNING! Version incorrectly set in {os.path.realpath(__file__)}. Assuming 1.16+!")
            self.nbt.value["UUID"] = uuid_util.to_tag_int_array(value)
        else:
            # Use most/least tags, 1.15.2 or earlier
            tags = uuid_util.to_tag_most_least(value)
            self.nbt.value["UUIDMost"] = tags["most"]
            self.nbt.value["UUIDLeast"] = tags["least"]

    def new_uuid(self):
        """Give this entity a new random UUID."""
        self.uuid = uuid_util.generate()

    @property
    def pos(self):
        """Returns the entity's coordinates as (x, y, z).

        >>> print(self.pos)
        (2.71817181, 63.5, 3.1415)
        """
        if self.root_entity is not self:
            return self.root_entity.pos

        elif self.nbt.has_path('Pos'):
            x = self.nbt.at_path('Pos[0]').value
            y = self.nbt.at_path('Pos[1]').value
            z = self.nbt.at_path('Pos[2]').value

            return (x, y, z)

        else:
            return None

    @pos.setter
    def pos(self, pos):
        """Set the entity's coordinates to pos=[x, y, z].

        If this is not a root entity, this method does nothing.

        >>> self.pos = [2.71817181, 63.5, 3.1415]
        """
        if self.root_entity is not self:
            return
        elif len(pos) != 3:
            raise IndexError('pos must have 3 entries; x, y, z')

        elif self.nbt.has_path('Pos'):
            for i in range(3):
                self.nbt.at_path(f'Pos[{i}]').value = pos[i]

        else:
            return

    @property
    def rotation(self):
        """Returns the entity's rotation as [yaw, pitch]

        >>> print(self.rotation)
        [180.0, 45.0]
        """
        yaw = self.nbt.at_path('Rotation[0]').value
        pitch = self.nbt.at_path('Rotation[1]').value

        return [yaw, pitch]

    @rotation.setter
    def rotation(self, rotation):
        """Set the entity's rotation to rotation=[yaw, pitch]

        >>> self.rotation = [180.0, 45.0]
        """
        if len(rotation) != 2:
            raise IndexError('rotation must have 2 entries; yaw, pitch')
        for i in range(2):
            self.nbt.at_path(f'Rotation[{i}]').value = rotation[i]

    @property
    def motion(self):
        """Returns the entity's motion as [x, y, z]

        >>> print(self.motion)
        [0.7, -1.5, 0.3]
        """
        x = self.nbt.at_path('Motion[0]').value
        y = self.nbt.at_path('Motion[1]').value
        z = self.nbt.at_path('Motion[2]').value

        return [x, y, z]

    @motion.setter
    def motion(self, motion):
        """Set the entity's coordinates to motion=[x, y, z]

        >>> self.motion = [0.7, -1.5, 0.3]
        """
        if len(motion) != 3:
            raise IndexError('motion must have 3 entries; x, y, z')
        for i in range(3):
            self.nbt.at_path('Motion[{i}]').value = motion[i]

    @property
    def tags(self):
        """Returns the entity's tags as a list of strings

        >>> print(self.tags)
        ["TagA", "TagB"]
        """
        result = []
        if self.nbt.has_path('Tags'):
            for tag in self.nbt.iter_multipath('Tags[]'):
                result.append(tag.value)

        return result

    @tags.setter
    def tags(self, tags):
        """Replace the entity's tags with a list of strings

        >>> self.tags = ["TagA", "TagB"]
        """
        self.nbt.value['Tags'] = nbt.TagList([])
        result = self.nbt.at_path('Tags').value
        for tag in tags:
            result.append(nbt.TagString(tag))

    def modify_tags(self, tags):
        """Add and remove tags more like the in-game "/tags" command.

        Will not duplicate tags or throw errors for valid tags.

        >>> self.modify_tags("!DeletedTag")
        >>> self.modify_tags("NewTag")
        >>> self.modify_tags(["!DeletedTag", "NewTag", "AlsoNew"])
        """
        if isinstance(tags, str):
            tags = [tags]

        result = self.tags

        for tag in tags:
            if tag.startswith('!'):
                tag = tag[1:]
                if tag in result:
                    result.remove(tag)
            else:
                if tag not in result:
                    result.append(tag)

        self.tags = result

    def __repr__(self):
        return f'Entity(nbt.TagCompound.from_mojangson({self.nbt.to_mojangson()!r}))'


from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.player_dat_format.item import Item
from minecraft.util import uuid_util

