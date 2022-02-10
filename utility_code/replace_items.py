#!/usr/bin/env pypy3

import os
import getopt
import multiprocessing
import sys
import traceback
import yaml

from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.common import eprint
from lib_py3.timing import Timings

from minecraft.chunk_format.schematic import Schematic
from minecraft.chunk_format.structure import Structure
from minecraft.world import World

def usage():
    sys.exit("Usage: {} <--worlds /path/to/folder_containing_worlds | --world /path/to/world | --schematics /path/to/schematics> | --structures /path/to/structures [--logfile <stdout|stderr|path>] [--num-threads num] [--dry-run]".format(sys.argv[0]))

def process_init(mgr, dry):
    global item_replace_manager, dry_run
    item_replace_manager = mgr
    dry_run = dry

def process_region(region):
    replacements_log = {}
    num_replacements = 0
    for chunk in region.iter_chunks(autosave=(not dry_run)):
        for item in chunk.recursive_iter_items():
            if item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=item.get_path_str()):
                num_replacements += 1

    return (num_replacements, replacements_log)

def process_schematic_or_structure(obj):
    replacements_log = {}
    num_replacements = 0

    for item in obj.recursive_iter_items():
        if item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=item.get_path_str()):
            num_replacements += 1

    if not dry_run and num_replacements > 0:
        obj.save()

    return (num_replacements, replacements_log)

def err_func(ex, args):
    eprint(f"Caught exception: {ex}")
    eprint(f"While iterating: {args}")
    eprint(traceback.format_exc())
    return (0, {})

if __name__ == '__main__':
    multiprocessing.set_start_method("fork")

    try:
        opts, args = getopt.getopt(sys.argv[1:], "z:w:s:g:l:j:d", ["worlds=", "world=", "schematics=", "structures=", "logfile=", "num-threads=", "dry-run"])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    worlds_path = None
    world_path = None
    schematics_path = None
    structures_path = None
    logfile = None
    num_threads = 4
    dry_run = False

    for o, a in opts:
        if o in ("-w", "--world"):
            world_path = a
        elif o in ("-z", "--worlds"):
            worlds_path = a
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

    if worlds_path is None and world_path is None and schematics_path is None and structures_path is None:
        eprint("--worlds, --world, --schematics, or --structures must be specified!")
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

    num_replacements = 0
    replacements_log = {}

    if world_path or worlds_path:
        worlds = []
        if world_path:
            worlds.append(world_path)
        if worlds_path:
            for worldname in World.enumerate_worlds(worlds_path):
                worlds.append(os.path.join(worlds_path, worldname))

        for world_path in worlds:
            if not os.path.exists(world_path):
                eprint(f"World path '{world_path}' does not exist")
                usage()

            world = World(world_path)
            timings.nextStep("Loaded world")

            generator = world.iter_regions_parallel(process_region, err_func, num_processes=num_threads, initializer=process_init, initargs=(item_replace_manager, dry_run))
            replacements, replacements_log = item_replace_manager.merge_log_tuples(generator, replacements_log)
            num_replacements += replacements

            timings.nextStep(f"World replacements done, {replacements} replacements")

    if schematics_path:
        # Note: autosave=False is because we only save schematics that had some item replacements in them
        generator = Schematic.iter_schematics_parallel(schematics_path, process_schematic_or_structure, err_func, num_processes=num_threads, autosave=False, initializer=process_init, initargs=(item_replace_manager, dry_run))
        replacements, replacements_log = item_replace_manager.merge_log_tuples(generator, replacements_log)
        num_replacements += replacements

        timings.nextStep(f"Schematics replacements done, {replacements} replacements")

    if structures_path:
        # Note: autosave=False is because we only save structures that had some item replacements in them
        generator = Structure.iter_structures_parallel(structures_path, process_schematic_or_structure, err_func, num_processes=num_threads, autosave=False, initializer=process_init, initargs=(item_replace_manager, dry_run))
        replacements, replacements_log = item_replace_manager.merge_log_tuples(generator, replacements_log)
        num_replacements += replacements

        timings.nextStep(f"Structures replacements done, {replacements} replacements")

    if log_handle is not None:
        yaml.dump(replacements_log, log_handle, width=2147483647, allow_unicode=True)
        timings.nextStep("Logs written")

    if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
        log_handle.close()

    print("Replaced {} items".format(num_replacements))
