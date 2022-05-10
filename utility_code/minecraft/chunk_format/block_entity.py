import os
import sys

from lib_py3.common import parse_name_possibly_json
from minecraft.util.debug_util import NbtPathDebug
from minecraft.util.iter_util import RecursiveMinecraftIterator, TypeMultipathMap

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

class BlockEntity(RecursiveMinecraftIterator, NbtPathDebug):
    """An object for editing a block entity (1.13+)."""
    __CLASS_UNINITIALIZED = True
    __MULTIPATHS = TypeMultipathMap()

    def __init__(self, nbt, parent=None, data_version=None):
        """Load a block entity from an NBT tag.

        Must be saved from wherever the tag was loaded from to apply.
        path_debug is the new NbtPathDebug object for this object, missing its references to this.
        root is the base Entity, BlockEntity, or Item of this BlockEntity, which may be itself.
        """
        if type(self).__CLASS_UNINITIALIZED:
            self._init_multipaths(type(self).__MULTIPATHS)
            type(self).__CLASS_UNINITIALIZED = False
        self._multipaths = type(self).__MULTIPATHS

        self.nbt_path_init(nbt, parent, parent.root if parent is not None and parent.root is not None else self, data_version)

    def _init_multipaths(self, multipaths):
        super()._init_multipaths(multipaths)
        multipaths[Entity] |= frozenset({
            'Bees[]',
            'SpawnData',
            'SpawnData.entity',
            'SpawnPotentials[].Entity',
            'SpawnPotentials[].data.entity',
        })
        multipaths[Item] |= frozenset({
            'Book',
            'Items[]',
            'RecordItem',
        })

    def get_debug_str(self):
        name = None
        if self.nbt.has_path("CustomName"):
            name = parse_name_possibly_json(self.nbt.at_path("CustomName").value, remove_color=True)

            # Don't print names of things that are just "@" (commands do this a lot apparently)
            if name == "@":
                name = None

        return f"""{self.id.replace("minecraft:","")}{" " + " ".join(str(x) for x in self.pos) if self.pos is not None else ""}{" " + name if name is not None else ""}"""

    @property
    def id(self):
        if self.nbt.has_path("id"):
            return self.nbt.at_path("id").value
        elif self.nbt.has_path("Id"):
            return self.nbt.at_path("Id").value
        else:
            # TODO Try getting ID from parent
            return "unknown_check_parent"

    @property
    def pos(self):
        """Returns the block entity's coordinates as (x, y, z).

        >>> print(self.pos)
        (2, 63, 3)
        """
        if self.parent is not None and self.parent.pos is not None:
            return self.parent.pos

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
        if self.root is not self:
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
        return f'BlockEntity(nbt.TagCompound.from_mojangson({self.nbt.to_mojangson()!r}))'


from minecraft.chunk_format.entity import Entity
from minecraft.player_dat_format.item import Item

