#!/usr/bin/env python3

import json
import os
import re
import sys

from pathlib import Path

from lib_py3.block_map import block_map
from lib_py3.common import bounded_range, get_item_name_from_nbt
from lib_py3.loot_table_manager import LootTableManager
from minecraft.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt
from quarry.types.chunk import BlockArray


RE_NOT_RCI_SAFE = re.compile('[^0-9a-z_-]+')
RELEASE_STATUSES = (
    "public",
    "mod",
    "unreleased",
)

# if enabled, prints all the places that the debug item has been found at
# (checks if the item name contains the substring DEBUG_ITEM_CONTAINS)
# this includes the blocks that the item is above, and the world it was found at
DEBUG = False
DEBUG_ITEM_CONTAINS = "Morphic Breaker"

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
                                if item.tag.has_path('Monumenta.Masterwork'):
                                    masterwork = item.tag.at_path('Monumenta.Masterwork').value
                                    item_name += f'_m{masterwork}'

                                item_data = items.get(item_name, {})

                                above_blocks = item_data.get("above_blocks", set())
                                above_blocks.add(column_y0_type[f"{int(item.pos[0])}-{int(item.pos[2])}"])
                                item_data["above_blocks"] = above_blocks

                                # Debug to easily find midplaced copies of certain items
                                if DEBUG and DEBUG_ITEM_CONTAINS in item_name:
                                    print(f'Found {item_name} at: {int(item.pos[0])}, {int(item.pos[1])}, {int(item.pos[2])}')
                                    print(f'It is above: {above_blocks}, in world {world.path}')

                                types = item_data.get("types", set())
                                types.add(item.id)
                                item_data["types"] = types

                                items[item_name] = item_data


def get_tag_safe_rci(text):
    return RE_NOT_RCI_SAFE.sub('', text.lower().replace(' ', '_'))


def get_refined_creative_tab_flags(item_tag):
    result = ['monumenta']

    if item_tag.has_path('Monumenta'):
        monumenta_tag = item_tag.at_path('Monumenta')

        if monumenta_tag.has_path('Region'):
            region = monumenta_tag.at_path('Region').value
            region = get_tag_safe_rci(region)
            result.append(f"region_{region}")

        if monumenta_tag.has_path('Tier'):
            tier = monumenta_tag.at_path('Tier').value
            tier = get_tag_safe_rci(tier)
            result.append(f"tier_{tier}")

        if monumenta_tag.has_path('Location'):
            location = monumenta_tag.at_path('Location').value
            location = get_tag_safe_rci(location)
            result.append(f"location_{location}")

        if monumenta_tag.has_path('Stock'):
            stock_tag = monumenta_tag.at_path('Stock')

            if stock_tag.has_path('Attributes'):
                for attribute in stock_tag.at_path('Attributes').value:
                    attribute_name = attribute.at_path('AttributeName').value
                    attribute_name = get_tag_safe_rci(attribute_name)
                    result.append(f"attr_{attribute_name}")

            if stock_tag.has_path('Enchantments'):
                for enchantment_name in stock_tag.at_path('Enchantments').value.keys():
                    enchantment_name = get_tag_safe_rci(enchantment_name)
                    result.append(f"ench_{enchantment_name}")

            if stock_tag.has_path('Effects[0].EffectType'):
                for effect_type_tag in stock_tag.iter_multipath('Effects[].EffectType'):
                    effect_type = get_tag_safe_rci(effect_type_tag.value)
                    result.append(f"effect_{effect_type}")

    return result


out_name = sys.argv[1]
refined_creative_inventory_folder = sys.argv[2]
release_status_filter = lambda status: True
if len(sys.argv) == 4:
    release_status_filter_regex = re.compile(sys.argv[3])
    release_status_filter = lambda status: bool(release_status_filter_regex.search(status))

print(f"Will output the following types of items to {out_name}")
print("public    :", release_status_filter("public"))
print("mod       :", release_status_filter("mod"))
print("unreleased:", release_status_filter("unreleased"))


out_map = {}

mgr = LootTableManager()
mgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")

for item_type in mgr.item_map:
    next_map = mgr.item_map[item_type]
    items = {}
    for item_name in next_map:
        item = next_map[item_name]
        locs = []
        nbt_ = None
        if isinstance(item, list):
            for elem in item:
                if not elem.get("generated", False):
                    locs.append(elem["file"].replace("/home/epic/project_epic/server_config/", ""))
                    nbt_ = elem["nbt"]
        else:
            if not item.get("generated", False):
                locs.append(item["file"].replace("/home/epic/project_epic/server_config/", ""))
                nbt_ = item["nbt"]

        if nbt_ is not None:
            items[item_name] = {"files": locs, "nbt": nbt_.to_mojangson(), "nbt_as_json": nbt_.to_json(), "release_status": "unreleased"}
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
load_world_warp_items(items_at_warp_items, World('/home/epic/project_epic/ring/Project_Epic-ring'), min_x, min_y, min_z, max_x, max_y, max_z)

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
            if DEBUG and DEBUG_ITEM_CONTAINS in item_name:
                print(f'Finally, {item_name} has been declared {out_dict["release_status"]}')

# Filter the actual json output map that gets written based on the release status filter specified on the command line
json_out_map = {}
for item_type, out_types in sorted(out_map.items()):
    item_type_out = {}
    for item_name, item_entry in sorted(out_types.items()):
        if release_status_filter(item_entry["release_status"]):
            # Filter matches, add to json_out_map
            item_type_out[item_name] = item_entry
    if len(item_type_out) > 0:
        json_out_map[item_type] = item_type_out


with open(out_name, 'w') as outfile:
    json.dump(json_out_map, outfile, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

# If exporting refined creative inventory files is desired, do so
if refined_creative_inventory_folder:
    rci_item_releases = {}
    for status in RELEASE_STATUSES[1:]:
        rci_item_releases[status] = []

    for item_id in out_map:
        for item_name in out_map[item_id]:
            compendium_details = out_map[item_id][item_name]

            release_status = compendium_details["release_status"]
            if release_status not in RELEASE_STATUSES:
                continue

            mojangson = compendium_details["nbt"]
            item_tag = nbt.TagCompound.from_mojangson(mojangson)
            item_stack = nbt.TagCompound({
                "Count": nbt.TagByte(1),
                "id": nbt.TagString(item_id),
                "tag": item_tag,
            })

            rci_flags = get_refined_creative_tab_flags(item_tag)
            rci_flags.append(f'published_{get_tag_safe_rci(release_status)}')

            rci_entry = {
                "nbt": item_stack.to_mojangson(),
                "custom": True,
                "flags": rci_flags
            }

            publish_status_found = False
            for status in RELEASE_STATUSES:
                if status == release_status:
                    publish_status_found = True
                if status == 'public' or not publish_status_found:
                    continue
                rci_item_releases[status].append(rci_entry)

    rci_root_path = Path(refined_creative_inventory_folder)
    for release, entries in rci_item_releases.items():
        release_dir = rci_root_path / release
        release_dir.mkdir(mode=0o755, parents=True, exist_ok=True)
        items_json = release_dir / 'items.json'
        with items_json.open('w') as fp:
            json.dump({"items": entries}, fp, ensure_ascii=True, sort_keys=False, indent=2, separators=(',', ': '))
