#!/usr/bin/python3

import os
import sys
from pprint import pprint
from minecraft.world import World
from minecraft.region import Region, EntitiesRegion

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types.chunk import BlockArray
from lib_py3.block_map import block_map

# Prune this world of region files that contain no Entities, Tile Entities, or non-air blocks
def process_region(region):
    confirmed_valid = False

    for chunk in region.iter_chunks():
        if confirmed_valid:
            break

        if type(region) is EntitiesRegion:
            # Check if there are entities (fast check)
            if chunk.nbt.count_multipath('Entities[]') > 0:
                confirmed_valid = True
                break
        elif type(region) is Region:
            # Check if there are entities (fast check)
            if chunk.nbt.count_multipath('Level.Entities[]') > 0:
                confirmed_valid = True
                break

            # Check if there are tile entities (fast check)
            if chunk.nbt.count_multipath('Level.TileEntities[]') > 0:
                confirmed_valid = True
                break

            # Check if there are block entities (fast check)
            if chunk.nbt.count_multipath('Level.BlockEntities[]') > 0:
                confirmed_valid = True
                break

            # Check for non-air blocks
            # This is an expensive check, keep it low priority
            for section in chunk.nbt.at_path('Level.Sections').value:
                try:
                    blocks = BlockArray.from_nbt(section, block_map)
                    for block in blocks:
                        if block['name'] != "minecraft:air":
                            confirmed_valid = True
                            break
                except IndexError:
                    print("Warning: unable to iterate blocks. Assuming region is valid")
                    confirmed_valid = True
                    break

    if not confirmed_valid:
        os.remove(region.path)
        print(f"region({region.rx}, {region.rz}) is completely empty; deleted")

    return confirmed_valid

args = sys.argv
name = args.pop(0)
if len(sys.argv) == 0:
    print("Usage: {} /path/to/world1 [/path/to/world2 ...]".format(name))
    sys.exit()


while len(args) >= 1:
    worldPath = args.pop(0)
    print("\n\nPruning empty regions from {}...".format(worldPath))

    world = World(worldPath)

    print("Deleting completely empty region files:")

    results = world.iter_regions_parallel(process_region, num_processes=4, region_types=(Region, EntitiesRegion)) # TODO: PoiRegion ignored for now
    deleted = 0
    for region_result in results:
        if not region_result:
            deleted += 1

    print(f"Deleted {deleted} empty region files of {len(results)} total regions")

