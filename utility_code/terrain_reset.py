#!/usr/bin/env python3

import os
import sys
import datetime
import codecs
import multiprocessing as mp
import tempfile
import traceback

from score_change_list import world_dungeon_score_rules
from lib_py3.terrain_reset import terrain_reset_instance
from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.common import eprint
from lib_py3.redis_scoreboard import RedisScoreboard

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

datapacks_default = ['file/vanilla','file/bukkit']
datapacks_base = datapacks_default + ['file/base']
datapacks_dungeon = datapacks_base + ['file/dungeon']

loot_table_manager = LootTableManager()
loot_table_manager.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")
item_replace_manager = ItemReplacementManager(loot_table_manager.get_unique_item_map(show_errors=False))

redisScoreboard = RedisScoreboard("play", redis_host="redis")

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
                        eprint("WARNING: Item {!r} updated multiple times!".format(replacements_log[to_item]["NAME"]))

                    # NBT is the "same" as the loot table entry but in a different order
                    # Need to update the loot tables with the correctly ordered NBT
                    loot_table_manager.update_item_in_loot_tables(replacements_log[to_item]["ID"], from_nbt)
                    log_handle.write("        Updated loot tables with this item!\n")

            for from_location in replacements_log[to_item]["FROM"][from_item]:
                log_handle.write("            {}\n".format(from_location))

        log_handle.write("\n")

def get_dungeon_config(name, objective):
    return {
        "server":name,
        "localMainFolder":"/home/epic/project_epic/0_PREVIOUS/{0}/Project_Epic-{0}/".format(name),
        "localBuildFolder":"/home/epic/5_SCRATCH/tmpreset/TEMPLATE/{0}/Project_Epic-{0}/".format(name),
        "localDstFolder":"/home/epic/project_epic/{0}/Project_Epic-{0}/".format(name),
        "copyBaseFrom":"build",
        "copyMainPaths":["stats", "data/scoreboard.dat"],
        "copyMaps": "build",
        "datapacks":datapacks_dungeon + ['file/'+name],
        "preserveInstance":{
            "dungeonScore":objective,
            "targetRegion":{"x":-3, "z":-2},
            "redisScoreboard": redisScoreboard,

            # Replace items in preserved instances
            "replace_items": item_replace_manager,
        },
    }

plots = {
    "server":"plots",

    "localMainFolder":"/home/epic/project_epic/0_PREVIOUS/plots/Project_Epic-plots/",
    "localDstFolder":"/home/epic/project_epic/plots/Project_Epic-plots/",

    "copyBaseFrom":"main",

    "datapacks":datapacks_base + ['file/plots'],

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
    "copyMainPaths":["stats", "data/scoreboard.dat"],
    "datapacks":datapacks_dungeon + ['file/roguelike'],
}

rush = {
    "server":"rush",
    "localMainFolder":"/home/epic/project_epic/0_PREVIOUS/rush/Project_Epic-rush/",
    "localBuildFolder":"/home/epic/5_SCRATCH/tmpreset/TEMPLATE/rush/Project_Epic-rush/",
    "localDstFolder":"/home/epic/project_epic/rush/Project_Epic-rush/",
    "copyBaseFrom":"build",
    "copyMainPaths":["stats", "data/scoreboard.dat"],
    "datapacks":datapacks_dungeon + ['file/rush'],
}

region_1 = {
    "server":"region_1",

    # Dst is the destination world, which gets overwritten by the build world.
    # Then, data from the main world replaces the relevant parts of the dst world.
    # Please note that no special care need be taken with whitespace in filenames.
    "localMainFolder":"/home/epic/project_epic/0_PREVIOUS/region_1/Project_Epic-region_1/",
    "localBuildFolder":"/home/epic/5_SCRATCH/tmpreset/TEMPLATE/region_1/Project_Epic-region_1/",
    "localDstFolder":"/home/epic/project_epic/region_1/Project_Epic-region_1/",

    # World score changes ($last...)
    "worldScoreChanges": world_dungeon_score_rules,

    "datapacks":datapacks_base + ['file/region_1'],

    "coordinatesToFill":(
        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441), 'block': {'name': 'minecraft:air'}},
    ),

    # Which folder to copy the base world from. Either "build", "main", or not set
    "copyBaseFrom":"build",
    "copyMainPaths":["stats", "data"],
    "copyMaps": "build",

    "coordinatesToCopy":(
        # "name":"a unique name"
        # "pos1":(x1,y1,z1)
        # "pos2":(x2,y2,z2)
        {"name":"Apartments_101-132",     "pos1":( -811,  99,   44), "pos2":(-873,  99,   44), "replace_items": item_replace_manager},
        {"name":"Apartments_201-232",     "pos1":( -811,  99,   36), "pos2":(-873,  99,   36), "replace_items": item_replace_manager},
        {"name":"Apartments_301-332",     "pos1":( -811,  99,   31), "pos2":(-873,  99,   31), "replace_items": item_replace_manager},
        {"name":"Apartments_401-432",     "pos1":( -811,  99,   23), "pos2":(-873,  99,   23), "replace_items": item_replace_manager},
        {"name":"Apartments_501-524",     "pos1":( -815,  99,   10), "pos2":(-861,  99,   10), "replace_items": item_replace_manager},
        {"name":"Apartments_601-624",     "pos1":( -815,  99,    5), "pos2":(-861,  99,    5), "replace_items": item_replace_manager},
        {"name":"Apartments_701-816",     "pos1":( -811,  99,   18), "pos2":(-873,  99,   18), "replace_items": item_replace_manager},
        {"name":"Apartments_units",       "pos1":( -817, 109,   87), "pos2":(-859, 164,   16), "replace_items": item_replace_manager},
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

    # World score changes ($last...)
    "worldScoreChanges": world_dungeon_score_rules,

    "datapacks":datapacks_base + ['file/region_2'],

    "coordinatesToFill":(
        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441), 'block': {'name': 'minecraft:air'}},
    ),

    # Which folder to copy the base world from. Either "build", "main", or not set
    "copyBaseFrom":"build",
    "copyMainPaths":["stats", "data/scoreboard.dat"],
    "copyMaps": "build",
}

available_configs = {
    "plots": plots,
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
    "purple": get_dungeon_config("purple", "D11Access"),
    "willows": get_dungeon_config("willows", "DB1Access"),
    "reverie": get_dungeon_config("reverie", "DCAccess"),
    "sanctum": get_dungeon_config("sanctum", "DS1Access"),
    "labs": get_dungeon_config("labs", "D0Access"),
    "shiftingcity": get_dungeon_config("shiftingcity", "DRL2Access"),
    "roguelike": roguelike,
    "rush": rush,
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
if not os.path.isdir(os.path.dirname(logfile)):
    os.makedirs(os.path.dirname(logfile), mode=0o775)
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
