import json
import math
import os
import sys
import ctypes

# TODO: This needs to get moved into this library
from lib_py3.block_map import block_map
from lib_py3.common import bounded_range

from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.entity import Entity
from minecraft.util.debug_util import NbtPathDebug
from minecraft.util.iter_util import RecursiveMinecraftIterator, TypeMultipathMap

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types.chunk import BlockArray


class BaseChunk(RecursiveMinecraftIterator, NbtPathDebug):
    """A base chunk that is common to all types, loaded from a tag."""
    __CLASS_UNINITIALIZED = True
    __MULTIPATHS = TypeMultipathMap()


    def __init__(self, nbt, region):
        """Load an entity from an NBT tag.

        Must be saved from wherever the tag was loaded from for changes to apply.

        region should be a reference to the parent region that contains this chunk
            (which will further be of region_type region, entities, poi)
        """
        if type(self).__CLASS_UNINITIALIZED:
            self._init_multipaths(type(self).__MULTIPATHS)
            type(self).__CLASS_UNINITIALIZED = False
        self._multipaths = type(self).__MULTIPATHS

        self.region = region

        self.nbt_path_init(nbt, region, self, nbt.at_path('DataVersion').value)


    def _init_multipaths(self, multipaths):
        super()._init_multipaths(multipaths)
        multipaths[BlockEntity] |= frozenset({
            'Level.TileEntities[]',
            'block_entities[]',
        })
        multipaths[Entity] |= frozenset({
            'Level.Entities[]',
            'Entities[]',
        })


    def get_debug_str(self):
        return str(self)


    @property
    def pos(self):
        """Chunks don't return a position, even though they have one,
        because everything inside a chunk should have a position
        """
        return None


class Chunk(BaseChunk):
    """A 'region' chunk"""


    def yield_wallet_block(self):
        world_path = self.region.get_world_path()

        cx = self.cx
        cz = self.cz
        rx = cx // 32
        rz = cz // 32

        monumenta_chunk_path = world_path / 'monumenta' / f'r.{rx}.{rz}' / f'c.{cx}.{cz}'

        for wallet_block_path in monumenta_chunk_path.glob('wallet_block.*.json'):
            wallet_block_temp_path = wallet_block_path.parent / (wallet_block_path.name + '.tmp')
            json_data = None

            try:
                with open(wallet_block_path, 'r', encoding='utf-8-sig') as fp:
                    json_data = json.load(fp)
            except Exception:
                print("Error loading {!r}:".format(wallet_block_path), file=sys.stderr)
                raise

            from lib_py3.plugin_data import MonumentaWallet
            yield MonumentaWallet(json_data, self)

            try:
                with open(wallet_block_temp_path, 'w', encoding='utf-8') as fp:
                    json.dump(json_data, fp, ensure_ascii=False)

                wallet_block_path.unlink()
                wallet_block_temp_path.rename(wallet_block_path)
            except Exception:
                print("Error saving {!r}:".format(wallet_block_path), file=sys.stderr)
                raise


    def iter_all_types(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        yield from super().iter_all_types(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z)

        for wallet_block in self.yield_wallet_block():
            yield from wallet_block.iter_all_types()


    def iter_items(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        yield from super().iter_items(min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf)

        for wallet_block in self.yield_wallet_block():
            yield from wallet_block.iter_items()


    def __str__(self):
        return f'Chunk ({self.cx}, {self.cz})'


    def __repr__(self):
        return f'Chunk(nbt.TagCompound.from_mojangson({self.nbt.to_mojangson()!r}))'


    @property
    def cx(self):
        if self.nbt.has_path("Level"): # 1.17 and before
            return self.nbt.at_path('Level.xPos').value
        return self.nbt.at_path('xPos').value


    @cx.setter
    def cx(self, value):
        if self.nbt.has_path("Level"): # 1.17 and before
            self.nbt.at_path('Level.xPos').value = value
        else:
            self.nbt.at_path('xPos').value = value


    @property
    def cz(self):
        if self.nbt.has_path("Level"): # 1.17 and before
            return self.nbt.at_path('Level.zPos').value
        return self.nbt.at_path('zPos').value


    @cz.setter
    def cz(self, value):
        if self.nbt.has_path("Level"): # 1.17 and before
            self.nbt.at_path('Level.zPos').value = value
        else:
            self.nbt.at_path('zPos').value = value


    @property
    def sections(self):
        path = "sections[]"
        if self.nbt.has_path("Level"): # 1.17 and before
            path = "Level.Sections[]"
        yield from self.nbt.iter_multipath(path)


    def get_block(self, pos: [int, int, int]):
        """
        Get the block at position (x, y, z).
        Example block:
        {'facing': 'north', 'waterlogged': 'false', 'name': 'minecraft:wall_sign'}

        Liquids are not yet supported
        """
        x, y, z = (int(pos[0]), int(pos[1]), int(pos[2]))
        # bx, by, bz are block coordinates within the chunk section
        bx = x % 512
        by = y
        bz = z % 512
        bx = bx % 16
        cy, by = divmod(by, 16)
        bz = bz % 16

        if self.cx != x // 16 or self.cz != z // 16:
            raise Exception("Coordinates don't match this chunk!")

        for section in self.sections:
            if section.at_path('Y').value == cy:
                blocks = BlockArray.from_nbt(section, block_map)
                return blocks[256 * by + 16 * bz + bx]

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
        for section in self.sections:
            if section.at_path('Y').value == cy:
                section_not_found = False
                blocks = BlockArray.from_nbt(section, block_map)
                blocks[256 * by + 16 * bz + bx] = block
                break

        if section_not_found:
            raise Exception("Chunk section not found")


    def fill_blocks(self, pos1, pos2, block):
        """
        Set a block at position (x, y, z).
        Example block:
        {'snowy': 'false', 'name': 'minecraft:grass_block'}

        In this version:
        - All block properties are mandatory (no defaults are filled in for you)
        - Block NBT cannot be set, but can be read.
        - Existing block NBT for the specified coordinate is cleared.
        - Liquids are not yet supported

        Note that if pos1 / pos2 can exceed the bounds of this chunk for simplicity;
        out-of-bounds blocks will not be filled
        """
        min_x = min(pos1[0], pos2[0])
        min_y = min(pos1[1], pos2[1])
        min_z = min(pos1[2], pos2[2])
        max_x = max(pos1[0], pos2[0])
        max_y = max(pos1[1], pos2[1])
        max_z = max(pos1[2], pos2[2])

        min_cy = min_y // 16
        max_cy = max_y // 16
        required_sections_left = set(range(min_cy, max_cy + 1))

        # Handle blocks - eventually liquids, lighting, etc will be handled here too
        for section in self.sections:
            cy = section.at_path("Y").value
            if min_cy > cy or cy > max_cy:
                continue
            required_sections_left.remove(cy)
            blocks = BlockArray.from_nbt(section, block_map)

            for by in bounded_range(min_y, max_y, cy, 16):
                for bz in bounded_range(min_z, max_z, self.cz, 16):
                    for bx in bounded_range(min_x, max_x, self.cx, 16):
                        blocks[256 * by + 16 * bz + bx] = block

        if len(required_sections_left) != 0:
            rx = self.region.rx
            rz = self.region.rz
            raise KeyError(f'Could not find cy={required_sections_left} in chunk {self.cx},{self.cz} of region file {rx},{rz} in world {self.region.get_world_path()}')


class EntitiesChunk(BaseChunk):
    """An 'entities' chunk"""


    def __str__(self):
        return f'EntitiesChunk ({self.cx}, {self.cz})'


    def __repr__(self):
        return f'EntitiesChunk(nbt.TagCompound.from_mojangson({self.nbt.to_mojangson()!r}))'


    @property
    def cx(self):
        return ctypes.c_int32(self.nbt.at_path('Position').value[0]).value


    @cx.setter
    def cx(self, value):
        self.nbt.at_path('Position').value[0] = ctypes.c_uint32(value).value


    @property
    def cz(self):
        return ctypes.c_int32(self.nbt.at_path('Position').value[1]).value


    @cz.setter
    def cz(self, value):
        self.nbt.at_path('Position').value[1] = ctypes.c_uint32(value).value


class PoiChunk(BaseChunk):
    """An 'entities' chunk"""


    def __str__(self):
        return f'PoiChunk ({self.cx}, {self.cz})'


    def __repr__(self):
        return f'PoiChunk(nbt.TagCompound.from_mojangson({self.nbt.to_mojangson()!r}))'


    @property
    def cx(self):
        raise NotImplementedError


    @cx.setter
    def cx(self, value):
        raise NotImplementedError


    @property
    def cz(self):
        raise NotImplementedError


    @cz.setter
    def cz(self, value):
        raise NotImplementedError
