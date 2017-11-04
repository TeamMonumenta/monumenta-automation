#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).
"""

from lib_terrain_reset import terrainReset

config = {
    # Dst is the destination world, which gets overwritten by the build world.
    # Then, data from the main world replaces the relevant parts of the dst world.
    # Please note that no special care need be taken with whitespace in filenames.
    "localMainFolder":"/home/rock/tmp/PRE_RESET/region_1/Project_Epic-region_1/",
    "localBuildFolder":"/home/rock/project_epic/region_1/Project_Epic-region_1/",
    "localDstFolder":"/home/rock/tmp/POST_RESET/region_1/Project_Epic-region_1/",

    # No 0.5 offset here, add it yourself if you like.
    # (x,y,z,ry,rx)
    "safetyTpLocation":(-1450, 241, -1498, 270.0, 0.0),

    "coordinatesToFill":(
        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
            "replace":True, "material":(0, 0), "materialName":"air"},
    ),

    # If this is set to True, instead of copying the coordinates from the Main server
    # it treats them as additional coordinatesToFill instead, filling those regions
    # so that their positions can be easily checked in-game
    "coordinatesDebug":False,

    "coordinatesToCopy":(
        # ("a unique name",        (lowerCoordinate),  (upperCoordinate), replaceBlocks, ( id, dmg), "block name (comment)"),
        {"name":"Apartments_100",         "pos1":( -874,  99,   44), "pos2":(-809,  96,   44), "replace":False, "material":( 41,  0), "materialName":"gold"),
        {"name":"Apartments_200",         "pos1":( -874,  99,   36), "pos2":(-809,  96,   36), "replace":False, "material":( 41,  0), "materialName":"gold"),
        {"name":"Apartments_300",         "pos1":( -874,  99,   31), "pos2":(-809,  96,   31), "replace":False, "material":( 41,  0), "materialName":"gold"),
        {"name":"Apartments_400",         "pos1":( -874,  99,   23), "pos2":(-809,  96,   23), "replace":False, "material":( 41,  0), "materialName":"gold"),
        {"name":"Apartments_500",         "pos1":( -864,  99,   23), "pos2":(-813,  96,   23), "replace":False, "material":( 41,  0), "materialName":"gold"),
        {"name":"Apartments_600",         "pos1":( -864,  99,   23), "pos2":(-813,  96,   23), "replace":False, "material":( 41,  0), "materialName":"gold"),
        {"name":"Apartments_700_800",     "pos1":( -874,  99,   18), "pos2":(-809,  96,   18), "replace":False, "material":( 41,  0), "materialName":"gold"),
        {"name":"Apartments_units",       "pos1":( -817, 109,   87), "pos2":(-859, 164,   16), "replace":False, "material":( 41,  0), "materialName":"gold"),
        {"name":"Guild_Room",             "pos1":( -800, 109,  -75), "pos2":(-758, 104, -102), "replace":False, "material":( 41,  0), "materialName":"gold"),
        {"name":"Guild_1",                "pos1":( -586,   0,  137), "pos2":(-622, 255,  105), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_2",                "pos1":( -570,   0,  112), "pos2":(-534, 255,  154), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_3",                "pos1":( -581,   0,  150), "pos2":(-613, 255,  186), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_4",                "pos1":( -649,   0,  275), "pos2":(-617, 255,  311), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_5",                "pos1":( -683,   0,  275), "pos2":(-651, 255,  311), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_6",                "pos1":( -685,   0,  275), "pos2":(-717, 255,  311), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_7",                "pos1":( -816,   0,  235), "pos2":(-780, 255,  267), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_8",                "pos1":( -832,   0,  257), "pos2":(-868, 255,  289), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_9",                "pos1":( -816,   0,  269), "pos2":(-780, 255,  301), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_10",               "pos1":( -937,   0,  272), "pos2":(-969, 255,  308), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_11",               "pos1":( -969,   0,  256), "pos2":(-937, 255,  220), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_12",               "pos1":( -958,   0,  104), "pos2":(-994, 255,  136), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_13",               "pos1":( -942,   0,   93), "pos2":(-906, 255,  125), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_14",               "pos1":( -958,   0,   70), "pos2":(-994, 255,  102), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_15",               "pos1":( -920,   0,  -88), "pos2":(-952, 255,  -52), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_16",               "pos1":( -936,   0, -102), "pos2":(-900, 255, -134), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_17",               "pos1":( -955,   0, -106), "pos2":(-987, 255,  -70), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_18",               "pos1":( -954,   0, -120), "pos2":(-990, 255, -152), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_19",               "pos1":( -936,   0, -168), "pos2":(-900, 255, -136), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_20",               "pos1":( -751,   0, -230), "pos2":(-787, 255, -198), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_21",               "pos1":( -787,   0, -232), "pos2":(-751, 255, -264), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_22",               "pos1":( -600,   0, -191), "pos2":(-564, 255, -159), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_23",               "pos1":( -615,   0, -180), "pos2":(-651, 255, -212), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_24",               "pos1":( -564,   0, -192), "pos2":(-600, 255, -224), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_25",               "pos1":( -581,   0,  -64), "pos2":(-613, 255, -100), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_26",               "pos1":( -596,   0,  -46), "pos2":(-564, 255,  -10), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        {"name":"Guild_27",               "pos1":( -548,   0,  -64), "pos2":(-580, 255, -100), "replace":True,  "material":( 19,  0), "materialName":"sponge"),

        # These are coordinates for the plots around the capital and are no longer needed, but kept just in case
        #{"name":"Plot_Pressure_Plates",   "pos1":( -719, 106, -118), "pos2":(-665, 106,  -74), "replace":False, "material":( 41,  0), "materialName":"gold"),
        #{"name":"Section_1",              "pos1":(-1130,   0, -267), "pos2":(-897, 255,  318), "replace":True,  "material":( 41,  0), "materialName":"gold"),
        #{"name":"Section_2",              "pos1":( -896,   0,  208), "pos2":(-512, 255,  318), "replace":True,  "material":( 57,  0), "materialName":"diamond"),
        #{"name":"Section_3",              "pos1":( -896,   0,  207), "pos2":(-788, 255,  119), "replace":True,  "material":( 42,  0), "materialName":"iron"),
        #{"name":"Section_4",              "pos1":( -896,   0, -267), "pos2":(-825, 255,  -28), "replace":True,  "material":( 22,  0), "materialName":"lapis"),
        #{"name":"Section_5",              "pos1":( -512,   0,  207), "pos2":(-640, 255, -273), "replace":True,  "material":( 24,  0), "materialName":"sandstone"),
        #{"name":"Section_6",              "pos1":( -824,   0, -169), "pos2":(-641, 255, -272), "replace":True,  "material":(152,  0), "materialName":"redstone"),
        #{"name":"Section_7",              "pos1":( -641,   0, -168), "pos2":(-677, 255, -132), "replace":True,  "material":(155,  0), "materialName":"quartz"),
        #{"name":"Section_8",              "pos1":( -774,   0, -168), "pos2":(-813, 255, -150), "replace":True,  "material":( 17, 14), "materialName":"birch wood"),
        #{"name":"Section_9",              "pos1":( -641,   0,  -25), "pos2":(-655, 255,  -52), "replace":True,  "material":( 17, 15), "materialName":"jungle wood"),
        #{"name":"Section_10",             "pos1":( -680,   0,  183), "pos2":(-641, 255,  207), "replace":True,  "material":( 19,  0), "materialName":"sponge"),
        #{"name":"Section_11",             "pos1":( -668,   0,  -14), "pos2":(-641, 255,   25), "replace":True,  "material":(  1,  1), "materialName":"granite"),
    ),
}

terrainReset(config)

