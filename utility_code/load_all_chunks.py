#!/usr/bin/env pypy3

import os
import sys
import concurrent
from minecraft.world import World
from minecraft.region import Region, EntitiesRegion

read_only = True

def process_region(arg):
    full_path, rx, rz, region_type = arg
    region = region_type(full_path, rx, rz, read_only=read_only)

    num_entities = 0
    num_block_entities = 0
    has_blocks = set()

    for chunk in region.iter_chunks(autosave = not read_only):
        # Do nothing - just loading chunks here
        pass

    print(f"Loaded all chunks for region {region}")
    return True

if __name__ == '__main__':
    args = sys.argv
    name = args.pop(0)
    if len(sys.argv) == 0:
        print("Usage: {} /path/to/world1 [/path/to/world2 ...]".format(name))
        sys.exit()

    regions = []
    all_world_paths = []
    for arg_path in args:
        for world_path in World.enumerate_worlds(arg_path):
            all_world_paths.append(world_path)

    if len(all_world_paths) <= 0:
        sys.exit("No valid worlds found to load")

    print(f"Loading all chunks from worlds:")
    for world_path in all_world_paths:
        print(f"  {world_path}")

    for world_path in all_world_paths:
        world = World(world_path)
        for full_path, rx, rz, region_type in world.enumerate_regions():
            regions.append((full_path, rx, rz, region_type))

    for region_data in regions:
        process_region(region_data)

    print(f"Done")
