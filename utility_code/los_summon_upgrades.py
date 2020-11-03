#!/usr/bin/env python3

import sys
import os
import re
import json
from pprint import pprint
from lib_py3.library_of_souls import LibraryOfSouls

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

from quarry.types import nbt
from quarry.types.nbt import TagCompound
from quarry.types.nbt import TagString

los = LibraryOfSouls("./data/plugins/all/LibraryOfSouls/souls_database.json")
los.upgrade_all()

def upgrade_line_nbt_format(line: str) -> str:
    # Note the non-greedy match on the NBT
    # This might return something embedded in " " (if it's in a JSON file)
    matches = re.match('''^(.*)summon  *([^ ]*)  *([-~^\.0-9]*)  *([-~^\.0-9]*)  *([-~^\.0-9]*)  *(\{.*?)([\r\n, "]*)$''', line)
    if matches:
        try:
            # summon command
            groups = matches.groups()
            prefix = groups[0]
            mobid = groups[1].lower()
            if not mobid.startswith("minecraft:"):
                mobid = "minecraft:" + mobid

            try:
                mobnbt = TagCompound.from_mojangson(groups[5])
                nbtstr = TagCompound.to_mojangson(los.upgrade_nbt(mobnbt))
            except Exception as e:
                try:
                    testjson = '"' + groups[5] + '"'
                    mobnbt = TagCompound.from_mojangson(json.loads(testjson))
                    nbtstr = json.dumps(TagCompound.to_mojangson(los.upgrade_nbt(mobnbt)), ensure_ascii=False)
                    nbtstr = nbtstr[1:-1]
                except Exception as e:
                    print("Failed to parse mojangson directly or as embedded json")
                    raise e

            newline = "{}summon {} {} {} {} {}{}".format(prefix, groups[1], groups[2], groups[3], groups[4], nbtstr, groups[6])
            line = newline
        except Exception as e:
            print("Failed to process {}: {}".format(path, e))

    return line

def upgrade_line_to_los(line: str) -> str:
    # Note the non-greedy match on the NBT
    # This might return something embedded in " " (if it's in a JSON file)
    matches = re.match('''^(.*)summon  *([^ ]*)  *([-~^\.0-9]*)  *([-~^\.0-9]*)  *([-~^\.0-9]*)  *(\{.*?)([\r\n, "]*)$''', line)
    if matches:
        try:
            # summon command
            groups = matches.groups()
            prefix = groups[0]
            mobid = groups[1].lower()
            if not mobid.startswith("minecraft:"):
                mobid = "minecraft:" + mobid

            if mobid not in ["minecraft:armor_stand", "minecraft:villager", "minecraft:area_effect_cloud", "minecraft:falling_block", "minecraft:potion", "minecraft:item", "minecraft:shulker"]:
                try:
                    mobnbt = TagCompound.from_mojangson(groups[5])
                except Exception as e:
                    try:
                        testjson = '"' + groups[5] + '"'
                        mobnbt = TagCompound.from_mojangson(json.loads(testjson))
                    except Exception as e:
                        print("Failed to parse mojangson directly or as embedded json")
                        raise e

                if mobnbt.has_path("CustomName"):
                    mobnbt.value["id"] = TagString(mobid)
                    name = los.add_soul(mobnbt)
                    newline = "{}los summon {} {} {} {}{}".format(prefix, groups[2], groups[3], groups[4], name, groups[6])
                    print("####################################################################################################")
                    print("Replace:\n\n")
                    print("         ", line)
                    print("\nWith:\n\n")
                    print("         ", newline)
                    inp = input("Enter = yes, other = no:")
                    if inp:
                        print("Skipping")
                    else:
                        print("Added")
                        line = newline
        except Exception as e:
            print("Failed to process {}: {}".format(path, e))

    return line


for root, subdirs, files in os.walk("data"):
    for fname in files:
        if fname.endswith(".json") or fname.endswith(".mcfunction"):
            path = os.path.join(root, fname)
            lines = []
            with open(path, 'r') as fp:
                lines = fp.readlines()
            newlines = []
            for line in lines:
                newlines.append(upgrade_line_nbt_format(line))
            with open(path, 'w') as fp:
                fp.writelines(newlines)

los.save()
