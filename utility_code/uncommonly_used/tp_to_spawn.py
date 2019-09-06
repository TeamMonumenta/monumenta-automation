#!/usr/bin/env python3

import sys

from score_change_list import dungeon_score_rules
from lib_py3.terrain_reset import terrain_reset_instance

def get_dungeon_config(name, scoreboard):
    return {
        "server":name,
        "localDstFolder":"/home/epic/project_epic/{0}/Project_Epic-{0}/".format(name),
        "tagPlayers":["MidTransfer","resetMessage"],
        "tpToSpawn":True,
    }

region_1 = {
    "server":"region_1",
    "localDstFolder":"/home/epic/project_epic/region_1/Project_Epic-region_1/",
    "tpToSpawn":True,
    "tagPlayers":["MidTransfer","resetMessage"],
}

available_configs = {
    "betaplots": None,
    "plots": None,
    "region_1": region_1,
    "white": get_dungeon_config("white", "D1Access"),
    "orange": get_dungeon_config("orange", "D2Access"),
    "magenta": get_dungeon_config("magenta", "D3Access"),
    "lightblue": get_dungeon_config("lightblue", "D4Access"),
    "yellow": get_dungeon_config("yellow", "D5Access"),
    "willows": get_dungeon_config("willows", "DB1Access"),
    "reverie": get_dungeon_config("reverie", "DCAccess"),
    "roguelike": None, # TODO
    "build": None,
    "tutorial": None,
    "bungee": None,
    "purgatory": None,
    #"rollback": nov17_plots_rollback,
}

if (len(sys.argv) < 2):
    sys.exit("Usage: {} <server1> [server2] ...".format(sys.argv[0]))

reset_name_list = []
reset_config_list = []
for arg in sys.argv[1:]:
    if arg in available_configs:
        reset_name_list.append(arg)
        if available_configs[arg] is not None:
            reset_config_list.append(available_configs[arg])
    else:
        print("ERROR: Unknown shard {} specified!".format(arg))
        sys.exit("Usage: {} <server1> [server2] ...".format(sys.argv[0]))

for config in reset_config_list:
    terrain_reset_instance(config)

print("Shards reset successfully: {}".format(reset_name_list))
