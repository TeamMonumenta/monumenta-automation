#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
from lib_monumenta.repair_block_entities import repair_block_entities

sys.argv.pop(0)

if len(sys.argv) == 0:
    print("No specified shards on this server.")
    exit()

def attempt_on_shard(worldDir):
    if not os.path.isdir(worldDir):
        print("No such directory: " + worldDir)
        return
    try:
        repair_block_entities(worldDir)
        print("Done with world: " + worldDir)
    except:
        print("Caught exception on world:" + worldDir)
        pass

for worldDir in sys.argv:
    attempt_on_shard(worldDir)
print("Done.")

