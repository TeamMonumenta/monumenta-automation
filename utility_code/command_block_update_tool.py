#!/usr/bin/env pypy3

"""A tool to export/import command block commands to/from json for bulk editing"""

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


def out_region_iter(region):
    """Export commands from a region file to json

    Returns a list of command block info
    """
    world_path = str(region.get_world_path())
    out = []
    for chunk in region.iter_chunks(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z, autosave=False):
        for block_entity in chunk.recursive_iter_block_entities():
            if block_entity.nbt.has_path('Command'):
                block = chunk.get_block(block_entity.pos)

                # Check that we're actually exactly within the bounding box (inclusive)
                bpos = block_entity.pos
                if bpos[0] < min_x or bpos[1] < min_y or bpos[2] < min_z:
                    continue
                if bpos[0] > max_x or bpos[1] > max_y or bpos[2] > max_z:
                    continue

                block_name = block['name']

                entry = {}
                entry['world_path'] = world_path
                entry['pos'] = block_entity.pos
                entry['command'] = block_entity.nbt.at_path('Command').value
                entry['name'] = block_name
                entry['auto'] = block_entity.nbt.at_path('auto').value
                entry['powered'] = block_entity.nbt.at_path('powered').value
                if 'facing' in block:
                    entry['facing'] = block['facing']
                else:
                    entry['facing'] = None

                out.append(entry)

    return out


def in_region_iter(region):
    """Import commands from json to a region file

    Returns the number of commands imported
    """
    num_replaced = 0
    world_path = str(region.get_world_path())

    for chunk in region.iter_chunks(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z, autosave=False):
        changed = False
        for block_entity in chunk.recursive_iter_block_entities():
            if block_entity.nbt.has_path('Command'):
                command_to_load = commands.get(f"{world_path} {block_entity.pos[0]} {block_entity.pos[1]} {block_entity.pos[2]}", None)
                if command_to_load is not None:
                    # Only update the command itself, none of the other stats
                    block_entity.nbt.at_path('Command').value = command_to_load["command"]
                    num_replaced += 1
                    changed = True
        if changed:
            region.save_chunk(chunk)

    return num_replaced


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


def export_commands(output_path, world_paths, min_x, min_y, min_z, max_x, max_y, max_z, num_threads):
    """Exports command blocks from a list of worlds to a json file."""
    out = []

    for world_path in world_paths:
        world = World(world_path)
        for result in world.iter_regions_parallel(out_region_iter, err_func, num_processes=num_threads, read_only=True,
                                                  min_x=min_x, min_y=min_y, min_z=min_z,
                                                  max_x=max_x, max_y=max_y, max_z=max_z):
            for item in result:
                out.append(item)

    with open(output_path, 'w') as outfile:
        json.dump(out, outfile, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

    print(f"Wrote {len(out)} command blocks to {output_path}")


def import_commands(input_path, world_paths, min_x, min_y, min_z, max_x, max_y, max_z, num_threads):
    """Imports command blocks to a list of worlds from a json file."""
    # Build a map of all the commands that need updating
    # key = "world_path x y z"
    # value = { world/pos/command/name/auto/powered }
    global commands
    commands = {}
    num_to_replace = 0
    with open(input_path, 'r') as outfile:
        data = json.load(outfile)
        for element in data:
            if "command_block" not in element["name"]:
                eprint("Warning: Refusing to update command block contained within an item: ", json.dumps(element))
            else:
                commands[f"{element['world_path']} {element['pos'][0]} {element['pos'][1]} {element['pos'][2]}"] = element
                num_to_replace += 1

    num_replaced = 0
    for world_path in world_paths:
        world = World(world_path)
        # Iterate the world and update things from the map
        for result in world.iter_regions_parallel(in_region_iter, err_func, num_processes=num_threads,
                                                  min_x=min_x, min_y=min_y, min_z=min_z,
                                                  max_x=max_x, max_y=max_y, max_z=max_z):
            num_replaced += result

    print(f"{num_replaced} / {num_to_replace} command blocks updated")


def main():
    """Argument handling for this command block update tool"""
    multiprocessing.set_start_method("fork")

    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('world', type=Path, nargs='+')
    arg_parser.add_argument('--output', type=Path, nargs='?', help='Export command blocks to json')
    arg_parser.add_argument('--input', type=Path, nargs='?', help='Import command blocks from json')
    arg_parser.add_argument('--pos1', type=str, nargs='?', help='x,y,z')
    arg_parser.add_argument('--pos2', type=str, nargs='?', help='x,y,z')
    arg_parser.add_argument('-j', '--num-threads', type=int, default=4)
    args = arg_parser.parse_args()

    if bool(args.input) + bool(args.output) != 1:
        eprint('Either --input or --output must be specified!')
        sys.exit()
    output_path = args.output
    input_path = args.input


    world_paths = []
    for worlds_path in args.world:
        for world_path in World.enumerate_worlds(worlds_path):
            print(world_path)
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


    output_mode = (input_path is None)

    if output_mode:
        export_commands(output_path, world_paths, min_x, min_y, min_z, max_x, max_y, max_z, num_threads)

    else:
        import_commands(input_path, world_paths, min_x, min_y, min_z, max_x, max_y, max_z, num_threads)

if __name__ == '__main__':
    main()
