#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from lib_monumenta.common import copyFile
from lib_monumenta.iter_entity import IterEntities

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
from pymclevel import nbt
from pymclevel import regionfile

def copyRegion(old,new,newRX,newRZ):
    """
    copy the old region file "old"
    to the new region file "new",
    where both are full paths.

    newRX and newRZ should be the
    numbers from new, like
    r.{newRX}.{newRZ}.mca

    Also Fixes entity positions
    after copying.
    """
    copyFile(old,new)
    region = regionfile.MCRegionFile(new,(newRX,newRZ))
    rx, rz = region.regionCoords
    regionCoords = [0,0]
    entityIter = IterEntities(["entities","block entities","tile ticks","search spawners"],_fixEntityCoordinates,regionCoords)
    for index, offset in enumerate(region.offsets):
        if offset:
            cx = index & 0x1f
            cz = index >> 5
            cx += rx << 5
            cz += rz << 5
            regionCoords[0] = cx
            regionCoords[1] = cz
            #try:
            data = region.readChunk(cx, cz)
            chunkTag = nbt.load(buf=data)
            entityIter.InChunkTag(chunkTag)
            data = chunkTag.save(compressed=False)
            region.saveChunk(cx, cz, data) # saves region file too
            """
            except Exception, e:
                sectorStart = offset >> 8
                sectorCount = offset & 0xff
                print "Unexpected chunk error at sector {sector} ({exc})".format(sector=sectorStart, exc=e)
            """
    region.close()

def _fixEntityCoordinates(onMatchArgs,entityDetails):
    cx = onMatchArgs[0]
    cz = onMatchArgs[1]
    entity = entityDetails["entity"]
    if "Pos" in entity:
        entity["Pos"][0].value = (cx << 4) + (entity["Pos"][0].value % 16)
        entity["Pos"][2].value = (cz << 4) + (entity["Pos"][2].value % 16)
    if "x" in entity:
        entity["x"].value = (cx << 4) + (entity["x"].value % 16)
        entity["z"].value = (cz << 4) + (entity["z"].value % 16)

