#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import numpy

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
from pymclevel import nbt

# This is the whole config
dataDir = "/home/rock/tmp/dungeons-out/roguelike/Project_Epic-roguelike/data/"
maxID = 400

startX = -3 * 512 + 320
startZ = -2 * 512 + 320

dX = 0
dZ = 512

# Find the number in this table, multiply by 4, add 1.
# https://minecraft.gamepedia.com/Map_item_format#Base_colors
fillColor = 117
# End of config

idCounts = nbt.TAG_Compound()
idCounts['map'] = nbt.TAG_Short(maxID-1)
idCounts.save(dataDir+"idcounts.dat",compressed=False)

baseMap = nbt.json_to_tag(u'{data:{unlimitedTracking:0b,trackingPosition:1b,width:128s,scale:1b,dimension:0b,height:128s}}')
mapColors = nbt.TAG_Byte_Array( numpy.full( 128*128, fillColor, dtype=numpy.dtype('uint8') ) )
baseMapJson = baseMap.json()

for mapID in range(0,maxID):
    thisMap = nbt.json_to_tag(baseMapJson)
    thisMap['data']['xCenter'] = nbt.TAG_Int( mapID * dX + startX )
    thisMap['data']['zCenter'] = nbt.TAG_Int( mapID * dZ + startZ )
    thisMap['data']['colors'] = mapColors
    thisMap.save(dataDir+"map_"+str(mapID)+".dat")

