#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys

from lib_monumenta.json_file import jsonFile
from lib_monumenta.item_replace import removeFormatting

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
from pymclevel import nbt

def replacements_from_loot_table(loot_table):
    if "pools" not in loot_table:
        return
    for pool in loot_table["pools"]:
        if "entries" not in pool:
            continue
        for entry in pool["entries"]:
            if "type" not in entry:
                continue
            if entry["type"] != "item":
                continue
            if "name" not in entry:
                continue
            item_id = entry["name"]
            # Don't replace normal potion types
            if "minecraft:potion" in item_id:
                continue
            if "functions" not in entry:
                continue
            item_tag_json = None
            item_name = None
            for function in entry["functions"]:
                if "function" not in function:
                    continue
                function_type = function["function"]
                if function_type == "set_nbt":
                    if "tag" not in function:
                        continue
                    item_tag_json = function["tag"]
                    item_tag_nbt = nbt.json_to_tag(item_tag_json)
                    if (
                        "display" not in item_tag_nbt or
                        "name" not in item_tag_nbt["display"]
                    ):
                        continue
                    item_name = item_tag_nbt["display"]["name"].value
                    item_name = removeFormatting(item_name)
            if item_name is None:
                continue
            if item_tag_json is None:
                continue
            if gverbose:
                print >> sys.stderr, item_id + " - " + item_name
            print "  ["
            print "    {"
            print "      'id':'{" + item_id + "}',"
            print "      'name':u'''" + item_name + "''',"
            print "    },"
            print "    ["
            print "      'nbt', 'replace', ur'''" + tag + "'''"
            print "    ]"
            print "  ],"

def usage():
    sys.exit("Usage: " + sys.argv[0] + " [--verbose] </path/to/loot_tables> <dir2> ...")

# Main entry point
if (len(sys.argv) < 2):
    usage()

lootFolders = [];
for arg in sys.argv[1:]:
    if (arg == "--verbose"):
        gverbose = True
    else:
        if (not os.path.isdir(arg)):
            usage()
        lootFolders += [arg,]

if (len(lootFolders) < 1):
    print "ERROR: No folders specified"
    usage()

for lootPath in lootFolders:
    for root, dirs, files in os.walk(lootPath):
        for file in files:
            if file.endswith(".json"):
                 filePath = os.path.join(root, file)
                 #print(filePath)
                 loot_table = jsonFile(filePath)
                 #fixup_file(filePath)
                 replacements_from_loot_table(loot_table.dict)

if gverbose:
    print >> sys.stderr, "Done"
