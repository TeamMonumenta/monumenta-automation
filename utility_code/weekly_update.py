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
from lib_py3.redis_scoreboard import RedisScoreboard, RedisRBoard
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

playerplots = {
    "server":"playerplots",
    "previous_world_path":f"{last_week_dir}/playerplots/Project_Epic-playerplots/",
    "output_world_path":f"{output_dir}/playerplots/Project_Epic-playerplots/",
    "copy_base_from":"previous",
    "datapacks":datapacks_base + ['file/playerplots'],
    "replace_items_globally": True,
}

tutorial = {
    "server":"tutorial",
    "output_world_path":f"{output_dir}/tutorial/Project_Epic-tutorial/",
    "datapacks":datapacks_dungeon + ['file/tutorial'],
}

corridors = {
    "server":"corridors",
    "previous_world_path":f"{last_week_dir}/corridors/Project_Epic-corridors/",
    "build_world_path":f"{build_template_dir}/corridors/Project_Epic-corridors/",
    "output_world_path":f"{output_dir}/corridors/Project_Epic-corridors/",
    "copy_base_from":"build",
    "copy_previous_paths":["stats", "data/scoreboard.dat"],
    "datapacks":datapacks_dungeon + ['file/corridors'],
}

verdant = {
    "server":"verdant",
    "previous_world_path":f"{last_week_dir}/verdant/Project_Epic-verdant/",
    "build_world_path":f"{build_template_dir}/verdant/Project_Epic-verdant/",
    "output_world_path":f"{output_dir}/verdant/Project_Epic-verdant/",
    "copy_base_from":"build",
    "copy_previous_paths":["stats", "data/scoreboard.dat"],
    "datapacks":datapacks_dungeon + ['file/verdant'],
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

mist = {
    "server":"mist",
    "previous_world_path":f"{last_week_dir}/mist/Project_Epic-mist/",
    "build_world_path":f"{build_template_dir}/mist/Project_Epic-mist/",
    "output_world_path":f"{output_dir}/mist/Project_Epic-mist/",
    "copy_base_from":"build",
    "copy_previous_paths":["stats", "data/scoreboard.dat"],
    "datapacks":datapacks_dungeon + ['file/mist'],
}

remorse = {
    "server":"remorse",
    "previous_world_path":f"{last_week_dir}/remorse/Project_Epic-remorse/",
    "build_world_path":f"{build_template_dir}/remorse/Project_Epic-remorse/",
    "output_world_path":f"{output_dir}/remorse/Project_Epic-remorse/",
    "copy_base_from":"build",
    "copy_previous_paths":["stats", "data/scoreboard.dat"],
    "datapacks":datapacks_dungeon + ['file/remorse'],
}

depths = {
    "server":"depths",
    "previous_world_path":f"{last_week_dir}/depths/Project_Epic-depths/",
    "build_world_path":f"{build_template_dir}/depths/Project_Epic-depths/",
    "output_world_path":f"{output_dir}/depths/Project_Epic-depths/",
    "copy_base_from":"build",
    "copy_previous_paths":["stats", "data/scoreboard.dat"],
    "datapacks":datapacks_dungeon + ['file/depths'],
}

valley = {
    "server":"valley",
    "previous_world_path":f"{last_week_dir}/valley/Project_Epic-valley/",
    "build_world_path":f"{build_template_dir}/valley/Project_Epic-valley/",
    "output_world_path":f"{output_dir}/valley/Project_Epic-valley/",
    "copy_base_from":"build",
    "copy_previous_paths":["stats", "data"],
    "copy_maps": "build",
    "datapacks":datapacks_base + ['file/valley'],
    "coordinates_to_fill":(
        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441), 'block': {'name': 'minecraft:air'}},
    ),
}

isles = {
    "server":"isles",
    "previous_world_path":f"{last_week_dir}/isles/Project_Epic-isles/",
    "build_world_path":f"{build_template_dir}/isles/Project_Epic-isles/",
    "output_world_path":f"{output_dir}/isles/Project_Epic-isles/",
    "copy_base_from":"build",
    "copy_previous_paths":["stats", "data/scoreboard.dat"],
    "copy_maps": "build",
    "datapacks":datapacks_base + ['file/isles'],
    "coordinates_to_fill":(
        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441), 'block': {'name': 'minecraft:air'}},
    ),
}

available_configs = {
    "plots": plots,
    "playerplots": playerplots,
    "valley": valley,
    "isles": isles,
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
    "forum": get_dungeon_config("forum", "DFFAccess"),
    "shiftingcity": get_dungeon_config("shiftingcity", "DRL2Access"),
    "corridors": corridors,
    "verdant": verdant,
    "rush": rush,
    "mist": mist,
    "remorse": remorse,
    "depths": depths,
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
loot_table_manager.load_loot_tables_subdirectories(f"{output_dir}/server_config/data/datapacks")
timings.nextStep("Loaded loot tables")
unique_item_map = loot_table_manager.get_unique_item_map(show_errors=False)
if len(unique_item_map) == 0:
    sys.exit("ERROR: No loot tables were loaded for replacements")

item_replace_manager = ItemReplacementManager(unique_item_map)
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
            if val < 10000:
                inval_scores.add(val)
            else:
                dungeon_scores.add(val)
        if inval_scores:
            eprint(f"WARNING: Found dungeon scores [{','.join([str(x) for x in inval_scores])}] for {config['server']} that are less than 10000! This indicates score changes didn't run correctly. This is fine on stage, but a serious problem on the play server")
        dungeon_scores = sorted(list(dungeon_scores))
        preserve_instances["dungeon_scores"] = dungeon_scores
timings.nextStep("Loaded dungeon scores")

##################################################################################
# Update number of instances

print("Updating number of instances...")

try:
    rboard = RedisRBoard("play", redis_host=redis_host)
    with open(os.path.join(build_template_dir, "dungeon_info.yml")) as f:
        dungeon_info = yaml.load(f, Loader=yaml.FullLoader)["dungeons"]

    last_dict = {}
    instances_dict = {}
    for config in config_list:
        server = config['server']
        # Some shards don't have instances to update
        if server in dungeon_info:
            objective = dungeon_info[server]['objective']
            instances = dungeon_info[server]['count']
            last_dict[objective] = 0
            instances_dict[objective] = instances
    print("Setting rboard scores for $Last:")
    pprint(last_dict)
    print("Setting rboard scores for $Instances:")
    pprint(instances_dict)
    print(f"$Instances.{objective} = {instances}")
    rboard.setmulti("$Last", last_dict)
    rboard.setmulti("$Instances", instances_dict)
except Exception as ex:
    eprint(f"!!!!!! WARNING: Failed to set redis instance count/used values: {ex}")

timings.nextStep("Updated number of instances")

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
            eprint("!!!!!! WARNING: Missing previous week previous folder {!r}!".format(config["previous_world_path"]))
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

        instances_per_week = 10000

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
        for _, rx, rz, __ in worlds[config["server"]].enumerate_regions():
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
                if item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=item.get_path_str()):
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
