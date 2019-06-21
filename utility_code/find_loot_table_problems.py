#!/usr/bin/env python3

# For interactive shell
import readline
import code

import os
import sys
import getopt
from pprint import pprint

from lib_py3.common import eprint
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.world import World


def usage():
    sys.exit("Usage: {} [--world /path/to/world] [--interactive]".format(sys.argv[0]))


try:
    opts, args = getopt.getopt(sys.argv[1:], "w:i", ["world=", "interactive"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_paths = []
interactive = False

for o, a in opts:
    if o in ("-w", "--world"):
        world_paths.append(a)
    elif o in ("-i", "--interactive"):
        interactive = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

mgr = LootTableManager()

mgr.load_loot_tables_subdirectories("/home/rock/project_epic/server_config/data/datapacks")
mgr.load_advancements_subdirectories("/home/rock/project_epic/server_config/data/datapacks")
mgr.load_functions_subdirectories("/home/rock/project_epic/server_config/data/datapacks")
mgr.load_scripted_quests_directory("/home/rock/project_epic/server_config/data/scriptedquests")

if len(world_paths) != 0:
    for world_entry in world_paths:
        mgr.load_world(World(world_entry))

invalid_references = mgr.get_invalid_loot_table_references()
if len(invalid_references.keys()) > 0:
    print("\033[1;31m", end="")
    print("ERROR! Invalid references found!")
    pprint(invalid_references)
    print("\033[0;0m")
    print("\n\n\n")

mgr.get_unique_item_map(show_errors=True)

if interactive:
    print("\n\n\n")
    print("Try looking at mgr.item_map and mgr.table_map")
    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.interact()
