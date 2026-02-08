#!/usr/bin/env python3

"""List items and loot tables in a world, with an optional search area."""

import argparse
import math
import sys
from collections import Counter
from pathlib import Path

from lib_py3.common import eprint

from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.entity import Entity
from minecraft.player_dat_format.item import Item
from minecraft.world import World

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('world', type=Path, help="A world folder")
    arg_parser.add_argument('x1', type=int, nargs='?')
    arg_parser.add_argument('y1', type=int, nargs='?')
    arg_parser.add_argument('z1', type=int, nargs='?')
    arg_parser.add_argument('x2', type=int, nargs='?')
    arg_parser.add_argument('y2', type=int, nargs='?')
    arg_parser.add_argument('z2', type=int, nargs='?')

    args = arg_parser.parse_args()

    if not args.world.is_dir():
        arg_parser.error('world must be a path to a world folder')
        sys.exit()

    min_x = -math.inf
    min_y = -math.inf
    min_z = -math.inf
    max_x = math.inf
    max_y = math.inf
    max_z = math.inf
    if args.x1 is not None:
        if args.z2 is None:
            arg_parser.error('coordinates must either fully set or fully unset')
            sys.exit()

        min_x = min(args.x1, args.x2)
        min_y = min(args.y1, args.y2)
        min_z = min(args.z1, args.z2)
        max_x = max(args.x1, args.x2)
        max_y = max(args.y1, args.y2)
        max_z = max(args.z1, args.z2)

    print(f"Scanning {min_x} {min_y} {min_z} {max_x} {max_y} {max_z}")

    if max_x is not None:
        max_x += 1
        max_y += 1
        max_z += 1

    found_items = False
    world = World(str(args.world))
    for region in world.iter_regions(min_x, min_y, min_z, max_x, max_y, max_z, read_only=True):
        for chunk in region.iter_chunks(min_x, min_y, min_z, max_x, max_y, max_z):
            for item in chunk.recursive_iter_items(min_x, min_y, min_z, max_x, max_y, max_z):
                if item.pos is None:
                    continue
                x, y, z = item.pos
                if 'valley' in str(args.world):
                    if 1136 <= x and 0 <= y and 2560 <= z and x <= 1279 and y <= 127 and z <= 2815:
                        # /warp items
                        continue
                if 'isles' in str(args.world):
                    if 1136 <= x and 0 <= y and 2560 <= z and x <= 1279 and y <= 127 and z <= 2815:
                        # /warp items
                        continue
                if item.nbt.has_path('tag.Monumenta.Tier'):
                    if item.nbt.at_path('tag.Monumenta.Tier').value == "legacy":
                        print(item.get_debug_str())
                        found_items = True

    if not found_items:
        print("No legacy items found.")
