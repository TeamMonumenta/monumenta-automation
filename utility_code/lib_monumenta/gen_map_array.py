#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import numpy

# Import pymclevel from MCLevel-Unified
from pymclevel import nbt

# For fillColor:
#   Find the number in this table, multiply by 4, add 1.
#   https://minecraft.gamepedia.com/Map_item_format#Base_colors
def gen_map_array(dataDir, count, startX, startZ, dX, dZ, fillColor = 117):

    idCounts = nbt.TAG_Compound()
    idCounts['map'] = nbt.TAG_Short(count - 1)
    idCounts.save(dataDir+"idcounts.dat",compressed=False)

    baseMap = nbt.json_to_tag(u'{data:{unlimitedTracking:0b,trackingPosition:1b,width:128s,scale:1b,dimension:0b,height:128s}}')
    mapColors = nbt.TAG_Byte_Array( numpy.full( 128*128, fillColor, dtype=numpy.dtype('uint8') ) )
    baseMapJson = baseMap.json()

    for mapID in range(0, count):
        thisMap = nbt.json_to_tag(baseMapJson)
        thisMap['data']['xCenter'] = nbt.TAG_Int( mapID * dX + startX )
        thisMap['data']['zCenter'] = nbt.TAG_Int( mapID * dZ + startZ )
        thisMap['data']['colors'] = mapColors
        thisMap.save(dataDir+"map_"+str(mapID)+".dat")
