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
                        if "minecraft:item_frame" in idt or "minecraft:armor_stand" in idt or "minecraft:villager" in idt or (entityNbt.has_path("CustomName") and entityNbt.at_path("CustomName").value):
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
                        entity.nbt.value.at_path("Tags").value = nbt.TagList([nbt.TagString("UNPUSHABLE"),])
                    entity.nbt.value["Invulnerable"] = nbt.TagByte(1)
                elif entityNbt.has_path("CustomName") and entityNbt.at_path("CustomName").value:
                    if entity.nbt.has_path("Tags"):
                        entity.nbt.at_path("Tags").value.append(nbt.TagString("UNPUSHABLE"))
                    else:
                        entity.nbt.value.at_path("Tags").value = nbt.TagList([nbt.TagString("UNPUSHABLE"),])
                    entity.nbt.value["NoAI"] = nbt.TagByte(1)
                    entity.nbt.value["Invulnerable"] = nbt.TagByte(1)
                else:
                    print(f"Found entity {entity.id} but should have already been removed at this point")

# TODO: Need to lock all plots, not just plots players own?

# Get the plot command blocks and their orientations
with open("all_plot_records_with_mail.json", "r") as fp:
    plots = json.load(fp)

world = World("/home/epic/stage/m12/plots/Project_Epic-plots")

mailbox_sizes = {}
entity_sizes = {}

for plot_id in plots:
    plot = plots[plot_id]

    if (int(plot["world_id"]) % 50) == 0:
        print(plot["world_id"])

    min_x = plot["min"][0]
    min_y = plot["min"][1]
    min_z = plot["min"][2]
    max_x = plot["max"][0]
    max_y = plot["max"][1]
    max_z = plot["max"][2]

    lock_things(world, min_x - 4, 0, min_z - 4, max_x + 4, 255, max_z + 4)

    break # TODO
