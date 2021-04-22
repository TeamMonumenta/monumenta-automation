#!/usr/bin/env python3
import os
import sys
import uuid
from collections import defaultdict

from lib_py3.scoreboard import Scoreboard

root = '/home/epic/play/project_epic'
log_dir = '/home/epic/5_SCRATCH/score_counts'
shards = []
for shard in sorted(os.listdir(root)):
    if shard == 'purgatory':
        continue
    if not os.path.isfile(os.path.join(root, shard, f'Project_Epic-{shard}', 'data/scoreboard.dat')):
        continue
    shards.append(shard)

for i, shard in enumerate(shards):
    print(f'{i+1:>2}/{len(shards)} {shard:>12}: Loading scoreboard...')
    scoreboard = Scoreboard(os.path.join(root, shard, f'Project_Epic-{shard}', 'data/scoreboard.dat'))

    print(f'{i+1:>2}/{len(shards)} {shard:>12}: Counting scores...')
    name_score_counts = defaultdict(int)
    for score in scoreboard.all_scores:
        name_score_counts[score.at_path('Name').value] += 1

    print(f'{i+1:>2}/{len(shards)} {shard:>12}: Saving logs...')
    with open(os.path.join(log_dir, f'{shard}.csv'), 'w') as fp:
        fp.write(f'"score_count","name"\n')
        for name in sorted(name_score_counts, key=name_score_counts.get, reverse=True):
            score_count = name_score_counts[name]
            fp.write(f'{score_count},{name}\n')
        fp.close()

print('Done.')

