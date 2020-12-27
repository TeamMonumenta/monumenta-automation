#!/usr/bin/env python3

import os
import sys
import time
import zlib
import math
import multiprocessing

from minecraft.level_dat import LevelDat
from minecraft.region import Region
from minecraft.player_dat_format.player import PlayerFile

# This wraps the callback for iter_regions_parallel so that the region
# files themselves are loaded by the process that will work on them.
# Calling the callback directly would force the caller to handle instantiating
# the region files, and it isn't possible to copy a loaded Region file across
# processes so it has to be loaded afterwards
def _parallel_region_wrapper(arg):
    full_path, rx, rz, callback = arg
    return callback(Region(full_path, rx, rz))

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

    def enumerate_regions(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        """
        Enumerates region files in this world without loading them

        Only returns regions that are within the bounds specified by min/max coordinates

        yiels tuples of (full_path, rx, rz) which is what is needed to load the region file
        """
        region_folder = os.path.join(self.path, 'region')
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
            yield full_path, rx, rz

    def iter_regions(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf):
        """
        Iterates region files in this world

        Only returns regions that are within the bounds specified by min/max coordinates

        returns loaded Region objects
        """

        for full_path, rx, rz in self.enumerate_regions(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z):
            yield Region(full_path, rx, rz)

    def iter_regions_parallel(self, func, num_processes=4):
        """
        Iterates regions in parallel using multiple processes.

        func will be called with each Region object that this world contains.

        Any value returned by that function will be collected into a list and
        returned to the caller. For example, if there are three regions, func
        will be called three times. If each one returns a dict, the return value
        from this function will be: [{}, {}, {}]

        Processes are pooled such that only at most num_processes will run
        simultaneously
        """

        region_list = []
        for full_path, rx, rz in self.enumerate_regions():
            region_list.append((full_path, rx, rz, func))

        if len(region_list) > 0:
            with multiprocessing.Pool(num_processes) as pool:
                return pool.map(_parallel_region_wrapper, region_list)

    def get_region(self, rx, rz):
        rx = int(rx)
        rz = int(rz)
        full_path = os.path.join(self.path, 'region', f'r.{rx}.{rz}.mca')
        return Region(full_path, rx, rz)

    def iter_players(self, autosave=False):
        if self.level_dat is not None:
            yield self.level_dat.player

            if autosave:
                self.level_dat.save()

        for filename in os.listdir(os.path.join(self.path, 'playerdata')):
            if not filename.endswith('.dat'):
                continue

            full_path = os.path.join(self.path, 'playerdata', filename)
            if os.path.getsize(full_path) <= 0:
                continue
            player_file = PlayerFile(full_path)
            yield player_file.player
            if autosave:
                player_file.save()

    def __repr__(self):
        return f'World({self.path!r}, {self.name!r})'
