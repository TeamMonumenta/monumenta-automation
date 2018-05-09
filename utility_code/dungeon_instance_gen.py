#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys

# The effective working directory for this script must always be the MCEdit-Unified directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))

from lib_monumenta.dungeon_instance_gen import gen_dungeon_instances

config = {
    "dungeonRefFolder":"/home/rock/5_SCRATCH/tmpreset/Project_Epic-dungeon/",
    "templateFolder":"/home/rock/5_SCRATCH/tmpreset/Project_Epic-template/",
    "outFolder":"/home/rock/5_SCRATCH/tmpreset/dungeons-out/",

    # Dungeons are placed one per MC region file (32x32 chunks)
    # Each dungeon starts in the most-negative corner of the region
    # Regions with dungeons form a line of consecutive regions in +z
    #
    # Each region containing a dungeon is full of void biome
    # There is a padding layer of void biome in the -x and -z directions as specified below
    #
    # All dungeons fit in a region file; even corrupted sierhaven is only 30x24 chunks

    "dungeons":(
        {
            "name":"white",
            "size":(160, 256, 352),
            "region":{"x":-3, "z":-2},
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(35, 0), "materialName":"white wool"},
            ),
            "chestContentsLoreToIgnore":("Monument Block",),
            "chestWhitelist":(
                (-1409,  37, -776),
                (-1409,  37, -775),
                (-1443,  42, -828),
                (-1442,  42, -828),
                (-1458,  30, -816),
                (-1487,  71, -920),
                (-1529, 120, -975),
                (-1517,  32, -782),
                (-1387,  24, -756),
                (-1420,  42, -877),
            ),
        },{
            "name":"orange",
            "size":(320, 120, 352),
            "region":{"x":-3, "z":-1},
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(35, 1), "materialName":"orange wool"},
            ),
            "chestContentsLoreToIgnore":("Monument Block",),
            "chestWhitelist":(),
        },{
            "name":"magenta",
            "size":(256, 256, 256),
            "region":{"x":-3, "z":0},
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(35, 2), "materialName":"magenta wool"},
            ),
            "chestContentsLoreToIgnore":("Monument Block",),
            "chestWhitelist":(
                (-1381, 88, 91),
                (-1379, 88, 92),
            ),
        },{
            "name":"lightblue",
            "size":(288, 256, 272),
            "region":{"x":-3, "z":1},
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(35, 3), "materialName":"light blue wool"},
            ),
            "chestContentsLoreToIgnore":("Monument Block", "D4 Key"),
            "chestWhitelist":(
                (-1381, 180, 645),
                (-1456, 170, 694),
                (-1371, 175, 598),
                (-1423, 178, 593),
                (-1265, 181, 598),
            ),
        },{
            "name":"yellow",
            "size":(256, 256, 256),
            "region":{"x":-3, "z":2},
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(35, 4), "materialName":"yellow wool"},
            ),
            "chestContentsLoreToIgnore":("Monument Block", "D5 Key"),
            "chestWhitelist":(
                (-1488,  65, 1086),
                (-1460,  90, 1239),
                (-1489,  65, 1087),
                (-1506, 103, 1165),
                (-1513,  40, 1152),
                (-1493,  65, 1095),
                (-1493,  65, 1096),
                (-1493,  63, 1094),
                (-1491,  65, 1089),
                (-1490,  65, 1088),
                (-1490,  65, 1098),
                (-1490,  63, 1098),
                (-1493,  40, 1094),
                (-1490,  42, 1098),
                (-1462, 140, 1104),
                (-1488,  65, 1098),
                (-1487,  65, 1098),
                (-1486,  63, 1098),
                (-1455, 104, 1178),
            ),
        },{
            "name":"r1bonus",
            "size":(288, 93, 368),
            "region":{"x":-3, "z":3},
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(18, 4), "materialName":"oak leaves"},
            ),
        },{
            "name":"roguelike",
            "size":(464, 101, 464),
            "region":{"x":-2, "z":-1},
            "numDungeons":400,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(213, 0), "materialName":"magma block"},
            ),
            "generateMaps":{"offset":{"x":320, "z":320}},
        },{
            "name":"nightmare",
            "size":(382, 255, 476),
            "region":{"x":-3, "z":4},
            "numDungeons":50,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(214, 0), "materialName":"nether wart block"},
            ),
            "chestWhitelist":(
                (-1341, 128, 2154),
                (-1358,  59, 2306),
                (-1453,  51, 2295),
                (-1261,  49, 2416),
                (-1450, 103, 2318),
                (-1393,  41, 2312),
                (-1265,  90, 2337),
                (-1358,  59, 2329),
                (-1307,   3, 2170),
                (-1332, 120, 2411),
                (-1304,  59, 2246),
                (-1280,  77, 2177),
                (-1280,  77, 2176),
            ),
        },{
            "name":"tutorial",
            "size":(80, 72, 96),
            "region":{"x":-2, "z":0},
            "numDungeons":200,
            "coordinatesToFill":(
                {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
                    "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
                {"name":"Indicator", "pos1":(-1450, 232, -1503), "pos2":(-1450, 232, -1503),
                    "replaceBlocks":True, "material":(133, 0), "materialName":"emerald block"},
            ),
            "chestWhitelist":(),
        },
    ),

    # If using only one item, ALWAYS use a trailing comma.
    # Possible values: "chest" (trapped chest shares ID), "dispenser", "dropper", "shulker_box", "hopper"
    # These are actually namespaced; default is "minecraft:*" in this code.
    "tileEntitiesToCheck":("chest",),

    # 16 chunks of void-biome padding on the -x and -z sides
    "voidPadding":16,

    # Dungeons placed in region -3,-2 - a region is 32x32 chunks
    "targetRegion":{"x":-3, "z":-2},
}

################################################################################
gen_dungeon_instances(config)

