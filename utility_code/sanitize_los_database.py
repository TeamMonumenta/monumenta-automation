#!/usr/bin/env python3

import os
import sys
import json
from typing import cast
from lib_py3.common import get_entity_name_from_nbt
from argparse import ArgumentParser
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

from quarry.types.nbt import TagCompound

def load_souls_db(file: str):
    with open(file, "r") as fp:
        souls = json.load(fp)
    
    return (cast(list, souls["souls"]), cast(int, souls["data_version"]))

def write_souls_db(file: str, souls: list, dataVersion: int):
    with open(file, "w") as fp:
        json.dump({
            "souls": souls,
            "data_version": dataVersion
        }, fp)

def process_soul(soul, timestamp_max: int | None):
    if "location_names" in soul and len(soul["location_names"]) > 0:
        # Only keep the most recent history element
        entries = soul["history"] if timestamp_max is None else list(filter(lambda s: s["modified_on"] <= timestamp_max, soul["history"]))

        if len(entries) != 0:
            soul["history"] = entries
            return soul

def main(file: str, timestamp_max: int | None):
    with open(file, "r") as fp:
        souls = json.load(fp)

    location_set = set()

    for soul in souls:
        if "location_names" in soul:
            for loc in soul["location_names"]:
                location_set.add(loc)

    print("Removed mobs:")
    new_souls = []
    for soul in souls:
        processed_soul = process_soul(soul, timestamp_max)

        if processed_soul is None:
            name = get_entity_name_from_nbt(TagCompound.from_mojangson(soul["history"][0]["mojangson"]), True)
            print("  " + name)
        else:
            new_souls.append(soul)

    print("\n\n\nAll locations:")
    for name in sorted(location_set):
        print("  " + name)

    with open(sys.argv[1], "w") as fp:
        json.dump(new_souls, fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

if __name__ == '__main__':
    args = ArgumentParser()
    args.add_argument("--before", type = int, required = False)
    args.add_argument("file")
    parsed = args.parse_args(sys.argv)

    main(parsed.file, parsed.before)
