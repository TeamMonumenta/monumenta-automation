#!/usr/bin/env python3
"""Locks guild plots on the plots shard after they've been migrated"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from lib_py3.common import eprint
from lib_py3.timing import Timings
from minecraft.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt


UNNATURAL_CHARACTERS_RE = re.compile('[^a-zA-Z0-9]+')
LOWERCASE_NAME_PREFIXES = set()
for x in (
    # Tlaxan
    "C'",
    "R'",
    "Ta'",
    "T'",
    "Z'",

    # English articles
    "An ",
    "A ",
    "The ",

    # English honorifics (wikipedia: https://en.wikipedia.org/wiki/English_honorifics)
    # Common titles
    "Master ",
    "Mr ",
    "Mr. ",
    "Mister ", # For some reason not explicitly listed
    "Miss ",
    "Mrs ",
    "Mrs. ",
    "Ms ",
    "Ms. ",
    "Mx ",
    "Mx. ",

    # Formal titles
    "Sir ",
    "Gentleman ",
    "Sire ",
    "Mistress ",
    "Madam ",
    "Ma'am ",
    "Dame ",
    "Lord ",
    "Baron ",
    "Viscount ",
    "Count ",
    "Earl ",
    "Marquess ",
    "Lady ",
    "Baroness ",
    "Viscountess ",
    "Countess ",
    "Marchioness ",
    "Esq ",
    "Excellency ",
    "His Honor ",
    "His Honour ",
    "Her Honor ",
    "Her Honour ",
    "The Honorable ",
    "The Honourable ",
    "The Right Honorable ",
    "The Right Honourable ",
    "The Most Honorable ",
    "The Most Honourable ",

    # Academic and professional titles
    "Dr ",
    "Dr. ",
    "Doctor ",
    "Doc ",
    "PhD ",
    "Ph.D. ",
    "MD ",
    "M.D. ",
    "Professor ",
    "Prof ",
    "Cl ",
    "SCl ",
    "Chancellor ",
    "Vice-Chancellor ",
    "Principal ",
    "Vice-Principal ",
    "President ",
    "Vice-President ",
    # "Master ", already listed above
    "Warden ",
    "Dean ",
    "Regent ",
    "Rector ",
    "Provost ",
    "Director ",
    "Chief Executive ",

    # How are these not listed?
    "King ",
    "Queen ",
    "Duchess "
):
    LOWERCASE_NAME_PREFIXES.add(x.lower())
LOWERCASE_NAME_PREFIXES = sorted(LOWERCASE_NAME_PREFIXES)


# Copied from deprecated/plot_migrate_lock.py
def lock_things(world, min_x, min_y, min_z, max_x, max_y, max_z):
    for region in world.iter_regions(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z, read_only=False):
        for chunk in region.iter_chunks(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z, autosave=True):
            # Remove and lock all block entities
            for block_entity in chunk.iter_block_entities(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z):
                #if block_entity.nbt.has_path("Book"):
                    #block_entity.nbt.value.pop("Book")
                    #Can't remove books from lecterns in adventure, no need to nuke them
                if block_entity.nbt.has_path("Items"):
                    block_entity.nbt.value.pop("Items")
                if block_entity.nbt.has_path("RecordItem"):
                    block_entity.nbt.value.pop("RecordItem")
                block_entity.nbt.value["Lock"] = nbt.TagString("AdminEquipmentTool")
                if block_entity.id not in ["minecraft:lectern",]:
                    for item in block_entity.iter_items():
                        print(f"Item {block_entity.id} should not exist at {block_entity.pos}")

            # Remove all entities except item frames, armor stands, and villagers
            if chunk.nbt.has_path("Entities"):
                lst = []
                for entityNbt in chunk.nbt.at_path("Entities").value:
                    if not entityNbt.has_path("id"):
                        print(f"Got entity entry in {chunk.pos} that doesn't have an id: {entityNbt.to_mojangson()}")
                    else:
                        idt = entityNbt.at_path("id").value
                        if (
                                (idt in ("minecraft:item_frame", "minecraft:glow_item_frame") and entityNbt.has_path("Item.id") and "minecraft:air" not in entityNbt.at_path("Item.id").value)
                                or idt in ("minecraft:armor_stand", "minecraft:villager", "minecraft:painting")
                                or (entityNbt.has_path("CustomName") and len(entityNbt.at_path("CustomName").value) > 0)
                            ):
                            lst.append(entityNbt)

                chunk.nbt.at_path("Entities").value = lst

            # Remove all entities except item frames, armor stands, and villagers
            for entity in chunk.iter_entities(min_x=min_x, min_y=min_y, min_z=min_z, max_x=max_x, max_y=max_y, max_z=max_z):
                if entity.id in ("minecraft:item_frame", "minecraft:glow_item_frame"):
                    entity.nbt.value["Fixed"] = nbt.TagByte(1)
                    entity.nbt.value["Invulnerable"] = nbt.TagByte(1)
                elif "minecraft:armor_stand" in entity.id:
                    entity.nbt.value["NoGravity"] = nbt.TagByte(1)
                    entity.nbt.value["Invulnerable"] = nbt.TagByte(1)
                    entity.nbt.value["Marker"] = nbt.TagByte(1)
                    entity.nbt.value["DisabledSlots"] = nbt.TagInt(16777215)
                elif "minecraft:villager" in entity.id:
                    if entity.nbt.has_path("Offers"):
                        entity.nbt.value.pop("Offers")
                    if entity.nbt.has_path("Tags"):
                        entity.nbt.at_path("Tags").value.append(nbt.TagString("UNPUSHABLE"))
                    else:
                        entity.nbt.value["Tags"] = nbt.TagList([nbt.TagString("UNPUSHABLE"),])
                    entity.nbt.value["Invulnerable"] = nbt.TagByte(1)
                elif entity.nbt.has_path("CustomName") and len(entity.nbt.at_path("CustomName").value) > 0:
                    if entity.nbt.has_path("Tags"):
                        entity.nbt.at_path("Tags").value.append(nbt.TagString("UNPUSHABLE"))
                    else:
                        entity.nbt.value["Tags"] = nbt.TagList([nbt.TagString("UNPUSHABLE"),])
                    entity.nbt.value["NoAI"] = nbt.TagByte(1)
                    entity.nbt.value["Invulnerable"] = nbt.TagByte(1)
                elif entity.id == "minecraft:painting":
                    entity.nbt.value["Invulnerable"] = nbt.TagByte(1)
                else:
                    print(f"Found entity {entity.id} but should have already been removed at this point")
                    entity.nbt.tree()
                    raise Exception('This should never happen!')


def lock_guild(guild_name, guild_details, plots_world):
    prefix = f'  - [{guild_name!r}]'
    print(f'{prefix}: Start')
    mailbox_bb = guild_details['mailbox'][0]
    plot_bbs = guild_details['plot']
    island_bbs = guild_details['island']
    door_bb = guild_details['door']

    print(f'{prefix}: Locking main plot')
    for bb in plot_bbs:
        lock_things(
            plots_world,
            min_x=bb["min_x"], min_y=bb["min_y"], min_z=bb["min_z"],
            max_x=bb["max_x"], max_y=bb["max_y"], max_z=bb["max_z"]
        )

    print(f'{prefix}: Locking island (if it exists)')
    for bb in island_bbs:
        lock_things(
            plots_world,
            min_x=bb["min_x"], min_y=bb["min_y"], min_z=bb["min_z"],
            max_x=bb["max_x"], max_y=bb["max_y"], max_z=bb["max_z"]
        )

    print(f'{prefix}: Locking mail')
    bb = mailbox_bb
    lock_things(
        plots_world,
        min_x=bb["min_x"], min_y=bb["min_y"], min_z=bb["min_z"],
        max_x=bb["max_x"], max_y=bb["max_y"], max_z=bb["max_z"]
    )

    # If this doesn't work, just use FAWE's `//fill minecraft:sponge minecraft:yellow_stained_glass`
    print(f'{prefix}: Removing sponge')
    for bb in [plot_bbs[0],] + island_bbs:
        plots_world.fill_blocks(
            (bb["min_x"], 10, bb["min_z"]),
            (bb["max_x"] - 1, 10, bb["max_z"] - 1),
            {'name': 'minecraft:yellow_stained_glass'}
        )

    # If this doesn't work, just run over the pressure plates later
    print(f'{prefix}: Opening door')
    plots_world.fill_blocks(
        (door_bb["min_x"], door_bb["min_y"], door_bb["min_z"]),
        (door_bb["max_x"] - 1, door_bb["max_y"] - 1, door_bb["max_z"] - 1),
        {'name': 'minecraft:air'}
    )

    print(f'{prefix}: Done')


def get_longest_prefix(str_with_prefix):
    longest_prefix = ''

    for x in LOWERCASE_NAME_PREFIXES:
        if str_with_prefix.startswith(x) and len(x) > len(longest_prefix):
            longest_prefix = x

    return longest_prefix


def sort_key(dict_entry):
    key = dict_entry[0]
    sort_prefix = key.lower()
    prefixes = []
    while True:
        prefix = get_longest_prefix(sort_prefix)
        if not prefix:
            break
        prefixes.append(prefix)
        sort_prefix = sort_prefix[len(prefix):]
    string_builder = sort_prefix
    for prefix in prefixes:
        string_builder += prefix
    natural_same_case = UNNATURAL_CHARACTERS_RE.sub('', string_builder)
    return f'{natural_same_case} {key}'


def main():
    # Parse arguments
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('host_path', type=Path, help='The path to the host server containing both plots and playerplots')
    args = arg_parser.parse_args()

    host_path = args.host_path


    # Set up shortcuts for various frequently used path variables
    plots_shard_path = host_path / 'plots'
    guild_plots_json_file = plots_shard_path / 'plugins/Monumenta/plots_guild_bounds.json'
    plots_world_path = plots_shard_path / 'Project_Epic-plots'


    # Check if all files are available
    if not guild_plots_json_file.is_file():
        eprint(f'Could not find required file {guild_plots_json_file!r}')
        sys.exit()
    if not (plots_world_path / 'level.dat').is_file():
        eprint(f'Could not find required world {plots_world_path!r}')
        sys.exit()


    # Load list of guild plot bounds/coordinates
    guild_plots_json = {}
    with open(guild_plots_json_file, 'r', encoding='utf-8') as fp:
        guild_plots_json = json.load(fp)


    # Locking the plots
    timings = Timings(enabled=True)
    plots_world = World(plots_world_path)


    timings.nextStep("Locking guild plots")
    i = 0
    num_guilds = len(guild_plots_json)
    for guild_name, guild_details in sorted(guild_plots_json.items(), key=sort_key):
        i += 1
        lock_guild(f'[{i}/{num_guilds}] {guild_name}', guild_details, plots_world)

    timings.nextStep("Locked guild plots")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
