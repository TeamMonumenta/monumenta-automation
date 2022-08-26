#!/usr/bin/env pypy3

import os
import sys
import multiprocessing
import concurrent.futures
import getopt
import yaml

from lib_py3.common import copy_paths, copy_maps, eprint
from lib_py3.timing import Timings
from minecraft.world import World

def usage():
    sys.exit(f"""
Usage: {sys.argv[0]} <--dungeon-path /path/to/dungeon> <--out-folder /path/to/out> [--count #] [--skip #] [--num-threads #] [dungeon1 dungeon2 ...]

Arguments:
    --dungeon-path path
        The path to the dungeon folder which contains Project_Epic-dungeon and other worlds as a template to generate instances
    --out-folder out
        Output folder where instances will be generated
    --count #
        Number of instances to generate of each dungeon
    --skip #
        Skip the first # instances. This is useful when generating new instances to add to the already existing ones on the play server
        If --skip is specified, will also skip copying the spawn region
    dungeon1 dungeon2 ...
        The names of dungeons to generate
""")

def create_instance(instance_arg):
    rx, rz = instance_arg
    ref_region.copy_to(new_world, rx, rz)

if __name__ == '__main__':
    multiprocessing.set_start_method("fork")

    config = {
        # Dungeons are placed one per MC region file (32x32 chunks)
        # Each dungeon starts in the most-negative corner of the region
        # Regions with dungeons form a line of consecutive regions in +z
        #
        # Each region containing a dungeon is full of void biome
        # There is a padding layer of void biome in the -x and -z directions as specified below
        #
        # All dungeons fit in a region file; even corrupted sierhaven is only 30x24 chunks

        "dungeons":{
            "labs":{
                "world": "labs",
                "objective":"D0Access"
            },
            "white":{
                "world": "white",
                "objective":"D1Access"
            },
            "orange":{
                "world": "orange",
                "objective":"D2Access"
            },
            "magenta":{
                "world": "magenta",
                "objective":"D3Access"
            },
            "lightblue":{
                "world": "lightblue",
                "objective":"D4Access"
            },
            "yellow":{
                "world": "yellow",
                "objective":"D5Access"
            },
            "lime":{
                "world": "lime",
                "objective":"D6Access"
            },
            "pink":{
                "world": "pink",
                "objective":"D7Access"
            },
            "gray":{
                "world": "gray",
                "objective":"D8Access"
            },
            "lightgray":{
                "world": "lightgray",
                "objective":"D9Access"
            },
            "cyan":{
                "world": "cyan",
                "objective":"D10Access"
            },
            "purple":{
                "world": "purple",
                "objective":"D11Access"
            },
            "willows":{
                "world": "willows",
                "objective":"DB1Access"
            },
            "verdant":{
                "world": "verdant",
                "objective":"DVAccess"
            },
            "corridors":{
                "world": "corridors",
                "objective":"DRAccess"
            },
            "reverie":{
                "world": "reverie",
                "objective":"DCAccess"
            },
            "tutorial":{
                "world": "tutorial",
                "objective":"DTAccess"
            },
            "sanctum":{
                "world": "sanctum",
                "objective":"DFSAccess"
            },
            "shiftingcity":{
                "world": "shiftingcity",
                "objective":"DRL2Access"
            },
            "teal":{
                "world": "teal",
                "objective":"DTLAccess"
            },
            "forum":{
                "world": "forum",
                "objective":"DFFAccess"
            },
            "remorse":{
                "world": "remorse",
                "objective":"DSRAccess"
            },
            "rush":{
                "world": "rush",
                "objective":"DRDAccess"
            },
            "mist":{
                "world": "mist",
                "objective":"DBMAccess"
            },
            "depths":{
                "world": "depths",
                "objective":"DDAccess"
            },

            "gallery":{
                "world": "gallery",
                "objective":"DGAccess"
            },
        },

        # Chunk to copy directly from the reference folder
        "spawn_region":{"x":-3, "z":-3},

        # Dungeon instances start nn region -3,-2 and move in +z - a region is 32x32 chunks
        "target_region":{"x":-3, "z":-2},

        # Files/directories to copy from reference
        "copy_paths":[
            "level.dat",
        ],

        # Blocks to set
        "set_blocks_in_spawn":[
            {'pos': [-1441, 2, -1441], 'block': {'name': 'minecraft:air'}},
        ],
    }

    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:w:o:c:s:j:", ["dungeon-path=", "master-world=", "out-folder=", "count=", "skip=", "num-threads="])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    dungeon_path = None
    world_path = None
    out_folder = None
    force_count = None
    skip_count = None
    num_threads = 4
    specific_worlds = []

    for o, a in opts:
        if o in ("-d", "--dungeon-path"):
            dungeon_path = a
            if not dungeon_path.endswith("/"):
                dungeon_path += "/"
        elif o in ("-w", "--master-world"):
            eprint("--master-world is deprecated, use --dungeon-path instead")
            world_path = a
            if not world_path.endswith("/"):
                world_path += "/"
        elif o in ("-o", "--out-folder"):
            out_folder = a
            if not out_folder.endswith("/"):
                out_folder += "/"
        elif o in ("-c", "--count"):
            force_count = int(a)
            if force_count < 1 or force_count > 10000:
                eprint("--count must be between 1 and 10000")
                usage()
        elif o in ("-s", "--skip"):
            skip_count = int(a)
            if skip_count < 1 or skip_count > 10000:
                eprint("--skip must be between 1 and 10000")
                usage()
        elif o in ("-j", "--num-threads"):
            num_threads = int(a)
            if num_threads < 1 or num_threads > 16:
                eprint("--num-threads must be between 1 and 16")
                usage()
            if num_threads > 4:
                eprint(f"WARNING: --num-threads={num_threads} is unusually high. Unless you know what you are doing, suggest using a value <= 4 to avoid significant performance problems for the play server.")
        else:
            eprint("Unknown argument: {}".format(o))
            usage()

    # Parse additional non-option arguments
    for arg in args:
        match = None
        if arg not in config["dungeons"]:
            eprint("Unknown dungeon: {}".format(arg))
            usage()
        else:
            specific_worlds.append(arg)

    if dungeon_path is None:
        if world_path is not None:
            dungeon_path = os.path.join(world_path, "..")
        else:
            eprint("--dungeon-path must be specified!")
            usage()

    if out_folder is None:
        eprint("--out-folder must be specified!")
        usage()

    if force_count is not None:
        # Override all dungeon counts
        for name in config["dungeons"]:
            if "count" in config["dungeons"][name]:
                config["dungeons"][name]["count"] = force_count

    if len(specific_worlds) > 0:
        # Only generate the specified worlds
        new_dungeons = {}
        for specified in specific_worlds:
            new_dungeons[specified] = config["dungeons"][specified]
        config["dungeons"] = new_dungeons

    # Decrease the priority for this work so it doesn't slow down other things
    os.nice(20)

    timings = Timings(enabled=True)
    for name in config["dungeons"]:
        print(f"Generating {name} instances...")
        dungeon = config["dungeons"][name]
        # Compute where the new world will be
        new_shard_path = os.path.join(out_folder, f"{name}")
        new_world_path = os.path.join(new_shard_path, f"Project_Epic-{name}")
        dungeon_template_world_path = os.path.join(dungeon_path, "Project_Epic-dungeon")

        # Create target directories
        for region_type in ('entities', 'poi', 'region'):
            if not os.path.isdir(os.path.join(new_world_path, region_type)):
                os.makedirs(os.path.join(new_world_path, region_type), mode=0o775)

        # Copy files/directories
        copy_paths(dungeon_template_world_path, new_world_path, config["copy_paths"])
        copy_maps(dungeon_template_world_path, new_world_path)

        # Load new and old worlds
        ref_world = World(dungeon_template_world_path)
        new_world = World(new_world_path)

        # TODO: Change level.dat uuid and name

        # Copy spawn chunks
        if skip_count is None:
            spawn_region = config["spawn_region"]
            ref_world.get_region(spawn_region["x"], spawn_region["z"], read_only=True).copy_to(new_world, spawn_region["x"], spawn_region["z"])

            # Set blocks in sorting box if one was made
            if "set_blocks_in_spawn" in config:
                for block in config["set_blocks_in_spawn"]:
                    new_world.set_block(block["pos"], block["block"])

        if "region" in dungeon:
            ################ Create the new instances from a given region

            # Open the source region as a global variable
            ref_region = ref_world.get_region(dungeon["region"]["x"], dungeon["region"]["z"], read_only=True)

            # Create a list of all the region files that need copying to
            args = []
            for i in range(dungeon["count"]):
                if skip_count is not None and i < skip_count:
                    continue
                args.append((config["target_region"]["x"], config["target_region"]["z"] + i))

            if num_threads == 1:
                # Don't bother with processes if only going to use one
                # This makes debugging much easier
                for arg in args:
                    create_instance(arg)
            else:
                done_count = 0
                with concurrent.futures.ProcessPoolExecutor(max_workers=num_threads) as pool:
                    for _ in pool.map(create_instance, args):
                        done_count += 1

                        print(f"  {done_count} / {dungeon['count']} instances generated")

            timings.nextStep(f"{name}: {dungeon['count']} instances generated")

        elif "world" in dungeon:
            ################ Copy the template world that instances will be created from
            copy_paths(dungeon_path, new_shard_path, [dungeon["world"],])

            timings.nextStep(f"{name}: world copied")

    with open(os.path.join(out_folder, "dungeon_info.yml"), "w") as fp:
        yaml.dump(config, fp, width=2147483647, allow_unicode=True)

    print("Dungeon instance generation complete")
