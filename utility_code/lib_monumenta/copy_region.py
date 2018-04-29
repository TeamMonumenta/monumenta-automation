#!/usr/bin/env python2.7
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

def copyRegion(dirSrc,dirDst,rxSrc,rzSrc,rxDst,rzDst):
    """
    copy the old region file {dirSrc}/r.{rxSrc}.{rzSrc}.mca
    to the new region file {dirDst}/r.{rxDst}.{rzDst}.mca

    Also Fixes entity positions after copying.
    """
    if dirSrc[-1] != '/':
        dirSrc = dirSrc + '/'
    regionPathSrc = "{}r.{}.{}.mca".format(dirSrc,rxSrc,rzSrc)

    if dirDst[-1] != '/':
        dirDst = dirDst + '/'
    regionPathDst = "{}r.{}.{}.mca".format(dirDst,rxDst,rzDst)

    dx = 512 * ( rxDst - rxSrc )
    dz = 512 * ( rzDst - rzSrc )
    onMatchArgs = (dx,dz)

    if not copyFile(regionPathSrc,regionPathDst):
        print "*** Region not copied; not edited destination file"
        return False
    region = regionfile.MCRegionFile(regionPathDst,(rxDst,rzDst))
    entityIter = IterEntities(["entities","block entities","tile ticks","search spawners"],_fixEntity,onMatchArgs)
    for index, offset in enumerate(region.offsets):
        if offset:
            cx = index & 0x1f
            cz = index >> 5
            cx += rxDst << 5
            cz += rzDst << 5

            data = region.readChunk(cx, cz)
            chunkTag = nbt.load(buf=data)
            chunkTag['Level']['xPos'].value = cx
            chunkTag['Level']['zPos'].value = cz
            entityIter.InChunkTag(chunkTag)
            data = chunkTag.save(compressed=False)
            region.saveChunk(cx, cz, data) # saves region file too
    region.close()
    return True

def _fixEntity(onMatchArgs,entityDetails):
    dx,dz = onMatchArgs
    entity = entityDetails["entity"]

    if "Pos" in entity:
        entity["Pos"][0].value += dx
        entity["Pos"][2].value += dz
    if "x" in entity:
        entity["x"].value += dx
        entity["z"].value += dz
    if "TileX" in entity:
        # Painting/item frame
        entity["TileX"].value += dx
        entity["TileZ"].value += dz
    if "BeamTarget" in entity and "X" in entity["BeamTarget"]:
        entity["BeamTarget"]["X"] += dx
        entity["BeamTarget"]["Z"] += dz
    if "ExitPortal" in entity and "X" in entity["ExitPortal"]:
        entity["ExitPortal"]["X"] += dx
        entity["ExitPortal"]["Z"] += dz

    if "UUIDMost" in entity:
        newUUID = mcUUID()
        UUIDMost, UUIDLeast = newUUID.asTuple()
        if UUIDMost >= 2**63:
            UUIDMost -= 2**64
        if UUIDLeast >= 2**63:
            UUIDLeast -= 2**64
        entity["UUIDMost"].value  = UUIDMost
        entity["UUIDLeast"].value = UUIDLeast

