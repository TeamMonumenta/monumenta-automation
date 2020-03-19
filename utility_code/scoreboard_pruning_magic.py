#!/usr/bin/env python3
import os
import sys

from lib_py3.scoreboard import Scoreboard
from lib_py3.world import World

root='/home/epic/play/project_epic'
shards = [
    'betaplots',
    'build',
    'cyan',
    'gray',
    'labs',
    'lightblue',
    'lightgray',
    'lime',
    'magenta',
    'orange',
    'pink',
    'plots',
    #'purgatory', # NO! Bad!
    'purple',
    'region_1',
    'region_2',
    'reverie',
    'roguelike',
    'sanctum',
    'shiftingcity',
    'tutorial',
    'white',
    'willows',
    'yellow',
]

for i, shard in enumerate(shards):
    try:
        print(f'{i+1:>2}/{len(shards)} {shard:>12}: Loading world...')
        world = World(os.path.join(root, shard, 'Project_Epic-' + shard))
        print(f'{i+1:>2}/{len(shards)} {shard:>12}: Loading scoreboard...')
        scoreboard = world.scoreboard
        print(f'{i+1:>2}/{len(shards)} {shard:>12}: Getting living UUIDs...')
        alive = world.entity_uuids()
        print(f'{i+1:>2}/{len(shards)} {shard:>12}: Getting tracked UUIDs...')
        tracked = set()
        for score in scoreboard.all_scores.scores:
            owner = score.at_path("Name").value
            if len(owner) == 36:
                tracked.add(owner)
        print(f'{i+1:>2}/{len(shards)} {shard:>12}: Getting list of dead entities...')
        dead = tracked - alive
        print(f'{i+1:>2}/{len(shards)} {shard:>12}: Creating mcfunction...')
        mcfunction_dir = os.path.join(root, 'server_config/data/datapacks', shard, 'data/monumenta/functions')
        os.makedirs(mcfunction_dir, exist_ok=True)
        with open(os.path.join(mcfunction_dir, 'prune_scores.mcfunction'), 'w') as fp:
            for uuid in dead:
                fp.write(f'scoreboard players reset {uuid}\n')
            fp.close()
        print(f'{i+1:>2}/{len(shards)} {shard:>12}: Done.')
    except Exception: # Don't catch keyboard interrupts - let those stop the script
        print(f'{i+1:>2}/{len(shards)} {shard:>12}: Exception caught, skipping.')

print('Done.')
