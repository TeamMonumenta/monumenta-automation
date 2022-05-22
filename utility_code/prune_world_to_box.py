#!/usr/bin/env python3

import sys
import os
import pprint
import getopt

from minecraft.world import World

def usage():
    sys.exit(f"Usage: {sys.argv[0]} --world /path/to/world [--pos1 x,y,z] [--pos2 x,y,z]")

try:
    opts, args = getopt.getopt(sys.argv[1:], "j:", ["world=", "pos1=", "pos2="])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
pos1 = (-math.inf, -math.inf, -math.inf)
pos2 = (math.inf, math.inf, math.inf)

for o, a in opts:
    if o in ("--world",):
        world_path = a
    elif o in ("--pos1",):
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

if world_path is None:
    eprint("--world must be specified!")
    usage()

world = World(world_path)

min_x = min(pos1[0], pos2[0])
min_z = min(pos1[2], pos2[2])
max_x = max(pos1[0], pos2[0])
max_z = max(pos1[2], pos2[2])

minxregion = min_x//512
minzregion = min_z//512
maxxregion = max_x//512
maxzregion = max_z//512
for region in world.iter_regions:
    if region.rx < minxregion or region.rx > maxxregion or region.rz < minzregion or region.rz > maxzregion:
        print("rm", os.path.join(world.path, "region", "r.{}.{}.mca".format(region.rx, region.rz)))

