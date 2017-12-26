#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tim's test terrain reset script - used on tiny local worlds to debug quickly.
"""

import shutil

from lib_monumenta.terrain_reset import terrainReset
from lib_monumenta import item_replace
import item_replace_list

itemReplacementsTest = item_replace.ReplaceItems([],[
    # Bow (testing spawners)
    [{"id":"minecraft:bow",},["remove"]],

    # Other:
    [ {"id":"minecraft:emerald"}, ["name","set",u"Decayed Item"] ],

    [
        {
            "id":"minecraft:wool",
            "damage":0,
        },
        [
            "nbt","replace",ur'''{display:{Name:"§0Test"}}''',
        ]
    ],
    [
        {
            "id":"minecraft:wool",
            "damage":1,
        },
        [
            "nbt","replace",ur'''{display:{Name:"§1Test"}}''',
        ]
    ],
    [
        {
            "id":"minecraft:wool",
            "damage":2,
        },
        [
            "nbt","replace",ur'''{display:{Name:"§2Test"}}''',
        ]
    ],
    [
        {
            "id":"minecraft:wool",
            "damage":3,
        },
        [
            "nbt","replace",ur'''{display:{Name:"§33§cc"}}''',
        ]
    ],
    [
        {
            "id":"minecraft:wool",
            "name":"Test",
        },
        [
            "nbt","replace",ur'''{display:{Name:"Baaaa!"}}''',
        ]
    ],
    [
        {
            "name":"Decayed Item",
        },
        [
            #"print","Replacing item with notice:",
            #"print item",
            "id","minecraft:rotten_flesh",
            "count","=",1,
            "damage","=",0,
            "nbt","replace",ur'''{ench:[{lvl:1s,id:71s}],display:{Name:"§cDecayed Item",Lore:["You had something","you shouldn't have,","didn't you?"]}}''',
            #"name","color","green",
        ]
    ],
])


configList = [
    {
        "server":"dst_merged",

        "localMainFolder":"/home/tim/.minecraft/saves/main/",
        "localBuildFolder":"/home/tim/.minecraft/saves/build/",
        "localDstFolder":"/home/tim/.minecraft/saves/dst/",

        "safetyTpLocation":(149.0, 76.0, 133.0, 0.0, 0.0),

        "resetRegionalDifficulty":True,

        "copyBaseFrom":"build",
        "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],

        "blockReplacements":item_replace_list.blockReplacements,
        "blockReplaceLocations":["schematics",],

        "itemReplacements":item_replace_list.KingsValley,
        "itemReplaceLocations":["schematics","players",],

        "coordinatesToFill":(
            {"name":"Meh block", "pos1":(146,72,110), "pos2":(146,72,110), "replaceBlocks":True, "material":(0,0), "materialName":"air"},
        ),

        "coordinatesToCopy":(
            {"name":"hut1",       "pos1":(153,68,104), "pos2":(156,73,108), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut2fence",  "pos1":(159,64,112), "pos2":(163,69,116), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut3",       "pos1":(150,70,112), "pos2":(154,75,115), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"church",     "pos1":(138,73,113), "pos2":(146,84,117), "replaceBlocks":False, "replaceItems":False, "material":(0,0), "materialName":"air"},
            {"name":"hut4",       "pos1":(113,62,126), "pos2":(116,68,130), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"farm1s",     "pos1":(120,62,122), "pos2":(126,64,130), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut5",       "pos1":(133,70,126), "pos2":(136,74,130), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut6",       "pos1":(155,70,126), "pos2":(158,74,130), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"farm2l",     "pos1":(164,67,122), "pos2":(176,69,130), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"well",       "pos1":(146,58,130), "pos2":(151,73,135), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut7",       "pos1":(111,61,134), "pos2":(115,67,138), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"farm3l",     "pos1":(118,62,134), "pos2":(130,64,142), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut8TShape", "pos1":(136,63,136), "pos2":(147,73,144), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut9fence",  "pos1":(153,68,134), "pos2":(157,74,138), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut10fence", "pos1":(150,64,139), "pos2":(154,70,143), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"farm4l",     "pos1":(164,68,134), "pos2":(176,70,142), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"farm5s",     "pos1":(150,63,146), "pos2":(158,65,152), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
            {"name":"farm6l",     "pos1":(138,62,153), "pos2":(146,64,165), "replaceBlocks":True,  "replaceItems":True,  "material":(0,0), "materialName":"air"},
        ),

        "itemLog":"/home/tim/Desktop/village.txt",
    },
    {
        "server":"item_cave",

        "localMainFolder":"/home/tim/.minecraft/saves/Item Reset Test/",
        "localDstFolder":"/home/tim/.minecraft/saves/Item Reset dst/",

        "copyBaseFrom":"main",
        "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],

        "blockReplacements":item_replace_list.blockReplacements,
        "blockReplaceLocations":["world",],

        "itemReplacements":itemReplacementsTest,
        "itemReplaceLocations":["world",],

        "itemLog":"/home/tim/Desktop/item_cave.txt",
    }
]

"""
configList = [
    {
        "server":"r1plots",

        "localMainFolder":"/home/tim/.minecraft/saves/Project_Epic-r1plots_pre/",
        "localDstFolder":"/home/tim/.minecraft/saves/Project_Epic-r1plots_post/",

        "copyBaseFrom":"main",

        "itemReplacements":item_replace_list.KingsValley,
        "itemReplaceLocations":["world",],
        "itemLog":"/home/tim/Desktop/items_r1plots.txt",
    },{
        "server":"betaplots",

        "localMainFolder":"/home/tim/.minecraft/saves/Project_Epic-betaplots_pre/",
        "localDstFolder":"/home/tim/.minecraft/saves/Project_Epic-betaplots_post/",

        "copyBaseFrom":"main",

        "itemReplacements":item_replace_list.KingsValley,
        "itemReplaceLocations":["world",],
        "itemLog":"/home/tim/Desktop/items_betaplots.txt",
    },{
        "server":"region_1",

        "localMainFolder":"/home/tim/.minecraft/saves/Project_Epic-region_1_pre/",
        "localDstFolder":"/home/tim/.minecraft/saves/Project_Epic-region_1_post/",

        "copyBaseFrom":"main",

        "itemReplacements":item_replace_list.KingsValley,
        "itemReplaceLocations":["world",],
        "itemLog":"/home/tim/Desktop/items_region_1.txt",
    }
]
"""
#shutil.rmtree("/home/tim/.minecraft/saves/dst", ignore_errors=True)
#shutil.rmtree("/home/tim/.minecraft/saves/Item Reset dst", ignore_errors=True)
shutil.rmtree("/home/tim/.minecraft/saves/Project_Epic-r1plots_post/", ignore_errors=True)
terrainReset(configList)

