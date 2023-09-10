#!/usr/bin/env pypy3

from datetime import datetime, timedelta
import os
import sys
import getopt
import multiprocessing
from pathlib import Path
import concurrent
import traceback
from minecraft.world import World
from lib_py3.common import eprint
from lib_py3.timing import Timings

def usage():
    """Prints usage and exits with error"""
    sys.exit(f"Usage: {sys.argv[0]} [--verbose] [--num-threads 4] /path/to/world [/path/to/parent ...]")

def disk_usage_for_path(path):
    """Gets approximate real disk usage for a path"""
    # TODO: Everything I've tried is garabage, this is definitely wrong
    # Needs replacing with a function that actually works
    return os.stat(path).st_blocks * 512

def process_region(arg):
    """Defragments a single region file"""
    full_path, rx, rz, region_type, verbose = arg
    region = region_type(full_path, rx, rz)

    if verbose:
        print("Processing ", full_path)

    try:
        initial_size = disk_usage_for_path(full_path)
        region.defragment()
        final_size = disk_usage_for_path(full_path)
    except Exception as ex:
        eprint(f"Failed to process file {full_path}: {ex}")
        eprint(traceback.format_exc())
        return (full_path, -1, -1)

    return (full_path, initial_size, final_size)

if __name__ == '__main__':
    multiprocessing.set_start_method("fork")

    try:
        opts, args = getopt.getopt(sys.argv[1:], "vj:", ["verbose", "num-threads=", ])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    num_threads = 4
    verbose = False

    for o, a in opts:
        if o in ("-j", "--num-threads"):
            num_threads = int(a)
            if num_threads < 0:
                num_threads = os.cpu_count()
        elif o in ("-v", "--verbose"):
            verbose = True
        else:
            eprint("Unknown argument: {}".format(o))
            usage()

    if len(args) < 1:
        usage()

    timings = Timings(enabled=True)

    # Decrease the priority for this work so it doesn't slow down other things
    os.nice(20)

    regions = []

    all_world_paths = []
    for arg_path in args:
        for world_path in World.enumerate_worlds(arg_path):
            all_world_paths.append(world_path)

    if len(all_world_paths) <= 0:
        sys.exit("No valid worlds found to defragment")

    print(f"Defragmenting regions from:")
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
                timings.longStep(f'{num_processed}/{num_regions} region files defragmented')
                next_update = now + timedelta(seconds=1)
    # Print new line
    print('')

    # TODO: Would be great to print these sizes but they're just wrong/misleading today. Fix the above TODO and re-enable this
    #timings.nextStep(f"Defragemented {len(regions)} regions, reducing size from {initial_size / (1024 * 1024)} MB to {final_size / (1024 * 1024)} MB")
    timings.nextStep(f"Defragemented {len(regions)} regions")
