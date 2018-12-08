#!/usr/bin/python3

import os
import sys
import json
from collections import OrderedDict

allowedTypes = (
    ".json",
)


advancements_removed = (
    "monumenta:speedster/r1/all",
    "monumenta:speedster/r1/high_to_low/0",
    "monumenta:speedster/r1/high_to_low/1",
    "monumenta:speedster/r1/high_to_low/2",
    "monumenta:speedster/r1/high_to_low/3",
    "monumenta:speedster/r1/mariyas_game/0",
    "monumenta:speedster/r1/mariyas_game/1",
    "monumenta:speedster/r1/mariyas_game/2",
    "monumenta:speedster/r1/mariyas_game/3",
    "monumenta:speedster/r1/tree_hopping_madness/0",
    "monumenta:speedster/r1/tree_hopping_madness/1",
    "monumenta:speedster/r1/tree_hopping_madness/2",
    "monumenta:speedster/r1/tree_hopping_madness/3",
    "monumenta:speedster/r1/tutorial_plus/0",
    "monumenta:speedster/r1/tutorial_plus/1",
    "monumenta:speedster/r1/tutorial_plus/2",
    "monumenta:speedster/r1/tutorial_plus/3",
)

advancements_renamed = (
    (r'''"C'Taz"''',r'''"C\u0027Taz"'''),
    (r'''"Ta'Eldim"''',r'''"Ta\u0027Eldim"'''),
)

def fix_file(filePath):
    advancements_json = ""
    print (filePath)
    with open(filePath, "rb") as fp:
        advancements_json = json.load(fp, object_pairs_hook=OrderedDict)

    # Manipulate here
    for remove in advancements_removed:
        advancements_json.pop(remove, None)

    outstr = json.dumps(advancements_json, indent=2)
    for rename in advancements_renamed:
        outstr = outstr.replace(rename[0], rename[1])

    with open(filePath, "w") as fp:
        fp.write(outstr)

def usage():
    sys.exit("Usage: {} </path/to/advancements1> [/path/to/advancements2] ...".format(sys.argv[0]))

if (len(sys.argv) < 2):
    usage()

folders_to_walk = []
for arg in sys.argv[1:]:
    if os.path.isdir(arg):
        folders_to_walk.append(arg)
    else:
        print("ERROR: Folder '{}' does not exist!".format(arg))
        usage()

for folder_path in folders_to_walk:
    for folderInfo in os.walk(folder_path):
        folder=folderInfo[0]
        files =folderInfo[2]
        for fileName in files:
            for aType in allowedTypes:
                if fileName[-len(aType):] == aType:
                    filePath = folder+'/'+fileName
                    if os.path.isfile(filePath):
                        print(filePath)
                        fix_file(filePath)

