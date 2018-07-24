#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys

from StringIO import StringIO
import traceback

import multiprocessing as mp

from lib_monumenta.repair_block_entities import repair_block_entities

sys.argv.pop(0)

if len(sys.argv) == 0:
    print("No specified shards on this server.")
    exit()

def attempt_on_shard(worldDir,statusQueue):
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    status = {"worldDir":worldDir}

    if not os.path.isdir(worldDir):
        print("No such directory: " + worldDir)
        return
    try:
        repair_block_entities(worldDir)
        print("Done with world: " + worldDir)
    except:
        print("Caught exception on world:" + worldDir)
        print(traceback.format_exc())
        pass

    sys.stdout = old_stdout
    status["msg"] = mystdout.getvalue()
    statusQueue.put(status)

processes = {}
statusQueue = mp.Queue()
for worldDir in sys.argv:
    processes[worldDir] = mp.Process(target=attempt_on_shard, args=(worldDir, statusQueue))

for p in processes.values():
    p.start()

while len(processes.keys()) > 0:
    statusUpdate = statusQueue.get()
    statusFrom = statusUpdate["worldDir"]
    
    p = processes[statusFrom]
    p.join()
    processes.pop(statusFrom)
    
    print("Results from {}:".format(statusFrom))
    if "msg" in statusUpdate:
        print(statusUpdate["msg"]),
    print("Done with {}.\n".format(statusFrom))

print "Done!"

