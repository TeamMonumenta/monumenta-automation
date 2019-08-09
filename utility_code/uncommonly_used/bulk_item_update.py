#!/usr/bin/env python3

import os
import sys
import getopt
from pprint import pprint

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from lib_py3.common import eprint
from lib_py3.loot_table_manager import LootTableManager


def usage():
    sys.exit("Usage: {} --input /path/to/file".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "i:", ["input=",])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

input_path = None

for o, a in opts:
    if o in ("-i", "--input"):
        input_path = a
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if input_path is None:
    eprint("--input argument required")
    usage()

mgr = LootTableManager()

mgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")

failed = []
succeeded = []

processed = 0
with open(input_path) as f:
    allargs = f.readlines()
    for commandArgs in allargs:
        try:
            if '{' not in commandArgs:
                raise Exception("Item must be of the form minecraft:id{nbt}")

            # Parse id / nbt arguments
            partitioned = commandArgs.strip().partition("{")
            item_id = partitioned[0].strip()
            item_nbt_str = partitioned[1] + partitioned[2].strip()

            if item_id.startswith("/"):
                item_id = item_id[1:]
            if item_id.startswith("give @p "):
                item_id = item_id[len("give @p "):]

            if item_nbt_str[-1] != '}':
                item_nbt_str = item_nbt_str[:item_nbt_str.rfind("}") + 1]

            mgr = LootTableManager()
            #mgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")
            mgr.load_loot_tables_subdirectories("/home/epic/MCEdit-And-Automation/utility_code/uncommonly_used/datapacks")
            locations = mgr.update_item_in_loot_tables(item_id, item_nbt_str=item_nbt_str)

            succeeded.append(commandArgs)

        except Exception as e:
            failed.append((commandArgs, str(e)))
        processed += 1
        print("Processed: {}/{}".format(processed, len(allargs)))

print("\n\nSucceeded:\n")
pprint(succeeded)
print("\n\n\n\n\n\n\n\n\n\n\n\nFailed:\n")
pprint(failed)
print("\n\n\n\n\n\n\n\n\n\n\n\nFailed (errors only):\n")
pprint([x[1] for x in failed])
