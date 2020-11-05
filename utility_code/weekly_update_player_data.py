#!/usr/bin/env python3

import os
import sys
import getopt

from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path
from lib_py3.common import eprint
from lib_py3.fake_redis_world import FakeRedisWorld

def usage():
    sys.exit("Usage: {} <--redisworld /path/to/world> <--datapacks /path/to/datapacks> [--logfile <stdout|stderr|path>] [--dry-run]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:p:l:d", ["redisworld=", "datapacks=", "logfile=", "dry-run"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
datapacks = None
logfile = None
dry_run = False

for o, a in opts:
    if o in ("-w", "--redisworld"):
        world_path = a
    elif o in ("-p", "--datapacks"):
        datapacks = a
    elif o in ("-l", "--logfile"):
        logfile = a
    elif o in ("-d", "--dry-run"):
        dry_run = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None:
    eprint("--redisworld must be specified!")
    usage()
if datapacks is None:
    eprint("--datapacks must be specified!")
    usage()

loot_table_manager = LootTableManager()
loot_table_manager.load_loot_tables_subdirectories(datapacks)
item_replace_manager = ItemReplacementManager(loot_table_manager.get_unique_item_map(show_errors=True))
world = FakeRedisWorld(world_path)

log_handle = None
if logfile == "stdout":
    log_handle = sys.stdout
elif logfile == "stderr":
    log_handle = sys.stderr
elif logfile is not None:
    log_handle = open(logfile, 'w')

num_replacements = 0
replacements_log = {}

for player in world.players():
    player.full_heal()
    tags = set(player.tags)
    tags.add("resetMessage")
    if "MidTransfer" in tags:
        tags.remove("MidTransfer")
    player.tags = tags
    if not dry_run:
        player.save()

for item, _, entity_path in world.items(readonly=dry_run):
    if item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=get_debug_string_from_entity_path(entity_path)):
        num_replacements += 1

if log_handle is not None:
    for to_item in replacements_log:
        log_handle.write("{}\n".format(to_item))
        log_handle.write("    TO:\n")
        log_handle.write("        {}\n".format(replacements_log[to_item]["TO"]))
        log_handle.write("    FROM:\n")

        for from_item in replacements_log[to_item]["FROM"]:
            log_handle.write("        {}\n".format(from_item))

            for from_location in replacements_log[to_item]["FROM"][from_item]:
                log_handle.write("            {}\n".format(from_location))

        log_handle.write("\n")

if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
    log_handle.close()

print("Replaced {} items".format(num_replacements))
