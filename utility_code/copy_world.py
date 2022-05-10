#!/usr/bin/env pypy3

import sys
import getopt
import math
from minecraft.world import World

def usage():
    sys.exit(f"Usage: {sys.argv[0]} <existing world path> <new world path> [--pos1 x,y,z] [--pos2 x,y,z]")

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["pos1=", "pos2="])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

from_path = args[0]
dest_path = args[1]

pos1 = (-math.inf, -math.inf, -math.inf)
pos2 = (math.inf, math.inf, math.inf)

for o, a in opts:
    if o in ("--pos1",):
        try:
            split = a.split(",")
            pos1 = (int(split[0]), int(split[1]), int(split[2]))
        except:
            eprint("Invalid --pos1 argument")
            usage()
    elif o in ("--pos2",):
        try:
            split = a.split(",")
            pos2 = (int(split[0]), int(split[1]), int(split[2]))
        except:
            eprint("Invalid --pos2 argument")
            usage()
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

source_world = World(from_path)
source_world.copy_to(dest_path, clear_world_uuid=True, min_x=pos1[0], min_y=pos1[1], min_z=pos1[2], max_x=pos2[0], max_y=pos2[1], max_z=pos2[2])
