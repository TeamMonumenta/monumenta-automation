#!/usr/bin/env python3

import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.nbt import RegionFile

from lib_py3.common import copy_file

def copy_region(dir_src,dir_dst,rx_src,rz_src,rx_dst,rz_dst,item_replacements=None,entity_updates=None):
    """
    copy the old region file {dir_src}/r.{rx_src}.{rz_src}.mca
    to the new region file {dir_dst}/r.{rx_dst}.{rz_dst}.mca

    Also Fixes entity positions after copying.
    """
    region_path_src = os.path.join(dir_src,"r.{}.{}.mca".format(rx_src,rz_src))
    region_path_dst = os.path.join(dir_dst,"r.{}.{}.mca".format(rx_dst,rz_dst))
    dx = ( rx_dst - rx_src ) << 9
    dz = ( rz_dst - rz_src ) << 9
    dpos = (dx,dz)

    if not copy_file(region_path_src,region_path_dst):
        print("*** Region not copied; not editing destination file")
        return False

    with RegionFile(region_path_dst) as region:
        for cz in range(32):
            for cx in range(32):
                try:
                    # May not exist; skip if missing
                    chunk = region.load_chunk(cx, cz)

                    chunk.body.at_path('Level.xPos').value += dx >> 4
                    chunk.body.at_path('Level.zPos').value += dz >> 4

                    try:
                        # May not exist; skip if missing
                        entities = chunk.body.at_path('Level.Entities').value
                        for entity in entities:
                            _fixEntity(dpos,{"entity":entity})
                    except:
                        pass

                    try:
                        # May not exist; skip if missing
                        block_entities = chunk.body.at_path('Level.TileEntities').value
                        for block_entity in block_entities:
                            _fixEntity(dpos,{"entity":block_entity})
                    except:
                        pass

                    try:
                        # May not exist; skip if missing
                        tile_ticks = chunk.body.at_path('Level.TileTicks').value
                        for tile_tick in tile_ticks:
                            _fixEntity(dpos,{"entity":tile_tick})
                    except:
                        pass

                    try:
                        # May not exist; skip if missing
                        liquid_ticks = chunk.body.at_path('Level.LiquidTicks').value
                        for liquid_tick in liquid_ticks:
                            _fixEntity(dpos,{"entity":liquid_tick})
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
        new_uuid = uuid.uuid4()
        uuid_most, uuid_least = ( int(new_uuid)>>64, int(new_uuid) & ((1<<64)-1) )
        if uuid_most >= 2**63:
            uuid_most -= 2**64
        if uuid_least >= 2**63:
            uuid_least -= 2**64
        entity.value["UUIDMost"].value  = uuid_most
        entity.value["UUIDLeast"].value = uuid_least

