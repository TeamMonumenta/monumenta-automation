#!/usr/bin/env python3
import yaml
import os
import sys
import datetime
import multiprocessing
import getopt
from pprint import pprint, pformat

from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.common import eprint, copy_folder, copy_paths, copy_maps
from lib_py3.redis_scoreboard import RedisScoreboard
from lib_py3.timing import Timings

from minecraft.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

datapacks_default = ['file/vanilla','file/bukkit']
datapacks_base = datapacks_default + ['file/base']
datapacks_dungeon = datapacks_base + ['file/dungeon']

def usage():
    sys.exit("Usage: {} <--last_week_dir dir> <--build_template_dir dir> <--output_dir dir> [--redis_host host] [--num-threads #] <server1> [server2] [...]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "j:", ["last_week_dir=", "build_template_dir=", "output_dir=", "redis_host=", "num-threads="])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

last_week_dir = None
build_template_dir = None
output_dir = None
num_threads = 4
redis_host = 'redis'

for o, a in opts:
    if o in ("--last_week_dir"):
        last_week_dir = a
        if last_week_dir.endswith("/"):
            last_week_dir = last_week_dir[:-1]
    elif o in ("--build_template_dir"):
        build_template_dir = a
        if build_template_dir.endswith("/"):
            build_template_dir = build_template_dir[:-1]
    elif o in ("--output_dir",):
        output_dir = a
        if output_dir.endswith("/"):
            output_dir = output_dir[:-1]
    elif o in ("--redis_host"):
        redis_host = a
    elif o in ("-j", "--num-threads"):
        num_threads = int(a)
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if last_week_dir is None:
    eprint("--last_week_dir must be specified!")
    usage()
if build_template_dir is None:
    eprint("--build_template_dir must be specified!")
    usage()
if output_dir is None:
    eprint("--output_dir must be specified!")
    usage()

def get_dungeon_config(name, objective):
    return {
        "server":f"{name}",
        "previous_world_path":f"{last_week_dir}/{name}/Project_Epic-{name}/",
        "build_world_path":f"{build_template_dir}/{name}/Project_Epic-{name}/",
        "output_world_path":f"{output_dir}/{name}/Project_Epic-{name}/",
        "copy_base_from":"build",
        "copy_previous_paths":["stats", "data/scoreboard.dat"],
        "copy_maps": "build",
        "datapacks":datapacks_dungeon + [f'file/{name}'],
        "preserve_instances":{
            "dungeon_objective":f"{objective}",
            "start_rx":-3,
            "start_rz":-2,
        },
    }

plots = {
    "server":"plots",
    "previous_world_path":f"{last_week_dir}/plots/Project_Epic-plots/",
    "output_world_path":f"{output_dir}/plots/Project_Epic-plots/",
    "copy_base_from":"previous",
    "datapacks":datapacks_base + ['file/plots'],
    "replace_items_globally": True,
}

tutorial = {
    "server":"tutorial",
    "output_world_path":f"{output_dir}/tutorial/Project_Epic-tutorial/",
    "datapacks":datapacks_dungeon + ['file/tutorial'],
}

roguelike = {
    "server":"roguelike",
    "previous_world_path":f"{last_week_dir}/roguelike/Project_Epic-roguelike/",
    "build_world_path":f"{build_template_dir}/roguelike/Project_Epic-roguelike/",
    "output_world_path":f"{output_dir}/roguelike/Project_Epic-roguelike/",
    "copy_base_from":"build",
    "copy_previous_paths":["stats",],
    "datapacks":datapacks_dungeon + ['file/roguelike'],
}

rush = {
    "server":"rush",
    "previous_world_path":f"{last_week_dir}/rush/Project_Epic-rush/",
    "build_world_path":f"{build_template_dir}/rush/Project_Epic-rush/",
    "output_world_path":f"{output_dir}/rush/Project_Epic-rush/",
    "copy_base_from":"build",
    "copy_previous_paths":["stats", "data/scoreboard.dat"],
    "datapacks":datapacks_dungeon + ['file/rush'],
}

region_1 = {
    "server":"region_1",
    "previous_world_path":f"{last_week_dir}/region_1/Project_Epic-region_1/",
    "build_world_path":f"{build_template_dir}/region_1/Project_Epic-region_1/",
    "output_world_path":f"{output_dir}/region_1/Project_Epic-region_1/",
    "copy_base_from":"build",
    "copy_previous_paths":["stats", "data"],
    "copy_maps": "build",
    "datapacks":datapacks_base + ['file/region_1'],
    "coordinates_to_fill":(
        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441), 'block': {'name': 'minecraft:air'}},
    ),
}

region_2 = {
    "server":"region_2",
    "previous_world_path":f"{last_week_dir}/region_2/Project_Epic-region_2/",
    "build_world_path":f"{build_template_dir}/region_2/Project_Epic-region_2/",
    "output_world_path":f"{output_dir}/region_2/Project_Epic-region_2/",
    "copy_base_from":"build",
    "copy_previous_paths":["stats", "data/scoreboard.dat"],
    "copy_maps": "build",
    "datapacks":datapacks_base + ['file/region_2'],
    "coordinates_to_fill":(
        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441), 'block': {'name': 'minecraft:air'}},
    ),
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
    "teal": get_dungeon_config("teal", "DTLAccess"),
    "shiftingcity": get_dungeon_config("shiftingcity", "DRL2Access"),
    "roguelike": roguelike,
    "rush": rush,
    "tutorial": tutorial,
    "build": None,
    "bungee": None,
    "purgatory": None,
}

# Parse additional non-option arguments and copy those configs to the list of servers to update
config_list = []
for arg in args:
    if arg in available_configs:
        if available_configs[arg] is not None:
            config = available_configs[arg]
            config_list.append(available_configs[arg])
    else:
        print("ERROR: Unknown shard {} specified!".format(arg))
        usage()

timings = Timings(enabled=True)

# Decrease the priority for this work so it doesn't slow down other things
os.nice(20)

##################################################################################
# Set up global state
loot_table_manager = LootTableManager()
loot_table_manager.load_loot_tables_subdirectories(f"{build_template_dir}/server_config/data/datapacks")
timings.nextStep("Loaded loot tables")
item_replace_manager = ItemReplacementManager(loot_table_manager.get_unique_item_map(show_errors=False))
timings.nextStep("Loaded item replacement manager")

redis_scoreboard = RedisScoreboard("play", redis_host=redis_host)
timings.nextStep("Loaded redis scoreboard")

##################################################################################
# Fetch dungeon scores

print("Loading dungeon scores...")
for config in config_list:
    if "preserve_instances" in config:
        preserve_instances = config["preserve_instances"]
        score_objects = redis_scoreboard.search_scores(Objective=preserve_instances["dungeon_objective"],Score={"min":1})
        dungeon_scores = set()
        inval_scores = set()
        for score in score_objects:
            val = score.at_path("Score").value
            if val < 1000:
                inval_scores.add(val)
            else:
                dungeon_scores.add(val)
        if inval_scores:
            eprint(f"WARNING: Found dungeon scores [{','.join([str(x) for x in inval_scores])}] for {config['server']} that are less than 1000! This indicates score changes didn't run correctly. This is fine on stage, but a serious problem on the play server")
        dungeon_scores = sorted(list(dungeon_scores))
        preserve_instances["dungeon_scores"] = dungeon_scores
timings.nextStep("Loaded dungeon scores")

##################################################################################
# Copy base world files

print("Copying base worlds...")
# First check for missing directories and fail if any are found
for config in config_list:
    if "copy_base_from" in config:
        if config["copy_base_from"] == "build":
            if not os.path.exists(config["build_world_path"]):
                raise Exception("ERROR: Build folder {!r} does not exist!!".format(config["build_world_path"]))
        elif config["copy_base_from"] == "previous":
            if not os.path.exists(config["previous_world_path"]):
                raise Exception("ERROR: Previous folder {!r} does not exist!!".format(config["previous_world_path"]))

# Do the actual copying in parallel
def parallel_copy(config):
    server = config["server"]
    if "copy_base_from" in config:
        if config["copy_base_from"] == "build":
            print(f"  {server} - Copying base from {config['build_world_path']} to {config['output_world_path']}")
            copy_folder(config["build_world_path"], config["output_world_path"])
        elif config["copy_base_from"] == "previous":
            print(f"  {server} - Copying base from {config['previous_world_path']} to {config['output_world_path']}")
            copy_folder(config["previous_world_path"], config["output_world_path"])

    if "copy_previous_paths" in config:
        print(f"  {server} - Copying previous paths from {config['previous_world_path']}/[{','.join(config['copy_previous_paths'])}] to {config['output_world_path']}")
        copy_paths(config["previous_world_path"], config["output_world_path"], config["copy_previous_paths"])

    if "copy_maps" in config:
        if config["copy_maps"] == "build":
            print(f"  {server} - Copying maps from {config['build_world_path']} to {config['output_world_path']}")
            copy_maps(config["build_world_path"], config["output_world_path"])
        elif config["copy_maps"] == "previous":
            print(f"  {server} - Copying maps from {config['previous_world_path']} to {config['output_world_path']}")
            copy_maps(config["previous_world_path"], config["output_world_path"])

with multiprocessing.Pool(num_threads) as pool:
    pool.map(parallel_copy, config_list)
timings.nextStep("Copied base worlds")

##################################################################################
# Open the worlds for use

print("Opening worlds, changing datapacks & filling areas...")
worlds = {}
prev_worlds = {}
for config in config_list:
    world = World(config["output_world_path"])
    worlds[config["server"]] = world

    if "datapacks" in config:
        world.level_dat.enabled_datapacks = config["datapacks"]
        world.level_dat.save()

    if "coordinates_to_fill" in config:
        print(f"  {config['server']} - Filling selected regions with specified blocks...")
        for section in config["coordinates_to_fill"]:
            print(f"    Filling {repr(section['name'])} with {section['block']}")
            world.fill_blocks(section["pos1"], section["pos2"], section["block"])

    if "previous_world_path" in config:
        if not os.path.exists(config["previous_world_path"]):
            eprint("!!!!!! WARNING: Missing previous week previous folder {!r}!".format(config["build_world_path"]))
            eprint("If you are not adding a shard, this is a critical problem!")
        else:
            prev_worlds[config['server']] = World(config["previous_world_path"])
timings.nextStep("Loaded worlds, changed datapacks & filled areas")


##################################################################################
# Compute which region files need attention

print("Computing region files to process...")
# This list of regions will be processed by pooled process workers
# Format is:
# [
#   {
#     "world": str
#     "rx": int
#     "rz": int
#     # If being copied from the previous play server
#     "preserve": {
#       "rx": int
#       "rz": int
#     }
#   }
# ]
regions = []
for config in config_list:
    if "preserve_instances" in config:
        preserve_instances = config["preserve_instances"]
        start_rx = preserve_instances["start_rx"]
        start_rz = preserve_instances["start_rz"]

        instances_per_week = 1000

        print(f"  {config['server']} - Instances preserved this week: [{','.join(str(x) for x in preserve_instances['dungeon_scores'])}]")
        for instance in preserve_instances["dungeon_scores"]:
            instance_week = instance // instances_per_week
            instance_in_week = instance % instances_per_week

            new_rx = start_rx + instance_week
            new_rz = start_rz + instance_in_week - 1 # index starts at 1
            old_rx = new_rx - 1
            old_rz = new_rz

            regions.append({
                "world": config["server"],
                "rx": new_rx,
                "rz": new_rz,
                "preserve": {
                    "rx": new_rx - 1,
                    "rz": new_rz,
                }
            })
    elif "replace_items_globally" in config and config["replace_items_globally"]:
        for _, rx, rz in worlds[config["server"]].enumerate_regions():
            regions.append({
                "world": config["server"],
                "rx": rx,
                "rz": rz,
            })

print("\n  Regions to process:")
pprint(regions)
print("")
timings.nextStep("Computed regions to process")

##################################################################################
# Processing regions

num_regions = len(regions)
print(f"Processing {num_regions} regions...")

def process_region(region_config):
    try:
        world = worlds[region_config["world"]]
        rx = region_config["rx"]
        rz = region_config["rz"]
        if "preserve" in region_config:
            prev_world = prev_worlds[region_config["world"]]
            prev_region = prev_world.get_region(region_config["preserve"]["rx"], region_config["preserve"]["rz"], read_only=True)
            region = prev_region.copy_to(world, rx, rz, regenerate_uuids=False)
        else:
            region = world.get_region(rx, rz)

        replacements_log = {}
        num_replacements = 0
        for chunk in region.iter_chunks(autosave=True):
            for item in chunk.recursive_iter_items():
                if item_replace_manager.replace_item(item.nbt, log_dict=replacements_log, debug_path=item.get_path_str()):
                    num_replacements += 1

        return (region_config["world"], num_replacements, replacements_log)
    except Exception as ex:
        eprint("WARNING: Failed to process region:", pformat(region_config))
        eprint("  Error was:", ex)
        return (region_config["world"], 0, {})

# Run the regions in parallel using a pool. As results come in, accumulate them to the appropriate list based on the world
num_global_replacements = 0
replacements_to_merge = {}
done_count = 0
with multiprocessing.Pool(num_threads) as pool:
    for world_name, num_replacements, replacements_log in pool.imap_unordered(process_region, regions):
        done_count += 1
        num_global_replacements += num_replacements
        if world_name not in replacements_to_merge:
            replacements_to_merge[world_name] = []
        replacements_to_merge[world_name].append(replacements_log)

        print(f"  {done_count} / {num_regions} regions processed, {num_global_replacements} replacements so far")
timings.nextStep("Processed regions")

##################################################################################
# Merge replacements logs

print(f"Merging replacements logs...")

replacements_log = {}
for world_name in replacements_to_merge:
    replacements_log[world_name] = item_replace_manager.merge_logs(replacements_to_merge[world_name])
timings.nextStep("Replacements logs merged")

##################################################################################
# Writing logs

print(f"Writing replacements logs...")

logfile = "/home/epic/0_OLD_BACKUPS/terrain_reset_item_replacements_log_{}.log".format(datetime.date.today().strftime("%Y-%m-%d"))
if not os.path.isdir(os.path.dirname(logfile)):
    os.makedirs(os.path.dirname(logfile), mode=0o775)
with open(logfile, "w") as fd:
    yaml.dump(replacements_log, fd, width=2147483647, allow_unicode=True)

timings.nextStep("Logs written")

print("Finished")