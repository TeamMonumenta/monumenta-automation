#!/usr/bin/env pypy3

import sys
import getopt
import math
from minecraft.world import World

def usage():
    sys.exit(f"Usage: {sys.argv[0]} <existing world path> <new world path>")

try:
    opts, args = getopt.getopt(sys.argv[1:], "", [])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

if len(args) < 2:
    usage()

from_path = args[0]
dest_path = args[1]

for o, a in opts:
    eprint("Unknown argument: {}".format(o))
    usage()

source_world = World(from_path)
source_world.defragment_to(dest_path, clear_world_uuid=True)
