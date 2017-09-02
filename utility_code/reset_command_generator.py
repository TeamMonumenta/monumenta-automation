#!/usr/bin/python

print "load"
print "/home/rock/tmp/region_1_beta_old/Project_Epic"

region_dir = "/home/rock/tmp/regions"
regions = [
        ("Apartments_buying_room",  -809,   99,    47,     -874,   96,     4,      "41:0",     "gold"),
        ("Apartments_units",        -817,   113,    87,     -859,   164,    16,     "41:0",     "gold"),
        ("Plot_Pressure_Plates",    -719,   106,    -118,   -665,   106,    -74,    "41:0",     "gold"),
        ("Guild_Room",              -800,   109,    -75,    -758,   104,    -102,   "41:0",     "gold"),
        ("Section_1",               -1120,  0,      -267,   -897,   255,    318,    "41:0",     "gold"),
        ("Section_2",               -896,   0,      208,    -512,   255,    318,    "57:0",     "diamond"),
        ("Section_3",               -896,   0,      207,    -788,   255,    119,    "42:0",     "iron"),
        ("Section_4",               -896,   0,      -267,   -825,   255,    -28,    "22:0",     "lapis"),
        ("Section_5",               -512,   0,      207,    -640,   255,    -273,   "24:0",     "sandstone"),
        ("Section_6",               -824,   0,      -169,   -641,   255,    -272,   "152:0",    "redstone"),
        ("Section_7",               -641,   0,      -168,   -677,   255,    -132,   "155:0",    "quartz"),
        ("Section_8",               -774,   0,      -168,   -813,   255,    -150,   "17:14",    "birch wood"),
        ("Section_9",               -641,   0,      -25,    -655,   255,    -52,    "17:15",    "jungle wood"),
        ("Section_10",              -680,   0,      183,    -641,   255,    207,    "19:0",     "sponge"),
        ("Section_11",              -668,   0,      -14,    -641,   255,    25,     "1:1",      "granite"),
        #("Ugly_Market",             -399,   95,     -108,   -497,   255,    -206,   "1:5",      "andesite"),
        #("Lowtide",                 672,    60,     416,    751,    255,    517,    "1:3",      "diorite"),
    ]

for name, x1, y1, z1, x2, y2, z2, blockid, block in regions:
    xmin = min(x1, x2)
    xmax = max(x1, x2)
    ymin = min(y1, y2)
    ymax = max(y1, y2)
    zmin = min(z1, z2)
    zmax = max(z1, z2)
    xsize = xmax - xmin + 1
    ysize = ymax - ymin + 1
    zsize = zmax - zmin + 1

    min_point = "(" + str(xmin) + ", " + str(ymin) + ", " + str(zmin) + ")"
    box_size = "(" + str(xsize) + ", " + str(ysize) + ", " + str(zsize) + ")"
    box = min_point + ", " + box_size

    #print "fill " + blockid + " " + box
    print "export " + region_dir + "/" + name + " " + box

print "quit"
print "n"

print
################################################################################
print

print "load"
print "/home/rock/tmp/region_1/Project_Epic"
for name, x1, y1, z1, x2, y2, z2, blockid, block in regions:
    xmin = min(x1, x2)
    xmax = max(x1, x2)
    ymin = min(y1, y2)
    ymax = max(y1, y2)
    zmin = min(z1, z2)
    zmax = max(z1, z2)
    xsize = xmax - xmin + 1
    ysize = ymax - ymin + 1
    zsize = zmax - zmin + 1

    min_point = "(" + str(xmin) + ", " + str(ymin) + ", " + str(zmin) + ")"
    box_size = "(" + str(xsize) + ", " + str(ysize) + ", " + str(zsize) + ")"
    box = min_point + ", " + box_size

    print "removeEntities " + box
    print "import " + region_dir + "/" + name + " " + min_point

print "fill 0:0 (-1441, 2, -1441), (1, 1, 1)"
print "save"
print "quit"
print "n"

print
