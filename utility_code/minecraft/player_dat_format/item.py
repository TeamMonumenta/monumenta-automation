import os
import sys

from lib_py3.common import parse_name_possibly_json
from minecraft.util.debug_util import NbtPathDebug
from minecraft.util.iter_util import RecursiveMinecraftIterator, TypeMultipathMap

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry/brigadier.py"))
from brigadier.string_reader import StringReader

class Item(RecursiveMinecraftIterator, NbtPathDebug):
    """An item slot with optional slot ID."""
    __CLASS_UNINITIALIZED = True
    __MULTIPATHS = TypeMultipathMap()

    def __init__(self, nbt=None, parent=None, data_version=None):
        """Load an item from an NBT tag.

        Must be saved from wherever the tag was loaded from for changes to apply.
        """
        if type(self).__CLASS_UNINITIALIZED:
            self._init_multipaths(type(self).__MULTIPATHS)
            type(self).__CLASS_UNINITIALIZED = False
        self._multipaths = type(self).__MULTIPATHS

        self.nbt_path_init(nbt if nbt is not None else nbt.TagCompound({}), parent, parent.root if parent is not None and parent.root is not None else self, data_version)

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
            # Bundles
            'tag.Items[]',
        })

    def get_debug_str(self):
        name = None
        if self.nbt.has_path("tag.display.Name"):
            name = parse_name_possibly_json(self.nbt.at_path("tag.display.Name").value, remove_color=True)

        return f"""{self.id.replace("minecraft:","")}{" " + " ".join(str(round(x, 1)) for x in self.pos) if self.pos is not None else ""}{" " + name if name is not None else ""}"""

    @classmethod
    def from_command_format(cls, command, check_count=True):
        """Get an item from a command, optionally checking the count of the command."""
        if isinstance(command, str):
            command = StringReader(command)
        if not isinstance(command, StringReader):
            raise TypeError("Expected command to be type str or StringReader.")

        item = cls()
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

    @classmethod
    def from_raw_json_text_hover_event(cls, hover_event: dict):
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
        return cls(item_nbt)

    def to_raw_json_text_hover_event(self):
        return {
            "action": "show_item",
            "value": self.nbt.to_mojangson()
        }

    @classmethod
    def from_simple_loot_table_entry(cls, entry: dict, check_count: bool = True):
        id_ = None
        tag = None
        count = 1

        if not isinstance(entry, dict):
            raise TypeError("Expected loot table entry to be a dict.")
        if entry.get("type", None) not in ("minecraft:item", "item"):
            raise ValueError("Expected loot table entry to be type item.")

        id_ = entry.get("name", None)
        if not isinstance(id_, str):
            raise TypeError("Expected loot table entry name (id) to be type str")

        for function in entry.get("functions", []):
            func_type = function.get("function", None)
            if func_type in ("minecraft:set_nbt" or "set_nbt"):
                mojangson = function.get("tag", None)
                if not isinstance(mojangson, str):
                    raise TypeError("Loot table function set_nbt requiers a Mojangson string.")

                reader = StringReader(mojangson)
                tag = nbt.MojangsonParser(reader).parse_compound()
                if reader.can_read():
                    raise SyntaxError(f'Unexpected text after Mojangson in set_nbt loot table function: {reader.get_remaining()!r}')

            elif func_type in ("minecraft:set_count" or "set_count"):
                count = function.get("count", None)
                if isinstance(count, int):
                    pass
                else:
                    raise NotImplementedError(f'Unsupported set_count format: {count!r}')

            else:
                raise NotImplementedError(f'Unsupported function type {func_type!r}')

        item = cls()
        item.id = id_
        item.count = count
        if tag is not None:
            item.tag = tag
        return item

    def to_loot_table_entry(self, include_count: bool = False, weight: int = None) -> dict:
        entry = {"type": "item"}

        if weight is not None:
            entry["weight"] = int(weight)

        entry["name"] = self.id

        if self.has_tag() or include_count:
            entry["functions"] = []

            if self.has_tag():
                entry["functions"].append({
                    "function": "set_nbt",
                    "tag": self.tag.to_mojangson()
                })

            if include_count:
                entry["functions"].append({
                    "function": "set_count",
                    "count": self.count
                })

        return entry

    @classmethod
    def from_simple_item_predicate(cls, item_predicate: dict):
        """For use with advancement requirements, predicate files, etc."""
        if not isinstance(item_predicate, dict):
            raise TypeError(f'item_predicate must be type dict, not {type(item_predicate)}.')

        if "item" not in item_predicate:
            raise KeyError('item_predicate must specify "item" id.')

        item = cls()
        item.id = item_predicate["item"]
        if "nbt" in item_predicate:
            mojangson = item_predicate["nbt"]
            nbt_ = nbt.TagCompound.from_mojangson(mojangson)
            item.tag = nbt_

        return item

    def to_item_predicate(self, include_count=False):
        result = {"id": item.id}
        if self.has_tag():
            result["nbt"] = self.tag.to_mojangson()
        if include_count:
            result["count"] = self.count
        return result

    @property
    def pos(self):
        """Returns the items's coordinates as (x, y, z).

        Always the coordinates of the parent or None, items don't have a position themselves
        """
        if self.parent is not None:
            return self.parent.pos
        return None

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

    def has_tag(self):
        return self.nbt.has_path('tag')

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

    def is_damageable(self):
        if self.id in (
            "minecraft:shears",
            "minecraft:fishing_rod",
            "minecraft:carrot_on_a_stick",
            "minecraft:flint_and_steel",
            "minecraft:bow",
            "minecraft:trident",
            "minecraft:elytra",
            "minecraft:shield",
            "minecraft:crossbow",
            "minecraft:warped_fungus_on_a_stick",
        ):
            return True

        for item_type in (
            "_helmet",
            "_chestplate",
            "_leggings",
            "_boots",
            "_axe",
            "_pickaxe",
            "_shovel",
            "_hoe",
            "_sword",
        ):
            if self.id.endswith(item_type):
                return True

        return False

    def __repr__(self):
        return f'Item(nbt.TagCompound.from_mojangson({self.nbt.to_mojangson()!r}))'

from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.entity import Entity
from minecraft.util.namespace_util import NamespacedID
