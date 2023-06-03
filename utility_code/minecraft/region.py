import math
import os
import shutil
import sys
import uuid

from collections.abc import MutableMapping
from pathlib import Path

from lib_py3.common import copy_file, uuid_to_mc_uuid_tag_int_array
from lib_py3.entity_scores import set_entity_scores

from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.chunk import Chunk, EntitiesChunk, PoiChunk
from minecraft.chunk_format.entity import Entity
from minecraft.util.debug_util import NbtPathDebug

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt
from quarry.types.buffer import Buffer, BufferUnderrun


def shorten_path(path):
    if "/" in path:
        split = path.split("/")
        if len(split) >= 3:
            return "/".join(split[-3:])
    return path


def _fix_entity_nbt(dx, dz, entity, regenerate_uuids, clear_world_uuid=False):
    nbtPaths = (
        ('x', 'z'),
        ('AX', 'AZ'),
        ('APX', 'APZ'),
        ('BeamTarget.X', 'BeamTarget.Z'),
        ('BoundX', 'BoundZ'),
        ('Brain.memories.{}.value.pos[0]', 'Brain.memories.{}.value.pos[-1]'),
        ('enteredNetherPosition.x', 'enteredNetherPosition.z'),
        ('ExitPortal.X', 'ExitPortal.Z'),
        ('HomePosX', 'HomePosZ'),
        ('Leash.X', 'Leash.Z'),
        ('Pos[0]', 'Pos[2]'),
        ('SleepingX', 'SleepingZ'),
        ('SpawnX', 'SpawnZ'),
        ('TileX', 'TileZ'), # Painting/item frame
        ('TreasurePosX', 'TreasurePosZ'),
        ('TravelPosX', 'TravelPosZ'),
        ('xTile', 'zTile'),
    )

    for nbtPath in nbtPaths:
        if (
                bool(entity.count_multipath(nbtPath[0])) and
                bool(entity.count_multipath(nbtPath[1]))
        ):
            for xTag in entity.iter_multipath(nbtPath[0]):
                xTag.value += dx
            for zTag in entity.iter_multipath(nbtPath[1]):
                zTag.value += dz

    # Generate new UUIDs
    if regenerate_uuids and (entity.has_path("UUIDMost") or entity.has_path("UUIDLeast") or entity.has_path("UUID")):
        entity.value.pop("UUIDMost", None)
        entity.value.pop("UUIDLeast", None)
        entity.value["UUID"] = uuid_to_mc_uuid_tag_int_array(uuid.uuid4())

    # Clear Bukkit world UUID if set
    if clear_world_uuid:
        entity.value.pop("WorldUUIDMost", None)
        entity.value.pop("WorldUUIDLeast", None)


class BaseRegion(MutableMapping, NbtPathDebug):
    """A base region file that is common to all types"""


    def __init__(self, path, rx, rz, read_only=False):
        """Load a region file from the path provided, and allow saving."""
        self.path = path
        self.rx = rx
        self.rz = rz
        self._region = nbt.RegionFile(self.path, read_only=read_only)

        self.nbt_path_init(None, None, self, None)


    @classmethod
    def get_region_type(cls, folder_name: str) -> object:
        for region_type in (Region, EntitiesRegion, PoiRegion):
            if folder_name == region_type.folder_name():
                return region_type
        return None


    def get_debug_str(self):
        return str(self)


    def has_chunk(self, cx, cz):
        """Return True if this region contains chunk cx, cz (global coordinates)."""
        entry = self._get_entry(cx, cz) & 0xffffffff
        return self._entry_valid(entry)


    def load_chunk(self, cx, cz):
        """Return the Chunk for a given cx, cz coordinate.

        Raises KeyError if chunk is not present.
        """
        if not self.has_chunk(cx, cz):
            raise KeyError(f'Chunk {cx},{cz} not found.')

        try:
            chunk_tag = self._region.load_chunk(cx & 0x1f, cz & 0x1f)
        except Exception as ex:
            print(f"Failed to load chunk {cx},{cz} in region {self.rx},{self.rz} global coords {cx*16},{cz*16}")
            raise ex

        chunk_tag = chunk_tag.body

        if isinstance(self, Region):
            return Chunk(chunk_tag, self)
        if isinstance(self, EntitiesRegion):
            return EntitiesChunk(chunk_tag, self)
        if isinstance(self, PoiRegion):
            return PoiChunk(chunk_tag, self)
        raise Exception(f"Unable to load chunk for region of type {type(self)}")


    def save_chunk(self, chunk, cx=None, cz=None):
        """Save the Chunk at cx, cz.

        If cx, cz is not in this region, raises KeyError.
        """
        if cx is None:
            cx = chunk.cx
        if cz is None:
            cz = chunk.cz

        if cx != chunk.cx or cz != chunk.cz:
            raise NotImplementedError('Saving chunks at new coordinates not yet supported.')

        local_cx = cx - 32 * self.rx
        local_cz = cz - 32 * self.rz

        if (
                local_cx < 0 or local_cx > 31 or
                local_cz < 0 or local_cz > 31
        ):
            raise KeyError(f'Region file ({self.rx}, {self.rz}) does not contain chunk coordinate ({cx}, {cz}).')

        chunk.cx = 32 * self.rx + local_cx
        chunk.cz = 32 * self.rz + local_cz

        chunk = nbt.TagRoot.from_body(chunk.nbt)

        self._region.save_chunk(chunk)


    def delete_chunk(self, cx, cz):
        """Save the Chunk at cx, cz.

        If cx, cz is not in this region, raises KeyError.
        """
        local_cx = cx - 32 * self.rx
        local_cz = cz - 32 * self.rz

        if (
                local_cx < 0 or local_cx > 31 or
                local_cz < 0 or local_cz > 31
        ):
            raise KeyError(f'Region file ({self.rx}, {self.rz}) does not contain chunk coordinate ({cx}, {cz}).')

        self._region.delete_chunk(local_cx, local_cz)


    def defragment(self):
        """Defragments unused space in this region file"""
        self_path = Path(self.path).absolute()
        self_name = self_path.name
        parent_path = self_path.parent
        work_path = Path(str(self_path) + ".defragmenting")
        done_path = Path(str(self_path) + ".defragmented")

        # Skip ahead if resuming completed defragment job
        if not done_path.is_dir():
            # Delete partially completed work; start again
            if work_path.exists():
                shutil.rmtree(work_path)
            Path(work_path).mkdir(mode=0o755, parents=True, exist_ok=True)

            # Create copy of self without unused space
            new_path = str(work_path / self_name)
            with open(new_path, 'wb') as fp:
                fp.write(b'\x00' * 4096)
            new_region = type(self)(new_path, self.rx, self.rz)
            for chunk in self.iter_chunks():
                new_region._region.save_chunk(nbt.TagRoot.from_body(chunk.nbt))
            new_region._region.fd.close()
            del new_region

            work_path.rename(done_path)

        # Delete existing region file contents, including oversized chunk files
        for cx, cz in self.iter_chunk_coordinates():
            self.delete_chunk(cx, cz)
        self._region.close()
        self_path.unlink()

        # Move done folder contents to this directory
        for child in list(done_path.iterdir()):
            child_name = child.name
            child.rename(parent_path / child_name)
        done_path.rmdir()

        # Reopen the region file in place (this point cannot be reached in read only mode)
        self._region = nbt.RegionFile(self.path, read_only=False)


    def copy_to(self, world, rx, rz, overwrite=False, regenerate_uuids=True, clear_world_uuid=False, clear_score_data=True):
        """Copies this region file to a new location and returns that new Region

        Also fixes entity positions after copying.

        Throws an exception and does nothing if overwrite is False but the destination file exists
        """
        rx = int(rx)
        rz = int(rz)
        new_path = os.path.join(world.path, self.folder_name(), f'r.{rx}.{rz}.mca')

        if os.path.exists(new_path) and not overwrite:
            raise Exception(f"Destination region already exists: {new_path}")

        copy_file(self.path, new_path)

        # Create the same type region object as the calling class (Region, EntitiesRegion, etc.)
        return type(self)(new_path, rx, rz)


    def move_to(self, world, rx, rz, overwrite=False, clear_world_uuid=False, clear_score_data=False):
        region = self.copy_to(world, rx, rz, overwrite=overwrite, regenerate_uuids=False, clear_world_uuid=clear_world_uuid, clear_score_data=clear_score_data)
        self._region.close()
        os.remove(self.path)
        return region


    def iter_chunk_coordinates(self):
        """Iterate over chunk coordinates `tuple(cx, cz)` in this region file."""
        yield from iter(self)


    def iter_chunks(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf, autosave=False, on_exception=None):
        """Iterates chunks in this region

        on_exception(exception) can be set to a lambda that handles exceptions on chunk load or save.
        If this function is defined this iterator will not throw exceptions, it will pass them to this function (which could then itself throw the exception)
        """
        for cx, cz in self.iter_chunk_coordinates():
            if (
                    16 * cx + 16 <= min_x or
                    16 * cx > max_x or
                    16 * cz + 16 <= min_z or
                    16 * cz > max_z
            ):
                continue

            try:
                chunk = self.load_chunk(cx, cz)
            except Exception as ex:
                if on_exception is not None:
                    on_exception(ex)
                    continue

                raise ex

            yield chunk

            if autosave:
                try:
                    self.save_chunk(chunk)
                except Exception as ex:
                    if on_exception is not None:
                        on_exception(ex)
                    else:
                        raise ex


    def _get_entry(self, cx, cz):
        local_cx = cx - 32 * self.rx
        local_cz = cz - 32 * self.rz

        if (
                local_cx < 0 or local_cx > 31 or
                local_cz < 0 or local_cz > 31
        ):
            return False

        # Read extent header
        self._region.fd.seek(4 * (32 * local_cz + local_cx))
        try:
            return Buffer(self._region.fd.read(4)).unpack('I') & 0xffffffff
        except BufferUnderrun:
            return False


    def _entry_valid(self, entry):
        entry = entry & 0xffffffff
        offset, length = entry >> 8, entry & 0xff
        return offset > 0 and length > 0


    def __len__(self):
        count = 0
        self._region.fd.seek(0)
        buff = Buffer(self._region.fd.read(4096))
        for _ in range(1024):
            entry = buff.unpack('I') & 0xffffffff
            if self._entry_valid(entry):
                count += 1
        return count


    def __length_hint__(self):
        # Typical case is 1024 chunks/region, hint may be over/under actual value.
        return 1024


    def __getitem__(self, chunk_coord_pair):
        """Get a chunk using a dict-style key access, ex: `return region[(5, 4)]`."""
        cx, cz = chunk_coord_pair
        return self.load_chunk(cx, cz)


    def __setitem__(self, chunk_coord_pair, chunk):
        """Set a chunk using a dict-style key access, ex: `region[(5, 4)] = chunk`."""
        cx, cz = chunk_coord_pair
        return self.save_chunk(chunk, cx, cz)


    def __delitem__(self, chunk_coord_pair):
        """Delete a chunk using a dict-style key access, ex: `del region[(5, 4)]`."""
        cx, cz = chunk_coord_pair
        return self.delete_chunk(cx, cz)


    def __iter__(self):
        """Iterate over chunk coordinates `tuple(cx, cz)` in this region file."""
        cx_offset = 32 * self.rx
        cz_offset = 32 * self.rz

        # Load extents
        for local_cz in range(32):
            cz = cz_offset + local_cz
            for local_cx in range(32):
                cx = cx_offset + local_cx
                if self.has_chunk(cx, cz):
                    yield (cx, cz)


    def __contains__(self, chunk_coord_pair):
        """Return true if chunk_coord_pair = (cx, cz) in this region file."""
        cx, cz = chunk_coord_pair
        return self.has_chunk(cx, cz)


class Region(BaseRegion):
    """A 'region' type region file"""


    @classmethod
    def folder_name(cls):
        return "region"


    def copy_to(self, world, rx, rz, overwrite=False, regenerate_uuids=True, clear_world_uuid=False, clear_score_data=True):
        # Copy the file itself which is common to all region types
        region = super().copy_to(world, rx, rz, overwrite, regenerate_uuids, clear_score_data=clear_score_data)
        dx = (rx - self.rx) * 512
        dz = (rz - self.rz) * 512

        for chunk in region.iter_chunks(autosave=True):
            if chunk.nbt.has_path("Level"): # Versions before 1.17
                prefix = "Level."
            else: # After 1.18
                prefix = ""

            chunk.nbt.at_path(f'{prefix}xPos').value = rx * 32 + (chunk.nbt.at_path(f'{prefix}xPos').value & 0x1f)
            chunk.nbt.at_path(f'{prefix}zPos').value = rz * 32 + (chunk.nbt.at_path(f'{prefix}zPos').value & 0x1f)

            # Level.* are in 1.17 and below - block_entities is in region files in 1.18+ but Entities are not
            for path in ['Level.TileTicks', 'Level.LiquidTicks']:
                if chunk.nbt.has_path(path):
                    for entity in chunk.nbt.iter_multipath(path + '[]'):
                        _fix_entity_nbt(dx, dz, entity, regenerate_uuids=regenerate_uuids, clear_world_uuid=clear_world_uuid)

            for thing in chunk.recursive_iter_all_types():
                if isinstance(thing, BlockEntity):
                    _fix_entity_nbt(dx, dz, thing.nbt, regenerate_uuids=regenerate_uuids, clear_world_uuid=clear_world_uuid)

                if isinstance(thing, Entity):
                    _fix_entity_nbt(dx, dz, thing.nbt, regenerate_uuids=regenerate_uuids, clear_world_uuid=clear_world_uuid)

                    # Clear entity scores
                    if clear_score_data:
                        set_entity_scores(thing, {})

        return region


    def get_block(self, pos: [int, int, int]):
        """Get the block at position (x, y, z).

        Example block:
        {'facing': 'north', 'waterlogged': 'false', 'name': 'minecraft:wall_sign'}

        Liquids are not yet supported
        """
        x, z = (int(pos[0]), int(pos[2]))
        if self.rx != x // 512 or self.rz != z // 512:
            raise Exception("Coordinates don't match this region!")

        return self.load_chunk(x // 16, z // 16).get_block(pos)


    def set_block(self, pos: [int, int, int], block):
        """Set a block at position (x, y, z).

        Example block:
        {'snowy': 'false', 'name': 'minecraft:grass_block'}

        In this version:
        - All block properties are mandatory (no defaults are filled in for you)
        - Block NBT cannot be set, but can be read.
        - Existing block NBT for the specified coordinate is cleared.
        - Liquids are not yet supported
        """
        x, y, z = (int(pos[0]), int(pos[1]), int(pos[2]))
        if self.rx != x // 512 or self.rz != z // 512:
            raise Exception("Coordinates don't match this region!")

        chunk = self.load_chunk(x // 16, z // 16)
        chunk.set_block(pos, block)
        self.save_chunk(chunk)



    def fill_blocks(self, pos1, pos2, block):
        """Set a block at position (x, y, z).

        Example block:
        {'snowy': 'false', 'name': 'minecraft:grass_block'}

        In this version:
        - All block properties are mandatory (no defaults are filled in for you)
        - Block NBT cannot be set, but can be read.
        - Existing block NBT for the specified coordinate is cleared.
        - Liquids are not yet supported

        Note that if pos1 / pos2 can exceed the bounds of this region for simplicity;
        out-of-bounds blocks will not be filled
        """
        min_x = min(pos1[0], pos2[0])
        min_z = min(pos1[2], pos2[2])
        max_x = max(pos1[0], pos2[0])
        max_z = max(pos1[2], pos2[2])

        for cz in range(min(max(min_z//16, self.rz*32), (self.rz + 1)*32 - 1), min(max(max_z//16, self.rz*32), (self.rz + 1)*32 - 1) + 1):
            for cx in range(min(max(min_x//16, self.rx*32), (self.rx + 1)*32 - 1), min(max(max_x//16, self.rx*32), (self.rx + 1)*32 - 1) + 1):
                chunk = self.load_chunk(cx, cz)
                chunk.fill_blocks(pos1, pos2, block)
                self.save_chunk(chunk)


    def __repr__(self):
        return f'Region({shorten_path(self.path)!r}, {self.rx!r}, {self.rz!r})'


class EntitiesRegion(BaseRegion):
    """An 'entities' type region file"""


    @classmethod
    def folder_name(cls):
        return "entities"


    def copy_to(self, world, rx, rz, overwrite=False, regenerate_uuids=True, clear_world_uuid=False, clear_score_data=True):
        # Copy the file itself which is common to all region types
        region = super().copy_to(world, rx, rz, overwrite, regenerate_uuids)
        dx = (rx - self.rx) * 512
        dz = (rz - self.rz) * 512

        for chunk in region.iter_chunks(autosave=True):
            # entities chunk format already has relative cx/cz values, so don't need to update Position here
            # Still need to fix the entities though
            for thing in chunk.recursive_iter_all_types():
                if isinstance(thing, BlockEntity):
                    _fix_entity_nbt(dx, dz, thing.nbt, regenerate_uuids=regenerate_uuids, clear_world_uuid=clear_world_uuid)

                if isinstance(thing, Entity):
                    _fix_entity_nbt(dx, dz, thing.nbt, regenerate_uuids=regenerate_uuids, clear_world_uuid=clear_world_uuid)

                    # Clear entity scores
                    if clear_score_data:
                        set_entity_scores(thing, {})

        return region


    def __repr__(self):
        return f'EntitiesRegion({shorten_path(self.path)!r}, {self.rx!r}, {self.rz!r})'


class PoiRegion(BaseRegion):
    """An 'poi' type region file"""


    @classmethod
    def folder_name(cls):
        return "poi"


    def copy_to(self, world, rx, rz, overwrite=False, regenerate_uuids=True, clear_world_uuid=False, clear_score_data=True):
        raise NotImplementedError


    def __repr__(self):
        return f'PoiRegion({shorten_path(self.path)!r}, {self.rx!r}, {self.rz!r})'
