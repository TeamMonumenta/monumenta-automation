#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from lib_monumenta.common import copyFile
from lib_monumenta.iter_entity import IterEntities
from lib_monumenta.mcUUID import mcUUID

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
from pymclevel import nbt
from pymclevel import regionfile

def copyRegion(old,new,rx,rz):
    """
    copy the old region file "old"
    to the new region file "new",
    where both are full paths.

    rx and rz should be the
    numbers from new, like
    r.{rx}.{rz}.mca

    Also Fixes entity positions
    after copying.
    """
    copyFile(old,new)
    region = regionfile.MCRegionFile(new,(rx,rz))
    entityIter = IterEntities(["entities","block entities","tile ticks","search spawners"],_fixEntity,None)
    for index, offset in enumerate(region.offsets):
        if offset:
            cx = index & 0x1f
            cz = index >> 5
            cx += rx << 5
            cz += rz << 5

            data = region.readChunk(cx, cz)
            chunkTag = nbt.load(buf=data)
            chunkTag['Level']['xPos'].value = cx
            chunkTag['Level']['zPos'].value = cz
            entityIter.InChunkTag(chunkTag)
            data = chunkTag.save(compressed=False)
            region.saveChunk(cx, cz, data) # saves region file too
    region.close()

def _fixEntity(onMatchArgs,entityDetails):
    cx,cz = entityDetails["chunk pos"]
    entity = entityDetails["entity"]
    minx = cx << 4
    minz = cz << 4
    rx = minx - (minx % 512)
    rz = minz - (minz % 512)

    if "Pos" in entity:
        entity["Pos"][0].value = rx + (entity["Pos"][0].value % 512)
        entity["Pos"][2].value = rz + (entity["Pos"][2].value % 512)
    if "x" in entity:
        entity["x"].value = rx + (entity["x"].value % 512)
        entity["z"].value = rz + (entity["z"].value % 512)
    if "TileX" in entity:
        # Painting/item frame
        entity["TileX"].value = rx + (entity["TileX"].value % 512)
        entity["TileZ"].value = rz + (entity["TileZ"].value % 512)
    if "BeamTarget" in entity and "X" in entity["BeamTarget"]:
        # end crystal - not correct if we copy more than a 1x1 chunk!
        entity["BeamTarget"]["X"] = rx + (entity["BeamTarget"]["X"] % 512)
        entity["BeamTarget"]["Z"] = rz + (entity["BeamTarget"]["Z"] % 512)
    if "ExitPortal" in entity and "X" in entity["ExitPortal"]:
        # end portal gateway - not correct if we copy more than a 1x1 chunk!
        entity["ExitPortal"]["X"] = rx + (entity["ExitPortal"]["X"] % 512)
        entity["ExitPortal"]["Z"] = rz + (entity["ExitPortal"]["Z"] % 512)

    if "UUIDMost" in entity:
        entity["UUIDMost"].value, entity["UUIDLeast"].value = mcUUID.asTuple()
    

