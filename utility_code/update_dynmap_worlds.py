#!/usr/bin/env python3
"""Updates the list of worlds displayed on the dynmap"""
import argparse
import json
from pathlib import Path
import re
import sys

from lib_py3.common import eprint
from minecraft.world import World


IGNORED_WORLD_RE = tuple([re.compile(x) for x in [
    'pregen_.*', # Never show pregenerated worlds
    '[A-Za-z_-]+[A-Za-z][0-9]+', # Never show generated worlds (ending in a number preceded by anything other than - or _)
]])


IGNORED_WORLD_EXCEPTIONS_RE = tuple([re.compile(x) for x in [
    'Project_Epic-dev[0-9]+', # Show dev shards despite matching instanced world names
    'portal2',
]])


def main():
    """Updates the dynmap world list"""
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('dynmap', type=Path, help='The dynmap web folder, containing standalone/')
    arg_parser.add_argument('host', type=Path, nargs='+', help='A host server path, containing all shard folders')
    args = arg_parser.parse_args()

    dynmap_path = args.dynmap
    host_paths = args.host

    dynmap_standalone = dynmap_path / 'standalone'
    reference_config_path = dynmap_standalone / 'dynmap_config_REFERENCE.json'
    if not reference_config_path.is_file():
        eprint(f'Could not find reference config {reference_config_path}')
        sys.exit()
    for host_path in host_paths:
        if not host_path.is_dir():
            eprint(f'Host path is not a directory: {host_path}')
            sys.exit()

    found_names = set()
    duplicate_names = set()
    world_paths = []
    for host_path in sorted(host_paths):
        for world_path in sorted(World.enumerate_worlds(host_path)):
            world_name = world_path.name
            if any([x.fullmatch(world_name) is not None for x in IGNORED_WORLD_RE]):
                if not any([x.fullmatch(world_name) is not None for x in IGNORED_WORLD_EXCEPTIONS_RE]):
                    print(f'-{world_path} (in ignored list, not in exception list)')
                    continue

            if world_name in found_names:
                duplicate_names.add(world_name)
            found_names.add(world_name)
            world_paths.append(world_path)

    world_configs = {}
    for world_path in world_paths:
        world_name = world_path.name
        if world_name in duplicate_names:
            print(f'-{world_path} (duplicate world name)')
            continue
        world_dynmap_config = dynmap_standalone / f'dynmap_{world_name}.json'
        if not world_dynmap_config.is_file():
            print(f'-{world_path} (no dynmap files found)')
            continue
        print(f'+{world_path}')

        world = World(world_path)
        level_dat = world.level_dat
        spawn = level_dat.spawn

        sort_key = str((world_name.lower(), world_name))

        world_configs[sort_key] = {
            "sealevel": 63,
            "protected": False,
            "maps": [
                {
                    "nightandday": False,
                    "shader": "stdtexture",
                    "compassview": "S",
                    "prefix": "flat",
                    "tilescale": 0,
                    "icon": None,
                    "scale": 4,
                    "azimuth": 270,
                    "type": "HDMapType",
                    "title": "Flat",
                    "backgroundday": None,
                    "protected": False,
                    "mapzoomout": 5,
                    "perspective": "iso_S_90_lowres",
                    "worldtomap": [
                        4,
                        0,
                        -2.4492935982947064e-16,
                        -2.4492935982947064e-16,
                        0,
                        -4,
                        0,
                        1,
                        0
                    ],
                    "inclination": 90,
                    "image-format": "jpg",
                    "lighting": "default",
                    "bigmap": True,
                    "maptoworld": [
                        0.25,
                        -1.5308084989341915e-17,
                        0,
                        0,
                        0,
                        1,
                        -1.5308084989341915e-17,
                        -0.25,
                        0
                    ],
                    "background": None,
                    "boostzoom": 0,
                    "name": "flat",
                    "backgroundnight": None,
                    "mapzoomin": 2
                }
            ],
            "extrazoomout": 2,
            "center": {
                "x": int(spawn[0]),
                "y": int(spawn[1]),
                "z": int(spawn[2])
            },
            "name": world_name,
            "title": world_name,
            "worldheight": 512
        }

    config = {}
    with open(reference_config_path, 'r', encoding='utf-8-sig') as fp:
        config = json.load(fp)

    config["worlds"] = [world_config for _, world_config in sorted(world_configs.items())]

    final_config_path = dynmap_standalone / 'dynmap_config_web.json'
    with open(final_config_path, 'w', encoding='utf-8') as fp:
        json.dump(
            config,
            fp,
            ensure_ascii=False,
            indent=2,
            separators=(',', ': '),
            sort_keys=False
        )
        fp.write("\n")


if __name__ == '__main__':
    main()
