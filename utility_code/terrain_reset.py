#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).
"""

import sys

from lib_monumenta.terrain_reset import terrainReset
from shard_reset import allConfigDict

itemCountLog = "/home/rock/5_SCRATCH/tmpreset/all_items.txt"

if (len(sys.argv) < 2):
    sys.exit("Usage: {} <server1> [server2] ...".format(sys.argv[0]))

configList = []
resetList = []
for arg in sys.argv[1:]:
    if arg in allConfigDict:
        resetList.append(arg)
        if allConfigDict[arg] is not None:
            configList.append(allConfigDict[arg])
    else:
        print "ERROR: Unknown shard {} specified!".format(arg)
        sys.exit("Usage: {} <server1> [server2] ...".format(sys.argv[0]))

terrainReset(configList)
print "Saving items found after replacement to {}".format(itemCountLog)
print "Shards reset successfully: {}".format(resetList)

