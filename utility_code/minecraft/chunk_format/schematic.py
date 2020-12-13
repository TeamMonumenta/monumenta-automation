import os
import sys

from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.entity import Entity
from minecraft.util.iter_util import RecursiveMinecraftIterator, TypeMultipathMap
from minecraft.util.debug_util import NbtPathDebug

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

class Schematic(RecursiveMinecraftIterator):
    """A schematic, loaded from an nbt file."""
    __CLASS_UNINITIALIZED = True
    __MULTIPATHS = TypeMultipathMap()

    def __init__(self, path: str, path_debug=None):
        if type(self).__CLASS_UNINITIALIZED:
            self._init_multipaths(type(self).__MULTIPATHS)
            type(self).__CLASS_UNINITIALIZED = False
        self._multipaths = type(self).__MULTIPATHS

        self.path = path
        name = os.path.basename(path)
        self._schematic_name = os.path.splitext(name)[0]

        self._nbtfile = nbt.NBTFile.load(path)
        self.nbt = self._nbtfile.root_tag

        self.path_debug = NbtPathDebug(f'file://{os.path.realpath(self.path)}', self.nbt, self, "Schematic")

    def _init_multipaths(self, multipaths):
        super()._init_multipaths(multipaths)
        multipaths[BlockEntity] |= frozenset({
            'Schematic.TileEntities[]',
            'Schematic.BlockEntities[]',
        })
        multipaths[Entity] |= frozenset({
            'Schematic.Entities[]',
        })

    @property
    def name(self):
        return self._schematic_name

    @property
    def root_tag(self):
        return self.nbt

    def __str__(self):
        return f'Schematic({self._schematic_name})'

    def __repr__(self):
        return f'Schematic(self.root_tag.to_mojangson())'

    def save(self):
        self._nbtfile.save(self.path)
