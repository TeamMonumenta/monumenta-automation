#!/usr/bin/env python3

import sys
import getopt
import json
from pprint import pprint

from lib_py3.common import eprint
from minecraft.world import World

def usage():
    sys.exit("Usage: {} <--world /path/to/world> <--output file.json> [--pos1 x,y,z --pos2 x,y,z] [--dry-run]".format(sys.argv[0]))

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["world=", "output=", "pos1=", "pos2=", "dry-run"])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    world_path = None
    output_path = None
    pos1 = None
    pos2 = None
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
    pos1, pos2 = ((min(pos1[0], pos2[0]), min(pos1[1], pos2[1]), min(pos1[2], pos2[2])), (max(pos1[0], pos2[0]), max(pos1[1], pos2[1]), max(pos1[2], pos2[2])))

    out = []
    for region in world.iter_regions(pos1[0], pos1[1], pos1[2], pos2[0], pos2[1], pos2[2]):
        for chunk in region.iter_chunks(pos1[0], pos1[1], pos1[2], pos2[0], pos2[1], pos2[2]):
            for block_entity in chunk.iter_block_entities(pos1[0], pos1[1], pos1[2], pos2[0], pos2[1], pos2[2]):
                if not block_entity.nbt.has_path('RequiredPlayerRange'):
                    continue

                source_pos = block_entity.pos
                if source_pos is None:
                    continue

                if block_entity.nbt.at_path('RequiredPlayerRange').value == 16:
                    entry = {}
                    entry['pos'] = source_pos
                    entry['orig_RequiredPlayerRange'] = block_entity.nbt.at_path('RequiredPlayerRange').value
                    entry['new_RequiredPlayerRange'] = 12

                    if not dry_run:
                        block_entity.nbt.at_path('RequiredPlayerRange').value = 12

                    out.append(entry)

    with open(output_path, 'w') as outfile:
        json.dump(out, outfile, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))
