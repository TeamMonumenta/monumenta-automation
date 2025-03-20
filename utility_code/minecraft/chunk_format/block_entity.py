import json
import math
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))

from lib_py3.common import parse_name_possibly_json
from minecraft.util.debug_util import NbtPathDebug
from minecraft.util.iter_util import RecursiveMinecraftIterator, TypeMultipathMap

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
            'item', # Decorated pots
            'Items[]',
            'RecordItem',
        })

    def yield_wallet_block(self):
        if self.nbt.has_path('PublicBukkitValues."monumenta:wallet_block"'):
            json_str = self.nbt.at_path('PublicBukkitValues."monumenta:wallet_block"').value

            json_data = None
            try:
                json_data = json.loads(json_str)
            except Exception:
                return

            from lib_py3.plugin_data import MonumentaWallet
            yield MonumentaWallet(json_data, self)

            json_str = json.dumps(json_data, ensure_ascii=False)

            self.nbt.at_path('PublicBukkitValues."monumenta:wallet_block"').value = json_str

    def iter_all_types(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        yield from super().iter_all_types(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z)

        for wallet_block in self.yield_wallet_block():
            yield from wallet_block.iter_all_types()

    def iter_items(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        yield from super().iter_items(min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf)

        for wallet_block in self.yield_wallet_block():
            yield from wallet_block.iter_items()

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
        if self.nbt.has_path("Id"):
            return self.nbt.at_path("Id").value

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

        if self.nbt.has_path('x') and self.nbt.has_path('y') and self.nbt.has_path('z'):
            x = self.nbt.at_path('x').value
            y = self.nbt.at_path('y').value
            z = self.nbt.at_path('z').value

            return (x, y, z)

        return None

    @pos.setter
    def pos(self, pos):
        """Set the block entity's coordinates to pos=[x, y, z].

        If this is not a root block entity, this method does nothing.

        >>> self.pos = [2, 63, 3]
        """
        if self.root is not self:
            return

        if len(pos) != 3:
            raise IndexError('pos must have 3 entries; x, y, z')

        if self.nbt.has_path('x') and self.nbt.has_path('y') and self.nbt.has_path('z'):
            self.nbt.at_path('x').value = pos[0]
            self.nbt.at_path('y').value = pos[1]
            self.nbt.at_path('z').value = pos[2]

        else:
            return

    def __repr__(self):
        return f'BlockEntity(nbt.TagCompound.from_mojangson({self.nbt.to_mojangson()!r}))'


from minecraft.chunk_format.entity import Entity
from minecraft.player_dat_format.item import Item

