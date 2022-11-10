#!/usr/bin/env pypy3

from datetime import datetime

import sys
import getopt
import math
from minecraft.world import World

def usage():
    sys.exit(f"Usage: {sys.argv[0]} <existing world path>")

try:
    opts, args = getopt.getopt(sys.argv[1:], "", [])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

if len(args) < 1:
    usage()

from_path = args[0]

for o, a in opts:
    eprint("Unknown argument: {}".format(o))
    usage()

start = datetime.now()

source_world = World(from_path)
source_world.defragment()

print(datetime.now() - start)
