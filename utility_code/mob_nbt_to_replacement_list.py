#!/usr/bin/env python3

import sys
import os
import json
import re
from pprint import pprint

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

from lib_py3.common import eprint

def usage():
    sys.exit("Usage: {} nbt_in.txt nbt_out.py".format(sys.argv[0]))

if len(sys.argv) != 3:
    usage()

def get_name(name):
    name = re.sub(r"\\u0027", "'", name)
    try:
        name_json = json.loads(name)
        if "text" in name_json:
            name = name_json["text"]
    except:
        pass
    return name


with open(sys.argv[1], 'r') as in_file:
    with open(sys.argv[2], 'w') as out_file:
        out_file.write("mobs_to_replace = [\n")

        line = in_file.readline()
        while line:
            mob_nbt = nbt.TagCompound.from_mojangson(line)

            if not mob_nbt.has_path("id"):
                sys.exit("ERROR: mob does not have an id! : {}".format(line))

            if mob_nbt.has_path("CustomName"):
                mob_id = mob_nbt.at_path("id").value
                mob_name = get_name(mob_nbt.at_path("CustomName").value)

                out_file.write("    {\n")
                out_file.write("        'rules': {\n")
                out_file.write("            'id': '{}'\n".format(mob_id))
                out_file.write("            'CustomName': '{}'\n".format(mob_name))
                out_file.write("        },\n")
                out_file.write("        'nbt': r'''{}''',\n".format(line.strip()))
                out_file.write("    },\n")
            else:
                if not mob_nbt.has_path("HandItems"):
                    sys.exit("ERROR: mob does not have a name or HandItems! : {}".format(line))

                hand_items = []
                hand_items_nbt = mob_nbt.at_path("HandItems")
                named_item_found = False

                if len(hand_items_nbt.value) != 2:
                    sys.exit("NOT IMPLEMENTED: Mob has hand items length != 2 : {}".format(line))

                for hand_item in hand_items_nbt.value:
                    if hand_item.has_path("tag.display.Name"):
                        item_name = get_name(hand_item.at_path("tag.display.Name").value)
                        # Sorta janky - put quotes around the item name here
                        hand_items.append("'{}'".format(item_name))
                        named_item_found = True
                    else:
                        hand_items.append(None)

                if not named_item_found:
                    sys.exit("ERROR: mob does not have a name or named HandItems! : {}".format(line))


                out_file.write("    {\n")
                out_file.write("        'rules': {\n")
                out_file.write("            'id': '{}',\n".format(mob_id))
                out_file.write("            'HandItems': [{}, {}],\n".format(hand_items[0], hand_items[1]))
                out_file.write("        },\n")
                out_file.write("        'nbt': r'''{}''',\n".format(line.strip()))
                out_file.write("    },\n")



            line = in_file.readline()

        out_file.write("]\n")
