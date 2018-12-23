#!/usr/bin/env python3

import os
import sys
import codecs
import traceback
import json

from lib_py3.json_file import jsonFile
from lib_py3.common import eprint
from lib_py3.common import remove_formatting

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

gverbose = False

def replacements_from_loot_table(loot_table):
    result = ""
    if type(loot_table) != dict:
        raise TypeError('loot_table is type {}, not type dict'.format(type(loot_table)))
    if "pools" not in loot_table:
        return ""
    if type(loot_table["pools"]) != list:
        raise TypeError('loot_table["pools"] is type {}, not type list'.format(type(loot_table["pools"])))
    for pool in loot_table["pools"]:
        if type(pool) != dict:
            raise TypeError('pool is type {}, not type dict'.format(type(pool)))
        if "entries" not in pool:
            continue
        if type(pool["entries"]) != list:
            raise TypeError('pool["entries"] is type {}, not type list'.format(type(pool["entries"])))
        for entry in pool["entries"]:
            if type(entry) != dict:
                raise TypeError('entry is type {}, not type dict'.format(type(entry)))
            if "type" not in entry:
                continue
            if entry["type"] != "item":
                continue
            if "name" not in entry:
                continue
            item_id = entry["name"]
            # Don't replace normal potion types
            if item_id in ["minecraft:potion","minecraft:splash_potion","minecraft:lingering_potion"]:
                continue
            if "functions" not in entry:
                continue
            if type(entry["functions"]) != list:
                raise TypeError('entry["functions"] is type {}, not type list'.format(type(entry["functions"])))
            item_tag_json = None
            item_name = None
            for function in entry["functions"]:
                if type(function) != dict:
                    raise TypeError('function is type {}, not type dict'.format(type(function)))
                if "function" not in function:
                    continue
                function_type = function["function"]
                if function_type == "set_nbt":
                    if "tag" not in function:
                        continue
                    item_tag_json = function["tag"]
                    item_tag_nbt = nbt.TagCompound.from_mojangson(item_tag_json)
                    #item_tag_nbt.tree()
                    if (
                        "display" not in item_tag_nbt.value or
                        "Name" not in item_tag_nbt.value["display"].value
                    ):
                        continue
                    item_name = item_tag_nbt.value["display"].value["Name"].value
                    item_name = remove_formatting(item_name)
                    # If the item name is JSON, parse it down to just the name text
                    try:
                        name_json = json.loads(item_name)
                        if "text" in name_json:
                            item_name = name_json["text"]
                    except:
                        eprint("WARNING: Item '" + item_name + "isn't json!")


            if item_tag_json is None:
                continue
            if item_name is None:
                continue
            if gverbose:
                eprint(item_id + " - " + item_name)
            result += u"  [\n"
            result += u"    {\n"
            result += u"      'id':'" + item_id + u"',\n"
            result += u"      'name':u'''" + item_name + u"''',\n"
            result += u"    },\n"
            result += u"    [\n"
            result += u"      'nbt', 'replace', ur'''" + item_tag_json + u"'''\n"
            result += u"    ]\n"
            result += u"  ],\n"
    return result

def usage():
    sys.exit("Usage: " + sys.argv[0] + " [-v, --verbose] </path/to/output/replace_list> </path/to/loot_tables> <dir2> ...")

# Main entry point
if (len(sys.argv) < 3):
    usage()

replaceListDir = None
lootFolders = [];
for arg in sys.argv[1:]:
    if (arg == "--verbose"):
        gverbose = True
    elif (arg == "-v"):
        gverbose = True
    elif replaceListDir is None:
        replaceListDir = arg
    else:
        if (not os.path.isdir(arg)):
            usage()
        lootFolders += [arg,]

if (len(lootFolders) < 1):
    eprint("ERROR: No folders specified")
    usage()

try:
    f = open(replaceListDir, "w", encoding="utf-8")
except:
    eprint("ERROR: Cannot write to output file {}".format(replaceListDir))
    usage()
with f:
    f.write(r'''#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from lib_monumenta import item_replace

KingsValleyLootTables = item_replace.ReplaceItems([],[
''')
    for lootPath in lootFolders:
        for root, dirs, files in os.walk(lootPath):
            for aFile in files:
                if aFile.endswith(".json"):
                    filePath = os.path.join(root, aFile)
                    try:
                        #print(filePath)
                        loot_table = jsonFile(filePath)
                        newEntries = replacements_from_loot_table(loot_table.dict)
                        f.write(newEntries)
                    except:
                        eprint("Error parsing '" + filePath + "'")
                        eprint(str(traceback.format_exc()))
    f.write(u'''])''')
    f.close()

if gverbose:
    eprint("Done")
