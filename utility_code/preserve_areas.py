#!/usr/bin/env python3

import os

from lib_py3.world import World

################################################################################
# Roll back player.dat, player's advancement file, player's stats, and scores
# When: Week of Nov 10 - Nov 17
# Reason: stealing from the market
# IGN: BlackCat_FH
# UUID: dd428d17-ae23-4e3e-b0ff-0a56e2deda43

nov17_r1plots_rollback = (
        {"name":"shop plot A",               "pos1":(-2760,  76,  831), "pos2":(-2751,  80,  820), "replaceBlocks":False, "replaceItems":False, "updateEntities":False, "material":( 41,  0), "materialName":"gold"},
        {"name":"shop plot B",               "pos1":(-2764,  76,  784), "pos2":(-2773,  85,  790), "replaceBlocks":False, "replaceItems":False, "updateEntities":False, "material":( 41,  0), "materialName":"gold"},
        {"name":"shop plot C",               "pos1":( -811,  99,   31), "pos2":( -873,  99,   31), "replaceBlocks":False, "replaceItems":False, "updateEntities":False, "material":( 41,  0), "materialName":"gold"},
        {"name":"BlackCat_FH's player plot", "pos1":(-2641,  48,  210), "pos2":(-2617,  98,  228), "replaceBlocks":False, "replaceItems":False, "updateEntities":False, "material":( 41,  0), "materialName":"gold"},
)

coordinatesToCopy = (
        # "name":"a unique name"
        # "pos1":(x1,y1,z1)
        # "pos2":(x2,y2,z2)
        # "replaceBlocks":True/False - Not updated
        # "replaceItems":True/False - Not updated
        # "material":(id,dmg) # what to fill with - Not updated
        # "materialName":"block name" # comment
        {"name":"Apartments_101-132",     "pos1":( -811,  99,   44), "pos2":(-873,  99,   44), "replaceBlocks":False, "replaceItems":False, "updateEntities":False, "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_201-232",     "pos1":( -811,  99,   36), "pos2":(-873,  99,   36), "replaceBlocks":False, "replaceItems":False, "updateEntities":False, "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_301-332",     "pos1":( -811,  99,   31), "pos2":(-873,  99,   31), "replaceBlocks":False, "replaceItems":False, "updateEntities":False, "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_401-432",     "pos1":( -811,  99,   23), "pos2":(-873,  99,   23), "replaceBlocks":False, "replaceItems":False, "updateEntities":False, "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_501-524",     "pos1":( -815,  99,   10), "pos2":(-861,  99,   10), "replaceBlocks":False, "replaceItems":False, "updateEntities":False, "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_601-624",     "pos1":( -815,  99,    5), "pos2":(-861,  99,    5), "replaceBlocks":False, "replaceItems":False, "updateEntities":False, "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_701-816",     "pos1":( -811,  99,   18), "pos2":(-873,  99,   18), "replaceBlocks":False, "replaceItems":False, "updateEntities":False, "material":( 41,  0), "materialName":"gold"},
        {"name":"Apartments_units",       "pos1":( -817, 109,   87), "pos2":(-859, 164,   16), "replaceBlocks":False, "replaceItems":True,  "updateEntities":True,  "material":( 41,  0), "materialName":"gold"},
        {"name":"Guild_Room",             "pos1":( -800, 109,  -75), "pos2":(-758, 104, -102), "replaceBlocks":False, "replaceItems":False, "updateEntities":False, "material":( 41,  0), "materialName":"gold"},
        {"name":"Guild_1",                "pos1":( -586,   0,  137), "pos2":(-622, 255,  105), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_2",                "pos1":( -570,   0,  112), "pos2":(-534, 255,  154), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_3",                "pos1":( -581,   0,  150), "pos2":(-613, 255,  186), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_4",                "pos1":( -649,   0,  275), "pos2":(-617, 255,  311), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_5",                "pos1":( -683,   0,  275), "pos2":(-651, 255,  311), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_6",                "pos1":( -685,   0,  275), "pos2":(-717, 255,  311), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_7",                "pos1":( -816,   0,  235), "pos2":(-780, 255,  267), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_8",                "pos1":( -832,   0,  257), "pos2":(-868, 255,  289), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_9",                "pos1":( -816,   0,  269), "pos2":(-780, 255,  301), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_10",               "pos1":( -937,   0,  272), "pos2":(-969, 255,  308), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_11",               "pos1":( -969,   0,  256), "pos2":(-937, 255,  220), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_12",               "pos1":( -958,   0,  104), "pos2":(-994, 255,  136), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_14",               "pos1":( -958,   0,   70), "pos2":(-994, 255,  102), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_15",               "pos1":( -581,   0,  -64), "pos2":(-613, 255, -100), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_18",               "pos1":( -942,   0,   93), "pos2":(-906, 255,  125), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_20",               "pos1":( -751,   0, -230), "pos2":(-787, 255, -198), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_21",               "pos1":( -787,   0, -232), "pos2":(-751, 255, -264), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_22",               "pos1":( -600,   0, -191), "pos2":(-564, 255, -159), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_23",               "pos1":( -615,   0, -180), "pos2":(-651, 255, -212), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_24",               "pos1":( -564,   0, -192), "pos2":(-600, 255, -224), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_26",               "pos1":( -596,   0,  -46), "pos2":(-564, 255,  -10), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
        {"name":"Guild_27",               "pos1":( -548,   0,  -64), "pos2":(-580, 255, -100), "replaceBlocks":True,  "replaceItems":True,  "updateEntities":True,  "material":( 19,  0), "materialName":"sponge"},
)

outWorld = World('/home/rock/5_SCRATCH/reset/out')
playWorld = World('/home/rock/5_SCRATCH/reset/play')

for area in coordinatesToCopy:
    print( 'Starting on ' + area['name'] )
    outWorld.restore_area( area['pos1'], area['pos2'], playWorld )
    print( 'Done with ' + area['name'] )

