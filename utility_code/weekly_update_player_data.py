#!/usr/bin/env pypy3

import getopt
import multiprocessing
import os
import sys
import traceback
import yaml

from lib_py3.common import eprint
from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.market_data import MarketData
from lib_py3.plugin_data import iter_plugin_data_parallel
from lib_py3.timing import Timings
from lib_py3.upgrade import upgrade_entity
from minecraft.world import World


def usage():
    sys.exit("Usage: {} <--world /path/to/world> <--datapacks /path/to/datapacks> [--num-threads num] [--dry-run]".format(sys.argv[0]))

def process_init(mgr):
    global item_replace_manager
    item_replace_manager = mgr

def process_player(player):
    num_replacements = 0

    player.full_heal()
    tags = set(player.tags)
    tags.add("resetMessage")
    player.tags = tags
    upgrade_entity(player.nbt)

    for item in player.recursive_iter_items():
        if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
            num_replacements += 1

    return num_replacements

def process_plugin_data(plugin_data):
    num_replacements = 0

    for item in plugin_data.graves().recursive_iter_items():
        if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
            num_replacements += 1

    # TODO: Eventually should refactor plugin data so it has a top-level iterator interface to eliminate the need to call charms() directly
    for item in plugin_data.charms().recursive_iter_items():
        if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
            num_replacements += 1

    # TODO: Second verse, same as the first!
    for item in plugin_data.zenith_charms().recursive_iter_items():
        if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
            num_replacements += 1

    for item in plugin_data.wallet().recursive_iter_items():
        if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
            num_replacements += 1

    return num_replacements

def err_func(ex, args):
    eprint(f"Caught exception: {ex}")
    eprint(f"While iterating: {args}")
    eprint(traceback.format_exc())
    return 0

if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")

    try:
        opts, args = getopt.getopt(sys.argv[1:], "w:p:l:j:d", ["world=", "datapacks=", "num-threads=", "dry-run"])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    world_path = None
    datapacks = None
    dry_run = False
    num_threads = 4

    for o, a in opts:
        if o in ("-w", "--world"):
            world_path = a
        elif o in ("-p", "--datapacks"):
            datapacks = a
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

    # Note that these iterators are really generators - and will produce results as they come in
    # They are consumed here as they come in to avoid having to store the entire log in RAM all at once
    num_replacements = 0

    generator = world.iter_players_parallel(process_player, err_func, num_processes=num_threads, autosave=(not dry_run), initializer=process_init, initargs=(item_replace_manager,))
    replacements = 0
    for x in generator:
        replacements += x
    num_replacements += replacements

    timings.nextStep(f"Player replacements done: {replacements} replacements")

    generator = iter_plugin_data_parallel(os.path.join(world_path, "plugindata"), process_plugin_data, err_func, num_processes=num_threads, autosave=(not dry_run), initializer=process_init, initargs=(item_replace_manager,))
    replacements = 0
    for x in generator:
        replacements += x
    num_replacements += replacements

    timings.nextStep(f"Plugin data replacements done: {replacements} replacements")

    # Begin market replacements --
    replacements = 0

    mkt = MarketData(json_path=os.path.join(world_path, "itemDBIDToItem.json"), item_to_id=False)
    for item in mkt.recursive_iter_items():
        if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
            replacements += 1
    if not dry_run:
        mkt.save()

    mkt = MarketData(json_path=os.path.join(world_path, "itemDBItemToID.json"), item_to_id=True)
    for item in mkt.recursive_iter_items():
        if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
            replacements += 1
    if not dry_run:
        mkt.save()

    num_replacements += replacements
    timings.nextStep(f"Market data replacements done: {replacements} replacements")
    # -- End market replacements

    print("Replaced {} items".format(num_replacements))
