#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
import demjson
import collections
import traceback

def print_tag_as_replacement(itemType, tag):
    # Remove type specifiers for JSON parsing
    sanitizedTag = re.sub(r'(:[-\.0-9]+)[lLsSbBfFdD]*', r'\1', tag)

    # May throw exception
    decoded = demjson.decode(sanitizedTag)

    # Don't replace normal potion types
    if "minecraft:potion" in itemType:
        return;

    # Only automatically replace items that have display names
    if "display" in decoded:
        if "Name" in decoded["display"]:
            # Remove formatting codes from name if present
            itemName = re.sub(u'§[a-z0-9]', '', decoded["display"]["Name"])

            print >> sys.stderr, itemType + " - " + itemName

            print '\t['
            print '\t\t{'
            print '\t\t\t"id":"' + itemType + '",'
            print '\t\t\t"name":u\'\'\'' + itemName + '\'\'\','
            print '\t\t}'
            print '\t\t['
            print '\t\t\t"nbt", "replace", ur\'\'\'' + tag + '\'\'\''
            print '\t\t]'
            print '\t],'

# Apply NBT tag fixups to all NBT strings found in a loot table file
def fixup_file(filePath):
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(filePath) as old_file:
            lastType = "";
            for line in old_file:
                # Read lines from original file, modify them, and write them to the new file

                # Only operate on tag strings
                m = re.search(r'(^\s*"name":\s*")(.*)"\s*,*\s*$', line)
                if m:
                    preamble = m.group(1)
                    lastType = m.group(2)

                m = re.search(r'(^\s*"tag":\s*")(\{.*})"\s*$', line)
                if m:
                    preamble = m.group(1)
                    tag = m.group(2)

                    # Remove backslashes
                    tag = tag.replace("\\", "")

                    try:
                        print_tag_as_replacement(lastType, tag)

                    except Exception:
                        print >> sys.stderr, "Skipping file: " + filePath
                        print >> sys.stderr, "Failing tag was: '" + tag + "'"
                        traceback.print_exc()
                        print >> sys.stderr, "This is only a warning, processing will continue for other items"
                        print >> sys.stderr, ""
                        print >> sys.stderr, ""
                        return

if ((len(sys.argv) != 2) or (not os.path.isdir(sys.argv[1]))):
    sys.exit("Usage: " + sys.argv[0] + " </path/to/loot_tables>")

lootPath = sys.argv[1]

for root, dirs, files in os.walk(lootPath):
    for file in files:
        if file.endswith(".json"):
             filePath = os.path.join(root, file)
             #print(filePath)
             fixup_file(filePath)

sys.exit("Done")
