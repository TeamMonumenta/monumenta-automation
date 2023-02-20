#!/usr/bin/env python3

import argparse
import traceback
from datetime import datetime, timedelta
from multiprocessing import Pool
from pathlib import Path

from lib_py3.scoreboard import Scoreboard
from minecraft.region import EntitiesRegion
from minecraft.world import World
from entity_scores import get_entity_scores
from entity_scores import set_entity_scores


PROCESSES = 8


def folder_size_sort_key(path):
    return len(list(path.iterdir()))


def handle_region(arg):
    full_path, rx, rz, region_type = arg
    region = region_type(full_path, rx, rz)

    region_entity_scores = {}

    for chunk in region.iter_chunks(autosave=True):
        for entity in chunk.recursive_iter_entities():
            entity_uuid = entity.uuid
            if entity_uuid is None:
                continue

            owner = str(entity.uuid)
            entity_scores = get_entity_scores(entity)
            region_entity_scores[owner] = entity_scores
            set_entity_scores(entity, {})

    return region_entity_scores


def region_arg_iter(shard_path):
    for world_path in shard_path.iterdir():
        if not (world_path / 'level.dat').is_file():
            continue
        world = World(world_path)
        for full_path, rx, rz, region_type in world.enumerate_regions(region_types=(EntitiesRegion,)):
            yield (full_path, rx, rz, region_type)


def handle_shard(shard_path, pool):
    try:
        shard = shard_path.name
        scoreboard_path = shard_path / f'Project_Epic-{shard}' / 'data' / 'scoreboard.dat'
        if not scoreboard_path.is_file():
            return None

        print(f'Working on {shard}...')
        try:
            scoreboard = Scoreboard(scoreboard_path)
        except Exception:
            print(f'Could not load scoreboard file {scoreboard_path}')
            return None

        all_entity_scores = {}
        for region_entity_scores in pool.map(handle_region, region_arg_iter(shard_path)):
            all_entity_scores.update(region_entity_scores)

        print(f'Queueing scores of scoredboard for {shard} ({len(all_entity_scores)})...')
        return (shard, scoreboard, all_entity_scores)

    except Exception as ex:
        print(f'An exception occurred: {ex}')
        print(traceback.format_exc())
        return None


def finish_shard(shard, scoreboard, all_entity_scores):
    try:
        print(f'Setting scores in scoredboard for {shard} ({len(all_entity_scores)})...')

        for owner, entity_scores in all_entity_scores.items():
            scoreboard.reset_scores(Name=owner)
            for objective, score in entity_scores.items():
                scoreboard.set_score(owner, objective, score)

        scoreboard.save()
        print(f'Done with {shard}.')

    except Exception as ex:
        print(f'An exception occurred: {ex}')
        print(traceback.format_exc())


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('host_path', type=Path)
    args = arg_parser.parse_args()

    host_path = args.host_path
    start = datetime.now()
    with Pool(processes=PROCESSES) as pool:
        res = None
        for shard_path in sorted(host_path.iterdir(), key=folder_size_sort_key, reverse=True):
            finish_shard_arg = handle_shard(shard_path, pool)
            if res is not None:
                res.wait()
                res = None
            if finish_shard_arg is not None:
                res = pool.apply_async(finish_shard, finish_shard_arg)
                print(f'Queued scores of scoredboard for {finish_shard_arg[0]}...')

        if res is not None:
            res.wait()

    minutes, seconds = divmod(int((datetime.now() - start) / timedelta(seconds=1)), 60)
    hours, minutes = divmod(minutes, 60)
    print(f'Done in {hours}h{minutes:02d}m{seconds:02d}s')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
