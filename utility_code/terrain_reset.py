#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).
"""

from lib_monumenta.terrain_reset import terrainReset
import item_replace_list

itemCountLog = "/home/rock/tmp/all_items.txt"

configList = [{
    "server":"region_1",

    # Dst is the destination world, which gets overwritten by the build world.
    # Then, data from the main world replaces the relevant parts of the dst world.
    # Please note that no special care need be taken with whitespace in filenames.
    "localMainFolder":"/home/rock/tmp/PRE_RESET/region_1/Project_Epic-region_1/",
    "localBuildFolder":"/home/rock/project_epic/region_1/Project_Epic-region_1/",
    "localDstFolder":"/home/rock/tmp/POST_RESET/region_1/Project_Epic-region_1/",

    # (x,y,z,ry,rx)
    "safetyTpLocation":(-1450, 241, -1498, 270.0, 0.0),

    "coordinatesToFill":(
        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
            "replaceBlocks":True, "material":(0, 0), "materialName":"air"},
    ),

    "resetRegionalDifficulty":True,

    # Which folder to copy the base world from. Either "build", "main", or not set
    "copyBaseFrom":"build",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],

    # If this is set to True, instead of copying the coordinates from the Main server
    # it treats them as additional coordinatesToFill instead, filling those regions
    # so that their positions can be easily checked in-game
    #"coordinatesDebug":True,

    # List of places where block replacements should be run - options are "world", "schematics"
    "blockReplacements":item_replace_list.blockReplacements,
    "blockReplaceLocations":["schematics",],

    # List of places where item replacements should be run - options are "players", "world", "schematics"
    "itemReplacements":item_replace_list.itemReplacements,
    "itemReplaceLocations":["players", "schematics",],

    "coordinatesToCopy":(
        # "name":"a unique name"
        # "pos1":(x1,y1,z1)
        # "pos2":(x2,y2,z2)
        # "replaceBlocks":True/False
        # "replaceItems":True/False
        # "material":(id,dmg) # what to fill with
        # "materialName":"block name" # comment
        {"name":"Apartments_100",         "pos1":( -874,  99,   44), "pos2":(-809,  96,   44), "replaceBlocks":False, "replaceItems":False,  "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_200",         "pos1":( -874,  99,   36), "pos2":(-809,  96,   36), "replaceBlocks":False, "replaceItems":False,  "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_300",         "pos1":( -874,  99,   31), "pos2":(-809,  96,   31), "replaceBlocks":False, "replaceItems":False,  "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_400",         "pos1":( -874,  99,   23), "pos2":(-809,  96,   23), "replaceBlocks":False, "replaceItems":False,  "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_500",         "pos1":( -864,  99,   23), "pos2":(-813,  96,   23), "replaceBlocks":False, "replaceItems":False,  "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_600",         "pos1":( -864,  99,   23), "pos2":(-813,  96,   23), "replaceBlocks":False, "replaceItems":False,  "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_700_800",     "pos1":( -874,  99,   18), "pos2":(-809,  96,   18), "replaceBlocks":False, "replaceItems":False,  "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_units",       "pos1":( -817, 109,   87), "pos2":(-859, 164,   16), "replaceBlocks":False, "replaceItems":True,  "material":( 41,  0), "materialName":"gold"},
        {"name":"Guild_Room",             "pos1":( -800, 109,  -75), "pos2":(-758, 104, -102), "replaceBlocks":False, "replaceItems":False,  "material":( 41,  0), "materialName":"gold"},
        {"name":"Guild_1",                "pos1":( -586,   0,  137), "pos2":(-622, 255,  105), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_2",                "pos1":( -570,   0,  112), "pos2":(-534, 255,  154), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_3",                "pos1":( -581,   0,  150), "pos2":(-613, 255,  186), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_4",                "pos1":( -649,   0,  275), "pos2":(-617, 255,  311), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_5",                "pos1":( -683,   0,  275), "pos2":(-651, 255,  311), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_6",                "pos1":( -685,   0,  275), "pos2":(-717, 255,  311), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_7",                "pos1":( -816,   0,  235), "pos2":(-780, 255,  267), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_8",                "pos1":( -832,   0,  257), "pos2":(-868, 255,  289), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_9",                "pos1":( -816,   0,  269), "pos2":(-780, 255,  301), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_10",               "pos1":( -937,   0,  272), "pos2":(-969, 255,  308), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_11",               "pos1":( -969,   0,  256), "pos2":(-937, 255,  220), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_12",               "pos1":( -958,   0,  104), "pos2":(-994, 255,  136), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_13",               "pos1":( -942,   0,   93), "pos2":(-906, 255,  125), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_14",               "pos1":( -958,   0,   70), "pos2":(-994, 255,  102), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_15",               "pos1":( -920,   0,  -88), "pos2":(-952, 255,  -52), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_16",               "pos1":( -936,   0, -102), "pos2":(-900, 255, -134), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_17",               "pos1":( -955,   0, -106), "pos2":(-987, 255,  -70), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_18",               "pos1":( -954,   0, -120), "pos2":(-990, 255, -152), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_19",               "pos1":( -936,   0, -168), "pos2":(-900, 255, -136), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_20",               "pos1":( -751,   0, -230), "pos2":(-787, 255, -198), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_21",               "pos1":( -787,   0, -232), "pos2":(-751, 255, -264), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_22",               "pos1":( -600,   0, -191), "pos2":(-564, 255, -159), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_23",               "pos1":( -615,   0, -180), "pos2":(-651, 255, -212), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_24",               "pos1":( -564,   0, -192), "pos2":(-600, 255, -224), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_25",               "pos1":( -581,   0,  -64), "pos2":(-613, 255, -100), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_26",               "pos1":( -596,   0,  -46), "pos2":(-564, 255,  -10), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_27",               "pos1":( -548,   0,  -64), "pos2":(-580, 255, -100), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},

        # These are coordinates for the plots around the capital and are no longer needed, but kept just in case
        #{"name":"Plot_Pressure_Plates",   "pos1":( -719, 106, -118), "pos2":(-665, 106,  -74), "replaceBlocks":False, "replaceItems":True,  "material":( 41,  0), "materialName":"gold"},
        #{"name":"Section_1",              "pos1":(-1130,   0, -267), "pos2":(-897, 255,  318), "replaceBlocks":True,  "replaceItems":True,  "material":( 41,  0), "materialName":"gold"},
        #{"name":"Section_2",              "pos1":( -896,   0,  208), "pos2":(-512, 255,  318), "replaceBlocks":True,  "replaceItems":True,  "material":( 57,  0), "materialName":"diamond"},
        #{"name":"Section_3",              "pos1":( -896,   0,  207), "pos2":(-788, 255,  119), "replaceBlocks":True,  "replaceItems":True,  "material":( 42,  0), "materialName":"iron"},
        #{"name":"Section_4",              "pos1":( -896,   0, -267), "pos2":(-825, 255,  -28), "replaceBlocks":True,  "replaceItems":True,  "material":( 22,  0), "materialName":"lapis"},
        #{"name":"Section_5",              "pos1":( -512,   0,  207), "pos2":(-640, 255, -273), "replaceBlocks":True,  "replaceItems":True,  "material":( 24,  0), "materialName":"sandstone"},
        #{"name":"Section_6",              "pos1":( -824,   0, -169), "pos2":(-641, 255, -272), "replaceBlocks":True,  "replaceItems":True,  "material":(152,  0), "materialName":"redstone"},
        #{"name":"Section_7",              "pos1":( -641,   0, -168), "pos2":(-677, 255, -132), "replaceBlocks":True,  "replaceItems":True,  "material":(155,  0), "materialName":"quartz"},
        #{"name":"Section_8",              "pos1":( -774,   0, -168), "pos2":(-813, 255, -150), "replaceBlocks":True,  "replaceItems":True,  "material":( 17, 14), "materialName":"birch wood"},
        #{"name":"Section_9",              "pos1":( -641,   0,  -25), "pos2":(-655, 255,  -52), "replaceBlocks":True,  "replaceItems":True,  "material":( 17, 15), "materialName":"jungle wood"},
        #{"name":"Section_10",             "pos1":( -680,   0,  183), "pos2":(-641, 255,  207), "replaceBlocks":True,  "replaceItems":True,  "material":( 19,  0), "materialName":"sponge"},
        #{"name":"Section_11",             "pos1":( -668,   0,  -14), "pos2":(-641, 255,   25), "replaceBlocks":True,  "replaceItems":True,  "material":(  1,  1), "materialName":"granite"},
    ),
}, {
    "server":"betaplots",

    "localMainFolder":"/home/rock/tmp/PRE_RESET/betaplots/Project_Epic-betaplots/",
    "localDstFolder":"/home/rock/tmp/POST_RESET/betaplots/Project_Epic-betaplots/",

    "copyBaseFrom":"main",

    "blockReplacements":item_replace_list.blockReplacements,
    "blockReplaceLocations":["world",],
    "itemReplacements":item_replace_list.itemReplacements,
    "itemReplaceLocations":["players", "world",],
}, {
    "server":"r1plots",

    "localMainFolder":"/home/rock/tmp/PRE_RESET/r1plots/Project_Epic-r1plots/",
    "localDstFolder":"/home/rock/tmp/POST_RESET/r1plots/Project_Epic-r1plots/",

    "copyBaseFrom":"main",

    "blockReplacements":item_replace_list.blockReplacements,
    "blockReplaceLocations":["world",],
    "itemReplacements":item_replace_list.itemReplacements,
    "itemReplaceLocations":["players", "world",],
}, {
    "server":"white",
    "localMainFolder":"/home/rock/tmp/PRE_RESET/white/Project_Epic-white/",
    "localDstFolder":"/home/rock/tmp/POST_RESET/white/Project_Epic-white/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],
    "safetyTpLocation":(-1450, 241, -1498, 270.0, 0.0),
    "itemReplacements":item_replace_list.itemReplacements,
    "itemReplaceLocations":["players"],
}, {
    "server":"orange",
    "localMainFolder":"/home/rock/tmp/PRE_RESET/orange/Project_Epic-orange/",
    "localDstFolder":"/home/rock/tmp/POST_RESET/orange/Project_Epic-orange/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],
    "safetyTpLocation":(-1450, 241, -1498, 270.0, 0.0),
    "itemReplacements":item_replace_list.itemReplacements,
    "itemReplaceLocations":["players"],
}, {
    "server":"magenta",
    "localMainFolder":"/home/rock/tmp/PRE_RESET/magenta/Project_Epic-magenta/",
    "localDstFolder":"/home/rock/tmp/POST_RESET/magenta/Project_Epic-magenta/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],
    "safetyTpLocation":(-1450, 241, -1498, 270.0, 0.0),
    "itemReplacements":item_replace_list.itemReplacements,
    "itemReplaceLocations":["players"],
}, {
    "server":"lightblue",
    "localMainFolder":"/home/rock/tmp/PRE_RESET/lightblue/Project_Epic-lightblue/",
    "localDstFolder":"/home/rock/tmp/POST_RESET/lightblue/Project_Epic-lightblue/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],
    "safetyTpLocation":(-1450, 241, -1498, 270.0, 0.0),
    "itemReplacements":item_replace_list.itemReplacements,
    "itemReplaceLocations":["players"],
}, {
    "server":"yellow",
    "localMainFolder":"/home/rock/tmp/PRE_RESET/yellow/Project_Epic-yellow/",
    "localDstFolder":"/home/rock/tmp/POST_RESET/yellow/Project_Epic-yellow/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],
    "safetyTpLocation":(-1450, 241, -1498, 270.0, 0.0),
    "itemReplacements":item_replace_list.itemReplacements,
    "itemReplaceLocations":["players"],
}, {
    "server":"r1bonus",
    "localMainFolder":"/home/rock/tmp/PRE_RESET/r1bonus/Project_Epic-r1bonus/",
    "localDstFolder":"/home/rock/tmp/POST_RESET/r1bonus/Project_Epic-r1bonus/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],
    "safetyTpLocation":(-1450, 241, -1498, 270.0, 0.0),
    "itemReplacements":item_replace_list.itemReplacements,
    "itemReplaceLocations":["players"],
}]

terrainReset(configList)
print "Saving items found after replacement to {}".format(itemCountLog)
# Save this for when the item count stuff is working
#item_replace_list.itemReplacements.SaveGlobalLog(itemCountLog)
print "Remember that tutorial, purgatory, bungee, and build are not handled by this script"

