#!/usr/bin/python3
import sys
import math

from collections import OrderedDict
from lib_py3.redis_scoreboard import RedisScoreboard
from r1plot_lookup import lut
from pprint import pprint
from minecraft.world import World
import json

def get_items(world, min_x, min_y, min_z, max_x, max_y, max_z):
    items = []
    #print(min_x, min_y, min_z, max_x, max_y, max_z)
    for region in world.iter_regions(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x, max_y = max_y, max_z = max_z, read_only=True):
        for chunk in region.iter_chunks(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x, max_y = max_y, max_z = max_z, autosave=False):
            for block_entity in chunk.iter_block_entities(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x, max_y = max_y, max_z = max_z):
                #print(block_entity.pos)
                for item in block_entity.iter_items():
                    #print(item.id)
                    items.append(item.nbt.to_mojangson())

    return items

def get_entities(world, min_x, min_y, min_z, max_x, max_y, max_z):
    entities = []
    #print(min_x, min_y, min_z, max_x, max_y, max_z)
    for region in world.iter_regions(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x, max_y = max_y, max_z = max_z, read_only=True):
        for chunk in region.iter_chunks(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x, max_y = max_y, max_z = max_z, autosave=False):
            for entity in chunk.iter_entities(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x, max_y = max_y, max_z = max_z):
                entities.append(entity.nbt.to_mojangson())

    return entities


# Get the plot command blocks and their orientations
with open("all_plot_records.json", "r") as fp:
    plots = json.load(fp)

world = World("/home/epic/stage/m12/plots/Project_Epic-plots")

for plot_id in plots:
    plot = plots[plot_id]

    min_x = plot["min"][0]
    min_y = plot["min"][1]
    min_z = plot["min"][2]
    max_x = plot["max"][0]
    max_y = plot["max"][1]
    max_z = plot["max"][2]

    plot["border_item_frames"] = False
    for region in world.iter_regions(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x + 1, max_y = max_y + 1, max_z = max_z + 1, read_only=True):
        for chunk in region.iter_chunks(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x + 1, max_y = max_y + 1, max_z = max_z + 1, autosave=False):
            for entity in chunk.iter_entities(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x + 1, max_y = max_y + 1, max_z = max_z + 1):
                if "item_frame" in entity.id:
                    x = math.floor(entity.pos[0])
                    y = math.floor(entity.pos[1])
                    z = math.floor(entity.pos[2])
                    if (x == min_x or x == min_y or z == min_z or z == max_z or y == max_y):
                        plot["border_item_frames"] = True

    facing = plot["facing"]
    # The max arguments are exclusive for entity / block entities!
    if facing == "north":
        plot["mailbox_items"] = get_items(world, max_x - 11, min_y + 10, max_z + 1, max_x, min_y + 21, max_z + 3)
        plot["door_entities"] = get_entities(world, max_x - 11, min_y + 10, max_z + 1, max_x, min_y + 21, max_z + 3)
    elif facing == "east":
        plot["mailbox_items"] = get_items(world, min_x - 2, min_y + 10, max_z - 11, min_x, min_y + 21, max_z)
        plot["door_entities"] = get_entities(world, min_x - 2, min_y + 10, max_z - 11, min_x, min_y + 21, max_z)
    elif facing == "south":
        plot["mailbox_items"] = get_items(world, min_x + 1, min_y + 10, min_z - 2, min_x + 12, min_y + 21, min_z)
        plot["door_entities"] = get_entities(world, min_x + 1, min_y + 10, min_z - 2, min_x + 12, min_y + 21, min_z)
    elif facing == "west":
        plot["mailbox_items"] = get_items(world, max_x + 1, min_y + 10, min_z + 1, max_x + 3, min_y + 21, min_z + 12)
        plot["door_entities"] = get_entities(world, max_x + 1, min_y + 10, min_z + 1, max_x + 3, min_y + 21, min_z + 12)

#    if plot["world_id"] == 8:
#        pprint(plot)
#        break

with open("all_plot_records_with_mail.json", "w") as fp:
    json.dump(plots, fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))
