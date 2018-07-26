#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
This replaces items within the build server
"""

import sys

from lib_monumenta.terrain_reset import terrainReset
from shard_build import allConfigDict

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
print "Shards reset successfully: {}".format(resetList)

