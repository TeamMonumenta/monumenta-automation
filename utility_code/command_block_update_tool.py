#!/usr/bin/env python3

# For interactive shell
import readline
import code

import sys
import getopt
import json
from pprint import pprint

from score_change_list import dungeon_score_rules
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.common import eprint, get_item_name_from_nbt
from lib_py3.world import World
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path

def usage():
    sys.exit("Usage: {} <--world /path/to/world> <--output file.json | --input file.json> [--pos1 x,y,z --pos2 x,y,z] [--interactive]".format(sys.argv[0]))


try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["world=", "output=", "input=", "pos1=", "pos2=", "interactive"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
output_path = None
input_path = None
pos1 = None
pos2 = None
interactive = False

for o, a in opts:
    if o in ("--world"):
        world_path = a
    elif o in ("--output"):
        output_path = a
    elif o in ("--input"):
        input_path = a
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
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None:
    eprint("--world must be specified!")
    usage()
elif (input_path is None) and (output_path is None):
    eprint("Either --input or --output must be specified!")
    usage()
elif (input_path is not None) and (output_path is not None):
    eprint("Only one of --input or --output can be specified!")
    usage()
elif ((pos1 is not None) and (pos2 is None)) or ((pos1 is None) and (pos2 is not None)):
    eprint("--pos1 and --pos2 must be specified (or neither specified)!")
    usage()


world = World(world_path)

output_mode = (input_path is None)

if output_mode:
    out = []
    for entity, source_pos, entity_path in world.entity_iterator(pos1=pos1, pos2=pos2, readonly=True):
        if source_pos is not None and entity.has_path('Command'):
            block = world.get_block(source_pos)["block"]
            block_name = block['name']

            #pprint(block)
            #entity.tree()
            #break;

            entry = {}
            entry['pos'] = source_pos
            entry['command'] = entity.at_path('Command').value
            entry['name'] = block_name
            entry['auto'] = entity.at_path('auto').value
            entry['powered'] = entity.at_path('powered').value

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
else:
    if interactive:
        sys.exit("--interactive only makes sense with output mode")
    elif (pos1 is not None) or (pos2 is not None):
        sys.exit("--pos1 and --pos2 only make sense with output mode")

    # Load the data
    data = []
    with open(input_path, 'r') as outfile:
        data = json.load(outfile)

    #TODO
    eprint("ERROR WIP")
