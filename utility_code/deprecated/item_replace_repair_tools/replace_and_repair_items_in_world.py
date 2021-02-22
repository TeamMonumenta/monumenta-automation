#!/usr/bin/env python3

import os
import sys
import getopt
import json
from pprint import pprint

# TODO ItemReplacementManager now takes type Item instead of an NBT tag. Update before using this.
from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path
from lib_py3.common import eprint, get_item_name_from_nbt
from lib_py3.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

def get_item_location_key(debug_path: [nbt.TagCompound]) -> str:
    """
    Takes an item path and returns a unique-ish string like this to use as a hash key:
    x_y_z_topContainerId_itemDepth
    """

    x = None
    y = None
    z = None
    if debug_path[0].has_path("Pos"):
        x = debug_path[0].at_path('Pos').value[0].value
        y = debug_path[0].at_path('Pos').value[1].value
        z = debug_path[0].at_path('Pos').value[2].value

    if debug_path[0].has_path("x"):
        x = debug_path[0].at_path('x').value
        y = debug_path[0].at_path('y').value
        z = debug_path[0].at_path('z').value

    x = int(round(x))
    y = int(round(y))
    z = int(round(z))

    if x is None or y is None or z is None:
        raise Exception("Damaged item with no debug path location")

    return f"{x}_{y}_{z}_{debug_path[0].at_path('id').value.lower().replace('minecraft:','')}_{len(debug_path)}"

def usage():
    sys.exit("Usage: {} <--world /path/to/world> <--repair-map-in /path/to/repair_map.json> <--repair-map-out /path/to/repair_map_out.json> [--logfile <stdout|stderr|path>] [--dry-run]".format(sys.argv[0]))


try:
    opts, args = getopt.getopt(sys.argv[1:], "w:r:R:l:diu", ["world=", "repair-map-in=", "repair-map-out=", "logfile=", "dry-run"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
logfile = None
repair_map_in = None
repair_map_out = None
dry_run = False

for o, a in opts:
    if o in ("-w", "--world"):
        world_path = a
    elif o in ("-r", "--repair-map-in"):
        repair_map_in = a
    elif o in ("-R", "--repair-map-out"):
        repair_map_out = a
    elif o in ("-l", "--logfile"):
        logfile = a
    elif o in ("-d", "--dry-run"):
        dry_run = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None:
    eprint("--world must be specified!")
    usage()
if repair_map_in is None:
    eprint("--repair_map_in must be specified!")
    usage()
if repair_map_out is None:
    eprint("--repair_map_out must be specified!")
    usage()

loot_table_manager = LootTableManager()
loot_table_manager.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")
item_replace_manager = ItemReplacementManager(loot_table_manager.get_unique_item_map(show_errors=True))
world = World(world_path)

log_handle = None
if logfile == "stdout":
    log_handle = sys.stdout
elif logfile == "stderr":
    log_handle = sys.stderr
elif logfile is not None:
    log_handle = open(logfile, 'w')

repair_map = {}
with open(repair_map_in, "r") as fin:
    repair_map = json.load(fin)

num_repaired = 0
num_replacements = 0
replacements_log = {}
for item, _, entity_path in world.items(readonly=dry_run):
    if item.has_path("tag"):
        itemtag = item.at_path("tag")
        location_key = get_item_location_key(entity_path)
        if location_key in repair_map:
            item_name = get_item_name_from_nbt(itemtag, remove_color=True)
            if item_name is not None:
                for broken_item in repair_map[location_key]:
                    if "repaired" not in broken_item and item_name == broken_item["name"]:
                        broken_item["repaired"] = itemtag.to_mojangson()

                        # TODO DELETE
                        #item.tree()
                        #nbt.TagCompound.from_mojangson(broken_item["from"]).tree()
                        #sys.exit(1)
                        # TODO DELETE

                        itemtag.value = nbt.TagCompound.from_mojangson(broken_item["from"]).value
                        num_repaired += 1
                        break

    if item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=get_debug_string_from_entity_path(entity_path)):
        num_replacements += 1

    if num_replacements % 200 == 0:
        print(f"Repaired {num_repaired} items and replaced {num_replacements} items so far...")
        #if num_repaired > 100: # TODO DELETE
        #    break # TODO DELETE

with open(repair_map_out, "w") as fout:
    json.dump(repair_map, fout, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

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

print(f"Repaired {num_repaired} items")
print(f"Replaced {num_replacements} items")

num_not_repaired = 0
for broken_item_location in repair_map:
    for broken_item in repair_map[broken_item_location]:
        if "repaired" not in broken_item:
            num_not_repaired += 1
print(f"Did not repair {num_not_repaired} items that were originally broken")
