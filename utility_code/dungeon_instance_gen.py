#!/usr/bin/env pypy3

import os
import sys
import getopt
import yaml

from lib_py3.common import copy_paths, copy_maps, eprint
from lib_py3.timing import Timings
from minecraft.world import World
from minecraft.region import Region, EntitiesRegion

def usage():
    """
    Prints usage
    """

    sys.exit(f"""
Usage: {sys.argv[0]} <--dungeon-path /path/to/dungeon> <--out-folder /path/to/out> [dungeon1 dungeon2 ...]

Arguments:
    --dungeon-path path
        The path to the dungeon folder which contains Project_Epic-dungeon and other worlds as a template to generate instances
    --out-folder out
        Output folder where instances will be generated
    dungeon1 dungeon2 ...
        The names of dungeons to generate
""")

if __name__ == '__main__':
    config = {
        # Dungeons are placed one per MC region file (32x32 chunks)
        # Each dungeon starts in the most-negative corner of the region
        # Regions with dungeons form a line of consecutive regions in +z
        #
        # Each region containing a dungeon is full of void biome
        # There is a padding layer of void biome in the -x and -z directions as specified below
        #
        # All dungeons fit in a region file; even corrupted sierhaven is only 30x24 chunks

        "dungeons": {
            "labs": {
                "world": [
                    "labs",
                ],
                "objective":"D0Access"
            },
            "white": {
                "world": [
                    "white",
                    "whiteexalted",
                ],
                "objective":"D1Access"
            },
            "orange": {
                "world": [
                    "orange",
                    "orangeexalted",
                ],
                "objective":"D2Access"
            },
            "magenta": {
                "world": [
                    "magenta",
                    "magentaexalted",
                ],
                "objective":"D3Access"
            },
            "lightblue": {
                "world": [
                    "lightblue",
                    "lightblueexalted",
                ],
                "objective":"D4Access"
            },
            "yellow": {
                "world": [
                    "yellow",
                    "yellowexalted",
                ],
                "objective":"D5Access"
            },
            "lime": {
                "world": [
                    "lime",
                ],
                "objective":"D6Access"
            },
            "pink": {
                "world": [
                    "pink",
                ],
                "objective":"D7Access"
            },
            "gray": {
                "world": [
                    "gray",
                ],
                "objective":"D8Access"
            },
            "lightgray": {
                "world": [
                    "lightgray",
                ],
                "objective":"D9Access"
            },
            "cyan": {
                "world": [
                    "cyan",
                ],
                "objective":"D10Access"
            },
            "purple": {
                "world": [
                    "purple",
                ],
                "objective":"D11Access"
            },
            "blue": {
                "world": [
                    "blue",
                ],
                "objective":"D12Access"
            },
            "brown": {
                "world": [
                    "brown",
                ],
                "objective":"D13Access"
            },
            "willows": {
                "world": [
                    "willows",
                    "willowsexalted",
                ],
                "objective":"DB1Access"
            },
            "verdant": {
                "world": [
                    "verdant",
                ],
                "objective":"DVAccess"
            },
            "corridors": {
                "world": [
                    "corridors",
                ],
                "objective":"DRAccess"
            },
            "reverie": {
                "world": [
                    "reverie",
                ],
                "objective":"DCAccess"
            },
            "tutorial": {
                "world": [
                    "tutorial",
                ],
                "objective":"DTAccess"
            },
            "shiftingcity": {
                "world": [
                    "shiftingcity",
                ],
                "objective":"DRL2Access"
            },
            "teal": {
                "world": [
                    "teal",
                ],
                "objective":"DTLAccess"
            },
            "forum": {
                "world": [
                    "forum",
                ],
                "objective":"DFFAccess"
            },
            "rush": {
                "world": [
                    "rush",
                ],
                "objective":"DRDAccess"
            },
            "depths": {
                "world": [
                    "depths",
                ],
                "objective":"DDAccess"
            },

            "gallery": {
                "world": [
                    "gallery",
                ],
                "objective":"DGAccess"
            },
            "portal": {
                "world": [
                    "portal",
                ],
                "objective":"DPSAccess"
            },
            "ruin": {
                "world": [
                    "bluestrike",
                ],
                "objective":"DMASAccess"
            },
            "skt": {
                "world": [
                    "SKT",
                ],
                "objective":"DSKTAccess"
            },
        },

        # Chunk to copy directly from the reference folder
        "spawn_region": {"x":-3, "z":-3},

        # Dungeon instances start nn region -3,-2 and move in +z - a region is 32x32 chunks
        "target_region": {"x":-3, "z":-2},

        # Files/directories to copy from reference
        "copy_paths": [
            "level.dat",
        ],
    }

    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:o:", ["dungeon-path=", "out-folder="])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    dungeon_path = None
    out_folder = None
    specific_worlds = []

    for o, a in opts:
        if o in ("-d", "--dungeon-path"):
            dungeon_path = a
            if not dungeon_path.endswith("/"):
                dungeon_path += "/"
        elif o in ("-o", "--out-folder"):
            out_folder = a
            if not out_folder.endswith("/"):
                out_folder += "/"
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
        eprint("--dungeon-path must be specified!")
        usage()

    if out_folder is None:
        eprint("--out-folder must be specified!")
        usage()

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

        # Copy spawn chunks
        spawn_region = config["spawn_region"]
        ref_world.get_region(spawn_region["x"], spawn_region["z"], read_only=True, region_type=Region).copy_to(new_world, spawn_region["x"], spawn_region["z"])
        ref_world.get_region(spawn_region["x"], spawn_region["z"], read_only=True, region_type=EntitiesRegion).copy_to(new_world, spawn_region["x"], spawn_region["z"])

        ################ Copy the template world that instances will be created from
        for template_world in dungeon["world"]:
            source_template_world = World(os.path.join(dungeon_path, template_world))
            dest_template_world = source_template_world.copy_to(os.path.join(new_shard_path, template_world), clear_world_uuid=True)

            # Set copied world to normal mode
            dest_template_world.level_dat.difficulty = 2
            dest_template_world.level_dat.save()

        timings.nextStep(f"{name}: world copied")

    with open(os.path.join(out_folder, "dungeon_info.yml"), "w") as fp:
        yaml.dump(config, fp, width=2147483647, allow_unicode=True)

    print("Dungeon instance generation complete")
