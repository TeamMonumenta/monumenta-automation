#!/usr/bin/env pypy3

"""Run weekly update tasks for player data

...or anything else shared between shards.
...except for scores, which are handled by Rust code for performance reasons.
"""

import argparse
import json
import multiprocessing
from pathlib import Path
import traceback

from lib_py3.common import eprint
from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.market_data import MarketData
from lib_py3.plugin_data import iter_plugin_data_parallel
from lib_py3.timing import Timings
from lib_py3.upgrade import upgrade_entity
from minecraft.world import World


def process_init(mgr):
    """Initialize multiprocess iterator for multithreaded code"""
    global item_replace_manager
    item_replace_manager = mgr


def process_player(player):
    """Run weekly update tasks on players (healing, updating tags, updating items)"""
    num_replacements = 0

    player.full_heal()
    tags = set(player.tags)
    tags.add("resetMessage")
    if "ValentineDailyHotfix" in tags:
        tags.remove("ValentineDailyHotfix")
    player.tags = tags
    upgrade_entity(player.nbt)

    for item in player.recursive_iter_items():
        if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
            num_replacements += 1

    return num_replacements


def process_plugin_data(plugin_data):
    """Runs item updates on player plugin data"""
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

    for item in plugin_data.charm_bag().recursive_iter_items():
        if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
            num_replacements += 1

    return num_replacements


def err_func(ex, args):
    """Prints caught exceptions to stderr during multithreaded code"""
    eprint(f"Caught exception: {ex}")
    eprint(f"While iterating: {args}")
    eprint(traceback.format_exc())
    return 0


def temp_remove_nested_mail_items(main_item):
    """TODO Remove this once all nested mail items have been processed"""
    modified = False
    if main_item.nbt.has_path('tag.BlockEntityTag'):
        block_entity_tag = main_item.nbt.at_path('tag.BlockEntityTag')
        if block_entity_tag.has_path('Items[0]'):
            block_entity_tag.at_path('Items').value = []
            modified = True
        if block_entity_tag.has_path('Book'):
            del block_entity_tag.value['Book']
            modified = True
    if main_item.nbt.has_path('tag.ChargedProjectiles[0]'):
        main_item.nbt.at_path('tag.ChargedProjectiles').value = []
        modified = True
    if main_item.nbt.has_path('tag.Items[0]'):
        main_item.nbt.at_path('tag.Items').value = []
        modified = True
    if main_item.nbt.has_path('tag.Monumenta.PlayerModified.Items[0]'):
        main_item.nbt.at_path('tag.Monumenta.PlayerModified.Items').value = []
        modified = True
    return modified


if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")

    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('-w', '--world_path', type=Path, required=True)
    arg_parser.add_argument('-p', '--datapacks', type=Path, required=True)
    arg_parser.add_argument('-j', '--num-threads', type=int)
    arg_parser.add_argument('-d', '--dry-run', action='store_true')
    args = arg_parser.parse_args()

    world_path = args.world_path
    datapacks = args.datapacks
    dry_run = args.dry_run
    num_threads = args.num_threads

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
    eprint("Player replacements done")

    generator = iter_plugin_data_parallel(world_path / "plugindata", process_plugin_data, err_func, num_processes=num_threads, autosave=(not dry_run), initializer=process_init, initargs=(item_replace_manager,))
    replacements = 0
    for x in generator:
        replacements += x
    num_replacements += replacements

    timings.nextStep(f"Plugin data replacements done: {replacements} replacements")
    eprint("Plugin data replacements done")
    # Begin market replacements --
    replacements = 0
    original_item_count = 0
    after_item_count = 0

    # Get list of used IDs; no need to process the others
    used_id_data = {}
    with open(world_path / "itemDBUsedIds.json", 'r') as fp:
        used_id_data = json.load(fp)
    ids_used_by_listings = set(used_id_data.get("listings", []))
    ids_used_by_mail = set(used_id_data.get("mail", []))
    ids_used_by_anything = ids_used_by_listings | ids_used_by_mail
    # Temp set of mail-only IDs to clean up nested items that don't need to be nested
    mid_item_count = 0
    ids_used_by_mail_only = ids_used_by_mail - ids_used_by_listings


    # ID to Item map
    mkt = MarketData(json_path=world_path / "itemDBIDToItem.json", item_to_id=False)
    original_item_count += len(mkt)

    # Temp remove nested items from mail - TODO Remove this when done
    for main_item in mkt.iter_items(yield_ids=ids_used_by_mail_only):
        if temp_remove_nested_mail_items(main_item):
            replacements += 1
    mid_item_count += len(mkt)

    for main_item in mkt.iter_items(keep_ids=ids_used_by_anything):
        for item in main_item.recursive_iter_items():
            if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
                replacements += 1
    after_item_count += len(mkt)
    if not dry_run:
        mkt.save()


    # Item to ID map
    mkt = MarketData(json_path=world_path / "itemDBItemToID.json", item_to_id=True)
    original_item_count += len(mkt)

    # Temp remove nested items from mail - TODO Remove this when done
    for main_item in mkt.iter_items(yield_ids=ids_used_by_mail_only):
        if temp_remove_nested_mail_items(main_item):
            replacements += 1
    mid_item_count += len(mkt)

    for main_item in mkt.iter_items(keep_ids=ids_used_by_anything):
        for item in main_item.recursive_iter_items():
            if item_replace_manager.replace_item(item, debug_path=item.get_path_str()):
                replacements += 1
    after_item_count += len(mkt)
    if not dry_run:
        mkt.save()


    removed_items = original_item_count - after_item_count
    num_replacements += replacements
    timings.nextStep(f"Market data replacements done: {replacements} replacements, {removed_items}/{original_item_count} items removed, {after_item_count} remain, {mid_item_count} temp count")
    # -- End market replacements

    print(f"Replaced {num_replacements} items")
