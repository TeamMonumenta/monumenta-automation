#!/usr/bin/env python3

import sys
import os
import getopt
import yaml
from pprint import pprint

from lib_py3.mob_replacement_manager import MobReplacementManager
from lib_py3.common import eprint, get_entity_name_from_nbt
from lib_py3.timing import Timings

from minecraft.world import World

def usage():
    sys.exit("Usage: {} <--world /path/to/world> [--logfile <stdout|stderr|path>] [--num-threads num] [--dry-run]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:l:j:d", ["world=", "logfile=", "num-threads=", "dry-run"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
logfile = None
num_threads = 4
dry_run = False

for o, a in opts:
    if o in ("-w", "--world"):
        world_path = a
    elif o in ("-l", "--logfile"):
        logfile = a
    elif o in ("-j", "--num-threads"):
        num_threads = int(a)
    elif o in ("-d", "--dry-run"):
        print("Running in dry-run mode, changes will not be saved")
        dry_run = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None:
    eprint("--world or --schematics must be specified!")
    usage()

timings = Timings(enabled=dry_run)

log_handle = None
if logfile == "stdout":
    log_handle = sys.stdout
elif logfile == "stderr":
    log_handle = sys.stderr
elif logfile is not None:
    log_handle = open(logfile, 'w')

def process_entity(entity, replacements_log) -> None:
    nbt = entity.nbt

    if nbt.has_path("Offers.Recipes"):
        recipes_list = nbt.at_path("Offers.Recipes").value
        new_recipes_list = []
        modified = False
        for recipe in recipes_list:
            is_vanilla_trade = False
            for path in ["buy", "buyB", "sell"]:
                if recipe.has_path(f"{path}.id") and "emerald" in recipe.at_path(f"{path}.id").value:
                    is_vanilla_trade = True
            for path in ["buy", "buyB", "sell"]:
                if recipe.has_path(f"{path}.tag.display.Name") or recipe.has_path(f"{path}.tag.display.Lore"):
                    is_vanilla_trade = False

            if not is_vanilla_trade:
                # Still a good trade to keep, copy it
                new_recipes_list.append(recipe)
            else:
                # Don't copy this to the new list, and note that the lists are different
                modified = True

        if modified:
            orig_mojangson = nbt.to_mojangson()
            nbt.at_path("Offers.Recipes").value = new_recipes_list

            key = entity.get_path_str()
            if key not in replacements_log:
                replacements_log[key] = {}

                replacements_log[key]["NAME"] = get_entity_name_from_nbt(nbt)
                replacements_log[key]["TO"] = nbt.to_mojangson()
                replacements_log[key]["FROM"] = orig_mojangson
            else:
                eprint(f"WARNING: Got duplicate entity key {key}")

            return True
    return False

def process_region(region):
    replacements_log = {}
    num_replacements = 0
    for chunk in region.iter_chunks(autosave=(not dry_run)):
        for entity in chunk.recursive_iter_entities():
            if process_entity(entity, replacements_log):
                num_replacements += 1

    return (num_replacements, replacements_log)

if world_path:
    world = World(world_path)
    timings.nextStep("Loaded world")

    parallel_results = world.iter_regions_parallel(process_region, num_processes=num_threads)
    timings.nextStep("World replacements done")

num_replacements = 0
replacements_to_merge = []
for region_result in parallel_results:
    num_replacements += region_result[0]
    replacements_to_merge.append(region_result[1])

replacements_log = MobReplacementManager.merge_logs(replacements_to_merge)
timings.nextStep("Logs merged")

if log_handle is not None:
    yaml.dump(replacements_log, log_handle, width=2147483647, allow_unicode=True)
    timings.nextStep("Logs written")

if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
    log_handle.close()

print("{} mobs replaced".format(num_replacements))

