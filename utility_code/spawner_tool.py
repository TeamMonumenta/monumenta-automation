#!/usr/bin/env pypy3

import os
import getopt
import math
import multiprocessing
import sys
import traceback
import yaml

from lib_py3.common import eprint
from lib_py3.timing import Timings

from minecraft.chunk_format.schematic import Schematic
from minecraft.chunk_format.structure import Structure
from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.world import World
from replace_mobs import match_name

def usage():
    sys.exit("Usage: {} <--worlds /path/to/folder_containing_worlds | --world /path/to/world | --schematics /path/to/schematics | --structures /path/to/structures> [--pos1 x,y,z --pos2 x,y,z] [--logfile <stdout|stderr|path>] [--num-threads num] [--dry-run] [--force]".format(sys.argv[0]))

def set_spawn_range(spawner, spawn_range):
    spawner.nbt.at_path("SpawnRange").value = 1

# A rule matches a mob in the spawner, the lambda takes the spawner itself
rules = [
    (match_name('Vinelacquer Cluster'), lambda spawner: set_spawn_range(spawner, 1)),
    (match_name('Nightmare Cluster'), lambda spawner: set_spawn_range(spawner, 1)),
]

# This is handy here because it has direct access to previously defined globals
def process_entity(entity, replacements_log) -> bool:
    if not isinstance(entity, BlockEntity):
        return False

    # Skip entities outside the specified area
    if (entity.pos is not None and
        (
         entity.pos[0] < min_x or
         entity.pos[1] < min_y or
         entity.pos[2] < min_z or
         entity.pos[0] > max_x or
         entity.pos[1] > max_y or
         entity.pos[2] > max_z
        )):
        return False

    nbt = entity.nbt
    if nbt.has_path("SpawnPotentials"):

        # The rule index that matches this spawner
        match_idx = None
        # The action to take on a successful match
        match_action = None

        for nested_entity in nbt.iter_multipath('SpawnPotentials[]'):
            for i in range(len(rules)):
                rule = rules[i]
                if rule[0](nested_entity):
                    if match_action is not None:
                        sys.exit(f"Mob matched more than one rule! Problematic rules are {i} and {match_idx} which both matched spawner entity {nested_entity}")

                    match_action = rule[1]
                    match_idx = i

        if nbt.has_path("SpawnData"):
            ent = nbt.at_path("SpawnData.entity")
            for i in range(len(rules)):
                rule = rules[i]
                if rule[0](ent):
                    if match_action is not None:
                        sys.exit(f"Mob matched more than one rule! Problematic rules are {i} and {match_idx} which both matched spawner entity {ent}")

                    match_action = rule[1]
                    match_idx = i

        if match_action is not None:
            spawner_before = nbt.to_mojangson()
            match_action(entity)
            spawner_after = nbt.to_mojangson()
            replacements_log[entity.get_path_str()] = {"before": spawner_before, "after": spawner_after}

            return True

    return False

def process_init(dry, f, minx, miny, minz, maxx, maxy, maxz):
    global dry_run, force, min_x, min_y, min_z, max_x, max_y, max_z
    dry_run = dry
    force = f
    min_x = minx
    min_y = miny
    min_z = minz
    max_x = maxx
    max_y = maxy
    max_z = maxz


def process_region(region):
    replacements_log = {}
    num_replacements = 0
    for chunk in region.iter_chunks(autosave=(not dry_run)):
        for entity in chunk.recursive_iter_all_types():
            changed_something = process_entity(entity, replacements_log)
            if changed_something:
                num_replacements += 1

    return (num_replacements, replacements_log)

def process_schematic_or_structure(obj):
    replacements_log = {}
    num_replacements = 0

    for entity in obj.recursive_iter_all_types():
        changed_something = process_entity(entity, replacements_log)
        if changed_something:
            num_replacements += 1

    if not dry_run and num_replacements > 0:
        obj.save()

    return (num_replacements, replacements_log)

def err_func(ex, args):
    eprint(f"Caught exception: {ex}")
    eprint(f"While iterating: {args}")
    eprint(traceback.format_exc())
    return (0, {})

def merge_log_tuples(log_dicts_to_merge, out_log_dict={}):
    """Merges mob replacements log tuples. out_log_dict can be specified to merge multiple different result generators into the same output

    Returns a tuple(num_replacements, {dict})"""

    num_replacements = 0
    for replacements, log_dict in log_dicts_to_merge:
        num_replacements += replacements
        for log_key in log_dict:
            if log_key not in out_log_dict:
                # Cheat and just reference the entire structure in the output
                out_log_dict[log_key] = log_dict[log_key]
            else:
                for orig_tag_mojangson in log_dict[log_key]["FROM"]:
                    if orig_tag_mojangson not in out_log_dict[log_key]["FROM"]:
                        out_log_dict[log_key]["FROM"][orig_tag_mojangson] = []

                    for debug_path in log_dict[log_key]["FROM"][orig_tag_mojangson]:
                        out_log_dict[log_key]["FROM"][orig_tag_mojangson].append(debug_path)
    return num_replacements, out_log_dict

if __name__ == '__main__':
    # Note that this currently needs to be 'fork' and not 'spawn' because pypy can't pickle the lambdas used by mob substitutions
    # Can move the line that loads the substitutions into the process init handler, but then it's slower than without any multiprocessing
    # Will leave this as fork for now, this script seems pretty reliable
    multiprocessing.set_start_method("fork")

    try:
        opts, args = getopt.getopt(sys.argv[1:], "z:w:s:g:b:l:j:dif", ["worlds=", "world=", "schematics=", "structures=", "logfile=", "num-threads=", "dry-run", "pos1=", "pos2=", "force"])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    worlds_path = None
    world_path = None
    schematics_path = None
    structures_path = None
    pos1 = [-math.inf, -math.inf, -math.inf]
    pos2 = [math.inf, math.inf, math.inf]
    logfile = None
    num_threads = 4
    dry_run = False
    force = False

    for o, a in opts:
        if o in ("-z", "--worlds"):
            worlds_path = a
        elif o in ("-w", "--world"):
            world_path = a
        elif o in ("-s", "--schematics"):
            schematics_path = a
        elif o in ("-s", "--structures"):
            structures_path = a
        elif o in ("--pos1",):
            try:
                split = a.split(",")
                pos1 = (int(split[0]), int(split[1]), int(split[2]))
            except Exception:
                eprint("Invalid --pos1 argument")
                usage()
        elif o in ("--pos2",):
            try:
                split = a.split(",")
                pos2 = (int(split[0]), int(split[1]), int(split[2]))
            except Exception:
                eprint("Invalid --pos2 argument")
                usage()
        elif o in ("-l", "--logfile"):
            logfile = a
        elif o in ("-j", "--num-threads"):
            num_threads = int(a)
        elif o in ("-d", "--dry-run"):
            dry_run = True
        elif o in ("-f", "--force"):
            force = True
        else:
            eprint("Unknown argument: {}".format(o))
            usage()

    if worlds_path is None and world_path is None and schematics_path is None and structures_path is None:
        eprint("--worlds, --world, --schematics, or --structures must be specified!")
        usage()

    min_x = min(pos1[0], pos2[0])
    min_y = min(pos1[1], pos2[1])
    min_z = min(pos1[2], pos2[2])
    max_x = max(pos1[0], pos2[0])
    max_y = max(pos1[1], pos2[1])
    max_z = max(pos1[2], pos2[2])

    timings = Timings(enabled=dry_run)

    log_handle = None
    if logfile == "stdout":
        log_handle = sys.stdout
    elif logfile == "stderr":
        log_handle = sys.stderr
    elif logfile is not None:
        log_handle = open(logfile, 'w')

    num_replacements = 0
    replacements_log = {}

    if world_path or worlds_path:
        worlds = []
        if world_path:
            worlds.append(world_path)
        if worlds_path:
            for worldname in World.enumerate_worlds(worlds_path):
                worlds.append(os.path.join(worlds_path, worldname))

        for world_path in worlds:
            world = World(world_path)
            timings.nextStep("Loaded world")

            generator = world.iter_regions_parallel(process_region, err_func, num_processes=num_threads, initializer=process_init, initargs=(dry_run, force, min_x, min_y, min_z, max_x, max_y, max_z))
            replacements, replacements_log = merge_log_tuples(generator, replacements_log)
            num_replacements += replacements

            timings.nextStep(f"World replacements done, {replacements} replacements")

    if schematics_path:
        # Note: autosave=False is because we only save schematics that had some item replacements in them
        generator = Schematic.iter_schematics_parallel(schematics_path, process_schematic_or_structure, err_func, num_processes=num_threads, autosave=False, initializer=process_init, initargs=(dry_run, force, min_x, min_y, min_z, max_x, max_y, max_z))
        replacements, replacements_log = merge_log_tuples(generator, replacements_log)
        num_replacements += replacements

        timings.nextStep(f"Schematics replacements done, {replacements} replacements")

    if structures_path:
        # Note: autosave=False is because we only save structures that had some item replacements in them
        generator = Structure.iter_structures_parallel(structures_path, process_schematic_or_structure, err_func, num_processes=num_threads, autosave=False, initializer=process_init, initargs=(dry_run, force, min_x, min_y, min_z, max_x, max_y, max_z))
        replacements, replacements_log = merge_log_tuples(generator, replacements_log)
        num_replacements += replacements

        timings.nextStep(f"Structures replacements done, {replacements} replacements")

    if log_handle is not None:
        yaml.dump(replacements_log, log_handle, width=2147483647, allow_unicode=True)
        timings.nextStep("Logs written")

    if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
        log_handle.close()

    print("{} spawners modified".format(num_replacements))
