#!/usr/bin/env python3

import sys

from score_change_list import dungeon_score_rules
from lib_py3.terrain_reset import terrain_reset_instance

def get_dungeon_config(name, scoreboard):
    return {
        "server":name,
        "localMainFolder":"/home/rock/5_SCRATCH/tmpreset/PRE_RESET/{0}/Project_Epic-{0}/".format(name),
        "localBuildFolder":"/home/rock/5_SCRATCH/tmpreset/TEMPLATE/{0}/Project_Epic-{0}/".format(name),
        "localDstFolder":"/home/rock/5_SCRATCH/tmpreset/POST_RESET/{0}/Project_Epic-{0}/".format(name),
        "copyBaseFrom":"build",
        "copyMainPaths":["advancements", "playerdata", "stats", "data"],
        "playerScoreChanges":dungeon_score_rules,
        "preserveInstance":{
            "dungeonScore":scoreboard,
            "targetRegion":{"x":-3, "z":-2},
        },
        "tagPlayers":["MidTransfer","resetMessage"],
        "tpToSpawn":True,
    }

betaplots = {
    "server":"betaplots",

    "localMainFolder":"/home/rock/5_SCRATCH/tmpreset/PRE_RESET/betaplots/Project_Epic-betaplots/",
    "localDstFolder":"/home/rock/5_SCRATCH/tmpreset/POST_RESET/betaplots/Project_Epic-betaplots/",

    "copyBaseFrom":"main",

    "tagPlayers":["MidTransfer","resetMessage"],
    "playerScoreChanges":dungeon_score_rules,
}

r1plots = {
    "server":"r1plots",

    "localMainFolder":"/home/rock/5_SCRATCH/tmpreset/PRE_RESET/r1plots/Project_Epic-r1plots/",
    "localDstFolder":"/home/rock/5_SCRATCH/tmpreset/POST_RESET/r1plots/Project_Epic-r1plots/",

    "copyBaseFrom":"main",

    "tagPlayers":["MidTransfer","resetMessage"],
    "playerScoreChanges":dungeon_score_rules,
}

region_1 = {
    "server":"region_1",

    # Dst is the destination world, which gets overwritten by the build world.
    # Then, data from the main world replaces the relevant parts of the dst world.
    # Please note that no special care need be taken with whitespace in filenames.
    "localMainFolder":"/home/rock/5_SCRATCH/tmpreset/PRE_RESET/region_1/Project_Epic-region_1/",
    "localBuildFolder":"/home/rock/5_SCRATCH/tmpreset/TEMPLATE/region_1/Project_Epic-region_1/",
    "localDstFolder":"/home/rock/5_SCRATCH/tmpreset/POST_RESET/region_1/Project_Epic-region_1/",

    # Reset dungeon scores
    "playerScoreChanges":dungeon_score_rules,

    "tpToSpawn":True,
    "tagPlayers":["MidTransfer","resetMessage"],

    "coordinatesToFill":(
        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
            "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
    ),

    # Which folder to copy the base world from. Either "build", "main", or not set
    "copyBaseFrom":"build",
    "copyMainPaths":["advancements", "playerdata", "stats", "data"],

    "coordinatesToCopy":(
        # "name":"a unique name"
        # "pos1":(x1,y1,z1)
        # "pos2":(x2,y2,z2)
        {"name":"Apartments_101-132",     "pos1":( -811,  99,   44), "pos2":(-873,  99,   44)},
        {"name":"Apartments_201-232",     "pos1":( -811,  99,   36), "pos2":(-873,  99,   36)},
        {"name":"Apartments_301-332",     "pos1":( -811,  99,   31), "pos2":(-873,  99,   31)},
        {"name":"Apartments_401-432",     "pos1":( -811,  99,   23), "pos2":(-873,  99,   23)},
        {"name":"Apartments_501-524",     "pos1":( -815,  99,   10), "pos2":(-861,  99,   10)},
        {"name":"Apartments_601-624",     "pos1":( -815,  99,    5), "pos2":(-861,  99,    5)},
        {"name":"Apartments_701-816",     "pos1":( -811,  99,   18), "pos2":(-873,  99,   18)},
        {"name":"Apartments_units",       "pos1":( -817, 109,   87), "pos2":(-859, 164,   16)},
        {"name":"Guild_Room",             "pos1":( -800, 109,  -75), "pos2":(-758, 104, -102)},
        {"name":"Guild_1",                "pos1":( -586,   0,  137), "pos2":(-622, 255,  105)},
        {"name":"Guild_2",                "pos1":( -570,   0,  112), "pos2":(-534, 255,  154)},
        {"name":"Guild_3",                "pos1":( -581,   0,  150), "pos2":(-613, 255,  186)},
        {"name":"Guild_4",                "pos1":( -649,   0,  275), "pos2":(-617, 255,  311)},
        {"name":"Guild_5",                "pos1":( -683,   0,  275), "pos2":(-651, 255,  311)},
        {"name":"Guild_6",                "pos1":( -685,   0,  275), "pos2":(-717, 255,  311)},
        {"name":"Guild_7",                "pos1":( -816,   0,  235), "pos2":(-780, 255,  267)},
        {"name":"Guild_8",                "pos1":( -832,   0,  257), "pos2":(-868, 255,  289)},
        {"name":"Guild_9",                "pos1":( -816,   0,  269), "pos2":(-780, 255,  301)},
        {"name":"Guild_10",               "pos1":( -937,   0,  272), "pos2":(-969, 255,  308)},
        {"name":"Guild_11",               "pos1":( -969,   0,  256), "pos2":(-937, 255,  220)},
        {"name":"Guild_12",               "pos1":( -958,   0,  104), "pos2":(-994, 255,  136)},
        {"name":"Guild_14",               "pos1":( -958,   0,   70), "pos2":(-994, 255,  102)},
        {"name":"Guild_15",               "pos1":( -581,   0,  -64), "pos2":(-613, 255, -100)},
        {"name":"Guild_18",               "pos1":( -942,   0,   93), "pos2":(-906, 255,  125)},
        {"name":"Guild_20",               "pos1":( -751,   0, -230), "pos2":(-787, 255, -198)},
        {"name":"Guild_21",               "pos1":( -787,   0, -232), "pos2":(-751, 255, -264)},
        {"name":"Guild_22",               "pos1":( -600,   0, -191), "pos2":(-564, 255, -159)},
        {"name":"Guild_23",               "pos1":( -615,   0, -180), "pos2":(-651, 255, -212)},
        {"name":"Guild_24",               "pos1":( -564,   0, -192), "pos2":(-600, 255, -224)},
        {"name":"Guild_26",               "pos1":( -596,   0,  -46), "pos2":(-564, 255,  -10)},
        {"name":"Guild_27",               "pos1":( -548,   0,  -64), "pos2":(-580, 255, -100)},
    ),
}

available_configs = {
    "betaplots": betaplots,
    "r1plots": r1plots,
    "region_1": region_1,
    "white": get_dungeon_config("white", "D1Access"),
    "orange": get_dungeon_config("orange", "D2Access"),
    "magenta": get_dungeon_config("magenta", "D3Access"),
    "lightblue": get_dungeon_config("lightblue", "D4Access"),
    "yellow": get_dungeon_config("yellow", "D5Access"),
    "r1bonus": get_dungeon_config("r1bonus", "DB1Access"),
    "nightmare": get_dungeon_config("nightmare", "DCAccess"),
    "roguelike": None, # TODO
    "build": None,
    "tutorial": None,
    "bungee": None,
    "purgatory": None,
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
