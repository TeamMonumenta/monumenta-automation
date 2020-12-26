#!/usr/bin/env python3


import os
import sys
import getopt
import json
from pprint import pprint

from lib_py3.common import eprint
from lib_py3.upgrade import upgrade_entity
from lib_py3.world import World

def usage():
    sys.exit("Usage: {} <--world /path/to/world> [--logfile <stdout|stderr|path>] [--dry-run]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:l:diu", ["world=", "logfile=", "dry-run"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
logfile = None
dry_run = False

for o, a in opts:
    if o in ("-w", "--world"):
        world_path = a
    elif o in ("-l", "--logfile"):
        logfile = a
    elif o in ("-d", "--dry-run"):
        dry_run = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None:
    eprint("--world must be specified!")
    usage()

world = World(world_path)

log_handle = None
if logfile == "stdout":
    log_handle = sys.stdout
elif logfile == "stderr":
    log_handle = sys.stderr
elif logfile is not None:
    log_handle = open(logfile, 'w')

num_updates = 0
updates = []
for entity in world.base_entity_iterator(readonly=dry_run):
    try:
        orig = entity.deep_copy()
        upgrade_entity(entity)
        if entity != orig:
            update = {"Original": orig.to_mojangson(), "Upgraded": entity.to_mojangson()}
            updates.append(update)
            num_updates += 1
    except Exception as e:
        print(f"Failed to upgrade {orig.to_mojangson()}: {e}")
        entity.value = orig.value

if log_handle is not None:
    json.dump(updates, log_handle, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
    log_handle.close()

print(f"Upgraded {num_updates} entities")
