#!/usr/bin/env pypy3
"""For each world in a shard, import/export scores from/to json files in the world folders."""

import argparse
import concurrent
import json
import multiprocessing
import os
import sys

from datetime import datetime
from pathlib import Path
from lib_py3.scoreboard import Scoreboard
from minecraft.region import Region
from minecraft.world import World


def get_region_entity_uuids(arg):
    full_path, world_name, rx, rz, region_type = arg
    region = region_type(full_path, rx, rz, read_only=True)
    entity_uuids = set()
    for chunk in region.iter_chunks():
        for entity in chunk.recursive_iter_entities():
            entity_uuid = entity.uuid
            if entity_uuid is not None:
                entity_uuids.add(str(entity_uuid))
    return {world_name: entity_uuids}


def export_shard_scores(shard_path, num_threads, dry_run):
    scoreboard = get_main_scoreboard(shard_path)

    regions = []
    for world_name in World.enumerate_worlds(str(shard_path)):
        world = World(str(shard_path / world_name))
        for full_path, rx, rz, region_type in world.enumerate_regions():
            regions.append((full_path, world_name, rx, rz, region_type))

    print(f'Running with {num_threads} thread(s) for {len(regions)} region files.', flush=True)
    if num_threads == 1:
        results = []
        for region in regions:
            results.append(get_region_entity_uuids(region))
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_threads) as pool:
            results = pool.map(get_region_entity_uuids, regions)

    world_entity_uuids = {}
    entity_count = 0
    for region_entity_uuids in results:
        for world_name, uuids in region_entity_uuids.items():
            if world_name not in world_entity_uuids:
                world_entity_uuids[world_name] = set()
            world_entity_uuids[world_name] |= uuids
            entity_count += len(uuids)
    del results

    score_count = 0
    score_counts_by_world = {}
    for world_name, uuids in world_entity_uuids.items():
        world_json_file = shard_path / world_name / 'scores.json'
        world_scores = {}
        for entity in uuids:
            entity_scores = {}
            for score in scoreboard.search_scores(Name=entity):
                objective = score.at_path("Objective").value
                value = score.at_path("Score").value
                entity_scores[objective] = value

                score_count += 1
                if world_name not in score_counts_by_world:
                    score_counts_by_world[world_name] = 0
                score_counts_by_world[world_name] += 1

            if len(entity_scores) > 0:
                world_scores[entity] = entity_scores

        if not dry_run:
            with open(world_json_file, 'w', encoding='utf-8') as fp:
                json.dump(world_scores, fp, ensure_ascii=False, indent=2, sort_keys=True)

    print(f'Found {score_count} scores on {entity_count} living entity UUIDs in {len(world_entity_uuids)} worlds for {shard_path}', flush=True)
    for world, count in sorted(score_counts_by_world.items()):
        print(f'- {world}: {count}')


def import_shard_scores(shard_path, num_threads, dry_run):
    scoreboard = get_main_scoreboard(shard_path)

    score_count = 0
    score_counts_by_world = {}
    for world_name in World.enumerate_worlds(str(shard_path)):
        world_json_file = shard_path / world_name / 'scores.json'
        if not world_json_file.is_file():
            continue

        score_counts_by_world[world_name] = 0
        with open(world_json_file, 'r', encoding='utf-8') as fp:
            world_scores = json.load(fp)
        for entity, entity_scores in world_scores.items():
            for objective, value in entity_scores.items():
                score_count += 1
                score_counts_by_world[world_name] += 1
                scoreboard.set_score(entity, objective, value)

    if not dry_run:
        scoreboard.save()
        for world_name in World.enumerate_worlds(str(shard_path)):
            world_json_file = shard_path / world_name / 'scores.json'
            world_json_file.unlink(missing_ok=True)

    print(f'Found {score_count} scores in {len(score_counts_by_world)} worlds for {shard_path}', flush=True)
    for world, count in sorted(score_counts_by_world.items()):
        print(f'- {world}: {count}')


def get_main_scoreboard(shard_path):
    level_name_prefix = 'level-name='
    server_properties_path = shard_path / 'server.properties'

    main_world = None
    with open(server_properties_path, 'r') as fp:
        for line in fp:
            if line.startswith(level_name_prefix):
                main_world = shard_path / line[len(level_name_prefix):].rstrip()
                break
    if main_world is None:
        raise Exception(f'Could not find main world for shard {shard_path}')

    return Scoreboard(main_world / 'data' / 'scoreboard.dat')


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
    arg_parser.add_argument('--import', action='store_true', dest='import_')
    arg_parser.add_argument('--export', action='store_true')
    arg_parser.add_argument('-j', '--num-threads', type=int, default=default_thread_count)
    arg_parser.add_argument('--dry-run', action='store_true')
    args = arg_parser.parse_args()

    if not args.export and not args.import_:
        print('Must specify if exporting or importing')
        argparser.print_usage()
        sys.exit(1)

    if args.export and args.import_:
        print('Must specify only one of exporting or importing')
        argparser.print_usage()
        sys.exit(1)

    exporting = args.export

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
        if exporting:
            export_shard_scores(shard_path, num_threads, dry_run)
        else:
            import_shard_scores(shard_path, num_threads, dry_run)

    end = datetime.now()
    print(f'Finished in {end - start}', flush=True)


if __name__ == '__main__':
    main()
