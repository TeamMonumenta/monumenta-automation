#!/usr/bin/env pypy3

"""Replaces every item in the specified location with those from the loot tables"""

import argparse
import math
import os
import multiprocessing
from pathlib import Path
import sys
import traceback

from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.common import eprint
from lib_py3.timing import Timings

from minecraft.chunk_format.schematic import Schematic
from minecraft.chunk_format.structure import Structure
from minecraft.world import World

def process_init(mgr, dry, minx, miny, minz, maxx, maxy, maxz):
    global item_replace_manager, dry_run, min_x, min_y, min_z, max_x, max_y, max_z
    item_replace_manager = mgr
    dry_run = dry
    min_x = minx
    min_y = miny
    min_z = minz
    max_x = maxx
    max_y = maxy
    max_z = maxz

def process_region(region):
    num_replacements = 0
    for chunk in region.iter_chunks(autosave=(not dry_run), min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z):
        for item in chunk.recursive_iter_items(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z):
            if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
                num_replacements += 1

    return num_replacements

def process_schematic_or_structure(obj):
    num_replacements = 0

    for item in obj.recursive_iter_items(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z):
        if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
            num_replacements += 1

    if not dry_run and num_replacements > 0:
        obj.save()

    return num_replacements

def err_func(ex, args):
    eprint(f"Caught exception: {ex}")
    eprint(f"While iterating: {args}")
    eprint(traceback.format_exc())
    return 0

if __name__ == '__main__':
    multiprocessing.set_start_method("fork")

    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('--datapacks', type=Path, nargs='?', default=Path('/home/epic/project_epic/server_config/data/datapacks'))
    arg_parser.add_argument('-z', '--worlds', type=Path, nargs='?')
    arg_parser.add_argument('-w', '--world', type=Path, nargs='?')
    arg_parser.add_argument('-s', '--schematics', type=Path, nargs='?')
    arg_parser.add_argument('-g', '--structures', type=Path, nargs='?')
    arg_parser.add_argument('-j', '--num-threads', type=int, default=4)
    arg_parser.add_argument('--pos1', type=str, nargs='?', help='x,y,z')
    arg_parser.add_argument('--pos2', type=str, nargs='?', help='x,y,z')
    arg_parser.add_argument('-d', '--dry-run', action='store_true')
    args = arg_parser.parse_args()

    datapacks_path = args.datapacks
    worlds_path = args.worlds
    world_path = args.world
    schematics_path = args.schematics
    structures_path = args.structures
    num_threads = args.num_threads
    dry_run = args.dry_run
    pos1 = [-math.inf, -math.inf, -math.inf]
    pos2 = [math.inf, math.inf, math.inf]

    if args.pos1 is not None:
        try:
            pos1 = [int(x) for x in args.pos1.split(',')]
            if len(pos1) != 3:
                raise Exception('Invalid number of coordinates')
        except Exception:
            eprint("Invalid --pos1 argument")
            arg_parser.print_help(file=sys.stderr)

    if args.pos2 is not None:
        try:
            pos2 = [int(x) for x in args.pos2.split(',')]
            if len(pos2) != 3:
                raise Exception('Invalid number of coordinates')
        except Exception:
            eprint("Invalid --pos2 argument")
            arg_parser.print_help(file=sys.stderr)

    if dry_run:
        eprint("Running in dry-run mode; changes will not be saved")

    min_x = min(pos1[0], pos2[0])
    min_y = min(pos1[1], pos2[1])
    min_z = min(pos1[2], pos2[2])
    max_x = max(pos1[0], pos2[0])
    max_y = max(pos1[1], pos2[1])
    max_z = max(pos1[2], pos2[2])

    if worlds_path is None and world_path is None and schematics_path is None and structures_path is None:
        eprint("--worlds, --world, --schematics, or --structures must be specified!")
        arg_parser.print_help(file=sys.stderr)

    timings = Timings(enabled=dry_run)
    loot_table_manager = LootTableManager()
    loot_table_manager.load_loot_tables_subdirectories(datapacks_path)
    timings.nextStep("Loaded loot tables")
    item_replace_manager = ItemReplacementManager(loot_table_manager.get_unique_item_map(show_errors=True))
    timings.nextStep("Loaded item replacement manager")

    num_replacements = 0

    if world_path or worlds_path:
        worlds = []
        if world_path:
            worlds.append(world_path)
        if worlds_path:
            for world_path in World.enumerate_worlds(worlds_path):
                worlds.append(world_path)

        for world_path in worlds:
            if not os.path.exists(world_path):
                eprint(f"World path '{world_path}' does not exist")
                arg_parser.print_help(file=sys.stderr)

            world = World(world_path)
            timings.nextStep("Loaded world")

            generator = world.iter_regions_parallel(process_region, err_func, num_processes=num_threads, initializer=process_init, initargs=(item_replace_manager, dry_run, min_x, min_y, min_z, max_x, max_y, max_z))
            replacements = 0
            for x in generator:
                replacements += x
            num_replacements += replacements

            timings.nextStep(f"World replacements done, {replacements} replacements")

    if schematics_path:
        # Note: autosave=False is because we only save schematics that had some item replacements in them
        generator = Schematic.iter_schematics_parallel(schematics_path, process_schematic_or_structure, err_func, num_processes=num_threads, autosave=False, initializer=process_init, initargs=(item_replace_manager, dry_run, min_x, min_y, min_z, max_x, max_y, max_z))
        replacements = 0
        for x in generator:
            replacements += x
        num_replacements += replacements

        timings.nextStep(f"Schematics replacements done, {replacements} replacements")

    if structures_path:
        # Note: autosave=False is because we only save structures that had some item replacements in them
        generator = Structure.iter_structures_parallel(structures_path, process_schematic_or_structure, err_func, num_processes=num_threads, autosave=False, initializer=process_init, initargs=(item_replace_manager, dry_run, min_x, min_y, min_z, max_x, max_y, max_z))
        replacements = 0
        for x in generator:
            replacements += x
        num_replacements += replacements

        timings.nextStep(f"Structures replacements done, {replacements} replacements")

    print("Replaced {} items".format(num_replacements))
