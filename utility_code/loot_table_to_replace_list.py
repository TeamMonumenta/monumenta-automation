#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import codecs
import traceback

from lib_monumenta.json_file import jsonFile
from lib_monumenta.item_replace import removeFormatting

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
from pymclevel import nbt

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
                    item_tag_nbt = nbt.json_to_tag(item_tag_json)
                    if (
                        "display" not in item_tag_nbt or
                        "Name" not in item_tag_nbt["display"]
                    ):
                        continue
                    item_name = item_tag_nbt["display"]["Name"].value
                    item_name = removeFormatting(item_name)
            if item_tag_json is None:
                continue
            if item_name is None:
                continue
            if gverbose:
                print >> sys.stderr, item_id + " - " + item_name
            result += u"  [\n"
            result += u"    {\n"
            result += u"      'id':'{" + item_id + u"}',\n"
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
    print "ERROR: No folders specified"
    usage()

try:
    f = codecs.getwriter('utf8')(open(replaceListDir, "w"))
except:
    print "ERROR: Cannot write to output file {}".format(replaceListDir)
    usage()

with f:
    f.write(u'''#!/usr/bin/env python2.7
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
                        print >> sys.stderr, "Error parsing '" + filePath + "'"
                        print >> sys.stderr, str(traceback.format_exc())
    f.write(u'''])''')
    f.close()

if gverbose:
    print >> sys.stderr, "Done"
