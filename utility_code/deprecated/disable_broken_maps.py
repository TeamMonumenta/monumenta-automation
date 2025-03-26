#!/usr/bin/env pypy3

import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

os.chdir(sys.argv[1])

good_map_path = None
for file in os.listdir('.'):
    filename = os.fsdecode(file)
    path = filename
    if filename.startswith("map_") and filename.endswith(".dat"):
        try:
            root_tag = nbt.NBTFile.load(path).root_tag.value[""]
            dimension = root_tag.at_path("data.dimension").value
            if not root_tag.has_path("DataVersion"):
                continue
            data_version = root_tag.at_path("DataVersion").value
            if str(dimension) == "minecraft:overworld" and data_version == 3700:
                good_map_path = path
                print(f"Found good map {good_map_path} with version 3700")
                break
        except Exception as e:
            print(f"{filename}: failed to load: {e}")

if good_map_path is None:
    print(f"Couldn't find good map in folder {sys.argv[1]}")
    exit(1)

for file in os.listdir("."):
    filename = os.fsdecode(file)
    path = filename
    if filename.startswith("map_") and filename.endswith(".dat"):
        try:
            dimension = nbt.NBTFile.load(path).root_tag.value[""].at_path("data.dimension").value
            if dimension == 0:
                print(f"Disabled {path}")
                os.rename(path, path + ".disabled")
                os.symlink(good_map_path, path)
        except Exception as e:
            print(f"{filename}: failed to load: {e}")
