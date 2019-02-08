#!/usr/bin/env python3

# For interactive shell
import readline
import code

import os
import sys
import getopt
from pprint import pprint

from score_change_list import dungeon_score_rules
from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path
from lib_py3.common import eprint
from lib_py3.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

def usage():
    sys.exit("Usage: {} <--world /path/to/world> [--logfile <stdout|stderr|path>] [--dry-run] [--interactive] [--update-tables]".format(sys.argv[0]))


try:
    opts, args = getopt.getopt(sys.argv[1:], "w:l:diu", ["world=", "logfile=", "dry-run", "interactive", "update-tables"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
logfile = 'stdout'
dry_run = False
interactive = False
update_tables = False

for o, a in opts:
    if o in ("-w", "--world"):
        world_path = a
    elif o in ("-l", "--logfile"):
        logfile = a
    elif o in ("-d", "--dry-run"):
        dry_run = True
    elif o in ("-i", "--interactive"):
        interactive = True
    elif o in ("-u", "--update-tables"):
        update_tables = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None:
    eprint("--world must be specified!")
    usage()

loot_table_manager = LootTableManager()
loot_table_manager.load_loot_tables_subdirectories("/home/rock/project_epic/server_config/data/datapacks")
item_replace_manager = ItemReplacementManager(loot_table_manager.get_unique_item_map())
world = World(world_path)

log_handle = None
if logfile == "stdout":
    log_handle = sys.stdout
elif logfile == "stderr":
    log_handle = sys.stderr
elif logfile is not None:
    log_handle = open(logfile, 'w')

num_replacements = 0
replacements_log = {}
for item, source_pos, entity_path in world.items(readonly=dry_run):
    if item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=get_debug_string_from_entity_path(entity_path)):
        num_replacements += 1

if interactive:
    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.interact()

if log_handle is not None:
    for to_item in replacements_log:
        log_handle.write("{}\n".format(to_item))
        log_handle.write("    TO:\n")
        log_handle.write("        {}\n".format(replacements_log[to_item]["TO"]))
        log_handle.write("    FROM:\n")

        if update_tables:
            to_nbt = nbt.TagCompound.from_mojangson(replacements_log[to_item]["TO"])

        for from_item in replacements_log[to_item]["FROM"]:
            log_handle.write("        {}\n".format(from_item))

            if update_tables:
                from_nbt = nbt.TagCompound.from_mojangson(from_item)
                if (from_nbt == to_nbt) and (not from_nbt.equals_exact(to_nbt)):
                    # NBT is the "same" as the loot table entry but in a different order
                    # Need to update the loot tables with the correctly ordered NBT
                    loot_table_manager.update_item_in_loot_tables(replacements_log[to_item]["ID"], from_nbt)
                    log_handle.write("        Updated loot tables with this item!\n")

            for from_location in replacements_log[to_item]["FROM"][from_item]:
                log_handle.write("            {}\n".format(from_location))

        log_handle.write("\n")

if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
    log_handle.close()

eprint("Replaced {} items".format(num_replacements))
