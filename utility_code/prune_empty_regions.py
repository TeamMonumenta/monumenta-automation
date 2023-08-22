#!/usr/bin/env pypy3

import os
import sys
import multiprocessing
import concurrent
from minecraft.world import World
from minecraft.region import Region, EntitiesRegion

fast_mode = True

# Prune this world of region files that contain no Entities, Tile Entities, or non-air blocks
def process_region(arg):
    full_path, rx, rz, region_type = arg
    region = region_type(full_path, rx, rz, read_only=True)

    num_entities = 0
    num_block_entities = 0
    has_blocks = set()

    for chunk in region.iter_chunks():
        if len(has_blocks) > 10 or (fast_mode and (num_entities > 0 or num_block_entities > 0 or len(has_blocks) > 0)):
            break

        if isinstance(region, EntitiesRegion):
            # Check if there are entities (fast check)
            num_entities += chunk.nbt.count_multipath('Entities[]')
        elif isinstance(region, Region):
            # Check if there are entities (fast check)
            num_entities += chunk.nbt.count_multipath('Level.Entities[]')

            # Check if there are tile entities (fast check)
            num_block_entities += chunk.nbt.count_multipath('Level.TileEntities[]') # 1.17 and before
            num_block_entities += chunk.nbt.count_multipath('block_entities[]')

            # Check for non-air blocks
            # This is an expensive check, keep it low priority
            for section in chunk.sections:
                try:
                    # This section has no palette - it's using the global one
                    # NOTE: This is complicated to deal with. Odds are, it's using the global one just for air - and it's probably empty
                    # However, it might also be that this chunk section has tons of different types of blocks, so it's using the global palette because it's needed to capture that much data
                    # Here we gamble that it's not important - if there actually is data here, other nearby chunk sections will also have data and prevent the region from being deleted
                    if not section.has_path("block_states.palette"):
                        # Uncommenting the below line will cause chunk sections like this to keep the entire region, even though they might be empty
                        # TODO: Would be great to have an efficient method to test if this section is really junk or not...
                        #has_blocks.add("GLOBAL_PALETTE")
                        continue

                    for palette_entry in section.at_path("block_states.palette").value:
                        name = palette_entry.at_path("Name").value
                        if name not in ("minecraft:air", ):
                            #print(chunk.cx * 16, "~", chunk.cz * 16, name, flush=True)
                            has_blocks.add(name.replace("minecraft:", ""))
                            if fast_mode:
                                break
                except Exception:
                    print("Warning: unable to iterate blocks. Assuming there are some blocks", flush=True)
                    has_blocks.add("?????")
                    break

                if fast_mode and len(has_blocks) > 0:
                    break

    if num_entities > 0 or num_block_entities > 0 or len(has_blocks) > 0:
        if not fast_mode:
            print(f"{region} is valid: entities={num_entities}  block entities={num_block_entities}  has_blocks=[{','.join(has_blocks)}]", flush=True)
        else:
            print(f"{region} is valid", flush=True)
        return True

    os.remove(region.path)
    print(f"{region} is completely empty; deleted", flush=True)
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

    all_world_paths = []
    for arg_path in args:
        for world_path in World.enumerate_worlds(arg_path):
            all_world_paths.append(world_path)

    if len(all_world_paths) <= 0:
        sys.exit("No valid worlds found to prune")

    print(f"Pruning empty regions from:")
    for world_path in all_world_paths:
        print(f"  {world_path}")

    for world_path in all_world_paths:
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
