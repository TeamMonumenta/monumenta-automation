#!/usr/bin/env python3

import sys
import os
import json
from queue import Empty

from minecraft.world import World
from minecraft.player_dat_format.item import Item
from multiprocessing import Process, Queue

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

def get_mailbox_chests(world, read_only=True):
    for region in world.iter_regions(min_x = -1292, min_y = 100, min_z = -1292, max_x = -1292 + 1, max_y = 100 + 2, max_z = -1292 + 1, read_only=read_only):
        for chunk in region.iter_chunks(min_x = -1292, min_y = 100, min_z = -1292, max_x = -1292 + 1, max_y = 100 + 2, max_z = -1292 + 1, autosave=not read_only):
            for block_entity in chunk.iter_block_entities(min_x = -1292, min_y = 100, min_z = -1292, max_x = -1292 + 1, max_y = 100 + 2, max_z = -1292 + 1):
                yield block_entity

def process(inq, outq):
    template_world = World("template")
    template_filled_world = World("templatefilled")

    try:
        while not inq.empty():
            plot = inq.get(block=False)
            world_id = plot["world_id"]
            if plot["border_item_frames"]:
                world = template_filled_world.copy_to(f"plot{world_id}")
            else:
                world = template_world.copy_to(f"plot{world_id}")

            items = plot["mailbox_items"]
            if len(items) > 0:
                for block_entity in get_mailbox_chests(world, read_only=False):
                    if block_entity.id != "minecraft:chest":
                        print(f"WARNING: Got unexpected block entity {block_entity} at -1292 102 -1292 in world plot{world_id}")
                        continue

                    # Only chests here

                    slot = 0
                    while slot < 27 and len(items) > 0:
                        item_nbt = nbt.TagCompound.from_mojangson(items.pop())
                        item_nbt.value["Slot"] = nbt.TagByte(slot)
                        block_entity.nbt.at_path("Items").value.append(item_nbt)
                        slot += 1

            if len(items) > 0:
                print(f"WARNING: Still had {len(items)} mailbox items left after populating mailbox in world plot{world_id}")

            outq.put(plot["world_id"])
    except Empty:
        pass


# Get the plot command blocks and their orientations
with open("all_plot_records_with_mail.json", "r") as fp:
    plots = json.load(fp)

inq = Queue()
outq = Queue()
count = 0
for plot in plots:
    inq.put(plots[plot])
    count += 1
    if count > 0: # TODO: Remove this
        break

threads = 4
if threads > 1:
    procs = []
    for i in range(0, threads):
        p = Process(target=process, args=(inq,outq))
        p.start()
        procs.append(p)

    for proc in procs:
        proc.join()
else:
    process(inq, outq)

while not outq.empty():
    print(outq.get(block=False))

