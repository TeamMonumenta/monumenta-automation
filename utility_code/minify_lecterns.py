#!/usr/bin/env pypy3

import getopt
import json
import math
import sys

from lib_py3.common import eprint
from lib_py3.common import get_item_name_from_nbt
from lib_py3.loot_table_manager import LootTableManager
from minecraft.world import World


def usage():
    sys.exit("Usage: {} <--world /path/to/world> <--output file.mcfunction [--dry-run] [--pos1 x,y,z --pos2 x,y,z]".format(sys.argv[0]))


def main():
    ASSUMED_GOOD_PREFIXES = [
        'epic:books',
    ]

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["world=", "output=", "pos1=", "pos2=", "dry-run"])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    world_path = None
    output_path = None
    dry_run = False
    pos1 = (-math.inf, -math.inf, -math.inf)
    pos2 = (math.inf, math.inf, math.inf)

    for o, a in opts:
        if o in ("--world",):
            world_path = a
        elif o in ("--output",):
            output_path = a
        elif o in ("--dry-run",):
            print("Running in dry-run mode, changes will not be saved")
            dry_run = True
        elif o in ("--pos1",):
            try:
                split = a.split(",")
                pos1 = (int(split[0]), int(split[1]), int(split[2]))
            except:
                eprint("Invalid --pos1 argument")
                usage()
        elif o in ("--pos2",):
            try:
                split = a.split(",")
                pos2 = (int(split[0]), int(split[1]), int(split[2]))
            except:
                eprint("Invalid --pos2 argument")
                usage()
        else:
            eprint("Unknown argument: {}".format(o))
            usage()

    if world_path is None:
        eprint("--world must be specified!")
        usage()
    elif output_path is None:
        eprint("--output must be specified!")
        usage()
    elif ((pos1 is not None) and (pos2 is None)) or ((pos1 is None) and (pos2 is not None)):
        eprint("--pos1 and --pos2 must be specified (or neither specified)!")
        usage()


    mgr = LootTableManager()
    mgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")

    world = World(world_path)

    out = []
    for region in world.iter_regions(min_x=pos1[0], min_y=pos1[1], min_z=pos1[2], max_x=pos2[0], max_y=pos2[1], max_z=pos2[2]):
        for chunk in region.iter_chunks(autosave=not dry_run):
            for block_entity in chunk.recursive_iter_block_entities():
                if not block_entity.nbt.has_path('id'):
                    continue
                if block_entity.nbt.at_path('id').value != 'minecraft:lectern':
                    continue
                if not block_entity.nbt.has_path('Book.id') or not (block_entity.nbt.has_path('Book.tag.title') or block_entity.nbt.has_path('Book.tag.display.Name')):
                    continue

                block = chunk.get_block(block_entity.pos)
                block_name = block['name']

                book_id = block_entity.nbt.at_path('Book.id').value
                if block_entity.nbt.has_path('Book.tag.display.Name'):
                    book_name = get_item_name_from_nbt(block_entity.nbt.at_path('Book.tag'))
                else:
                    book_name = block_entity.nbt.at_path('Book.tag.title').value

                loot_tables = set()
                book_map = mgr.item_map.get(book_id, None)
                if book_map is None:
                    print(f'{book_id!r} not in {list(mgr.item_map.keys())[:5]!r}, etc')
                else:
                    item = book_map.get(book_name, None)
                    if item is None:
                        print(f'{book_id} named {book_name!r} not in {list(book_map.keys())[:5]!r}, etc')
                    else:
                        if isinstance(item, list):
                            for elem in item:
                                if not elem.get("generated", False):
                                    loot_tables.add(elem["namespaced_key"])
                        else:
                            if not item.get("generated", False):
                                loot_tables.add(item["namespaced_key"])
                if len(loot_tables) == 0:
                    print(f'{book_id} named {book_name} at {" ".join(block_entity.pos)} has no loot table!')
                    continue

                good_loot_tables = set()
                for loot_table in loot_tables:
                    for good_prefix in ASSUMED_GOOD_PREFIXES:
                        if loot_table.startswith(good_prefix):
                            good_loot_tables.add(loot_table)
                            break
                if len(good_loot_tables) == 0:
                    print(f'{book_id} named {book_name} has no known good loot table!')
                    print(f'- {sorted(loot_tables)}')
                    continue

                entry = {}
                entry['pos'] = block_entity.pos
                entry['block'] = block
                entry['book_id'] = book_id
                entry['book_name'] = book_name
                entry['loot_tables'] = list(sorted(loot_tables))
                entry['good_loot_tables'] = list(sorted(good_loot_tables))

                # Danger Will Robinson, danger, danger!
                if not dry_run:
                    block_entity.nbt.value.pop('Book')

                out.append(entry)

    with open(output_path, 'w') as outfile:
        #json.dump(out, outfile, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))
        for i, entry in enumerate(out):
            x, y, z = entry['pos']
            book_name = entry['book_name']
            loot_table = entry['good_loot_tables'][0]

            print(f'#{i+1} - {book_name}', file=outfile)
            print(f'execute if entity @e[type=minecraft:armor_stand,distance=..10,tag=Lectern,x={x},y={y},z={z}] run loot give @s loot {loot_table}', file=outfile)
            print('', file=outfile)

    print(f"Wrote {len(out)} lecturn books to {output_path}")


if __name__ == '__main__':
    main()
