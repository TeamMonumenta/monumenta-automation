#!/usr/bin/env pypy3

import os
import sys
import multiprocessing
from pprint import pprint, pformat
from minecraft.world import World
from minecraft.region import Region, EntitiesRegion

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types.chunk import BlockArray
from lib_py3.block_map import block_map

# Prune this world of region files that contain no Entities, Tile Entities, or non-air blocks
def process_region(arg):
    region, _ = arg
    num_entities = 0
    num_block_entities = 0
    has_blocks={}

    for chunk in region.iter_chunks():
        if len(has_blocks) > 10:
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
                except IndexError:
                    print("Warning: unable to iterate blocks. Assuming there are some blocks")
                    has_blocks = True
                    break

    if num_entities > 0 or num_block_entities > 0 or len(has_blocks) > 0:
        if len(has_blocks) > 5:
            blockstr = "(more than 5 kinds)"
        else:
            blockstr = pformat(has_blocks)
        print(f"region({region.rx}, {region.rz}) is valid: entities={num_entities}  block entities={num_block_entities}  has_blocks={blockstr}")
        return True
    else:
        os.remove(region.path)
        print(f"region({region.rx}, {region.rz}) is completely empty; deleted")
        return False

if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")

    args = sys.argv
    name = args.pop(0)
    if len(sys.argv) == 0:
        print("Usage: {} /path/to/world1 [/path/to/world2 ...]".format(name))
        sys.exit()

    for worldPath in args:
        print("\n\nPruning empty regions from {}...".format(worldPath))

        world = World(worldPath)

        print("Deleting completely empty region files:")

        results = world.iter_regions_parallel(process_region, num_processes=6, region_types=(Region, EntitiesRegion)) # TODO: PoiRegion ignored for now
        deleted = 0
        for region_result in results:
            if not region_result:
                deleted += 1

        print(f"Deleted {deleted} empty region files of {len(results)} total regions")

