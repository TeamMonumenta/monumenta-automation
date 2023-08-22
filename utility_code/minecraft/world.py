import os
import math
from pathlib import Path
import sys
import time
import zlib

from lib_py3.common import bounded_range

from minecraft.level_dat import LevelDat
from minecraft.region import Region, EntitiesRegion, PoiRegion
from minecraft.player_dat_format.player import PlayerFile
from minecraft.util.iter_util import process_in_parallel

def _create_region_lambda(region_type, full_path, rx, rz):
    return region_type(full_path, rx, rz)

# No _finalize_region_lambda, chunks are saved as they are iterated

def _create_player_lambda(full_path):
    return PlayerFile(full_path).player

def _finalize_player_lambda(player, autosave):
    if autosave:
        player.player_file.save()

class World():
    """A Minecraft world folder."""

    def __init__(self, path, name=None):
        """Load a world from the path provided."""
        self.path = path
        self.name = name
        self._level_dat_initialized = False
        self._level_dat = None
        if self.name is None:
            self.name = os.path.basename(os.path.realpath(self.path))

    @property
    def level_dat(self):
        if self._level_dat_initialized:
            return self._level_dat
        if os.path.isfile(os.path.join(self.path, 'level.dat')):
            self._level_dat = LevelDat(os.path.join(self.path, 'level.dat'))
        self._level_dat_initialized = True
        return self._level_dat

    @classmethod
    def enumerate_worlds(cls, dir_) -> [str]:
        """Returns the full world folder path of all folders in the specified directory that contain a level.dat"""
        results = []
        for level_dat in Path(dir_).glob('**/level.dat'):
            if not level_dat.is_file():
                continue
            # TODO Return the original Path object when we're confident none of our other code will break because of it
            results.append(str(level_dat.parent))
        return results

    def defragment(self):
        for region in self.iter_regions():
            try:
                region.defragment()
            except Exception as e:
                print(f'Exception defragmenting {region!r}')
                raise

    def copy_to(self, path, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf, regenerate_uuids=True, clear_world_uuid=False, clear_score_data=True):
        os.makedirs(path)
        if self.level_dat is not None:
            self.level_dat.save(os.path.join(path, 'level.dat'))
        new_world = World(path)
        for region in self.iter_regions(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z, read_only=True):
            try:
                region.copy_to(new_world, region.rx, region.rz, clear_world_uuid=clear_world_uuid, clear_score_data=clear_score_data)
            except Exception as e:
                print(f'Exception copying {region!r}')
                raise
        return new_world

    def enumerate_regions(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf, region_types=(Region, EntitiesRegion)): # TODO: PoiRegion
        """
        Enumerates region files in this world without loading them

        Only returns regions that are within the bounds specified by min/max coordinates

        yields tuples of (full_path, rx, rz, region_type) which is what is needed to load the region file
        """
        if min_x > max_x:
            temp = min_x;
            min_x = max_x
            max_x = temp
        if min_y > max_y:
            temp = min_y;
            min_y = max_y
            max_y = temp
        if min_z > max_z:
            temp = min_z;
            min_z = max_z
            max_z = temp

        for region_type in region_types:
            subfolder = region_type.folder_name()
            region_folder = os.path.join(self.path, subfolder)
            if not os.path.isdir(region_folder):
                continue
            for filename in os.listdir(region_folder):
                filename_parts = filename.split('.')
                if (
                    len(filename_parts) != 4 or
                    filename_parts[0] != 'r' or
                    filename_parts[3] != 'mca'
                ):
                    continue

                try:
                    rx = int(filename_parts[1])
                    rz = int(filename_parts[2])
                except ValueError:
                    continue

                if (
                    512*rx + 512 <= min_x or
                    512*rx       >  max_x or
                    512*rz + 512 <= min_z or
                    512*rz       >  max_z
                ):
                    continue

                full_path = os.path.join(region_folder, filename)
                yield full_path, rx, rz, region_type

    def iter_regions(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf, read_only=False, region_types=(Region, EntitiesRegion)): # TODO: PoiRegion
        """
        Iterates region files in this world

        Only returns regions that are within the bounds specified by min/max coordinates

        returns loaded Region objects
        """

        for full_path, rx, rz, region_type in self.enumerate_regions(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z, region_types=region_types):
            yield region_type(full_path, rx, rz, read_only=read_only)

    def iter_regions_parallel(self, func, err_func, num_processes=4, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf, region_types=(Region, EntitiesRegion), additional_args=(), initializer=None, initargs=()): # TODO: PoiRegion
        """Iterates regions in parallel using multiple processes.

        func will be called with each Region object that this folder contains
        plus any arguments supplied in additional_args

        This function is a generator - values returned by func(...) will be
        yielded back to the caller as those results become available.

        For example, if there are three regions, func will be called three
        times.  If each one returns a dict, the values yielded from this
        function will be: [{}, {}, {}]

        err_func will be called with (exception, args) if an exception is
        triggered and should return an empty result of the same type as func()

        Processes are pooled such that only at most num_processes will run
        simultaneously. If num_processes is set to 0 will automatically use as
        many CPUs as are available. If num_processes is 1, will iterate
        directly and not launch any new processes, which is easier to debug.

        initializer can be set to a function that initializes any variables
        once for each process worker, which for large static arguments is much
        faster than putting them in additional_args which would copy them for
        each iteration. initializer will be called with the arguments supplied
        in init_args.
        """

        parallel_args = []
        for full_path, rx, rz, region_type in self.enumerate_regions(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z, region_types=region_types):
            parallel_args.append((_create_region_lambda, (region_type, full_path, rx, rz), None, None, func, err_func, additional_args))

        yield from process_in_parallel(parallel_args, num_processes=num_processes, initializer=initializer, initargs=initargs)

    def get_region(self, rx, rz, read_only=False, region_type=Region):
        """
        Get and return a region file of the specified type.
        If the region file does not exist, return None
        """
        rx = int(rx)
        rz = int(rz)
        full_path = os.path.join(self.path, region_type.folder_name(), f'r.{rx}.{rz}.mca')
        if not os.path.exists(full_path):
            return None
        return region_type(full_path, rx, rz, read_only=read_only)

    def enumerate_players(self):
        """
        Note: Does not return the level.dat player
        """
        for filename in os.listdir(os.path.join(self.path, 'playerdata')):
            if not filename.endswith('.dat'):
                continue

            full_path = os.path.join(self.path, 'playerdata', filename)
            if os.path.getsize(full_path) <= 0:
                continue
            yield full_path

    def iter_players(self, autosave=False):
        if self.level_dat is not None:
            yield self.level_dat.player

            if autosave:
                self.level_dat.save()

        for full_path in self.enumerate_players():
            player_file = PlayerFile(full_path)
            yield player_file.player
            if autosave:
                player_file.save()

    def iter_players_parallel(self, func, err_func, num_processes=4, autosave=False, additional_args=(), initializer=None, initargs=()):
        """Iterates players in parallel using multiple processes.

        Does **NOT** include the level.dat player

        func will be called with each Player object that this folder contains
        plus any arguments supplied in additional_args

        This function is a generator - values returned by func(...) will be
        yielded back to the caller as those results become available.

        For example, if there are three players, func will be called three
        times.  If each one returns a dict, the values yielded from this
        function will be: [{}, {}, {}]

        err_func will be called with (exception, args) if an exception is
        triggered and should return an empty result of the same type as func()

        Processes are pooled such that only at most num_processes will run
        simultaneously. If num_processes is set to 0 will automatically use as
        many CPUs as are available. If num_processes is 1, will iterate
        directly and not launch any new processes, which is easier to debug.

        initializer can be set to a function that initializes any variables
        once for each process worker, which for large static arguments is much
        faster than putting them in additional_args which would copy them for
        each iteration. initializer will be called with the arguments supplied
        in init_args.
        """

        parallel_args = []
        for full_path in self.enumerate_players():
            parallel_args.append((_create_player_lambda, (full_path,), _finalize_player_lambda, (autosave,), func, err_func, additional_args))

        yield from process_in_parallel(parallel_args, num_processes=num_processes, initializer=initializer, initargs=initargs)

    def __repr__(self):
        return f'World({self.path!r}, {self.name!r})'

    def get_block(self, pos: [int, int, int]):
        """
        Get the block at position (x, y, z).
        Example block:
        {'facing': 'north', 'waterlogged': 'false', 'name': 'minecraft:wall_sign'}

        Liquids are not yet supported

        Returns None if the region file containing the requested block does not exist
        """
        x, y, z = (int(pos[0]), int(pos[1]), int(pos[2]))
        region = self.get_region(x // 512, z // 512)
        if region is None:
            return None
        return region.get_block(pos)

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

        Returns None if the region file containing the requested block does not exist
        """
        x, y, z = (int(pos[0]), int(pos[1]), int(pos[2]))
        region = self.get_region(x // 512, z // 512)
        if region is None:
            return None
        return region.set_block(pos, block)

    def fill_blocks(self, pos1, pos2, block):
        """
        Fill the blocks from pos1 to pos2 (x, y, z).
        Example block:
        {'snowy': 'false', 'name': 'minecraft:grass_block'}

        In this version:
        - All block properties are mandatory (no defaults are filled in for you)
        - Block NBT cannot be set, but can be read.
        - Similar to the vanilla /fill command, entities are ignored.
        - Existing block NBT for the specified coordinate is cleared.
        - Liquids are not yet supported

        Will not operate on blocks that don't exist (i.e. will not create regions)
        """
        min_x = min(pos1[0], pos2[0])
        min_z = min(pos1[2], pos2[2])
        max_x = max(pos1[0], pos2[0])
        max_z = max(pos1[2], pos2[2])

        for rz in range(min_z//512, (max_z - 1)//512 + 1):
            for rx in range(min_x//512, (max_x - 1)//512 + 1):
                region = self.get_region(rx, rz)
                if region is not None:
                    region.fill_blocks(pos1, pos2, block)
