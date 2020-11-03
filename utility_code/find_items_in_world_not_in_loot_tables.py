#!/usr/bin/env python3

# For interactive shell
import readline
import code

import sys
import getopt
from pprint import pprint

from score_change_list import dungeon_score_rules
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.common import eprint, get_item_name_from_nbt
from lib_py3.world import World

def usage():
    sys.exit("Usage: {} <--world /path/to/world> [--logfile <stdout|stderr|path>] [--interactive]".format(sys.argv[0]))


try:
    opts, args = getopt.getopt(sys.argv[1:], "w:l:di", ["world=", "logfile=", "interactive"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
logfile = 'stdout'
interactive = False

for o, a in opts:
    if o in ("-w", "--world"):
        world_path = a
    elif o in ("-l", "--logfile"):
        logfile = a
    elif o in ("-i", "--interactive"):
        interactive = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None:
    eprint("--world must be specified!")
    usage()

loot_table_manager = LootTableManager()
loot_table_manager.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")
item_map = loot_table_manager.get_unique_item_map(show_errors=False)
world = World(world_path)

log_handle = None
if logfile == "stdout":
    log_handle = sys.stdout
elif logfile == "stderr":
    log_handle = sys.stderr
elif logfile is not None:
    log_handle = open(logfile, 'w')

num_missing_items = 0
missing_items = {}
for item, source_pos, entity_path in world.items(readonly=True):
    if not (item.has_path('id') and item.has_path('tag.display.Name')):
        continue

    # For practical reasons, also ignore items that have no lore text
    if not item.has_path('tag.display.Lore'):
        continue

    # Get the correct replacement info; abort if none exists
    item_id = item.at_path('id').value
    item_name = get_item_name_from_nbt(item.at_path('tag'))

    # Ignore some commonly named development materials:
    if item_id in ("minecraft:chain_command_block", "minecraft:command_block", "minecraft:repeating_command_block", "minecraft:chest", "minecraft:trapped_chest", "minecraft:written_book"):
        continue

    new_item_tag = item_map.get(item_id,{}).get(item_name,None)
    if not new_item_tag:
        # This item is not in the loot tables - make a note!
        log_key = item_name + "  " + item_id

        if log_key not in missing_items:
            missing_items[log_key] = 1
            num_missing_items += 1
        else:
            missing_items[log_key] = missing_items[log_key] + 1

if interactive:
    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.interact()

if log_handle is not None:
    for item in sorted(missing_items.items(), key=lambda kv: kv[1]):
        log_handle.write("{} {}\n".format(item[0], item[1]))

if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
    log_handle.close()

eprint("{} named items do not exist in loot tables".format(num_missing_items))
