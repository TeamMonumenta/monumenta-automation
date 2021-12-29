#!/usr/bin/env pypy3

import os
import sys
import getopt

from lib_py3.block_map import block_map
from lib_py3.common import eprint, bounded_range

from minecraft.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types.chunk import BlockArray

def usage():
    print("This script removes all blocks above non-glowstone at y=0 except for sea lanterns, glass, and coal blocks")
    sys.exit("Usage: {} --world /path/to/world --pos1 x,y,z --pos2 x,y,z".format(sys.argv[0]))

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "w:", ["world=", "pos1=", "pos2="])

    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    world_path = None
    pos1 = None
    pos2 = None

    for o, a in opts:
        if o in ("-w", "--world"):
            world_path = a
        elif o in ("--pos1"):
            try:
                split = a.split(",")
                pos1 = (int(split[0]), int(split[1]), int(split[2]))
            except:
                eprint("Invalid --pos1 argument")
                usage()
        elif o in ("--pos2"):
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
    elif (pos1 is None) or (pos2 is None):
        eprint("--pos1 and --pos2 must be specified")
        usage()

    world = World(world_path)

    min_x = min(pos1[0], pos2[0])
    min_y = min(pos1[1], pos2[1])
    min_z = min(pos1[2], pos2[2])
    max_x = max(pos1[0], pos2[0])
    max_y = max(pos1[1], pos2[1])
    max_z = max(pos1[2], pos2[2])

    if min_y > 0:
        eprint("Minimum y coordinate must be 0")
        usage()

    blocks_removed = 0
    entities_removed = 0
    tile_entities_removed = 0
    for rz in range(min_z//512, (max_z - 1)//512 + 1):
        for rx in range(min_x//512, (max_x - 1)//512 + 1):
            region = world.get_region(rx, rz)
            for cz in range(min(max(min_z//16, rz*32), (rz + 1)*32 - 1), min(max(max_z//16, rz*32), (rz + 1)*32 - 1) + 1):
                for cx in range(min(max(min_x//16, rx*32), (rx + 1)*32 - 1), min(max(max_x//16, rx*32), (rx + 1)*32 - 1) + 1):
                    chunk = region.load_chunk(cx, cz)

                    # Figure out which x/z columns need to be pruned
                    columns_to_prune = set()
                    for section in chunk.nbt.iter_multipath('Level.Sections[]'):
                        cy = section.at_path("Y").value
                        if cy == 0:
                            blocks = BlockArray.from_nbt(section, block_map)
                            by = 0
                            for bz in bounded_range(min_z, max_z, cz, 16):
                                for bx in bounded_range(min_x, max_x, cx, 16):
                                    if blocks[256 * by + 16 * bz + bx]["name"] != "minecraft:glowstone":
                                        columns_to_prune.add(f"{bx}-{bz}")

                    # Prune them
                    for section in chunk.nbt.iter_multipath('Level.Sections[]'):
                        cy = section.at_path("Y").value
                        blocks = BlockArray.from_nbt(section, block_map)
                        for by in bounded_range(min_y, max_y, cy, 16):
                            for bz in bounded_range(min_z, max_z, cz, 16):
                                for bx in bounded_range(min_x, max_x, cx, 16):
                                    if f"{bx}-{bz}" in columns_to_prune:
                                        name = blocks[256 * by + 16 * bz + bx]["name"]
                                        if name != "minecraft:air" and (by + cy*16 > 2 or name not in ["minecraft:light_gray_stained_glass", "minecraft:coal_block", "minecraft:sea_lantern"]):
                                            blocks[256 * by + 16 * bz + bx] = {'name': 'minecraft:air'}
                                            blocks_removed += 1

                    # Remove tile entities
                    if chunk.nbt.has_path("Level.TileEntities"):
                        new_tile_entities = []
                        for block_entity in chunk.nbt.iter_multipath('Level.TileEntities[]'):
                            x = block_entity.at_path("x").value - (cx * 16)
                            z = block_entity.at_path("z").value - (cz * 16)
                            if f"{x}-{z}" in columns_to_prune:
                                tile_entities_removed += 1
                            else:
                                new_tile_entities.append(block_entity)

                        chunk.nbt.at_path("Level.TileEntities").value = new_tile_entities

                    # Remove regular entities
                    if chunk.nbt.has_path("Level.Entities"):
                        new_entities = []
                        for entity in chunk.nbt.iter_multipath('Level.Entities[]'):
                            x = int(entity.at_path("Pos").value[0].value) - (cx * 16)
                            z = int(entity.at_path("Pos").value[2].value) - (cz * 16)
                            if f"{x}-{z}" in columns_to_prune:
                                entities_removed += 1
                            else:
                                new_entities.append(entity)

                        chunk.nbt.at_path("Level.Entities").value = new_entities
                    region.save_chunk(chunk)

    print(f"{blocks_removed} blocks removed, {entities_removed} entities removed, {tile_entities_removed} tile entities removed")

