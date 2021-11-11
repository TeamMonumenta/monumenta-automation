#!/usr/bin/env python3

import sys
import os
from minecraft.world import World

args = sys.argv

if len(args) != 3:
    print("Usage: copy_world <existing world path> <new world path>")
    sys.exit(1)

from_path = args[1]
dest_path = args[2]

source_world = World(from_path)
source_world.copy_to(dest_path)
