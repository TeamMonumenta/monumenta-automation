#!/usr/bin/env python3

import sys
import os
import json
from pprint import pprint

from minecraft.chunk_format.entity import Entity

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

# Get the plot command blocks and their orientations
with open("all_plot_records_with_mail.json", "r") as fp:
    plots = json.load(fp)

for plot in plots:
    if len(plots[plot]["door_entities"]) > 0:
        entities = ""
        for entitystr in plots[plot]["door_entities"]:
            entitynbt = nbt.TagCompound.from_mojangson(entitystr)
            entities += Entity(entitynbt).id + " "


        print(f"/tp @s {plot}               {entities}")

print()
print()
print()
for plotkey in plots:
    plot = plots[plotkey]
    world_id = plot["world_id"]
    for uuid in plot["members"]:
        name = plot["members"][uuid]
        print(f"./redis_set_offline_player_score 'redis://127.0.0.1/' play {name} Plot {world_id} 'Set Plot score'")
        print(f"./redis_set_offline_player_score 'redis://127.0.0.1/' play {name} CurrentPlot {world_id} 'Set CurrentPlot score'")
