#!/usr/bin/env python3

import os
import sys
import traceback
import json

from lib_py3.json_file import jsonFile
from lib_py3.common import eprint
from lib_py3.common import remove_formatting
from lib_py3.loot_table_manager import LootTableManager

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

gverbose = False

def replacements_from_loot_table(loot_table):
    result = ""
    return result

def usage():
    sys.exit("Usage: " + sys.argv[0] + " [-v, --verbose] </path/to/loot_tables> <dir2> ...")

# Main entry point
if (len(sys.argv) < 2):
    usage()

loot_folders = [];
for arg in sys.argv[1:]:
    if (arg == "--verbose"):
        gverbose = True
    elif (arg == "-v"):
        gverbose = True
    else:
        if (not os.path.isdir(arg)):
            usage()
        loot_folders += [arg,]

if (len(loot_folders) < 1):
    eprint("ERROR: No folders specified")
    usage()

mgr = LootTableManager()

for loot_path in loot_folders:
    mgr.load_loot_tables_subdirectories(loot_path)

replacements = mgr.get_as_replacements()
#print(replacements)

