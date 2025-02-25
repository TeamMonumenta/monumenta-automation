#!/usr/bin/env pypy3
"""Removes empty chunks in region files"""

import argparse
from datetime import datetime, timedelta
import os
import sys
import multiprocessing
from pathlib import Path
import concurrent
import traceback
from minecraft.chunk_format.chunk import Chunk
from minecraft.region import Region, EntitiesRegion
from minecraft.world import World
from lib_py3.common import eprint
from lib_py3.timing import Timings

def disk_usage_for_path(path):
    """Gets approximate disk usage for a path"""
    with open(path, 'rb') as fp:
        fp.seek(0, os.SEEK_END)
        return fp.tell()

def process_chunk(region, cx, cz):
    """Checks if a chunk is empty, and if so, removes it"""
    chunk = region.load_chunk(cx, cz)

    # Check for non-blocks (really fast)
    for _ in chunk.iter_all_types():
        # Could be an entity, block entity, item, or some new thing - regardless, it's important! Don't delete!
        return

    # Check for non-air blocks
    if isinstance(chunk, Chunk):
        for section in chunk.sections:
            if not section.has_path("block_states.palette"):
                # Global palette - has lots of blocks, so we keep this
                return

            for palette_entry in section.at_path("block_states.palette").value:
                name = palette_entry.at_path("Name").value
                if name not in (
                        "minecraft:air",
                        "minecraft:cave_air",
                        "minecraft:void_air",
                ):
                    # Block is probably important - keep it
                    return

    # Empty chunk - safe to delete
    region.delete_chunk(cx, cz)

def process_region(arg):
    """Removes empty chunks a single region file"""
    full_path, rx, rz, region_type, verbose = arg
    region = region_type(full_path, rx, rz)

    if verbose:
        print("Processing ", full_path)

    try:
        initial_size = disk_usage_for_path(full_path)
        if isinstance(region, (Region, EntitiesRegion)):
            for cx, cz in list(region.iter_chunk_coordinates()):
                process_chunk(region, cx, cz)

        if len(list(region.iter_chunk_coordinates())) == 0:
            os.remove(region.path)
            final_size = 0
        else:
            region.defragment()
            final_size = disk_usage_for_path(full_path)
    except Exception as ex:
        eprint(f"Failed to process file {full_path}: {ex}")
        eprint(traceback.format_exc())
        return (full_path, -1, -1)

    return (full_path, initial_size, final_size)

if __name__ == '__main__':
    multiprocessing.set_start_method("fork")

    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('world', type=Path, nargs='+', help='A folder containing one or more worlds')
    arg_parser.add_argument('-j', '--num-threads', type=int, default=4)
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    args = arg_parser.parse_args()

    num_threads = args.num_threads
    if num_threads <= 0:
        num_threads = os.cpu_count()
    verbose = args.verbose

    timings = Timings(enabled=True)

    # Decrease the priority for this work so it doesn't slow down other things
    os.nice(20)

    regions = []

    all_world_paths = []
    for world_root_path in args.world:
        for world_path in World.enumerate_worlds(world_root_path):
            all_world_paths.append(world_path)

    if len(all_world_paths) <= 0:
        sys.exit("No valid worlds found")

    print(f"Removing empty chunks from from:")
    for world_path in all_world_paths:
        print(f"  {world_path}")

    for world_path in all_world_paths:
        world = World(world_path)
        for full_path, rx, rz, region_type in world.enumerate_regions():
            regions.append((full_path, rx, rz, region_type, verbose))

    timings.nextStep("Computed region files")

    initial_size = 0
    final_size = 0
    num_processed = 0
    num_regions = len(regions)
    next_update = datetime.now() + timedelta(seconds=1)
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_threads) as pool:
        for _, init, final in pool.map(process_region, regions):
            initial_size += init
            final_size += final
            num_processed += 1
            now = datetime.now()
            if now > next_update:
                timings.longStep(f'{num_processed}/{num_regions} region files checked')
                next_update = now + timedelta(seconds=1)
    # Print new line
    print('')

    timings.nextStep(f"Checked {len(regions)} regions, reducing size from {initial_size / (1024 * 1024)} MB to {final_size / (1024 * 1024)} MB")
