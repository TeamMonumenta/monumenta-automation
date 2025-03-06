#!/usr/bin/env python3
"""Migrates guild plots from the plots shard to guildplots

Before using, make sure to:
- Run weekly update, creating the guildplots shard folder and its starting contents
- Generate plots_guild_bounds.json in-game from the plots shard
- Stop both plots and guildplots - or for best results, all shards
"""

import argparse
import json
import multiprocessing
import os
import sys
from pathlib import Path

from lib_py3.common import eprint
from lib_py3.timing import Timings
from minecraft.region import Region
from minecraft.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt


GUILDPLOTS_ORIGIN_BY_FACING = {
      0: [ -33, 47,  139],
     90: [-125, 47,   56],
    180: [  23, 47, -105],
    270: [ 132, 47,   -2],
}


MAILBOX_START_BY_FACING = {
      0: [ -37, 47,  138],
     90: [-124, 47,   52],
    180: [  27, 47, -104],
    270: [ 131, 47,    2],
}


TEMPLATE_BARREL_NBT = nbt.TagCompound.from_mojangson(r'''{id:"minecraft:barrel",keepPacked:1b,CustomName:'{"text":"Mailbox","color":"gray","italic":false}',Items:[]}''')


def migrate_mailbox_contents(prefix, plots_world, facing, src_bb, guild_plot_world):
    # Get mail containers
    mailbox_containers = []
    for region in plots_world.iter_regions(
            min_x=src_bb['min_x'], min_y=src_bb['min_y'], min_z=src_bb['min_z'],
            max_x=src_bb['max_x'], max_y=src_bb['max_y'], max_z=src_bb['max_z'],
            read_only=True, region_types=(Region,)
    ):
        for chunk in region.iter_chunks(
                min_x=src_bb['min_x'], min_y=src_bb['min_y'], min_z=src_bb['min_z'],
                max_x=src_bb['max_x'], max_y=src_bb['max_y'], max_z=src_bb['max_z'],
                autosave=False, on_exception=None
        ):
            for block_entity in chunk.iter_block_entities(
                    min_x=src_bb['min_x'], min_y=src_bb['min_y'], min_z=src_bb['min_z'],
                    max_x=src_bb['max_x'], max_y=src_bb['max_y'], max_z=src_bb['max_z']
            ):
                if not block_entity.nbt.has_path('Items[0]'):
                    continue
                mailbox_containers.append(block_entity.nbt.at_path('Items').value)

    # Set mail containers
    pos = list(MAILBOX_START_BY_FACING[facing])
    rx = pos[0] // 512
    rz = pos[2] // 512
    region = guild_plot_world.get_region(rx, rz, read_only=False, region_type=Region)
    chunk = region.load_chunk(pos[0] // 16, pos[2] // 16)

    for mailbox_container in mailbox_containers:
        chunk.set_block(pos, {'name': 'minecraft:barrel', 'facing': 'up', 'open': 'false'})

        barrel_nbt = TEMPLATE_BARREL_NBT.deep_copy()
        barrel_nbt.value['x'] = nbt.TagInt(pos[0])
        barrel_nbt.value['y'] = nbt.TagInt(pos[1])
        barrel_nbt.value['z'] = nbt.TagInt(pos[2])
        barrel_nbt.value['Items'].value = mailbox_container

        # In case set_block removes this tag on the first pass
        if not chunk.nbt.has_path('block_entities'):
            chunk.nbt.value['block_entities'] = nbt.TagList([])
        chunk.nbt.at_path('block_entities').value.append(barrel_nbt)

        # Increment Y position
        pos[1] += 1

    region.save_chunk(chunk)
    print(f'{prefix}: Migrated mail: {len(mailbox_containers)}')


def migrate_guild_with_packed_args(args):
    return migrate_guild(*args)


def migrate_guild(guild_name, guild_details, plots_world, guildplots_shard_path, guildplots_template_world):
    prefix = f'  - [{guild_name!r}]'
    print(f'{prefix}: Start')
    plot_number = guild_details['plot_number']
    facing = guild_details['facing']
    old_origin = guild_details['origin']
    mailbox_bb = guild_details['mailbox'][0]
    plot_bbs = guild_details['plot']
    island_bbs = guild_details['island']

    guild_plot_world_path = guildplots_shard_path / f'guildplot{plot_number}'
    new_origin = list(GUILDPLOTS_ORIGIN_BY_FACING[facing])
    delta_pos = [new_origin[i] - old_origin[i] for i in range(3)]
    delta_bb = delta_pos + delta_pos

    print(f'{prefix}: Copying blank template')
    guildplots_template_world.copy_to(guild_plot_world_path, regenerate_uuids=True, clear_world_uuid=True, clear_score_data=True)
    guild_plot_world = World(guild_plot_world_path)

    # This is going in the plugin code instead probably
    '''
    print(f'{prefix}: Copying main plot')
    for bb in plot_bbs:
        src = [
            bb["min_x"], bb["min_y"], bb["min_z"],
            bb["max_x"], bb["max_y"], bb["max_z"],
        ]

        dst = [src[i] + delta_bb[i] for i in range(6)]

        guild_plot_world.copy_from_bounding_box(
            plots_world,
            min_x=dst[0], min_y=dst[1], min_z=dst[2],
            max_x=dst[3], max_y=dst[4], max_z=dst[5],
            src_x=src[0], src_y=src[1], src_z=src[2],
            regenerate_uuids=False, clear_world_uuid=True, clear_score_data=False
        )

    print(f'{prefix}: Copying island (if it exists)')
    for bb in island_bbs:
        guild_plot_world.copy_from_bounding_box(
            plots_world,
            min_x=-87, min_y=13, min_z=-87,
            max_x=86, max_y=151, max_z=86,
            src_x=bb["min_x"], src_y=bb["min_y"], src_z=bb["min_z"],
            regenerate_uuids=False, clear_world_uuid=True, clear_score_data=False
        )
    '''

    print(f'{prefix}: Copying mail')
    migrate_mailbox_contents(prefix, plots_world, facing, mailbox_bb, guild_plot_world)

    print(f'{prefix}: Done')
    return guild_name


def iter_migrate_args(guild_plots_json, plots_world, guildplots_shard_path, guildplots_template_world):
    for guild_name, guild_details in guild_plots_json.items():
        yield (guild_name, guild_details, plots_world, guildplots_shard_path, guildplots_template_world)


def main():
    # Parse arguments
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('host_path', type=Path, help='The path to the host server containing both plots and playerplots')
    arg_parser.add_argument('-j', '--num-threads', type=int, default=8)
    args = arg_parser.parse_args()

    host_path = args.host_path
    num_threads = args.num_threads


    # Set up shortcuts for various frequently used path variables
    plots_shard_path = host_path / 'plots'
    guild_plots_json_file = plots_shard_path / 'plugins/Monumenta/plots_guild_bounds.json'
    plots_world_path = plots_shard_path / 'Project_Epic-plots'

    guildplots_shard_path = host_path / 'guildplots'
    guildplots_template_world_path = guildplots_shard_path / 'guildplots_template'


    # Check if all files are available
    if not guild_plots_json_file.is_file():
        eprint(f'Could not find required file {guild_plots_json_file!r}')
        sys.exit()
    for required_world in (
            plots_world_path,
            guildplots_template_world_path,
    ):
        if not (required_world / 'level.dat').is_file():
            eprint(f'Could not find required world {required_world!r}')
            sys.exit()


    # Load list of guild plot bounds/coordinates
    guild_plots_json = {}
    with open(guild_plots_json_file, 'r', encoding='utf-8') as fp:
        guild_plots_json = json.load(fp)


    # Migrate the plots
    timings = Timings(enabled=True)
    plots_world = World(plots_world_path)
    guildplots_template_world = World(guildplots_template_world_path)


    timings.nextStep("Migrating mailboxes")
    with multiprocessing.Pool(processes=num_threads) as pool:
        for guild_name in pool.map(
                migrate_guild_with_packed_args,
                iter_migrate_args(
                    guild_plots_json,
                    plots_world,
                    guildplots_shard_path,
                    guildplots_template_world
                )
        ):
            pass
    timings.nextStep("Migrated mailboxes")


if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")
    try:
        main()
    except KeyboardInterrupt:
        pass
