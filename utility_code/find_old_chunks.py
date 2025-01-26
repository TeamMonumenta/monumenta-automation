#!/usr/bin/env pypy3

"""A tool to find outdated chunks

Output format is:
{
    "world/path": {
        "cx": {
            "cz": chunk_data_version
        }
    }
}
"""

import argparse
import json
import math
import multiprocessing
from pathlib import Path
import sys
import traceback

from lib_py3.common import eprint
from minecraft.world import World


min_x = min_y = min_z = -math.inf
max_x = max_y = max_z = math.inf
commands = {}


def out_region_iter(region, target_version):
    """Export commands from a region file to json

    Returns a list of command block info
    """
    out = {}
    for chunk in region.iter_chunks(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z, autosave=False):
        chunk_version = chunk.data_version
        if chunk_version < target_version:
            cx = str(chunk.cx)
            cx_contents = out.get(cx, dict())
            out[cx] = cx_contents
            cx_contents[str(chunk.cz)] = chunk.data_version

    return out


def err_func(ex, args):
    """Error handler for multiprocess code"""
    eprint(f"Caught exception: {ex}")
    eprint(f"While iterating: {args}")
    eprint(traceback.format_exc())
    return []


def parse_coordinate(coord_str):
    """Parse "x,y,z" strings into a tuple of integer coordinates"""
    try:
        result = [int(x) for x in coord_str.split(',')]
    except Exception:
        eprint('Expected x,y,z integer coordinate formatting')
        sys.exit()

    if len(result) != 3:
        eprint('Expected x,y,z coordinate formatting')
        sys.exit()

    return tuple(result)


def sort_coordinates(pos1, pos2):
    """Returns a min_pos and max_pos for a cuboid between two coordinates"""
    min_pos = []
    max_pos = []
    for i, c1 in enumerate(pos1):
        c2 = pos2[i]
        min_pos.append(min(c1, c2))
        max_pos.append(max(c1, c2))
    return tuple(min_pos), tuple(max_pos)


def export_old_chunk_versions(output_path, target_version, world_paths, min_x, min_y, min_z, max_x, max_y, max_z, num_threads):
    """Exports command blocks from a list of worlds to a json file."""
    out = {}

    for world_path in world_paths:
        world = World(world_path)
        world_results = {}
        outdated_chunk_count = 0
        for result in world.iter_regions_parallel(out_region_iter, err_func, num_processes=num_threads, read_only=True,
                                                  min_x=min_x, min_y=min_y, min_z=min_z,
                                                  max_x=max_x, max_y=max_y, max_z=max_z,
                                                  additional_args=(target_version,)):
            for cx, cz_and_version in result.items():
                cz_version_map = world_results.get(cx, dict())
                world_results[cx] = cz_version_map
                for cz, version in cz_and_version.items():
                    cz_version_map[cz] = version
                    outdated_chunk_count += 1

        print(f'{world_path}: {outdated_chunk_count} outdated chunks')
        if len(world_results) > 0:
            out[str(world_path)] = world_results

    with open(output_path, 'w') as outfile:
        json.dump(out, outfile, ensure_ascii=False, sort_keys=True, indent=2, separators=(',', ': '))

    print(f"Wrote {len(out)} worlds of outdated chunks to {output_path}")


def main():
    """Argument handling for this command block update tool"""
    multiprocessing.set_start_method("fork")

    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('output', type=Path, help='Json file to save outdated chunk locations to')
    arg_parser.add_argument('world', type=Path, nargs='+')
    arg_parser.add_argument('--target_version', type=int, default=3700, help='The data version for the target Minecraft version; see the Minecraft wiki (Default is for 1.20.4)')
    arg_parser.add_argument('--pos1', type=str, nargs='?', help='x,y,z')
    arg_parser.add_argument('--pos2', type=str, nargs='?', help='x,y,z')
    arg_parser.add_argument('-j', '--num-threads', type=int, default=4)
    args = arg_parser.parse_args()

    target_version = args.target_version
    output_path = args.output


    world_paths = []
    for worlds_path in args.world:
        for world_path in World.enumerate_worlds(worlds_path):
            world_paths.append(world_path)
    if not world_paths:
        eprint(f'No worlds found')
        sys.exit()


    pos1 = (-math.inf, -math.inf, -math.inf)
    pos2 = (math.inf, math.inf, math.inf)

    if bool(args.pos1) + bool(args.pos2) == 1:
        eprint(f'Must specify either --pos1 and --pos2, or neither')
        sys.exit()
    elif args.pos1:
        pos1, pos2 = sort_coordinates(parse_coordinate(args.pos1), parse_coordinate(args.pos2))

    global min_x, min_y, min_z, max_x, max_y, max_z
    min_x, min_y, min_z = pos1
    max_x, max_y, max_z = pos2


    num_threads = args.num_threads
    if num_threads <= 0:
        eprint(f'--num_threads must be >= 1')
        sys.exit()


    export_old_chunk_versions(output_path, target_version, world_paths, min_x, min_y, min_z, max_x, max_y, max_z, num_threads)

if __name__ == '__main__':
    main()
