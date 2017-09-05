#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import mclevel
from mclevel import nbt

shulkerIDNames = [
    "minecraft:white_shulker_box",
    "minecraft:orange_shulker_box",
    "minecraft:magenta_shulker_box",
    "minecraft:light_blue_shulker_box",
    "minecraft:yellow_shulker_box",
    "minecraft:lime_shulker_box",
    "minecraft:pink_shulker_box",
    "minecraft:gray_shulker_box",
    "minecraft:silver_shulker_box",
    "minecraft:cyan_shulker_box",
    "minecraft:purple_shulker_box",
    "minecraft:blue_shulker_box",
    "minecraft:brown_shulker_box",
    "minecraft:green_shulker_box",
    "minecraft:red_shulker_box",
    "minecraft:black_shulker_box",
]
shulkerIDNums = range(219,234+1)

containerTagNames = [
    # Humanoid Entities
    "HandItems",
    "ArmorItems",
    
    # Horses
    "ArmorItem",
    "SaddleItem",
    "Items",
    
    # Item Frames
    "Item",
]

def replaceItemStack(itemStack,replacementList):
    # TODO replace items
    if "id" not in itemStack:
        # No item in this slot (mob armor/hand items)
        return
    if itemStack["id"].value in shulkerIDNames:
        shulkerBoxContents = itemStack["tag"]["BlockEntityTag"]["Items"]
        replaceItemStacks(shulkerBoxContents,replacementList)
    elif itemStack["id"].value == u"minecraft:spawn_egg":
        spawnEggEntity = itemStack["tag"]["EntityTag"]
        replaceItemsOnEntity(spawnEggEntity,replacementList)
    else:
        print itemStack.json
    
def replaceItemStacks(itemStackContainer,replacementList):
    if type(itemStackContainer) is nbt.TAG_List:
        for itemStack in itemStackContainer:
            replaceItemStack(itemStack,replacementList)
    else:
        replaceItemStack(itemStackContainer,replacementList)
    
def replaceItemsOnPlayers(worldDir,replacementList):
    for playerFile in os.listdir(worldDir+"/playerdata"):
        playerFile = worldDir+"/playerdata/" + playerFile
        player = nbt.load(playerFile)
        replaceItemStacks(player["Inventory"],replacementList)
        replaceItemStacks(player["EnderItems"],replacementList)
        #player.save(playerFile)

def replaceItemsOnEntity(entity,replacementList):
    for containerTagName in containerTagNames:
        if containerTagName in entity:
            replaceItemStacks(entity[containerTagName],replacementList)

def replaceItemsInWorld(world,replacementList):
    for cx,cz in world.allChunks:
        aChunk = world.getChunk(cx,cz)
        
        for entity in aChunk.root_tag["Level"]["Entities"]:
            replaceItemsOnEntity(entity,replacementList)
        
        for tileEntity in aChunk.root_tag["Level"]["TileEntities"]:
            replaceItemsOnEntity(tileEntity,replacementList)



