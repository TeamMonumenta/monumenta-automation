#!/usr/bin/env pypy3

import os
import getopt
import math
import multiprocessing
import sys

from lib_py3.common import eprint
from replace_mobs import match_name, match_id, err_func

from minecraft.chunk_format.schematic import Schematic
from minecraft.chunk_format.structure import Structure
from minecraft.chunk_format.entity import Entity
from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.world import World

def usage():
    """Prints usage"""
    sys.exit("Usage: {} <--worlds /path/to/folder_containing_worlds | --world /path/to/world | --schematics /path/to/schematics | --structures /path/to/structures> [--pos1 x,y,z --pos2 x,y,z] [--logfile <stdout|stderr|path>] [--num-threads num]".format(sys.argv[0]))

def process_entity(entity) -> None:
    """Checks if an entity matches"""
    if not isinstance(entity, Entity) and not isinstance(entity, BlockEntity):
        return None

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
        return None

    if matcher(entity.nbt):
        return entity.get_path_str()

    return None

def process_init(match, minx, miny, minz, maxx, maxy, maxz):
    """Sets up global variables for process initialization"""
    global matcher, min_x, min_y, min_z, max_x, max_y, max_z
    matcher = match
    min_x = minx
    min_y = miny
    min_z = minz
    max_x = maxx
    max_y = maxy
    max_z = maxz

def process_region(region):
    """Processes one region file"""
    return_msgs = []
    num_matches = 0
    for chunk in region.iter_chunks(autosave=False):
        for entity in chunk.recursive_iter_all_types():
            msg = process_entity(entity)
            if msg:
                num_matches += 1
                return_msgs.append(msg)

    return (num_matches, return_msgs)

def process_schematic_or_structure(obj):
    """Processes one schematic file"""
    return_msgs = []
    num_matches = 0

    for entity in obj.recursive_iter_all_types():
        msg = process_entity(entity)
        if msg:
            num_matches += 1
            return_msgs.append(msg)

    return (num_matches, return_msgs)

if __name__ == '__main__':
    # Note that this currently needs to be 'fork' and not 'spawn' because pypy can't pickle the lambdas used by mob substitutions
    # Can move the line that loads the substitutions into the process init handler, but then it's slower than without any multiprocessing
    # Will leave this as fork for now, this script seems pretty reliable
    multiprocessing.set_start_method("fork")

    try:
        opts, args = getopt.getopt(sys.argv[1:], "z:w:s:l:j:d", ["worlds=", "world=", "schematics=", "structures=", "logfile=", "num-threads=", "pos1=", "pos2=", "force"])
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

    for o, a in opts:
        if o in ("-z", "--worlds"):
            worlds_path = a
        elif o in ("-w", "--world"):
            world_path = a
        elif o in ("-s", "--schematics"):
            schematics_path = a
        elif o in ("--structures",):
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

    log_handle = None
    if logfile == "stdout":
        log_handle = sys.stdout
    elif logfile == "stderr":
        log_handle = sys.stderr
    elif logfile is not None:
        log_handle = open(logfile, 'w')

    num_matches = 0
    found_msgs = []

    # TODO: This is the code that needs to be exposed via the command line - anything that works in replace_mobs can work here too.
    #matcher = match_id('minecraft:iron_golem')
    matcher = match_name('Fungusborn Brute')

    if world_path or worlds_path:
        worlds = []
        if world_path:
            worlds.append(world_path)
        if worlds_path:
            for worldname in World.enumerate_worlds(worlds_path):
                worlds.append(os.path.join(worlds_path, worldname))

        for world_path in worlds:
            world = World(world_path)

            for found, msgs in world.iter_regions_parallel(process_region, err_func, num_processes=num_threads, initializer=process_init, initargs=(matcher, min_x, min_y, min_z, max_x, max_y, max_z)):
                num_matches += found
                found_msgs += msgs

    if schematics_path:
        for found, msgs in Schematic.iter_schematics_parallel(schematics_path, process_schematic_or_structure, err_func, num_processes=num_threads, autosave=False, initializer=process_init, initargs=(matcher, min_x, min_y, min_z, max_x, max_y, max_z)):
            num_matches += found
            found_msgs += msgs

    if structures_path:
        for found, msgs in Structure.iter_structures_parallel(structures_path, process_schematic_or_structure, err_func, num_processes=num_threads, autosave=False, initializer=process_init, initargs=(matcher, min_x, min_y, min_z, max_x, max_y, max_z)):
            num_matches += found
            found_msgs += msgs

    if log_handle is not None:
        for msg in found_msgs:
            log_handle.write(msg)
            log_handle.write("\n")

    if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
        log_handle.close()

    print("{} matching mobs found".format(num_matches))
