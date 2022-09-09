#!/usr/bin/env pypy3
"""Removes the scores of entities no longer in the worlds of a given shard."""

import argparse
import concurrent
import multiprocessing
import os
import sys

from datetime import datetime
from pathlib import Path
from lib_py3.scoreboard import Scoreboard
from minecraft.region import Region
from minecraft.world import World


def get_region_entity_uuids(arg):
    full_path, rx, rz, region_type = arg
    region = region_type(full_path, rx, rz, read_only=True)
    entity_uuids = set()
    for chunk in region.iter_chunks():
        for entity in chunk.recursive_iter_entities():
            entity_uuid = entity.uuid
            if entity_uuid is not None:
                entity_uuids.add(str(entity_uuid))
    return entity_uuids


def handle_shard(shard_path, num_threads, dry_run):
    scoreboard_paths = list(shard_path.glob('**/scoreboard.dat'))
    if len(scoreboard_paths) == 0:
        print('No scoreboard files found.', file=sys.stderr, flush=True)
        return

    regions = []
    for level_dat_path in shard_path.glob('**/level.dat'):
        world_path = level_dat_path.parent
        world = World(world_path)
        for full_path, rx, rz, region_type in world.enumerate_regions():
            regions.append((full_path, rx, rz, region_type))

    print(f'Running with {num_threads} thread(s) for {len(regions)} region files.', flush=True)
    if num_threads == 1:
        results = []
        for region in regions:
            results.append(get_region_entity_uuids(region))
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_threads) as pool:
            results = pool.map(get_region_entity_uuids, regions)

    all_entity_uuids = set()
    for entity_uuids in results:
        all_entity_uuids |= entity_uuids

    print(f'Found {len(all_entity_uuids)} living entity UUIDs', flush=True)

    for scoreboard_path in scoreboard_paths:
        print(f'{scoreboard_path}: ', end='', flush=True)
        scoreboard = Scoreboard(scoreboard_path)
        before = len(scoreboard.all_scores)
        scoreboard.prune_missing_entities(all_entity_uuids)
        after = len(scoreboard.all_scores)
        if not dry_run:
            scoreboard.save()
        print(f'Pruned {before - after} scores out of {before}', flush=True)


def main():
    multiprocessing.set_start_method("fork")

    start = datetime.now()

    cpu_count = os.cpu_count()
    if cpu_count is None:
        cpu_count = 1
    default_thread_count = cpu_count // 4
    if default_thread_count < 1:
        default_thread_count = 1

    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('shard_path', type=Path, nargs='+')
    arg_parser.add_argument('-j', '--num-threads', type=int, default=default_thread_count)
    arg_parser.add_argument('--dry-run', action='store_true')
    args = arg_parser.parse_args()

    num_threads = args.num_threads
    dry_run = args.dry_run
    if dry_run:
        print('Dry run, changes will not be saved.', flush=True)

    shard_paths = args.shard_path
    got_bad_path = False
    for shard_path in shard_paths:
        if not shard_path.is_dir():
            got_bad_path = True
            print(f'{shard_path} is not a folder', file=sys.stderr, flush=True)
    if got_bad_path:
        sys.exit('Not all shard paths are folders.')

    for shard_path in shard_paths:
        handle_shard(shard_path, num_threads, dry_run)

    end = datetime.now()
    print(f'Finished in {end - start}', flush=True)


if __name__ == '__main__':
    main()
