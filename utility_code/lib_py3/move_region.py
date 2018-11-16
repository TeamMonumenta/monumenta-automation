#!/usr/bin/env python3

import os
import sys


sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.nbt import RegionFile

from lib_py3.common import move_file

def MoveRegion(dir_src,dir_dst,rx_src,rz_src,rx_dst,rz_dst,item_replacements=None,entity_updates=None):
    """
    move the old region file {dir_src}/r.{rx_src}.{rz_src}.mca
    to the new region file {dir_dst}/r.{rx_dst}.{rz_dst}.mca

    Also Fixes entity positions after copying.
    """
    region_path_src = os.path.join(dir_src,"r.{}.{}.mca".format(rx_src,rz_src))
    region_path_dst = os.path.join(dir_dst,"r.{}.{}.mca".format(rx_dst,rz_dst))
    dx = ( rx_dst - rx_src ) << 9
    dz = ( rz_dst - rz_src ) << 9
    dpos = (dx,dz)

    if not move_file(region_path_src,region_path_dst):
        print( "*** Could not move region {} to {}".format( repr( region_path_src ), repr( region_path_dst ) ) )
        return False

    try:
        region = RegionFile(region_path_dst)
    except:
        print( 'Could not load RegionFile({})'.format( repr( region_path_dst ) ) )
        return False

    for cz in range(32):
        for cx in range(32):
            try:
                chunk = region.load_chunk(cx, cz)
            except:
                # May not exist; skip if missing
                continue

            chunk.body.at_path('Level.xPos').value += dx >> 4
            chunk.body.at_path('Level.zPos').value += dz >> 4

            if chunk.body.has_path('Level.Entities'):
                # May not exist; skip if missing
                entities = chunk.body.at_path('Level.Entities').value
                for entity in entities:
                    _fixEntity(dpos,{"entity":entity})

            if chunk.body.has_path('Level.TileEntities'):
                # May not exist; skip if missing
                block_entities = chunk.body.at_path('Level.TileEntities').value
                for block_entity in block_entities:
                    _fixEntity(dpos,{"entity":block_entity})

            if chunk.body.has_path('Level.TileTicks'):
                # May not exist; skip if missing
                tile_ticks = chunk.body.at_path('Level.TileTicks').value
                for tile_tick in tile_ticks:
                    _fixEntity(dpos,{"entity":tile_tick})

            if chunk.body.has_path('Level.LiquidTicks'):
                # May not exist; skip if missing
                liquid_ticks = chunk.body.at_path('Level.LiquidTicks').value
                for liquid_tick in liquid_ticks:
                    _fixEntity(dpos,{"entity":liquid_tick})

            try:
                region.save_chunk(chunk)
            except:
                print( 'Error saving chunk ({},{}) RegionFile({})'.format( 32*rx+cx, 32*rz+cz, repr( region_path_dst ) ) )
                return False
    return True

def _fixEntity(onMatchArgs,entityDetails):
    dx,dz = onMatchArgs
    entity = entityDetails["entity"]

    if (
        entity.has_path("Pos[0]") and
        entity.has_path("Pos[2]")
    ):
        entity.at_path("Pos[0]").value += dx
        entity.at_path("Pos[2]").value += dz
    if (
        entity.has_path("x") and
        entity.has_path("z")
    ):
        entity.at_path("x").value += dx
        entity.at_path("z").value += dz
    if (
        entity.has_path("TileX") and
        entity.has_path("TileZ")
    ):
        # Painting/item frame
        entity.at_path("TileX").value += dx
        entity.at_path("TileZ").value += dz
    if (
        entity.has_path("BeamTarget.X") and
        entity.has_path("BeamTarget.Z")
    ):
        entity.at_path("BeamTarget.X").value += dx
        entity.at_path("BeamTarget.Z").value += dz
    if (
        entity.has_path("ExitPortal.X") and
        entity.has_path("ExitPortal.Z")
    ):
        entity.at_path("ExitPortal.X").value += dx
        entity.at_path("ExitPortal.Z").value += dz
    if (
        entity.has_path("TreasurePosX") and
        entity.has_path("TreasurePosZ")
    ):
        entity.at_path("TreasurePosX").value += dx
        entity.at_path("TreasurePosZ").value += dz
    if (
        entity.has_path("AX") and
        entity.has_path("AZ")
    ):
        entity.at_path("AX").value += dx
        entity.at_path("AZ").value += dz
    if (
        entity.has_path("APX") and
        entity.has_path("APZ")
    ):
        entity.at_path("APX").value += dx
        entity.at_path("APZ").value += dz
    if (
        entity.has_path("HomePosX") and
        entity.has_path("HomePosZ")
    ):
        entity.at_path("HomePosX").value += dx
        entity.at_path("HomePosZ").value += dz
    if (
        entity.has_path("TravelPosX") and
        entity.has_path("TravelPosZ")
    ):
        entity.at_path("TravelPosX").value += dx
        entity.at_path("TravelPosZ").value += dz
    if (
        entity.has_path("BoundX") and
        entity.has_path("BoundZ")
    ):
        entity.at_path("BoundX").value += dx
        entity.at_path("BoundZ").value += dz
    if (
        entity.has_path("xTile") and
        entity.has_path("zTile")
    ):
        entity.at_path("xTile").value += dx
        entity.at_path("zTile").value += dz

