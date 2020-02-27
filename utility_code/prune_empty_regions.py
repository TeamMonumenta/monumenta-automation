#!/usr/bin/python3

import sys
from lib_py3.world import World

args = sys.argv
name = args.pop(0)
if len(sys.argv) == 0:
    print("Usage: {} /path/to/world1 [/path/to/world2 ...]".format(name))
    sys.exit()

while len(args) >= 1:
    worldPath = args.pop(0)
    print("\n\n\nPruning empty regions from {}...".format(worldPath))

    w = World(worldPath)
    w.prune()
