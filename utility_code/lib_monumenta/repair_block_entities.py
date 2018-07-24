#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import codecs

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
import pymclevel
from pymclevel import nbt

from lib_monumenta.iter_entity import IterEntities

expectedBlocks = {
    "minecraft:banner":[176,177],
    "minecraft:beacon":[138],
    "minecraft:bed":[26],
    "minecraft:brewing_stand":[117],
    "minecraft:chest":[54,146],
    "minecraft:comparator":[149,150],
    "minecraft:command_block":[137,210,211],
    "minecraft:daylight_detector":[151,178],
    "minecraft:dispenser":[23],
    "minecraft:dropper":[158],
    "minecraft:enchanting_table":[116],
    "minecraft:ender_chest":[130],
    "minecraft:end_gateway":[209],
    "minecraft:end_portal":[119],
    "minecraft:flower_pot":[140],
    "minecraft:furnace":[61],
    "minecraft:hopper":[154],
    "minecraft:jukebox":[84],
    "minecraft:mob_spawner":[52],
    "minecraft:noteblock":[25],
    "minecraft:piston":[36], # piston extension technical block
    "minecraft:shulker_box":list(range(219,234+1)),
    "minecraft:sign":[63,68],
    "minecraft:skull":[144],
    "minecraft:structure_block":[255],
}

def repair_block_entities(worldDir):
    good = 0
    bad = 0
    ugly = 0
    world = pymclevel.loadWorld(worldDir)
    for cx,cz in world.allChunks:
        chunk = world.getChunk(cx,cz)
        chunkTag = chunk.root_tag
        if (
            "Level" not in chunkTag or
            "TileEntities" not in chunkTag["Level"]
        ):
            continue
        allBlockEntities = chunkTag["Level"]["TileEntities"]

        cx = chunkTag['Level']['xPos'].value
        cz = chunkTag['Level']['zPos'].value
        validBlockEntities = nbt.TAG_List()

        for blockEntity in allBlockEntities:
            if (
                type(blockEntity) is not nbt.TAG_Compound or
                "id" not in blockEntity or
                "x" not in blockEntity or
                "y" not in blockEntity or
                "z" not in blockEntity
            ):
                ugly += 1
                continue

            blockEntityId = blockEntity["id"].value
            x = blockEntity["x"].value
            y = blockEntity["y"].value
            z = blockEntity["z"].value
            blockId = world.blockAt(x,y,z)
            if blockId not in expectedBlocks[blockEntityId]:
                print("- {} block entity found in invalid block {} at 'tp @s {} {} {}'".format(blockEntityId,blockId,x,y,z))
                bad += 1
                continue

            good += 1
            validBlockEntities.append(blockEntity)

        chunkTag["Level"]["TileEntities"] = validBlockEntities
        chunk.chunkChanged(False) # needsLighting=False
    world.saveInPlace()
    print("{} good, {} bad, and {} unrecognizable block entities".format(good,bad,ugly))

