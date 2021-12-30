#!/usr/bin/env pypy3

import os
import sys
import multiprocessing
import concurrent
from pprint import pprint, pformat
from minecraft.world import World
from minecraft.region import Region, EntitiesRegion

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types.chunk import BlockArray
from lib_py3.block_map import block_map

fast_mode = True

# Prune this world of region files that contain no Entities, Tile Entities, or non-air blocks
def process_region(arg):
    full_path, rx, rz, region_type = arg
    region = region_type(full_path, rx, rz, read_only=True)

    num_entities = 0
    num_block_entities = 0
    has_blocks={}

    for chunk in region.iter_chunks():
        if len(has_blocks) > 10 or (fast_mode and (num_entities > 0 or num_block_entities > 0 or len(has_blocks) > 0)):
            break

        if type(region) is EntitiesRegion:
            # Check if there are entities (fast check)
            num_entities += chunk.nbt.count_multipath('Entities[]')
        elif type(region) is Region:
            # Check if there are entities (fast check)
            num_entities += chunk.nbt.count_multipath('Entities[]')

            # Check if there are tile entities (fast check)
            num_block_entities += chunk.nbt.count_multipath('Level.TileEntities[]')

            # Check if there are block entities (fast check)
            num_block_entities += chunk.nbt.count_multipath('Level.BlockEntities[]')

            # Check for non-air blocks
            # This is an expensive check, keep it low priority
            for section in chunk.nbt.at_path('Level.Sections').value:
                try:
                    blocks = BlockArray.from_nbt(section, block_map)
                    for block in blocks:
                        name = block['name']
                        if name not in ("minecraft:air", "minecraft:bedrock", "minecraft:black_concrete", "minecraft:black_concrete_powder"):
                            #print(chunk.cx * 16, "~", chunk.cz * 16, name)
                            has_blocks[name] = has_blocks.get(name, 0) + 1
                            if fast_mode:
                                break
                except IndexError:
                    print("Warning: unable to iterate blocks. Assuming there are some blocks")
                    has_blocks = True
                    break

                if fast_mode and len(has_blocks) > 0:
                    break

    if num_entities > 0 or num_block_entities > 0 or len(has_blocks) > 0:
        if not fast_mode:
            if len(has_blocks) > 5:
                blockstr = "(more than 5 kinds)"
            else:
                blockstr = pformat(has_blocks)
            print(f"{region} is valid: entities={num_entities}  block entities={num_block_entities}  has_blocks={blockstr}")
        else:
            print(f"{region} is valid")
        return True
    else:
        os.remove(region.path)
        print(f"{region} is completely empty; deleted")
        return False

if __name__ == '__main__':
    multiprocessing.set_start_method("fork")

    args = sys.argv
    name = args.pop(0)
    if len(sys.argv) == 0:
        print("Usage: {} [--details] /path/to/world1 [/path/to/world2 ...]".format(name))
        sys.exit()

    if args[0] == "--details":
        print("Detail mode enabled, will report details on each kept region\n")
        args.pop(0)
        fast_mode = False

    if len(sys.argv) == 0:
        print("Usage: {} [--details] /path/to/world1 [/path/to/world2 ...]".format(name))
        sys.exit()

    regions = []

    print(f"Pruning empty regions from:")
    for world_path in args:
        print(f"  {world_path}")
    for world_path in args:
        world = World(world_path)
        for full_path, rx, rz, region_type in world.enumerate_regions():
            regions.append((full_path, rx, rz, region_type))

    with concurrent.futures.ProcessPoolExecutor(max_workers=6) as pool:
        results = pool.map(process_region, regions)

    deleted = 0
    total = 0
    for region_result in results:
        total += 1
        if not region_result:
            deleted += 1

    print(f"Deleted {deleted} empty region files of {total} total regions")

