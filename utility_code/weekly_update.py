#!/usr/bin/env pypy3

import getopt
import multiprocessing
from pprint import pprint
import os
import sys
import traceback
import yaml

from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.common import eprint, move_folder, copy_folder, move_paths
from lib_py3.redis_scoreboard import RedisScoreboard
from lib_py3.timing import Timings

from minecraft.world import World
from minecraft.util.iter_util import process_in_parallel

def usage():
    sys.exit("Usage: {} <--last_week_dir dir> <--build_template_dir dir> <--output_dir dir> [--redis_host host] [--num-threads #] [--logfile <stdout|stderr|path>] <server1> [server2] [...]".format(sys.argv[0]))

def get_dungeon_config(name, objective):
    return {
        "server":f"{name}",
        "move_base_from":"build",
        "move_previous_paths":[f"Project_Epic-{name}/stats", f"Project_Epic-{name}/data/scoreboard.dat"],
        "datapacks":datapacks_dungeon + [f'file/{name}'],
        "replace_items_globally": True,
        "preserve_instances":{
            "dungeon_objective":f"{objective}",
        },
    }

def process_init(mgr):
    global item_replace_manager
    item_replace_manager = mgr

# Nothing actually to do here - just return the dict
def _create_region_lambda(region_config):
    return region_config

def process_region(region_config):
    world = World(region_config["world_path"])
    rx = region_config["rx"]
    rz = region_config["rz"]
    region = world.get_region(rx, rz)

    replacements_log = {}
    num_replacements = 0
    for chunk in region.iter_chunks(autosave=True):
        for item in chunk.recursive_iter_items():
            if item_replace_manager.replace_item(item, log_dict=replacements_log, debug_path=item.get_path_str()):
                num_replacements += 1

    return (num_replacements, replacements_log)

def err_func(ex, args):
    eprint(f"Caught exception: {ex}")
    eprint(f"While iterating: {args}")
    eprint(traceback.format_exc())
    return (0, {})

if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")

    datapacks_default = ['file/vanilla', 'file/bukkit']
    datapacks_base = datapacks_default + ['file/base']
    datapacks_dungeon = datapacks_base + ['file/dungeon']

    try:
        opts, args = getopt.getopt(sys.argv[1:], "j:", ["last_week_dir=", "build_template_dir=", "output_dir=", "redis_host=", "logfile=", "num-threads="])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    last_week_dir = None
    build_template_dir = None
    output_dir = None
    logfile = None
    num_threads = 4
    redis_host = 'redis'

    for o, a in opts:
        if o in ("--last_week_dir",):
            last_week_dir = a
            if last_week_dir.endswith("/"):
                last_week_dir = last_week_dir[:-1]
        elif o in ("--build_template_dir",):
            build_template_dir = a
            if build_template_dir.endswith("/"):
                build_template_dir = build_template_dir[:-1]
        elif o in ("--output_dir",):
            output_dir = a
            if output_dir.endswith("/"):
                output_dir = output_dir[:-1]
        elif o in ("--redis_host",):
            redis_host = a
        elif o in ("-l", "--logfile"):
            logfile = a
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

    plots = {
        "server":"plots",
        "move_base_from":"previous",
        "datapacks":datapacks_base + ['file/plots'],
        "move_previous_paths":["Project_Epic-plots/stats", "Project_Epic-plots/data/scoreboard.dat", "plugins/CoreProtect", "plugins/MonumentaWarps"],
        "replace_items_globally": True,
    }

    playerplots = {
        "server":"playerplots",
        "move_base_from":"previous",
        "datapacks":datapacks_base + ['file/playerplots'],
        "move_previous_paths":["Project_Epic-playerplots/stats", "Project_Epic-playerplots/data/scoreboard.dat", "plugins/CoreProtect", "plugins/MonumentaWarps"],
        "replace_items_globally": True,
    }

    tutorial = {
        "server":"tutorial",
        "move_base_from":"build",
        "datapacks":datapacks_dungeon + ['file/tutorial'],
    }

    corridors = {
        "server":"corridors",
        "move_base_from":"build",
        "move_previous_paths":["Project_Epic-corridors/stats", "Project_Epic-corridors/data/scoreboard.dat"],
        "datapacks":datapacks_dungeon + ['file/corridors'],
    }

    verdant = {
        "server":"verdant",
        "move_base_from":"build",
        "move_previous_paths":["Project_Epic-verdant/stats", "Project_Epic-verdant/data/scoreboard.dat"],
        "datapacks":datapacks_dungeon + ['file/verdant'],
    }

    rush = {
        "server":"rush",
        "move_base_from":"build",
        "move_previous_paths":["Project_Epic-rush/stats", "Project_Epic-rush/data/scoreboard.dat"],
        "datapacks":datapacks_dungeon + ['file/rush'],
    }

    mist = {
        "server":"mist",
        "move_base_from":"build",
        "move_previous_paths":["Project_Epic-mist/stats", "Project_Epic-mist/data/scoreboard.dat"],
        "datapacks":datapacks_dungeon + ['file/mist'],
    }

    remorse = {
        "server":"remorse",
        "move_base_from":"build",
        "move_previous_paths":["Project_Epic-remorse/stats", "Project_Epic-remorse/data/scoreboard.dat"],
        "datapacks":datapacks_dungeon + ['file/remorse'],
    }

    depths = {
        "server":"depths",
        "copy_base_from":"build",
        "move_previous_paths":["Project_Epic-depths/stats", "Project_Epic-depths/data/scoreboard.dat"],
        "datapacks":datapacks_dungeon + ['file/depths'],
    }

    valley = {
        "server":"valley",
        "copy_base_from":"build",
        "move_previous_paths":["Project_Epic-valley/stats", "Project_Epic-valley/data/scoreboard.dat"],
        "datapacks":datapacks_base + ['file/valley'],
        "coordinates_to_fill":(
            {"name":"Magic Block", "pos1":(-1441, 2, -1441), "pos2":(-1441, 2, -1441), 'block': {'name': 'minecraft:air'}},
        ),
    }

    isles = {
        "server":"isles",
        "copy_base_from":"build",
        "move_previous_paths":["Project_Epic-isles/stats", "Project_Epic-isles/data/scoreboard.dat"],
        "datapacks":datapacks_base + ['file/isles'],
        "coordinates_to_fill":(
            {"name":"Magic Block", "pos1":(-1441, 2, -1441), "pos2":(-1441, 2, -1441), 'block': {'name': 'minecraft:air'}},
        ),
    }

    available_configs = {
        "plots": plots,
        "playerplots": playerplots,
        "valley": valley,
        "valley-2": {**valley, **{"shard_name": "valley"}},
        "valley-3": {**valley, **{"shard_name": "valley"}},
        "isles": isles,
        "isles-2": {**isles, **{"shard_name": "isles"}},
        "isles-3": {**isles, **{"shard_name": "isles"}},
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
        "sanctum": get_dungeon_config("sanctum", "DFSAccess"),
        "labs": get_dungeon_config("labs", "D0Access"),
        "teal": get_dungeon_config("teal", "DTLAccess"),
        "forum": get_dungeon_config("forum", "DFFAccess"),
        "shiftingcity": get_dungeon_config("shiftingcity", "DRL2Access"),
        "corridors": corridors,
        "corridors-2": {**corridors, **{"shard_name": "corridors"}},
        "corridors-3": {**corridors, **{"shard_name": "corridors"}},
        "verdant": verdant,
        "rush": rush,
        "mist": mist,
        "remorse": remorse,
        "depths": depths,
        "depths-2": {**depths, **{"shard_name": "depths"}},
        "depths-3": {**depths, **{"shard_name": "depths"}},
        "tutorial": tutorial,
        "build": None,
        "bungee": None,
        "bungee-11": None,
        "purgatory": None,
    }

    # Parse additional non-option arguments and copy those configs to the list of servers to update
    config_list = []
    for server in args:
        if server in available_configs:
            if available_configs[server] is not None:
                config = available_configs[server]
                shard_name = config.get("shard_name", server)
                config["build_path"] = os.path.join(build_template_dir, shard_name)
                config["output_path"] = os.path.join(output_dir, server)
                config["previous_path"] = os.path.join(last_week_dir, server)
                config_list.append(available_configs[server])
        else:
            print("ERROR: Unknown shard {} specified!".format(server))
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
            score_objects = redis_scoreboard.search_scores(Objective=preserve_instances["dungeon_objective"], Score={"min":1})
            dungeon_scores = set()
            for score in score_objects:
                val = score.at_path("Score").value
                dungeon_scores.add(val)
            dungeon_scores = sorted(list(dungeon_scores))
            preserve_instances["dungeon_scores"] = dungeon_scores
    timings.nextStep("Loaded dungeon scores")

    ##################################################################################
    # Move base world files

    print("Moving base worlds...")
    # First check for missing directories and fail if any are found
    for config in config_list:
        server = config["server"]
        # If the shard name is specified, use this as the base name for the shard, rather than the server name
        shard_name = config.get("shard_name", server)

        # Move or copy base first - either from build or previously existing data
        if "move_base_from" in config:
            if config["move_base_from"] == "build":
                for world_name in World.enumerate_worlds(config["build_path"]):
                    from_world_path = os.path.join(config["build_path"], world_name)
                    output_world_path = os.path.join(config["output_path"], world_name)
                    print(f"  {server} - Moving world from {from_world_path} to {output_world_path}")
                    move_folder(from_world_path, output_world_path)

            elif config["move_base_from"] == "previous":
                for world_name in World.enumerate_worlds(config["previous_path"]):
                    from_world_path = os.path.join(config["previous_path"], world_name)
                    output_world_path = os.path.join(config["output_path"], world_name)
                    print(f"  {server} - Moving world from {from_world_path} to {output_world_path}")
                    move_folder(from_world_path, output_world_path)

        if "copy_base_from" in config:
            if config["copy_base_from"] == "build":
                for world_name in World.enumerate_worlds(config["build_path"]):
                    from_world_path = os.path.join(config["build_path"], world_name)
                    output_world_path = os.path.join(config["output_path"], world_name)
                    print(f"  {server} - Copying world from {from_world_path} to {output_world_path}")
                    copy_folder(from_world_path, output_world_path)

            elif config["copy_base_from"] == "previous":
                for world_name in World.enumerate_worlds(config["previous_path"]):
                    from_world_path = os.path.join(config["previous_path"], world_name)
                    output_world_path = os.path.join(config["output_path"], world_name)
                    print(f"  {server} - Copying world from {from_world_path} to {output_world_path}")
                    copy_folder(from_world_path, output_world_path)

        # Move any dungeon instances that should be preserved
        if "preserve_instances" in config:
            preserve_instances = config["preserve_instances"]

            print(f"  {server} - Instances preserved this week: [{','.join(str(x) for x in preserve_instances['dungeon_scores'])}]")
            for instance in preserve_instances["dungeon_scores"]:
                world_name = f"{shard_name}{instance}"
                from_world_path = os.path.join(config["previous_path"], world_name)
                output_world_path = os.path.join(config["output_path"], world_name)
                if os.path.exists(from_world_path):
                    move_folder(from_world_path, output_world_path)
                else:
                    eprint(f"WARNING: Unable to preserve {world_name} - previous world folder does not exist")

        # Move any overworld subfolders that need to be preserved
        if "move_previous_paths" in config:
            print(f"  {server} - Moving previous paths from {config['previous_path']}/[{','.join(config['move_previous_paths'])}] to {config['output_path']}")
            move_paths(config['previous_path'], config['output_path'], config["move_previous_paths"])

        # Enumerate all the resulting worlds for later use
        config["worlds"] = World.enumerate_worlds(config["output_path"])
        if len(config["worlds"]) == 0:
            raise Exception("ERROR: Config doesn't specify any worlds or they are missing: {!r}".format(config))

    timings.nextStep("Moved folders")

    ##################################################################################
    # Open the worlds for use

    print("Opening worlds, changing datapacks & filling areas...")
    worlds_paths = {}
    for config in config_list:
        for world_name in config["worlds"]:
            output_world_path = os.path.join(config["output_path"], world_name)

            world = World(output_world_path)
            worlds_paths[world_name] = output_world_path

            if "datapacks" in config:
                world.level_dat.enabled_datapacks = config["datapacks"]
                world.level_dat.save()

            if "coordinates_to_fill" in config:
                print(f"  {world_name} - Filling selected regions with specified blocks...")
                for section in config["coordinates_to_fill"]:
                    print(f"    Filling {repr(section['name'])} with {section['block']}")
                    world.fill_blocks(section["pos1"], section["pos2"], section["block"])

    timings.nextStep("Loaded worlds, changed datapacks & filled areas")


    ##################################################################################
    # Compute which region files need attention

    print("Computing region files to process...")
    # This list of regions will be processed by pooled process workers
    # Format is:
    # [
    #   {
    #     "world": str
    #     "world_path": str
    #     "rx": int
    #     "rz": int
    #   }
    # ]
    regions = []
    for config in config_list:
        if "replace_items_globally" in config and config["replace_items_globally"]:
            for world_name in config["worlds"]:
                world_path = worlds_paths[world_name]
                for _, rx, rz, __ in World(world_path).enumerate_regions():
                    regions.append({
                        "world": world_name,
                        "world_path": world_path,
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

    # Run the regions in parallel using a pool. As results come in, accumulate them to the appropriate list based on the world
    parallel_args = []
    for region_config in regions:
        parallel_args.append((_create_region_lambda, (region_config,), None, None, process_region, err_func, ()))

    generator = process_in_parallel(parallel_args, num_processes=num_threads, initializer=process_init, initargs=(item_replace_manager, ))
    num_global_replacements, replacements_log = item_replace_manager.merge_log_tuples(generator, {})

    timings.nextStep(f"Processed regions and merged logs: {num_global_replacements} replacements")

    ##################################################################################
    # Writing logs

    print(f"Writing replacements logs...")

    log_handle = None
    if logfile == "stdout":
        log_handle = sys.stdout
    elif logfile == "stderr":
        log_handle = sys.stderr
    elif logfile is not None:
        if os.path.dirname(logfile) and not os.path.isdir(os.path.dirname(logfile)):
            os.makedirs(os.path.dirname(logfile), mode=0o775)
        log_handle = open(logfile, 'w')

    if log_handle is not None:
        yaml.dump(replacements_log, log_handle, width=2147483647, allow_unicode=True)

    if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
        log_handle.close()

    timings.nextStep("Logs written")

    print("Finished")
