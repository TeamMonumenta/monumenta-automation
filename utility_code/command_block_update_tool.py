#!/usr/bin/env python3

import sys
import getopt
import json
from pprint import pprint, pformat

from lib_py3.common import eprint
from lib_py3.world import World

def usage():
    sys.exit("Usage: {} <--world /path/to/world> <--output file.json | --input file.json> [--pos1 x,y,z --pos2 x,y,z]".format(sys.argv[0]))


try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["world=", "output=", "input=", "pos1=", "pos2="])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
output_path = None
input_path = None
pos1 = None
pos2 = None

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
        json.dump(out, outfile, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

else:
    elif (pos1 is not None) or (pos2 is not None):
        sys.exit("--pos1 and --pos2 only make sense with output mode")

    # Load the data
    # key = "x y z"
    # value = { pos/command/name/auto/powered }
    commands = {}
    with open(input_path, 'r') as outfile:
        data = json.load(outfile)
        for element in data:
            if "pos" in element:
                key = "{} {} {}".format(element["pos"][0], element["pos"][1], element["pos"][2])
                commands[key] = element
            else:
                eprint("Warning: Skipping command without position: " + pformat(element))

    for entity, source_pos, entity_path in world.entity_iterator(pos1=pos1, pos2=pos2, readonly=False):
        if source_pos is not None and entity.has_path('Command'):
            key = "{} {} {}".format(source_pos[0], source_pos[1], source_pos[2])
            command_to_load = commands.get(key, None)
            if command_to_load is not None:
                entity.at_path('Command').value = command_to_load["command"]

            # TODO: This stuff was used to restore commands and upgrade stuff from 1.13. It's probably not needed anymore
            # from update_lore_everywhere import process_one_command
            # command_to_load = commands.get(key, None)
            # if command_to_load is not None:
            #     if not entity.at_path('Command').value.strip() and command_to_load["command"].strip():
            #         entity.at_path('Command').value = command_to_load["command"]
            #         print("")
            #         print("Command at {} is empty, restored to '{}'".format(key, command_to_load["command"]))
            #
            # orig_command = entity.at_path('Command').value
            # updated_command = process_one_command(orig_command)
            # if updated_command is not None:
            #     print("")
            #     print("LOC : " + key)
            #     print("ORIG: " + orig_command)
            #     print("NEW : " + updated_command)
            #     entity.at_path('Command').value = updated_command

