#!/usr/bin/env python3

import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.nbt import RegionFile

from lib_py3.common import copyFile

def copyRegion(dirSrc,dirDst,rxSrc,rzSrc,rxDst,rzDst,itemReplacements=None,entityUpdates=None):
    """
    copy the old region file {dirSrc}/r.{rxSrc}.{rzSrc}.mca
    to the new region file {dirDst}/r.{rxDst}.{rzDst}.mca

    Also Fixes entity positions after copying.
    """
    regionPathSrc = os.path.join(dirSrc,"r.{}.{}.mca".format(rxSrc,rzSrc))
    regionPathDst = os.path.join(dirDst,"r.{}.{}.mca".format(rxDst,rzDst))
    dx = ( rxDst - rxSrc ) << 9
    dz = ( rzDst - rzSrc ) << 9
    dPos = (dx,dz)

    if not copyFile(regionPathSrc,regionPathDst):
        print("*** Region not copied; not editing destination file")
        return False

    with RegionFile(regionPathDst) as region:
        for cz in range(32):
            for cx in range(32):
                try:
                    # May not exist; skip if missing
                    chunk = region.load_chunk(cx, cz)

                    chunk.body.at_path('Level.xPos').value += dx >> 4
                    chunk.body.at_path('Level.zPos').value += dz >> 4

                    try:
                        # May not exist; skip if missing
                        Entities = chunk.body.at_path('Level.Entities').value
                        for entity in Entities:
                            _fixEntity(dPos,{"entity":entity})
                    except:
                        pass

                    try:
                        # May not exist; skip if missing
                        TileEntities = chunk.body.at_path('Level.TileEntities').value
                        for tileEntity in TileEntities:
                            _fixEntity(dPos,{"entity":tileEntity})
                    except:
                        pass

                    try:
                        # May not exist; skip if missing
                        TileTicks = chunk.body.at_path('Level.TileTicks').value
                        for tileTick in TileTicks:
                            _fixEntity(dPos,{"entity":tileTick})
                    except:
                        pass

                    try:
                        # May not exist; skip if missing
                        LiquidTicks = chunk.body.at_path('Level.LiquidTicks').value
                        for LiquidTick in LiquidTicks:
                            _fixEntity(dPos,{"entity":LiquidTick})
                    except:
                        pass

                    region.save_chunk(chunk)
                except:
                    pass
    return True

def _fixEntity(onMatchArgs,entityDetails):
    dx,dz = onMatchArgs
    entity = entityDetails["entity"]

    if "Pos" in entity.value:
        entity.at_path("Pos[0]").value += dx
        entity.at_path("Pos[2]").value += dz
    if "x" in entity.value:
        entity.at_path("x").value += dx
        entity.at_path("z").value += dz
    if "TileX" in entity.value:
        # Painting/item frame
        entity.at_path("TileX").value += dx
        entity.at_path("TileZ").value += dz
    if "BeamTarget" in entity.value:
        entity.at_path("BeamTarget.X").value += dx
        entity.at_path("BeamTarget.Z").value += dz
    if "ExitPortal" in entity.value:
        entity.at_path("ExitPortal.X").value += dx
        entity.at_path("ExitPortal.Z").value += dz
    if "TreasurePosX" in entity.value:
        entity.at_path("TreasurePosX").value += dx
        entity.at_path("TreasurePosZ").value += dz
    if "AX" in entity.value:
        entity.at_path("AX").value += dx
        entity.at_path("AZ").value += dz
    if "APX" in entity.value:
        entity.at_path("APX").value += dx
        entity.at_path("APZ").value += dz
    if "HomePosX" in entity.value:
        entity.at_path("HomePosX").value += dx
        entity.at_path("HomePosZ").value += dz
    if "TravelPosX" in entity.value:
        entity.at_path("TravelPosX").value += dx
        entity.at_path("TravelPosZ").value += dz
    if "BoundX" in entity.value:
        entity.at_path("BoundX").value += dx
        entity.at_path("BoundZ").value += dz
    if "xTile" in entity.value:
        entity.at_path("xTile").value += dx
        entity.at_path("zTile").value += dz

    if "UUIDMost" in entity.value:
        newUUID = uuid.uuid4()
        UUIDMost, UUIDLeast = ( int(newUUID)>>64, int(newUUID) & ((1<<64)-1) )
        if UUIDMost >= 2**63:
            UUIDMost -= 2**64
        if UUIDLeast >= 2**63:
            UUIDLeast -= 2**64
        entity.value["UUIDMost"].value  = UUIDMost
        entity.value["UUIDLeast"].value = UUIDLeast

