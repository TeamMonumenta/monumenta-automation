#!/usr/bin/env python3

import sys
import os
import json
import re
from pprint import pprint

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

from lib_py3.common import eprint, parse_name_possibly_json, get_named_hand_items

def usage():
    sys.exit("Usage: {} nbt_in.txt nbt_out.py".format(sys.argv[0]))

if len(sys.argv) != 3:
    usage()


with open(sys.argv[1], 'r') as in_file:
    with open(sys.argv[2], 'w') as out_file:
        out_file.write("mobs_to_replace = [\n")

        line = in_file.readline()
        while line:
            mob_nbt = nbt.TagCompound.from_mojangson(line)

            if not mob_nbt.has_path("id"):
                sys.exit("ERROR: mob does not have an id! : {}".format(line))

            mob_id = mob_nbt.at_path("id").value

            if mob_nbt.has_path("CustomName"):
                mob_name = parse_name_possibly_json(mob_nbt.at_path("CustomName").value)

                out_file.write("    {\n")
                out_file.write("        'rules': {\n")
                out_file.write("            'id': '{}',\n".format(mob_id))
                out_file.write("            'CustomName': r'''{}'''\n".format(mob_name))
                out_file.write("        },\n")
                out_file.write("        'mojangson': r'''{}''',\n".format(line.strip()))
                out_file.write("    },\n")
            else:
                hand_items = get_named_hand_items(mob_nbt)

                if hand_items[0] is None and hand_items[1] is None:
                    sys.exit("ERROR: mob does not have a name or named HandItems! : {}".format(line))

                out_file.write("    {\n")
                out_file.write("        'rules': {\n")
                out_file.write("            'id': '{}',\n".format(mob_id))
                out_file.write("            'HandItems': {},\n".format(hand_items))
                out_file.write("        },\n")
                out_file.write("        'mojangson': r'''{}''',\n".format(line.strip()))
                out_file.write("    },\n")



            line = in_file.readline()

        out_file.write("]\n")
