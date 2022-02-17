#!/usr/bin/env pypy3

"""List items and loot tables in a world, with an optional search area."""

import argparse
import math
import sys
from pathlib import Path
import yaml

from lib_py3.common import parse_name_possibly_json
from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.entity import Entity
from minecraft.player_dat_format.item import Item
from minecraft.world import World

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('world', type=Path, help="A world folder")
    arg_parser.add_argument('--trades-only', action='store_true')
    arg_parser.add_argument('--logfile', type=Path, help="Log file to write to, defaults to stdout", nargs='?', default=sys.stdout)
    arg_parser.add_argument('x1', type=int, nargs='?')
    arg_parser.add_argument('y1', type=int, nargs='?')
    arg_parser.add_argument('z1', type=int, nargs='?')
    arg_parser.add_argument('x2', type=int, nargs='?')
    arg_parser.add_argument('y2', type=int, nargs='?')
    arg_parser.add_argument('z2', type=int, nargs='?')

    args = arg_parser.parse_args()

    if not args.world.is_dir():
        arg_parser.error('world must be a path to a world folder')
        sys.exit()

    min_x = -math.inf
    min_y = -math.inf
    min_z = -math.inf
    max_x = math.inf
    max_y = math.inf
    max_z = math.inf
    if args.x1 is not None:
        if args.z2 is None:
            arg_parser.error('coordinates must either fully set or fully unset')
            sys.exit()

        min_x = min(args.x1, args.x2)
        min_y = min(args.y1, args.y2)
        min_z = min(args.z1, args.z2)
        max_x = max(args.x1, args.x2)
        max_y = max(args.y1, args.y2)
        max_z = max(args.z1, args.z2)

    print(f"Scanning {min_x} {min_y} {min_z} {max_x} {max_y} {max_z}")

    if max_x is not None:
        max_x += 1
        max_y += 1
        max_z += 1

    loot_tables = {}
    items_found = {}

    world = World(str(args.world))
    for region in world.iter_regions(min_x, min_y, min_z, max_x, max_y, max_z, read_only=True):
        for chunk in region.iter_chunks(min_x, min_y, min_z, max_x, max_y, max_z, autosave=False):
            for thing in chunk.recursive_iter_all_types(min_x, min_y, min_z, max_x, max_y, max_z):
                if thing.parent is not None and (not args.trades_only or (isinstance(thing.parent, Entity) and (thing.parent.id == "villager" or thing.parent.id == "minecraft:villager"))):
                    parent_path = thing.parent.get_debug_str()
                    if isinstance(thing, Item) and thing.id != "minecraft:air":
                        locmap = items_found.get(parent_path, {})
                        name = ""
                        if thing.nbt.has_path("tag.display.Name"):
                            name = parse_name_possibly_json(thing.nbt.at_path("tag.display.Name").value, remove_color=True) + "   " + thing.id
                        lst = locmap.get(name, [])
                        lst.append(thing.nbt.to_mojangson())
                        locmap[name] = lst
                        items_found[parent_path] = locmap

                    elif isinstance(thing, (Entity, BlockEntity)):
                        if thing.nbt.has_path("LootTable"):
                            lst = loot_tables.get(parent_path, [])
                            lst.append(thing.nbt.at_path("LootTable").value)
                            loot_tables[parent_path] = lst

    outpath = 'stdout' if args.logfile is sys.stdout else args.logfile

    if args.logfile is not sys.stdout:
        args.logfile = open(args.logfile, "w")

    output = {"loot_tables": loot_tables, "items": items_found}
    yaml.dump(output, args.logfile, width=2147483647, allow_unicode=True)

    print(f"Wrote {len(items_found)} item locations and {len(loot_tables)} loot table locations to {outpath}")

    if args.logfile is not sys.stdout:
        args.logfile.close()
