#!/usr/bin/env python3

import os
import sys
import multiprocessing
import getopt
import yaml

from lib_py3.common import copy_paths, copy_maps, eprint
from lib_py3.timing import Timings
from minecraft.world import World

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
            "region":{"x":-2, "z":2},
            "count":700,
            "objective":"D0Access"
        },
        "white":{
            "region":{"x":-3, "z":-2},
            "count":150,
            "objective":"D1Access"
        },
        "orange":{
            "region":{"x":-3, "z":-1},
            "count":75,
            "objective":"D2Access"
        },
        "magenta":{
            "region":{"x":-3, "z":0},
            "count":50,
            "objective":"D3Access"
        },
        "lightblue":{
            "region":{"x":-3, "z":1},
            "count":40,
            "objective":"D4Access"
        },
        "yellow":{
            "region":{"x":-3, "z":2},
            "count":40,
            "objective":"D5Access"
        },
        "lime":{
            "region":{"x":-3, "z":5},
            "count":40,
            "objective":"D6Access"
        },
        "pink":{
            "region":{"x":-3, "z":7},
            "count":40,
            "objective":"D7Access"
        },
        "gray":{
            "region":{"x":-3, "z":6},
            "count":40,
            "objective":"D8Access"
        },
        "lightgray":{
            "region":{"x":-3, "z":8},
            "count":40,
            "objective":"D9Access"
        },
        "cyan":{
            "region":{"x":-3, "z":9},
            "count":40,
            "objective":"D10Access"
        },
        "purple":{
            "region":{"x":-3, "z":13},
            "count":40,
            "objective":"D11Access"
        },
        "willows":{
            "region":{"x":-3, "z":3},
            "count":50,
            "objective":"DB1Access"
        },
        "roguelike":{
            "region":{"x":-2, "z":-1},
            "count":100,
            "objective":"DRAccess"
        },
        "reverie":{
            "region":{"x":-3, "z":4},
            "count":40,
            "objective":"DCAccess"
        },
        "tutorial":{
            "region":{"x":-2, "z":1},
            "count":999,
            "objective":"DTAccess"
        },
        "sanctum":{
            "region":{"x":-3, "z":12},
            "count":40,
            "objective":"DS1Access"
        },
        "shiftingcity":{
            "region":{"x":-2, "z":9},
            "count":50,
            "objective":"DRL2Access"
        },
        "teal":{
            "region":{"x":-2, "z":12},
            "count":50,
            "objective":"DTLAccess"
        },
        "forum":{
            "region":{"x":-3, "z":16},
            "count":50,
            "objective":"DFFAccess"
        },
        "rush":{
            "region":{"x":-3, "z":15},
            "count":50,
            "objective":"DRDAccess"
        },
        "mist":{
            "region":{"x":-2, "z":3},
            "count":200,
            "objective":"DBMAccess"
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
    "set_blocks":[
        {'pos': [-1441, 2, -1441], 'block': {'name': 'minecraft:air'} },
    ],
}

def usage():
    sys.exit("Usage: {} <--master-world /path/to/world> <--out-folder /path/to/out> [--count #] [--num-threads #] [dungeon1 dungeon2 dungeon3 ...]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:o:c:j:", ["master-world=", "out-folder=", "count=", "num-threads="])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
out_folder = None
force_count = None
num_threads = 4
specific_worlds = []

for o, a in opts:
    if o in ("-w", "--master-world"):
        world_path = a
        if not world_path.endswith("/"):
            world_path += "/"
    elif o in ("-o", "--out-folder"):
        out_folder = a
        if not out_folder.endswith("/"):
            out_folder += "/"
    elif o in ("-c", "--count"):
        force_count = int(a)
        if force_count < 1 or force_count > 1000:
            eprint("--count must be between 1 and 1000")
            usage()
    elif o in ("-j", "--num-threads"):
        num_threads = int(a)
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

if world_path is None:
    eprint("--master-world must be specified!")
    usage()
if out_folder is None:
    eprint("--out-folder must be specified!")
    usage()

if force_count is not None:
    # Override all dungeon counts
    for name in config["dungeons"]:
        config["dungeons"][name]["count"] = force_count

if len(specific_worlds) > 0:
    # Only generate the specified worlds
    new_dungeons = {}
    for specified in specific_worlds:
        new_dungeons[specified] = config["dungeons"][specified]
    config["dungeons"] = new_dungeons

# Decrease the priority for this work so it doesn't slow down other things
os.nice(20)

def create_instance(arg):
    rx, rz = arg
    ref_region.copy_to(new_world, rx, rz)

timings = Timings(enabled=True)
for name in config["dungeons"]:
    print(f"Generating {name} instances...")
    dungeon = config["dungeons"][name]
    # Compute where the new world will be
    new_world_path = os.path.join(out_folder, f"{name}", f"Project_Epic-{name}")

    # Create target directories
    if not os.path.isdir(os.path.join(new_world_path, "region")):
        os.makedirs(os.path.join(new_world_path, "region"), mode=0o775)

    # Copy files/directories
    copy_paths(world_path, new_world_path, config["copy_paths"])
    copy_maps(world_path, new_world_path)

    # Load new and old worlds
    ref_world = World(world_path)
    new_world = World(new_world_path)

    # TODO: Change level.dat uuid and name

    # Copy spawn chunks
    spawn_region = config["spawn_region"]
    ref_world.get_region(spawn_region["x"], spawn_region["z"], read_only=True).copy_to(new_world, spawn_region["x"], spawn_region["z"])

    ###############
    # Create the new instances

    # Open the source region as a global variable
    ref_region = ref_world.get_region(dungeon["region"]["x"], dungeon["region"]["z"], read_only=True)

    # Create a list of all the region files that need copying to
    args = []
    for i in range(dungeon["count"]):
        args.append((config["target_region"]["x"], config["target_region"]["z"] + i))

    if num_threads == 1:
        # Don't bother with processes if only going to use one
        # This makes debugging much easier
        for arg in args:
            create_instance(arg)
    else:
        done_count = 0
        with multiprocessing.Pool(num_threads) as pool:
            for _ in pool.imap_unordered(create_instance, args):
                done_count += 1

                print(f"  {done_count} / {dungeon['count']} instances generated")

    # /Create the new instances
    ###############

    # Set blocks
    if "set_blocks" in config:
        for block in config["set_blocks"]:
            from pprint import pprint
            new_world.set_block(block["pos"], block["block"])

    timings.nextStep(f"{name}: {dungeon['count']} instances generated")

with open(os.path.join(out_folder, "dungeon_info.yml"), "w") as fp:
    yaml.dump(config, fp, width=2147483647, allow_unicode=True)

print("Dungeon instance generation complete")
