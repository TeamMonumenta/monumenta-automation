#!/usr/bin/env pypy3

import os
import sys
import getopt
import yaml
import multiprocessing
import concurrent.futures
import traceback

from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.common import eprint
from lib_py3.timing import Timings

from minecraft.chunk_format.schematic import Schematic
from minecraft.chunk_format.structure import Structure
from minecraft.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

def usage():
    sys.exit("Usage: {} <--world /path/to/world | --schematics /path/to/schematics> | --structures /path/to/structures [--logfile <stdout|stderr|path>] [--num-threads num] [--dry-run]".format(sys.argv[0]))

def process_region(arg):
    region, custom_args = arg
    item_replace_manager, dry_run = custom_args
    replacements_log = {}
    num_replacements = 0
    for chunk in region.iter_chunks(autosave=(not dry_run)):
        for item in chunk.recursive_iter_items():
            if item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=item.get_path_str()):
                num_replacements += 1

    return (num_replacements, replacements_log)

def process_schematic(arg):
    schem_path, custom_args = arg
    item_replace_manager, dry_run = custom_args
    replacements_log = {}
    num_replacements = 0

    try:
        schem = Schematic(schem_path)
        for item in schem.recursive_iter_items():
            if item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=item.get_path_str()):
                num_replacements += 1

        if not dry_run and num_replacements > 0:
            schem.save()
    except Exception as ex:
        eprint(f"Failed to process schematic '{schem_path}': {ex}\n{str(traceback.format_exc())}")
        replacements_log = {}
        num_replacements = 0

    return (num_replacements, replacements_log)

def process_structure(arg):
    struct_path, custom_args = arg
    item_replace_manager, dry_run = custom_args
    replacements_log = {}
    num_replacements = 0

    try:
        struct = Structure(struct_path)
        for item in struct.recursive_iter_items():
            if item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=item.get_path_str()):
                num_replacements += 1

        if not dry_run and num_replacements > 0:
            struct.save()
    except Exception as ex:
        eprint(f"Failed to process structatic '{struct_path}': {ex}\n{str(traceback.format_exc())}")
        replacements_log = {}
        num_replacements = 0

    return (num_replacements, replacements_log)

if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")

    try:
        opts, args = getopt.getopt(sys.argv[1:], "w:s:g:l:j:d", ["world=", "schematics=", "structures=", "logfile=", "num-threads=", "dry-run"])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    world_path = None
    schematics_path = None
    structures_path = None
    logfile = None
    num_threads = 4
    dry_run = False

    for o, a in opts:
        if o in ("-w", "--world"):
            world_path = a
        elif o in ("-s", "--schematics"):
            schematics_path = a
        elif o in ("-s", "--structures"):
            structures_path = a
        elif o in ("-l", "--logfile"):
            logfile = a
        elif o in ("-j", "--num-threads"):
            num_threads = int(a)
        elif o in ("-d", "--dry-run"):
            dry_run = True
        else:
            eprint("Unknown argument: {}".format(o))
            usage()

    if world_path is None and schematics_path is None and structures_path is None:
        eprint("--world, --schematics, or --structures must be specified!")
        usage()

    timings = Timings(enabled=dry_run)
    loot_table_manager = LootTableManager()
    loot_table_manager.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")
    timings.nextStep("Loaded loot tables")
    item_replace_manager = ItemReplacementManager(loot_table_manager.get_unique_item_map(show_errors=True))
    timings.nextStep("Loaded item replacement manager")

    log_handle = None
    if logfile == "stdout":
        log_handle = sys.stdout
    elif logfile == "stderr":
        log_handle = sys.stderr
    elif logfile is not None:
        log_handle = open(logfile, 'w')

    if world_path:
        world = World(world_path)
        timings.nextStep("Loaded world")

        parallel_results = world.iter_regions_parallel(process_region, num_processes=num_threads, arg=(item_replace_manager, dry_run))
        timings.nextStep("World replacements done")

    if schematics_path:
        args = []
        for root, subdirs, files in os.walk(schematics_path):
            for fname in files:
                if fname.endswith(".schematic"):
                    args.append((os.path.join(root, fname), (item_replace_manager, dry_run)))

        if num_threads == 1:
            # Don't bother with processes if only going to use one
            # This makes debugging much easier
            parallel_results = []
            for arg in args:
                parallel_results.append(process_schematic(arg))
        else:
            with concurrent.futures.ProcessPoolExecutor(max_workers=num_threads) as pool:
                parallel_results = pool.map(process_schematic, args)
        timings.nextStep("Schematics replacements done")

    if structures_path:
        args = []
        for root, subdirs, files in os.walk(structures_path):
            for fname in files:
                if fname.endswith(".nbt"):
                    args.append((os.path.join(root, fname), (item_replace_manager, dry_run)))

        if num_threads == 1:
            # Don't bother with processes if only going to use one
            # This makes debugging much easier
            parallel_results = []
            for arg in args:
                parallel_results.append(process_structure(arg))
        else:
            with concurrent.futures.ProcessPoolExecutor(max_workers=num_threads) as pool:
                parallel_results = pool.map(process_structure, args)
        timings.nextStep("Structures replacements done")

    num_replacements = 0
    replacements_to_merge = []
    for region_result in parallel_results:
        num_replacements += region_result[0]
        replacements_to_merge.append(region_result[1])

    replacements_log = item_replace_manager.merge_logs(replacements_to_merge)
    timings.nextStep("Logs merged")


    if log_handle is not None:
        yaml.dump(replacements_log, log_handle, width=2147483647, allow_unicode=True)
        timings.nextStep("Logs written")

    if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
        log_handle.close()

    print("Replaced {} items".format(num_replacements))
