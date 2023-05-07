#!/usr/bin/env python3

import os
import sys
import json
from lib_py3.library_of_souls import LibraryOfSouls

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

from quarry.types import nbt

if len(sys.argv) != 2:
    sys.exit(f"Usage: {sys.argv[0]} <output_path.json>")
out_name = sys.argv[1]

los = LibraryOfSouls("/home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json", readonly=True)
los.refresh_index()

outdata = []
for soul_name in los._index:
    soul = los._index[soul_name]
    location_names = soul["location_names"]
    lore = soul["lore"]
    current_data = soul["history"][0]
    last_modified_by = current_data["modified_by"]
    last_modified_on = current_data["modified_on"]
    current_nbt = nbt.TagCompound.from_mojangson(current_data["mojangson"])

    json_out = {
        "location_names": location_names,
        "lore": lore,
        "last_modified_by": last_modified_by,
        "last_modified_on": last_modified_on,
        "nbt": current_nbt.to_json(),
        "name": soul_name,
    }

    outdata.append(json_out)

with open(out_name, 'w') as outfile:
    json.dump(outdata, outfile, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))
