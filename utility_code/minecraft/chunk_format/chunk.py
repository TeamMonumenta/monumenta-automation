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
from quarry.types import nbt
from quarry.types.chunk import BlockArray


def _entity_coordinates_failed_check(entity_data, min_x, min_y, min_z, max_x, max_y, max_z, inside_is_bad):
    x = None
    if entity_data.has_path('x'):
        x = entity_data.at_path('x').value
    elif entity_data.has_path('Pos[0]'):
        x = entity_data.at_path('Pos[0]').value
    else:
        return True

    y = None
    if entity_data.has_path('y'):
        y = entity_data.at_path('y').value
    elif entity_data.has_path('Pos[1]'):
        y = entity_data.at_path('Pos[1]').value
    else:
        return True

    z = None
    if entity_data.has_path('z'):
        z = entity_data.at_path('z').value
    elif entity_data.has_path('Pos[2]'):
        z = entity_data.at_path('Pos[2]').value
    else:
        return True

    if (
            x <= min_x and x < max_x and
            y <= min_y and y < max_y and
            z <= min_z and z < max_z
    ):
        return inside_is_bad

    return not inside_is_bad


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
        super().__init__()
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


    def copy_from_bounding_box(self, src_chunk, min_x, min_y, min_z, max_x, max_y, max_z, src_x, src_y, src_z, fix_entity_nbt_function, regenerate_uuids=True, clear_world_uuid=False, clear_score_data=True):
        pass


    def _copy_entity_list_from_bounding_box(
            self, entity_list_path, src_chunk,
            min_x, min_y, min_z,
            max_x, max_y, max_z,
            src_x, src_y, src_z,
            fix_entity_nbt_function, regenerate_uuids=True,
            clear_world_uuid=False, clear_score_data=False
    ):
        dx = min_x - src_x
        dy = min_y - src_y
        dz = min_z - src_z

        src_max_x = max_x - dx
        src_max_y = max_y - dy
        src_max_z = max_z - dz

        dst_new_entities = []

        if self.nbt.has_path(entity_list_path):
            for entity_data in self.nbt.at_path(entity_list_path).value:
                if _entity_coordinates_failed_check(
                        entity_data,
                        min_x,
                        min_y,
                        min_z,
                        max_x,
                        max_y,
                        max_z,
                        True
                ):
                    continue

                dst_new_entities.append(entity_data)

        if src_chunk.nbt.has_path(entity_list_path):
            for entity_data in src_chunk.nbt.at_path(entity_list_path).value:
                if _entity_coordinates_failed_check(
                        entity_data,
                        src_x,
                        src_y,
                        src_z,
                        src_max_x,
                        src_max_y,
                        src_max_z,
                        False
                ):
                    continue

                entity_data = entity_data.deep_copy()
                if clear_score_data:
                    from lib_py3.entity_scores import set_entity_scores
                    entity = Entity(entity_data, self, self.root)
                    set_entity_scores(entity, {})
                    entity_data = entity.nbt
                fix_entity_nbt_function(
                    dx,
                    dz,
                    entity_data,
                    regenerate_uuids=regenerate_uuids,
                    clear_world_uuid=clear_world_uuid,
                    dy=dy
                )
                dst_new_entities.append(entity_data)

        self.nbt.value[entity_list_path] = nbt.TagList(dst_new_entities)


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


    def copy_from_bounding_box(self, src_chunk, min_x, min_y, min_z, max_x, max_y, max_z, src_x, src_y, src_z, fix_entity_nbt_function, regenerate_uuids=True, clear_world_uuid=False, clear_score_data=True):
        super().copy_from_bounding_box(src_chunk, min_x, min_y, min_z, max_x, max_y, max_z, src_x, src_y, src_z, fix_entity_nbt_function, regenerate_uuids=regenerate_uuids, clear_world_uuid=clear_world_uuid, clear_score_data=clear_score_data)
        dx = min_x - src_x
        dy = min_y - src_y
        dz = min_z - src_z

        for dst_bx in range(int(min_x), int(max_x)):
            src_bx = dst_bx - dx
            for dst_bz in range(int(min_z), int(max_z)):
                src_bz = dst_bz - dz
                for dst_by in range(int(min_y), int(max_y)):
                    src_by = dst_by - dy

                    src_coord = (src_bx, src_by, src_bz)
                    dst_coord = (dst_bx, dst_by, dst_bz)

                    block = src_chunk.get_block(src_coord)
                    self.set_block(dst_coord, block)

        self._copy_entity_list_from_bounding_box(
            'block_entities', src_chunk,
            min_x, min_y, min_z,
            max_x, max_y, max_z,
            src_x, src_y, src_z,
            fix_entity_nbt_function, regenerate_uuids=regenerate_uuids,
            clear_world_uuid=clear_world_uuid, clear_score_data=False
        )
        self._copy_entity_list_from_bounding_box(
            'fluid_ticks', src_chunk,
            min_x, min_y, min_z,
            max_x, max_y, max_z,
            src_x, src_y, src_z,
            fix_entity_nbt_function, regenerate_uuids=regenerate_uuids,
            clear_world_uuid=clear_world_uuid, clear_score_data=False
        )
        self._copy_entity_list_from_bounding_box(
            'block_ticks', src_chunk,
            min_x, min_y, min_z,
            max_x, max_y, max_z,
            src_x, src_y, src_z,
            fix_entity_nbt_function, regenerate_uuids=regenerate_uuids,
            clear_world_uuid=clear_world_uuid, clear_score_data=False
        )


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
            rx = min_x // 512
            rz = min_z // 512
            raise KeyError(f'Could not find cy={required_sections_left} in chunk {self.cx},{self.cz} of region file {rx},{rz} in world {self.region.path}')


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


    def copy_from_bounding_box(self, src_chunk, min_x, min_y, min_z, max_x, max_y, max_z, src_x, src_y, src_z, fix_entity_nbt_function, regenerate_uuids=True, clear_world_uuid=False, clear_score_data=True):
        super().copy_from_bounding_box(src_chunk, min_x, min_y, min_z, max_x, max_y, max_z, src_x, src_y, src_z, fix_entity_nbt_function, regenerate_uuids=regenerate_uuids, clear_world_uuid=clear_world_uuid, clear_score_data=clear_score_data)
        self._copy_entity_list_from_bounding_box(
            'Entities', src_chunk,
            min_x, min_y, min_z,
            max_x, max_y, max_z,
            src_x, src_y, src_z,
            fix_entity_nbt_function, regenerate_uuids=regenerate_uuids,
            clear_world_uuid=clear_world_uuid, clear_score_data=clear_score_data
        )


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

    def copy_from_bounding_box(self, src_chunk, min_x, min_y, min_z, max_x, max_y, max_z, src_x, src_y, src_z, fix_entity_nbt_function, regenerate_uuids=True, clear_world_uuid=False, clear_score_data=True):
        raise NotImplementedError
