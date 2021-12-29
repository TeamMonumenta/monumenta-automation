#!/usr/bin/python3
import os
import sys
import math

from collections import OrderedDict
from lib_py3.redis_scoreboard import RedisScoreboard
from r1plot_lookup import lut
from pprint import pprint
from minecraft.world import World
import json

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

def lock_things(world, min_x, min_y, min_z, max_x, max_y, max_z):
    for region in world.iter_regions(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x, max_y = max_y, max_z = max_z, read_only=False):
        for chunk in region.iter_chunks(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x, max_y = max_y, max_z = max_z, autosave=True):
            # Remove and lock all block entities
            for block_entity in chunk.iter_block_entities(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x, max_y = max_y, max_z = max_z):
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
            if chunk.nbt.has_path("Level.Entities"):
                lst = []
                for entityNbt in chunk.nbt.at_path("Level.Entities").value:
                    if not entityNbt.has_path("id"):
                        print(f"Got entity entry in {chunk.pos} that doesn't have an id: {entityNbt.to_mojangson()}")
                    else:
                        idt = entityNbt.at_path("id").value
                        if (
                                ("minecraft:item_frame" in idt and entityNbt.has_path("Item.id") and "minecraft:air" not in entityNbt.at_path("Item.id").value)
                                or "minecraft:armor_stand" in idt
                                or "minecraft:villager" in idt
                                or (entityNbt.has_path("CustomName") and len(entityNbt.at_path("CustomName").value) > 0)
                            ):
                            lst.append(entityNbt)

                chunk.nbt.at_path("Level.Entities").value = lst

            # Remove all entities except item frames, armor stands, and villagers
            for entity in chunk.iter_entities(min_x = min_x, min_y = min_y, min_z = min_z, max_x = max_x, max_y = max_y, max_z = max_z):
                if "minecraft:item_frame" in entity.id:
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
                else:
                    print(f"Found entity {entity.id} but should have already been removed at this point")
                    entity.nbt.tree()
                    die

# Get the plot command blocks and their orientations
with open("plots.json", "r") as fp:
    plotCommands = json.load(fp)

# Compute the plot coordinates for all plots, not just ones with owners
offsets = {"north": (0, -2, 3), "east": (-3, -2, 0), "south": (0, -2, -3), "west": (3, -2, 0)}
plots = {}
for command in plotCommands:
    if "function plot:plot/enter" not in command["command"]:
        continue

    facing = command["facing"]
    if facing is None:
        continue

    x, y, z = command["pos"]
    offx, offy, offz = offsets[facing]

    plotx = x - offx
    ploty = y - offy
    plotz = z - offz

    pos = f"{plotx} {ploty} {plotz}"
    slot = {}
    if facing == "north":
        slot["min"] = (plotx - 8, ploty - 17, plotz - 23)
        slot["max"] = (plotx + 8, ploty + 32, plotz - 1)
    elif facing == "east":
        slot["min"] = (plotx + 1, ploty - 17, plotz - 8)
        slot["max"] = (plotx + 23, ploty + 32, plotz + 8)
    elif facing == "south":
        slot["min"] = (plotx - 8, ploty - 17, plotz + 1)
        slot["max"] = (plotx + 8, ploty + 32, plotz + 23)
    elif facing == "west":
        slot["min"] = (plotx - 23, ploty - 17, plotz - 8)
        slot["max"] = (plotx - 1, ploty + 32, plotz + 8)
    slot["facing"] = facing

    plots[pos] = slot

#pprint(plots)

# Lock everything
world = World("Project_Epic-plots")
step = 0
for plot_id in plots:
    step += 1
    plot = plots[plot_id]

    #if (step < 2140):
        #continue
    print(f"{step} / {len(plots)}")
    pprint(plot)


    min_x = plot["min"][0]
    min_y = plot["min"][1]
    min_z = plot["min"][2]
    max_x = plot["max"][0]
    max_y = plot["max"][1]
    max_z = plot["max"][2]

    lock_things(world, min_x - 6, 0, min_z - 6, max_x + 7, 255, max_z + 7)
