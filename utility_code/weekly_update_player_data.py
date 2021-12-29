#!/usr/bin/env pypy3

import os
import sys
import getopt
import yaml
import multiprocessing

from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.common import eprint
from lib_py3.upgrade import upgrade_entity
from lib_py3.timing import Timings
from minecraft.world import World

def usage():
    sys.exit("Usage: {} <--world /path/to/world> <--datapacks /path/to/datapacks> [--logfile <stdout|stderr|path>] [--num-threads num] [--dry-run]".format(sys.argv[0]))

def process_init(mgr):
    global item_replace_manager
    item_replace_manager = mgr

def process_player(player):
    num_replacements = 0
    replacements_log = {}

    player.full_heal()
    tags = set(player.tags)
    tags.add("resetMessage")
    player.tags = tags
    upgrade_entity(player.nbt)

    for item in player.recursive_iter_items():
        if item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=item.get_path_str()):
            num_replacements += 1

    return (num_replacements, replacements_log)

def err_func(ex):
    eprint(f"Caught exception: {ex}")
    return (0, {})

if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")

    try:
        opts, args = getopt.getopt(sys.argv[1:], "w:p:l:j:d", ["world=", "datapacks=", "logfile=", "num-threads=", "dry-run"])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    world_path = None
    datapacks = None
    logfile = None
    dry_run = False
    num_threads = 4

    for o, a in opts:
        if o in ("-w", "--world"):
            world_path = a
        elif o in ("-p", "--datapacks"):
            datapacks = a
        elif o in ("-l", "--logfile"):
            logfile = a
        elif o in ("-j", "--num-threads"):
            num_threads = int(a)
        elif o in ("-d", "--dry-run"):
            dry_run = True
        else:
            eprint("Unknown argument: {}".format(o))
            usage()

    if world_path is None:
        eprint("--world must be specified!")
        usage()
    if datapacks is None:
        eprint("--datapacks must be specified!")
        usage()

    timings = Timings(enabled=dry_run)
    loot_table_manager = LootTableManager()
    loot_table_manager.load_loot_tables_subdirectories(datapacks)
    timings.nextStep("Loaded loot tables")
    item_replace_manager = ItemReplacementManager(loot_table_manager.get_unique_item_map(show_errors=False))
    timings.nextStep("Loaded item replacement manager")
    world = World(world_path)
    timings.nextStep("Loaded world")

    log_handle = None
    if logfile == "stdout":
        log_handle = sys.stdout
    elif logfile == "stderr":
        log_handle = sys.stderr
    elif logfile is not None:
        log_handle = open(logfile, 'w')

    player_results = world.iter_players_parallel(process_player, err_func, num_processes=num_threads, autosave=(not dry_run), initializer=process_init, initargs=(item_replace_manager,))
    timings.nextStep("Replacements done")

    num_replacements = 0
    replacements_to_merge = []
    for player_result in player_results:
        num_replacements += player_result[0]
        replacements_to_merge.append(player_result[1])

    replacements_log = item_replace_manager.merge_logs(replacements_to_merge)
    timings.nextStep("Logs merged")

    if log_handle is not None:
        yaml.dump(replacements_log, log_handle, width=2147483647, allow_unicode=True)
        timings.nextStep("Logs written")

    if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
        log_handle.close()

    print("Replaced {} items".format(num_replacements))
