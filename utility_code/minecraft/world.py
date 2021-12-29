import os
import sys
import time
import zlib
import math
import concurrent.futures

from lib_py3.common import bounded_range

from minecraft.level_dat import LevelDat
from minecraft.region import Region, EntitiesRegion, PoiRegion
from minecraft.player_dat_format.player import PlayerFile

# This wraps the callback for iter_regions_parallel so that the region
# files themselves are loaded by the process that will work on them.
# Calling the callback directly would force the caller to handle instantiating
# the region files, and it isn't possible to copy a loaded Region file across
# processes so it has to be loaded afterwards
def _parallel_region_wrapper(parallel_arg):
    full_path, rx, rz, func, region_type, additional_args = parallel_arg
    return func(*((region_type(full_path, rx, rz),) + additional_args))

# This wraps the callback for iter_players_parallel so that the player
# files themselves are loaded by the process that will work on them.
# Calling the callback directly would force the caller to handle instantiating
# the player files, and it isn't possible to copy a loaded player file across
# processes so it has to be loaded afterwards
def _parallel_player_wrapper(parallel_arg):
    full_path, autosave, func, err_func, additional_args = parallel_arg
    try:
        player_file = PlayerFile(full_path)
        result = func(*((player_file.player,) + additional_args))
        if autosave:
            player_file.save()
    except Exception as ex:
        result = err_func(ex)
    return result

class World():
    """A Minecraft world folder."""

    def __init__(self, path, name=None):
        """Load a world from the path provided."""
        self.path = path
        self.name = name
        if self.name is None:
            self.name = os.path.basename(os.path.realpath(self.path))
        if os.path.exists(os.path.join(self.path, 'level.dat')):
            self.level_dat = LevelDat(os.path.join(self.path, 'level.dat'))
        else:
            self.level_dat = None

    @classmethod
    def enumerate_worlds(cls, dir) -> [str]:
        """Returns the folder/world names of all folders in the specified directory that contain a level.dat"""
        if not os.path.isdir(dir):
            return []
        return [o for o in os.listdir(dir)
                    if os.path.isdir(os.path.join(dir,o)) and os.path.isfile(os.path.join(dir, o, "level.dat"))]

    def copy_to(self, path, regenerate_uuids=True):
        os.makedirs(path)
        self.level_dat.save(os.path.join(path, 'level.dat'))
        new_world = World(path)
        for region in self.iter_regions():
            region.copy_to(new_world, region.rx, region.rz)
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

    def iter_regions_parallel(self, func, num_processes=4, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf, region_types=(Region, EntitiesRegion), additional_args=(), initializer=None, initargs=()): # TODO: PoiRegion
        """
        Iterates regions in parallel using multiple processes.

        func will be called with each Region object that this world contains.

        Any value returned by that function will be collected into a list and
        returned to the caller. For example, if there are three regions, func
        will be called three times. If each one returns a dict, the return value
        from this function will be: [{}, {}, {}]

        Processes are pooled such that only at most num_processes will run
        simultaneously

        Set num_processes to 1 for debugging to invoke the function without creating a new process
        """

        if num_processes == 1:
            # Don't bother with processes if only going to use one
            # This makes debugging much easier
            retval = []
            for region in self.iter_regions(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z, region_types=region_types):
                retval.append(func(*((region,) + additional_args)))
            return retval
        else:
            region_list = []
            for full_path, rx, rz, region_type in self.enumerate_regions(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z, region_types=region_types):
                region_list.append((full_path, rx, rz, func, region_type, additional_args))

            if len(region_list) > 0:
                with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes, initializer=initializer, initargs=initargs) as pool:
                    return pool.map(_parallel_region_wrapper, region_list)

    def get_region(self, rx, rz, read_only=False, region_type=Region):
        rx = int(rx)
        rz = int(rz)
        full_path = os.path.join(self.path, region_type.folder_name(), f'r.{rx}.{rz}.mca')
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
        """
        Iterates players in parallel using multiple processes.

        Does **NOT** include the level.dat player

        func will be called with each Player object that this world contains.

        Any value returned by that function will be collected into a list and
        returned to the caller. For example, if there are three players, func
        will be called three times. If each one returns a dict, the return value
        from this function will be: [{}, {}, {}]

        Processes are pooled such that only at most num_processes will run
        simultaneously

        Set num_processes to 1 for debugging to invoke the function without creating a new process
        """
        if num_processes == 1:
            # Don't bother with processes if only going to use one
            # This makes debugging much easier
            retval = []
            for player in self.iter_players(autosave=autosave):
                retval.append(func(*((player,) + additional_args)))
            return retval
        else:
            player_list = []
            for full_path in self.enumerate_players():
                player_list.append((full_path, autosave, func, err_func, additional_args))

            if len(player_list) > 0:
                with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes, initializer=initializer, initargs=initargs) as pool:
                    return pool.map(_parallel_player_wrapper, player_list)

    def __repr__(self):
        return f'World({self.path!r}, {self.name!r})'

    def get_block(self, pos: [int, int, int]):
        """
        Get the block at position (x, y, z).
        Example block:
        {'facing': 'north', 'waterlogged': 'false', 'name': 'minecraft:wall_sign'}

        Liquids are not yet supported
        """
        x, y, z = (int(pos[0]), int(pos[1]), int(pos[2]))
        return self.get_region(x // 512, z // 512).get_block(pos)

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
        return self.get_region(x // 512, z // 512).set_block(pos, block)

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
        """
        min_x = min(pos1[0], pos2[0])
        min_z = min(pos1[2], pos2[2])
        max_x = max(pos1[0], pos2[0])
        max_z = max(pos1[2], pos2[2])

        for rz in range(min_z//512, (max_z - 1)//512 + 1):
            for rx in range(min_x//512, (max_x - 1)//512 + 1):
                self.get_region(rx, rz).fill_blocks(pos1, pos2, block)
