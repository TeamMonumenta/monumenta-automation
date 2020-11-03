#!/usr/bin/env python3

import os
import sys

from minecraft.util.iter_util import RecursiveMinecraftIterator, TypeMultipathMap

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt
from brigadier.string_reader import StringReader

class Item(RecursiveMinecraftIterator):
    """An item slot with optional slot ID."""
    __CLASS_UNINITIALIZED = True
    __MULTIPATHS = TypeMultipathMap()

    def __init__(self, nbt_=None, path_debug=None, root=None):
        """Load an item from an NBT tag.

        Must be saved from wherever the tag was loaded from to apply.
        path_debug is the new NbtPathDebug object for this object, missing its references to this.
        root is the base Entity, BlockEntity, or Item of this Entity, which may be itself.
        """
        if type(self).__CLASS_UNINITIALIZED:
            self._init_multipaths(type(self).__MULTIPATHS)
            type(self).__CLASS_UNINITIALIZED = False
        self._multipaths = type(self).__MULTIPATHS

        if nbt_ is None:
            nbt_ = nbt.TagCompound({})
        self.nbt = nbt_
        self.path_debug = path_debug
        self.root = root if root is not None else self
        self.root_entity = self
        if self.path_debug is not None:
            self.path_debug.obj = self
            parent = self.path_debug.parent.obj
            if isinstance(parent, (BlockEntity, Entity, Item)):
                self.root_entity = parent.root_entity
        else:
            self.root_entity = self

    def _init_multipaths(self, multipaths):
        super()._init_multipaths(multipaths)
        multipaths[BlockEntity] |= frozenset({
            'tag.BlockEntityTag',
        })
        multipaths[Entity] |= frozenset({
            'tag.EntityTag',
        })
        multipaths[Item] |= frozenset({
            # Crossbows
            'tag.ChargedProjectiles[]',
        })

    def get_legacy_debug(self):
        result = [self.nbt]
        parent = self.path_debug.parent.obj
        if isinstance(parent, (BlockEntity, Entity, Item)):
            result = parent.get_legacy_debug() + result
        return result

    @staticmethod
    def from_command_format(command, check_count=True):
        """Get an item from a command, optionally checking the count of the command."""
        if isinstance(command, str):
            command = StringReader(command)
        if not isinstance(command, StringReader):
            raise TypeError("Expected command to be type str or StringReader.")

        item = Item()
        item.id = str(NamespacedID.parse_no_separator(command))
        if command.can_read() and command.peek() == '{':
            item.tag = nbt.MojangsonParser(command).parse_compound()
        item.count = 1
        if check_count and command.can_read():
            if command.peek() != ' ':
                raise SyntaxError(f'Unexpected character {command.peek()!r}.')
            command.skip()

            # The count
            if not command.can_read():
                raise SyntaxError('Expected an item count.')
            item.count = command.read_int()

        return item

    def to_command_format(self, include_count=False, highlight=False):
        """Returns a string suitable for commands."""
        command_part = f'{self.id}{self.tag.to_mojangson(highlight=highlight)}'

        if include_count:
            if self.count is None:
                command_part += ' 1'
            else:
                command_part += f' {self.count}'

        return command_part

    @staticmethod
    def from_raw_json_text_hover_event(hover_event: dict):
        """Convert a raw json text hover event that shows an item into that item."""
        if not isinstance(hover_event, dict):
            raise TypeError('Expected hover event to be type dict.')

        if "action" not in hover_event:
            raise KeyError('Could not find "action" in hover event.')
        if hover_event["action"] != "show_item":
            raise KeyError('Expected hover event to be action "show_item"')

        if "value" not in hover_event:
            raise KeyError('Could not find "action" in hover event.')

        item_mojangson = hover_event["value"]
        item_nbt = nbt.TagCompound.from_mojangson(item_mojangson)
        return Item(item_nbt)

    def to_raw_json_text_hover_event(self):
        return {
            "action": "show_item",
            "value": self.nbt.to_mojangson()
        }

    @property
    def id(self):
        """Get the item ID as a string."""
        if not self.nbt.has_path('id'):
            return None
        return self.nbt.at_path('id').value

    @id.setter
    def id(self, value):
        """Set the item ID as a string."""
        if value is None:
            if self.nbt.has_path('id'):
                self.nbt.value.pop('id')
            return

        if not isinstance(value, str):
            raise TypeError('Item ID must be type str.')

        self.nbt.value['id'] = nbt.TagString(value)

    @property
    def count(self):
        """Get the item count for this slot."""
        if not self.nbt.has_path('id'):
            return 0
        if not self.nbt.has_path('Count'):
            return 1
        return self.nbt.at_path('Count').value

    @count.setter
    def count(self, value):
        """Set the item count for this slot."""
        if not isinstance(value, int):
            raise TypeError('Item count must be type int.')
        if value < 0:
            raise ValueError('Item count may not be negative.')
        if value > 64:
            raise ValueError('Item count may not be greater than 64.')

        if value == 0:
            self.nbt.clear()
            return

        self.nbt.value['Count'] = nbt.TagByte(value)

    @property
    def tag(self):
        """Get the tag of an item."""
        if not self.nbt.has_path('tag'):
            return nbt.TagCompound({})
        return self.nbt.at_path('tag')

    @tag.setter
    def tag(self, value):
        """Set the tag of an item."""
        if value is None:
            if self.nbt.has_path('tag'):
                self.nbt.value.pop('tag')
            return

        if not isinstance(value, nbt.TagCompound):
            raise TypeError('Item tag must be type TagCompound.')

        self.nbt.value['tag'] = value

    @property
    def slot(self):
        """Get the slot ID for this slot."""
        if not self.nbt.has_path('Slot'):
            return None
        return self.nbt.at_path('Slot').value

    @slot.setter
    def slot(self, value):
        """Set the slot ID for this slot."""
        if value is None:
            if self.nbt.has_path('Slot'):
                self.nbt.value.pop('Slot')
            return

        if not isinstance(value, int):
            raise TypeError('Item slot ID must be type int.')

        self.nbt.value['Slot'] = nbt.TagByte(value)

    def __repr__(self):
        return f'Item(nbt.TagCompound.from_mojangson({self.nbt.to_mojangson()}))'

from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.entity import Entity
from minecraft.util.namespace_util import NamespacedID

