#!/usr/bin/env python3

# For interactive shell
import readline
import code

import os
import sys
import getopt
import json
from pprint import pprint

from lib_py3.common import get_item_name_from_nbt
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path
from lib_py3.common import eprint, get_entity_uuid
from lib_py3.world import World
from uuid import UUID

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt


def usage():
    sys.exit("Usage: {} <--world /path/to/world> [--world /second/world ...] [--logfile <stdout|stderr|path>] [--interactive]".format(sys.argv[0]))


try:
    opts, args = getopt.getopt(sys.argv[1:], "w:li", ["world=", "logfile=", "interactive"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_paths = []
logfile = None
interactive = False

for o, a in opts:
    if o in ("-w", "--world"):
        world_paths.append(a)
    elif o in ("-l", "--logfile"):
        logfile = a
    elif o in ("-i", "--interactive"):
        interactive = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if len(world_paths) <= 0:
    eprint("--world must be specified!")
    usage()

num_items = 0
items = {}
for world_path in world_paths:
    print("Processing world: {}".format(world_path))
    world = World(world_path)

    for item, source_pos, entity_path in world.items(readonly=True):
        # Get the correct replacement info; abort if none exists
        if item.has_path('tag'):
            item_id = item.at_path('id').value
            item_name = get_item_name_from_nbt(item.at_path('tag'))

            if item_name is not None:
                num_items += 1

                # Compute something to use for a position (either coordinates or player uuid)
                pos = None
                if source_pos is not None:
                    pos = source_pos
                elif len(entity_path) > 0 and entity_path[0].has_path("playerGameType"):
                    # This is a player
                    player_uuid = get_entity_uuid(entity_path[0])
                    pos = "player:" + str(player_uuid)

                # Compute the quantity
                count = 1
                if item.has_path('Count'):
                    count = item.at_path('Count').value

                if item_id not in items:
                    items[item_id] = {}
                if item_name not in items[item_id]:
                    items[item_id][item_name] = []

                items[item_id][item_name].append((pos, count))

if interactive:
    print('''Try: pprint(items['minecraft:golden_chestplate']["King's Warden"])''')
    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.interact()

log_handle = None
if logfile == "stdout":
    log_handle = sys.stdout
elif logfile == "stderr":
    log_handle = sys.stderr
elif logfile is not None:
    log_handle = open(logfile, 'w')

if log_handle is not None:
    json.dump(items, log_handle, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
    log_handle.close()

print("Processed {} named items".format(num_items))
