#!/usr/bin/env python3

# For interactive shell
import readline
import code

import sys
import getopt
import json
from pprint import pprint

from lib_py3.common import eprint
from lib_py3.world import World

def usage():
    sys.exit("Usage: {} <--world /path/to/world> <--output file.json> [--pos1 x,y,z --pos2 x,y,z] [--interactive] [--dry-run]".format(sys.argv[0]))


try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["world=", "output=", "pos1=", "pos2=", "interactive", "dry-run"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
output_path = None
pos1 = None
pos2 = None
interactive = False
dry_run = False

for o, a in opts:
    if o in ("--world"):
        world_path = a
    elif o in ("--output"):
        output_path = a
    elif o in ("--pos1"):
        try:
            split = a.split(",")
            pos1 = (int(split[0]), int(split[1]), int(split[2]))
        except:
            eprint("Invalid --pos1 argument")
            usage()
    elif o in ("--pos2"):
        try:
            split = a.split(",")
            pos2 = (int(split[0]), int(split[1]), int(split[2]))
        except:
            eprint("Invalid --pos2 argument")
            usage()
    elif o in ("--interactive"):
        interactive = True
    elif o in ("--dry-run"):
        dry_run = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None:
    eprint("--world must be specified!")
    usage()
elif output_path is None:
    eprint("--output must be specified!")
    usage()
elif ((pos1 is not None) and (pos2 is None)) or ((pos1 is None) and (pos2 is not None)):
    eprint("--pos1 and --pos2 must be specified (or neither specified)!")
    usage()

world = World(world_path)

out = []
for entity, source_pos, entity_path in world.entity_iterator(pos1=pos1, pos2=pos2, readonly=dry_run):
    if source_pos is not None and entity.has_path('RequiredPlayerRange'):
        block = world.get_block(source_pos)["block"]
        block_name = block['name']

        if entity.at_path('RequiredPlayerRange').value == 16:
            entry = {}
            entry['pos'] = source_pos
            entry['orig_RequiredPlayerRange'] = entity.at_path('RequiredPlayerRange').value
            entry['new_RequiredPlayerRange'] = 12

            if not dry_run:
                entity.at_path('RequiredPlayerRange').value = 12

            out.append(entry)

with open(output_path, 'w') as outfile:
    json.dump(out, outfile, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': '))

if interactive:
    print("Starting interactive mode")
    print("output dataset is 'out'")
    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.interact()
