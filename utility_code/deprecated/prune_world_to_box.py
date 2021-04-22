#!/usr/bin/env python3

import sys
import os
import pprint

from lib_py3.world import World

world = World("Project_Epic-test")

minxregion = -1137//512 - 1
minzregion = -397//512 - 1
maxxregion = -350//512 + 1
maxzregion = 390//512 + 1
for region in world.region_files:
    if region[0] < minxregion or region[0] > maxxregion or region[1] < minzregion or region[1] > maxzregion:
        print("rm", os.path.join(world.path, "region", "r.{}.{}.mca".format(region[0], region[1])))

