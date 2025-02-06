#!/usr/bin/env python3
"""Updates the list of worlds displayed on the dynmap"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import yaml

from lib_py3.common import eprint
from minecraft.world import World


IGNORED_SHARD_RE = tuple(re.compile(x) for x in [
    # Can't have duplicate overworld names
    'valley-[2-9]',
    'valley-[1-9][0-9]+',
    'isles-[2-9]',
    'isles-[1-9][0-9]+',
    'ring-[2-9]',
    'ring-[1-9][0-9]+',
])


IGNORED_WORLD_RE = tuple(re.compile(x) for x in [
    'pregen_.*', # Never show pregenerated worlds
    '[A-Za-z_-]+[A-Za-z][0-9]+', # Never show generated worlds (ending in a number preceded by anything other than - or _)
])


IGNORED_WORLD_EXCEPTIONS_RE = tuple(re.compile(x) for x in [
    'Project_Epic-dev[0-9]+', # Show dev shards despite matching instanced world names
    'portal2',
])


def main():
    """Updates the dynmap world list"""
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('dynmap', type=Path, help='The dynmap web folder, containing standalone/')
    arg_parser.add_argument('host', type=Path, nargs='+', help='A host server path, containing all shard folders')
    args = arg_parser.parse_args()

    dynmap_path = args.dynmap
    host_paths = args.host

    dynmap_standalone = dynmap_path / 'standalone'
    dynmap_tiles = dynmap_path / 'tiles'
    reference_config_path = dynmap_standalone / 'dynmap_config_REFERENCE.json'
    if not reference_config_path.is_file():
        eprint(f'Could not find reference config {reference_config_path}')
        sys.exit()
    for host_path in host_paths:
        if not host_path.is_dir():
            eprint(f'Host path is not a directory: {host_path}')
            sys.exit()

    config = {}
    with open(reference_config_path, 'r', encoding='utf-8-sig') as fp:
        config = json.load(fp)

    example_world_config = config["worlds"][0]

    reference_maps = {}
    for reference_map in example_world_config["maps"]:
        reference_maps[reference_map["prefix"]] = reference_map

    found_names = set()
    duplicate_names = set()
    world_paths = []
    for host_path in sorted(host_paths):
        for world_path in sorted(World.enumerate_worlds(host_path)):
            shard_name = world_path.parent.name
            if any(x.fullmatch(shard_name) is not None for x in IGNORED_SHARD_RE):
                #print(f'-{shard_name} (shard in ignored list)')
                continue

            world_name = world_path.name
            if any(x.fullmatch(world_name) is not None for x in IGNORED_WORLD_RE):
                if not any(x.fullmatch(world_name) is not None for x in IGNORED_WORLD_EXCEPTIONS_RE):
                    #print(f'-{world_path} (in ignored list, not in exception list)')
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
        world_tiles = dynmap_tiles / world_name
        if not world_tiles.is_dir():
            print(f'-{world_path} (no dynmap tiles found)')
            continue
        print(f'+{world_path}')

        shard_path = world_path.parent
        shard_worlds_file = shard_path / 'plugins' / 'dynmap' / 'worlds.txt'
        if not shard_worlds_file.is_file():
            print(f'-{world_path} (plugins/dynmap/worlds.txt file found)')
            continue

        shard_worlds_config = None
        try:
            with open(shard_worlds_file, 'r', encoding='utf-8-sig') as fp:
                shard_worlds_config = yaml.load(fp, Loader=yaml.FullLoader)
        except Exception:
            print(f'-{world_path} (could not read plugins/dynmap/worlds.txt)')
            continue

        world_plugin_config = None
        for test_world_config in shard_worlds_config.get("worlds", []):
            if test_world_config.get("name", None) == world_name:
                world_plugin_config = test_world_config
                break

        world_title = world_plugin_config["title"]

        sort_key = str((world_title.lower(), world_title))

        map_configs = []
        for map_plugin_config in world_plugin_config["maps"]:
            map_prefix = map_plugin_config["prefix"]
            map_config = deepcopy(reference_maps.get(map_prefix, None))
            if map_config is None:
                continue

            map_config["title"] = map_plugin_config["title"]
            map_config["lighting"] = map_plugin_config["lighting"]
            if "background" in map_plugin_config:
                map_config["background"] = map_plugin_config["background"]
            if "icon" in map_plugin_config:
                map_config["icon"] = map_plugin_config["icon"]

            map_configs.append(map_config)

        world_config = deepcopy(example_world_config)
        world_config["name"] = world_plugin_config["name"]
        world_config["title"] = world_title
        world_config["center"] = world_plugin_config["center"]
        world_config["maps"] = map_configs

        world_configs[sort_key] = world_config

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
