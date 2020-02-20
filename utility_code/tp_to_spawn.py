#!/usr/bin/env python3

import sys

from lib_py3.terrain_reset import terrain_reset_instance

if (len(sys.argv) < 2):
    sys.exit("Usage: {} <server1> [server2] ...".format(sys.argv[0]))

valid_names = (
    "region_1",
    "region_2",
    "white",
    "orange",
    "magenta",
    "lightblue",
    "yellow",
    "lime",
    "pink",
    "gray",
    "lightgray",
    "cyan",
    "purple",
    "willows",
    "reverie",
    "sanctum",
    "labs",
    "shiftingcity",
    "roguelike",
    "tutorial",
)

reset_name_list = []
reset_config_list = []
for arg in sys.argv[1:]:
    if arg in valid_names:
        reset_name_list.append(arg)
        reset_config_list.append({
            "server":arg,
            "localDstFolder":"{0}/Project_Epic-{0}/".format(arg),
            "tpToSpawn":True,
        })
    else:
        print("ERROR: Unknown shard {} specified!".format(arg))
        sys.exit("Usage: {} <server1> [server2] ...".format(sys.argv[0]))

for config in reset_config_list:
    terrain_reset_instance(config)

print("Shards reset successfully: {}".format(reset_name_list))
