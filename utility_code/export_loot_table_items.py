#!/usr/bin/env python3

import os
import sys
import json

from lib_py3.block_map import block_map
from lib_py3.common import bounded_range, get_item_name_from_nbt
from lib_py3.loot_table_manager import LootTableManager
from minecraft.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types.chunk import BlockArray

def load_world_warp_items(items, world, min_x, min_y, min_z, max_x, max_y, max_z):
    for rz in range(min_z//512, (max_z - 1)//512 + 1):
        for rx in range(min_x//512, (max_x - 1)//512 + 1):
            region = world.get_region(rx, rz)
            for cz in range(min(max(min_z//16, rz*32), (rz + 1)*32 - 1), min(max(max_z//16, rz*32), (rz + 1)*32 - 1) + 1):
                for cx in range(min(max(min_x//16, rx*32), (rx + 1)*32 - 1), min(max(max_x//16, rx*32), (rx + 1)*32 - 1) + 1):
                    chunk = region.load_chunk(cx, cz)

                    # Get all the block types at y=0
                    column_y0_type = {}
                    for section in chunk.sections:
                        cy = section.at_path("Y").value
                        if cy == 0:
                            blocks = BlockArray.from_nbt(section, block_map)
                            by = 0
                            for bz in bounded_range(min_z, max_z, cz, 16):
                                for bx in bounded_range(min_x, max_x, cx, 16):
                                    column_y0_type[f"{cx*16 + bx}-{cz*16 + bz}"] = blocks[256 * by + 16 * bz + bx]["name"]

                    # Get all the items in this chunk and label them with what block they are above
                    for item in chunk.recursive_iter_items(min_x, min_y, min_z, max_x, max_y, max_z):
                        if item.tag is not None:
                            item_name = get_item_name_from_nbt(item.tag, remove_color=True)
                            if item_name is not None:
                                item_data = items.get(item_name, {})

                                above_blocks = item_data.get("above_blocks", set())
                                above_blocks.add(column_y0_type[f"{int(item.pos[0])}-{int(item.pos[2])}"])
                                item_data["above_blocks"] = above_blocks

                                types = item_data.get("types", set())
                                types.add(item.id)
                                item_data["types"] = types

                                items[item_name] = item_data


out_name = sys.argv[1]
out_map = {}

mgr = LootTableManager()
mgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")

for item_type in mgr.item_map:
    next_map = mgr.item_map[item_type]
    items = {}
    for item_name in next_map:
        item = next_map[item_name]
        locs = []
        nbt = None
        if isinstance(item, list):
            for elem in item:
                if not elem.get("generated", False):
                    locs.append(elem["file"].replace("/home/epic/project_epic/server_config/", ""))
                    nbt = elem["nbt"]
        else:
            if not item.get("generated", False):
                locs.append(item["file"].replace("/home/epic/project_epic/server_config/", ""))
                nbt = item["nbt"]

        if nbt is not None:
            items[item_name] = {"files": locs, "nbt": nbt.to_mojangson(), "release_status": "unreleased"}
    if len(items) > 0:
        out_map[item_type] = items


# Both R1 and R2 /warp items are at these same locations
min_x = 1140
min_y = 0
min_z = 2564
max_x = 1275
max_y = 123
max_z = 2811

# Scan through warp items for R1 and R2 and make note of what block each item is above
items_at_warp_items = {}
load_world_warp_items(items_at_warp_items, World('/home/epic/project_epic/valley/Project_Epic-valley'), min_x, min_y, min_z, max_x, max_y, max_z)
load_world_warp_items(items_at_warp_items, World('/home/epic/project_epic/isles/Project_Epic-isles'), min_x, min_y, min_z, max_x, max_y, max_z)

# Merge this into the out_map, marking things as public if above glowstone or mod if above lapis
for item_name in items_at_warp_items:
    item = items_at_warp_items[item_name]
    for item_type in item["types"]:
        if item_type in out_map and item_name in out_map[item_type]:
            out_dict = out_map[item_type][item_name]

            above_blocks = item["above_blocks"]
            if "minecraft:glowstone" in above_blocks:
                out_dict["release_status"] = "public"
            elif "minecraft:lapis_block" in above_blocks:
                out_dict["release_status"] = "mod"

with open(out_name, 'w') as outfile:
    json.dump(out_map, outfile, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))
