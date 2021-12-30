#!/usr/bin/env python3

import getopt
import os
import sys
import yaml
from pprint import pprint

from lib_py3.common import eprint

from minecraft.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

def usage():
    sys.exit("Usage: {} <--world /path/to/world> [--logfile <stdout|stderr|path>]".format(sys.argv[0]))

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "w:l", ["world=", "logfile="])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    world_path = None
    logfile = None

    for o, a in opts:
        if o in ("-w", "--world"):
            world_path = a
        elif o in ("-l", "--logfile"):
            logfile = a
        else:
            eprint("Unknown argument: {}".format(o))
            usage()

    if not world_path:
        eprint("--world must be specified!")
        usage()

    log_handle = sys.stdout
    if logfile == "stdout":
        log_handle = sys.stdout
    elif logfile == "stderr":
        log_handle = sys.stderr
    elif logfile is not None:
        log_handle = open(logfile, 'w')


    BAD_BLOCK_ENTITY_TAG = nbt.TagCompound.from_mojangson("""{Items:[],x:0,id:"minecraft:chest",z:0,y:0}""")

    known_bad_items = {}
    affected_loot_chests = 0

    world = World(world_path)
    for region in world.iter_regions(read_only=True):
        for chunk in region.iter_chunks():
            for item in chunk.recursive_iter_items():
                if item.nbt.count_multipath("tag.display.Lore") == 0:
                    # Broken items must have lore, or they're assumed to be successfully opened
                    continue

                if not item.nbt.has_path("tag.BlockEntityTag"):
                    continue
                if item.nbt.at_path("tag.BlockEntityTag") != BAD_BLOCK_ENTITY_TAG:
                    # If items don't have this compound, they weren't broken by the bug in question
                    continue

                key = item.get_path_str()
                if key not in known_bad_items:
                    known_bad_items[key] = {}
                known_bad_items[key][item.slot] = item.to_command_format(include_count=True)
                affected_loot_chests += item.count

    yaml.dump(known_bad_items, log_handle, width=2147483647, allow_unicode=True)
    print(f'Logged {affected_loot_chests} bad loot chests')
