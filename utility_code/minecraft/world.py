#!/usr/bin/env python3

import os
import sys
import time
import zlib

from minecraft.level_dat import LevelDat
from minecraft.region import Region
from minecraft.player_dat_format.player import PlayerFile
from minecraft.util.debug_util import NbtPathDebug

class World():
    """A Minecraft world folder."""

    def __init__(self, path, name=None):
        """Load a world from the path provided."""
        self.path = path
        self.name = name
        if self.name is None:
            self.name = os.path.basename(os.path.realpath(self.path))
        self.path_debug = NbtPathDebug(f'file://{os.path.realpath(self.path)}', self, self, f'"World {self.name}"')
        if os.path.exists(os.path.join(self.path, 'level.dat')):
            self.level_dat = LevelDat(os.path.join(self.path, 'level.dat'))
        else:
            self.level_dat = None

    def iter_regions(self):
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

            full_path = os.path.join(region_folder, filename)
            yield Region(full_path, rx, rz)

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
