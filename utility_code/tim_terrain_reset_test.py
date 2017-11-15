#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).
"""

from lib_monumenta.terrain_reset import terrainReset
from lib_monumenta import item_replace
import item_replace_list

itemReplacementsTest = item_replace.ReplaceItems([
    # Bow (testing spawners)
    [{"id":"minecraft:bow",},["remove"]],
    
    # Iron:
    [ {"id":"minecraft:iron_ore"}, ["remove"] ],
    [ {"id":"minecraft:iron_nugget"}, ["remove"] ],
    [ {"id":"minecraft:iron_ingot"}, ["remove"] ],
    [ {"id":"minecraft:iron_block"}, ["remove"] ],
    [ {"id":"minecraft:iron_helmet"}, ["remove"] ],
    [ {"id":"minecraft:iron_chestplate"}, ["remove"] ],
    [ {"id":"minecraft:iron_leggings"}, ["remove"] ],
    [ {"id":"minecraft:iron_boots"}, ["remove"] ],
    [ {"id":"minecraft:iron_axe"}, ["remove"] ],
    [ {"id":"minecraft:iron_hoe"}, ["remove"] ],
    [ {"id":"minecraft:iron_pickaxe"}, ["remove"] ],
    [ {"id":"minecraft:iron_shovel"}, ["remove"] ],
    [ {"id":"minecraft:iron_sword"}, ["remove"] ],

    # Diamond:
    [ {"id":"minecraft:diamond_ore"}, ["remove"] ],
    [ {"id":"minecraft:diamond"}, ["remove"] ],
    [ {"id":"minecraft:diamond_block"}, ["remove"] ],
    [ {"id":"minecraft:diamond_helmet"}, ["remove"] ],
    [ {"id":"minecraft:diamond_chestplate"}, ["remove"] ],
    [ {"id":"minecraft:diamond_leggings"}, ["remove"] ],
    [ {"id":"minecraft:diamond_boots"}, ["remove"] ],
    [ {"id":"minecraft:diamond_axe"}, ["remove"] ],
    [ {"id":"minecraft:diamond_hoe"}, ["remove"] ],
    [ {"id":"minecraft:diamond_pickaxe"}, ["remove"] ],
    [ {"id":"minecraft:diamond_shovel"}, ["remove"] ],
    [ {"id":"minecraft:diamond_sword"}, ["remove"] ],

    # Other:
    [ {"id":"minecraft:anvil"}, ["remove"] ],
    [ {"id":"minecraft:hopper"}, ["remove"] ],
    [ {"id":"minecraft:hopper_minecart"}, ["remove"] ],
    [ {"id":"minecraft:beacon"}, ["remove"] ],
    [ {"id":"minecraft:nether_star"}, ["remove"] ],

    [ {"id":"minecraft:bucket"}, ["remove"] ],
    [ {"id":"minecraft:water_bucket"}, ["remove"] ],
    [ {"id":"minecraft:lava_bucket"}, ["remove"] ],
    [ {"id":"minecraft:milk_bucket"}, ["remove"] ],
    [ {"id":"minecraft:emerald"}, ["remove","print","*** Emerald found",] ],

    [
        {
            "count":0,
        },
        [
            "id","minecraft:rotten_flesh",
            "count","=",1,
            "damage","=",0,
            "nbt","replace",ur'''{ench:[{lvl:1s,id:71s}],display:{Name:"§cDecayed Item",Lore:["You had something","you shouldn't have,","didn't you?"]}}''',
            "print","*** Notice given",
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

        "blockReplacements":item_replace_list.blockReplacements,
        "itemReplacements":item_replace_list.itemReplacements,

        "coordinatesToFill":(
            {"name":"Meh block", "pos1":(146,72,110), "pos2":(146,72,110), "replace":True, "material":(0,0), "materialName":"air"},
        ),

        "coordinatesToCopy":(
            {"name":"hut1",       "pos1":(153,68,104), "pos2":(156,73,108), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut2fence",  "pos1":(159,64,112), "pos2":(163,69,116), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut3",       "pos1":(150,70,112), "pos2":(154,75,115), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"church",     "pos1":(138,73,113), "pos2":(146,84,117), "replace":False, "material":(0,0), "materialName":"air"},
            {"name":"hut4",       "pos1":(113,62,126), "pos2":(116,68,130), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"farm1s",     "pos1":(120,62,122), "pos2":(126,64,130), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut5",       "pos1":(133,70,126), "pos2":(136,74,130), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut6",       "pos1":(155,70,126), "pos2":(158,74,130), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"farm2l",     "pos1":(164,67,122), "pos2":(176,69,130), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"well",       "pos1":(146,58,130), "pos2":(151,73,135), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut7",       "pos1":(111,61,134), "pos2":(115,67,138), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"farm3l",     "pos1":(118,62,134), "pos2":(130,64,142), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut8TShape", "pos1":(136,63,136), "pos2":(147,73,144), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut9fence",  "pos1":(153,68,134), "pos2":(157,74,138), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"hut10fence", "pos1":(150,64,139), "pos2":(154,70,143), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"farm4l",     "pos1":(164,68,134), "pos2":(176,70,142), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"farm5s",     "pos1":(150,63,146), "pos2":(158,65,152), "replace":True,  "material":(0,0), "materialName":"air"},
            {"name":"farm6l",     "pos1":(138,62,153), "pos2":(146,64,165), "replace":True,  "material":(0,0), "materialName":"air"},
        ),
    },
    {
        "server":"plots_world",

        "localMainFolder":"/home/tim/.minecraft/saves/Item Reset Test/",
        "localDstFolder":"/home/tim/.minecraft/saves/Item Reset dst/",

        "blockReplacements":item_replace_list.blockReplacements,
        "itemReplacements":itemReplacementsTest,
    }
]

terrainReset(configList)


