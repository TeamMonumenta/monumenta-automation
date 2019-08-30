#!/usr/bin/env python3

import os
import sys
import datetime
import codecs
import multiprocessing as mp
import tempfile
import traceback

from score_change_list import dungeon_score_rules
from lib_py3.terrain_reset import terrain_reset_instance
from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.common import eprint

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

datapacks_default = ['file/vanilla','file/bukkit']
datapacks_base = datapacks_default + ['file/base']
datapacks_dungeon = datapacks_base + ['file/dungeon']

loot_table_manager = LootTableManager()
loot_table_manager.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")
item_replace_manager = ItemReplacementManager(loot_table_manager.get_unique_item_map(show_errors=False))

# Log replacements separately by shard name
def log_replacements(log_handle, shard_name, replacements_log):
    log_handle.write("\n\n")
    log_handle.write("################################################################################\n")
    log_handle.write("# SHARD: {}\n\n".format(shard_name))

    for to_item in replacements_log:
        log_handle.write("{}\n".format(to_item))
        log_handle.write("    TO:\n")
        log_handle.write("        {}\n".format(replacements_log[to_item]["TO"]))
        log_handle.write("    FROM:\n")

        if update_tables:
            to_nbt = nbt.TagCompound.from_mojangson(replacements_log[to_item]["TO"])

        table_updates_from_this_item = 0
        for from_item in replacements_log[to_item]["FROM"]:
            log_handle.write("        {}\n".format(from_item))

            if update_tables:
                from_nbt = nbt.TagCompound.from_mojangson(from_item)
                if (from_nbt == to_nbt) and (not from_nbt.equals_exact(to_nbt)):
                    table_updates_from_this_item += 1
                    if table_updates_from_this_item > 1:
                        eprint("WARNING: Item '{}' updated multiple times!".format(replacements_log[to_item]["NAME"]))

                    # NBT is the "same" as the loot table entry but in a different order
                    # Need to update the loot tables with the correctly ordered NBT
                    loot_table_manager.update_item_in_loot_tables(replacements_log[to_item]["ID"], from_nbt)
                    log_handle.write("        Updated loot tables with this item!\n")

            for from_location in replacements_log[to_item]["FROM"][from_item]:
                log_handle.write("            {}\n".format(from_location))

        log_handle.write("\n")

def get_dungeon_config(name, scoreboard):
    return {
        "server":name,
        "localMainFolder":"/home/epic/project_epic/0_PREVIOUS/{0}/Project_Epic-{0}/".format(name),
        "localBuildFolder":"/home/epic/5_SCRATCH/tmpreset/TEMPLATE/{0}/Project_Epic-{0}/".format(name),
        "localDstFolder":"/home/epic/project_epic/{0}/Project_Epic-{0}/".format(name),
        "copyBaseFrom":"build",
        "copyMainPaths":["advancements", "playerdata", "stats", "data/scoreboard.dat"],
        "datapacks":datapacks_dungeon + ['file/'+name],
        "playerScoreChanges":dungeon_score_rules,
        "preserveInstance":{
            "dungeonScore":scoreboard,
            "targetRegion":{"x":-3, "z":-2},

            # Replace items in preserved instances
            "replace_items": item_replace_manager,
        },
        "tagPlayers":["MidTransfer","resetMessage"],
        "tpToSpawn":True,
    }

betaplots = {
    "server":"betaplots",

    "localMainFolder":"/home/epic/project_epic/0_PREVIOUS/betaplots/Project_Epic-betaplots/",
    "localDstFolder":"/home/epic/project_epic/betaplots/Project_Epic-betaplots/",

    "copyBaseFrom":"main",

    "datapacks":datapacks_base + ['file/betaplots'],
    "tagPlayers":["MidTransfer","resetMessage"],
    "playerScoreChanges":dungeon_score_rules,

    # Replace items worldwide
    "replace_items_globally": item_replace_manager,
}

r1plots = {
    "server":"r1plots",

    "localMainFolder":"/home/epic/project_epic/0_PREVIOUS/r1plots/Project_Epic-r1plots/",
    "localDstFolder":"/home/epic/project_epic/r1plots/Project_Epic-r1plots/",

    "copyBaseFrom":"main",

    "datapacks":datapacks_base + ['file/r1plots'],
    "tagPlayers":["MidTransfer","resetMessage"],
    "playerScoreChanges":dungeon_score_rules,

    # Replace items worldwide
    "replace_items_globally": item_replace_manager,
}

tutorial = {
    "server":"tutorial",

    "localDstFolder":"/home/epic/project_epic/tutorial/Project_Epic-tutorial/",

    "datapacks":datapacks_dungeon + ['file/tutorial'],
}

roguelike = {
    "server":"roguelike",
    "localMainFolder":"/home/epic/project_epic/0_PREVIOUS/roguelike/Project_Epic-roguelike/",
    "localBuildFolder":"/home/epic/5_SCRATCH/tmpreset/TEMPLATE/roguelike/Project_Epic-roguelike/",
    "localDstFolder":"/home/epic/project_epic/roguelike/Project_Epic-roguelike/",
    "copyBaseFrom":"build",
    "copyMainPaths":["advancements", "playerdata", "stats", "data/scoreboard.dat"],
    "datapacks":datapacks_dungeon + ['file/roguelike'],
    "playerScoreChanges":dungeon_score_rules,
    "tagPlayers":["MidTransfer","resetMessage"],
    "tpToSpawn":True,
}

region_1 = {
    "server":"region_1",

    # Dst is the destination world, which gets overwritten by the build world.
    # Then, data from the main world replaces the relevant parts of the dst world.
    # Please note that no special care need be taken with whitespace in filenames.
    "localMainFolder":"/home/epic/project_epic/0_PREVIOUS/region_1/Project_Epic-region_1/",
    "localBuildFolder":"/home/epic/5_SCRATCH/tmpreset/TEMPLATE/region_1/Project_Epic-region_1/",
    "localDstFolder":"/home/epic/project_epic/region_1/Project_Epic-region_1/",

    # Reset dungeon scores
    "playerScoreChanges":dungeon_score_rules,

    "datapacks":datapacks_base + ['file/region_1'],
    "tpToSpawn":True,
    "tagPlayers":["MidTransfer","resetMessage"],

    "coordinatesToFill":(
        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441), 'block': {'name': 'minecraft:air'}},
    ),

    # Which folder to copy the base world from. Either "build", "main", or not set
    "copyBaseFrom":"build",
    "copyMainPaths":["advancements", "playerdata", "stats", "data"],

    # Replace items on all players
    "replace_items_on_players": item_replace_manager,

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
        {"name":"Guild_1",                "pos1":( -583,   0,  137), "pos2":(-622, 255,  105), "replace_items":item_replace_manager},
        {"name":"Guild_2",                "pos1":( -573,   0,  112), "pos2":(-534, 255,  154), "replace_items":item_replace_manager},
        {"name":"Guild_3",                "pos1":( -581,   0,  147), "pos2":(-613, 255,  186), "replace_items":item_replace_manager},
        {"name":"Guild_4",                "pos1":( -649,   0,  272), "pos2":(-617, 255,  311), "replace_items":item_replace_manager},
        {"name":"Guild_5",                "pos1":( -683,   0,  272), "pos2":(-651, 255,  311), "replace_items":item_replace_manager},
        {"name":"Guild_6",                "pos1":( -685,   0,  272), "pos2":(-717, 255,  311), "replace_items":item_replace_manager},
        {"name":"Guild_7",                "pos1":( -819,   0,  235), "pos2":(-780, 255,  267), "replace_items":item_replace_manager},
        {"name":"Guild_8",                "pos1":( -829,   0,  257), "pos2":(-868, 255,  289), "replace_items":item_replace_manager},
        {"name":"Guild_9",                "pos1":( -819,   0,  269), "pos2":(-780, 255,  301), "replace_items":item_replace_manager},
        {"name":"Guild_10",               "pos1":( -937,   0,  269), "pos2":(-969, 255,  308), "replace_items":item_replace_manager},
        {"name":"Guild_11",               "pos1":( -969,   0,  259), "pos2":(-937, 255,  220), "replace_items":item_replace_manager},
        {"name":"Guild_12",               "pos1":( -955,   0,  104), "pos2":(-994, 255,  136), "replace_items":item_replace_manager},
        {"name":"Guild_14",               "pos1":( -955,   0,   70), "pos2":(-994, 255,  102), "replace_items":item_replace_manager},
        {"name":"Guild_15",               "pos1":( -581,   0,  -61), "pos2":(-613, 255, -100), "replace_items":item_replace_manager},
        {"name":"Guild_18",               "pos1":( -945,   0,   93), "pos2":(-906, 255,  125), "replace_items":item_replace_manager},
        {"name":"Guild_20",               "pos1":( -748,   0, -230), "pos2":(-787, 255, -198), "replace_items":item_replace_manager},
        {"name":"Guild_21",               "pos1":( -787,   0, -232), "pos2":(-748, 255, -264), "replace_items":item_replace_manager},
        {"name":"Guild_22",               "pos1":( -603,   0, -191), "pos2":(-564, 255, -159), "replace_items":item_replace_manager},
        {"name":"Guild_23",               "pos1":( -612,   0, -180), "pos2":(-651, 255, -212), "replace_items":item_replace_manager},
        {"name":"Guild_24",               "pos1":( -564,   0, -192), "pos2":(-603, 255, -224), "replace_items":item_replace_manager},
        {"name":"Guild_26",               "pos1":( -596,   0,  -49), "pos2":(-564, 255,  -10), "replace_items":item_replace_manager},
        {"name":"Guild_27",               "pos1":( -548,   0,  -61), "pos2":(-580, 255, -100), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_N1",       "pos1":(-1626,   0, 1411), "pos2":(-1594,255, 1444), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_N2",       "pos1":(-1589,   0, 1411), "pos2":(-1557,255, 1444), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_N3",       "pos1":(-1552,   0, 1411), "pos2":(-1520,255, 1444), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_N4",       "pos1":(-1515,   0, 1411), "pos2":(-1483,255, 1444), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_N5",       "pos1":(-1478,   0, 1411), "pos2":(-1446,255, 1444), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_E1",       "pos1":(-1444,   0, 1446), "pos2":(-1411,255, 1478), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_E2",       "pos1":(-1444,   0, 1483), "pos2":(-1411,255, 1515), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_E3",       "pos1":(-1444,   0, 1520), "pos2":(-1411,255, 1552), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_E4",       "pos1":(-1444,   0, 1557), "pos2":(-1411,255, 1589), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_E5",       "pos1":(-1444,   0, 1594), "pos2":(-1411,255, 1626), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_S1",       "pos1":(-1626,   0, 1625), "pos2":(-1594,255, 1664), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_S2",       "pos1":(-1589,   0, 1625), "pos2":(-1557,255, 1664), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_S3",       "pos1":(-1552,   0, 1625), "pos2":(-1520,255, 1664), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_S4",       "pos1":(-1515,   0, 1625), "pos2":(-1483,255, 1664), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_S5",       "pos1":(-1478,   0, 1625), "pos2":(-1446,255, 1664), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_W1",       "pos1":(-1664,   0, 1446), "pos2":(-1625,255, 1478), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_W2",       "pos1":(-1664,   0, 1483), "pos2":(-1625,255, 1515), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_W3",       "pos1":(-1664,   0, 1520), "pos2":(-1625,255, 1552), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_W4",       "pos1":(-1664,   0, 1557), "pos2":(-1625,255, 1589), "replace_items":item_replace_manager},
        {"name":"Guild_Archive_W5",       "pos1":(-1664,   0, 1594), "pos2":(-1625,255, 1626), "replace_items":item_replace_manager},
    ),
}


region_2 = {
    "server":"region_2",

    # Dst is the destination world, which gets overwritten by the build world.
    # Then, data from the main world replaces the relevant parts of the dst world.
    # Please note that no special care need be taken with whitespace in filenames.
    "localMainFolder":"/home/epic/project_epic/0_PREVIOUS/region_2/Project_Epic-region_2/",
    "localBuildFolder":"/home/epic/5_SCRATCH/tmpreset/TEMPLATE/region_2/Project_Epic-region_2/",
    "localDstFolder":"/home/epic/project_epic/region_2/Project_Epic-region_2/",

    # Reset dungeon scores
    "playerScoreChanges":dungeon_score_rules,

    "datapacks":datapacks_base + ['file/region_2'],
    "tpToSpawn":True,
    "tagPlayers":["MidTransfer","resetMessage"],

    "coordinatesToFill":(
        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441), 'block': {'name': 'minecraft:air'}},
    ),

    # Which folder to copy the base world from. Either "build", "main", or not set
    "copyBaseFrom":"build",
    "copyMainPaths":["advancements", "playerdata", "stats", "data/scoreboard.dat"],

    # Replace items on all players
    "replace_items_on_players": item_replace_manager,
}

available_configs = {
    "betaplots": betaplots,
    "r1plots": r1plots,
    "region_1": region_1,
    "region_2": region_2,
    "white": get_dungeon_config("white", "D1Access"),
    "orange": get_dungeon_config("orange", "D2Access"),
    "magenta": get_dungeon_config("magenta", "D3Access"),
    "lightblue": get_dungeon_config("lightblue", "D4Access"),
    "yellow": get_dungeon_config("yellow", "D5Access"),
    "lime": get_dungeon_config("lime", "D6Access"),
    "pink": get_dungeon_config("pink", "D7Access"),
    "gray": get_dungeon_config("gray", "D8Access"),
    "lightgray": get_dungeon_config("lightgray", "D9Access"),
    "cyan": get_dungeon_config("cyan", "D10Access"),
    "willows": get_dungeon_config("willows", "DB1Access"),
    "reverie": get_dungeon_config("reverie", "DCAccess"),
    "sanctum": get_dungeon_config("sanctum", "DS1Access"),
    "labs": get_dungeon_config("labs", "D0Access"),
    "roguelike": roguelike,
    "tutorial": tutorial,
    "build": None,
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

processes = {}
statusQueue = mp.Queue()
for config in reset_config_list:
    shard_name = config["server"]
    outputFile = tempfile.mktemp()
    processes[shard_name] = {
        "process":mp.Process(target=terrain_reset_instance, args=(config, outputFile, statusQueue)),
        "outputFile":outputFile,
    }

# Decrease the priority for this work so it doesn't slow down other things
os.nice(20)

for p in processes.values():
    p["process"].start()

logfile = "/home/epic/0_OLD_BACKUPS/terrain_reset_item_replacements_log_{}.log".format(datetime.date.today().strftime("%Y-%m-%d"))
update_tables = False
with open(logfile, 'w') as log_handle:
    while len(processes.keys()) > 0:
        statusUpdate = statusQueue.get()
        shard_name = statusUpdate["server"]
        p = processes[shard_name]

        if "done" in statusUpdate:
            p["process"].join()

            if "error" not in statusUpdate:
                print(shard_name + " completed successfully")

            try:
                logFile = codecs.open(p["outputFile"],'rb',encoding='utf8')
                print(logFile.read())
                logFile.close()
            except:
                print("Log file could not be read!")

            if "replacements_log" in statusUpdate:
                log_replacements(log_handle, shard_name, statusUpdate["replacements_log"])

            processes.pop(shard_name)

        if "error" in statusUpdate:
            print("\n!!! " + shard_name + " has crashed.\n")

            # stop all other subprocesses
            for p in processes.values():
                p["process"].terminate()

            raise RuntimeError(str(statusUpdate["error"]))

print("Shards reset successfully: {}".format(reset_name_list))
