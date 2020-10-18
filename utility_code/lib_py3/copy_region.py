#!/usr/bin/env python3

import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.nbt import RegionFile

from lib_py3.common import copy_file, get_entity_uuid, uuid_to_mc_uuid_tag_int_array

def pop_if_present(entity, key):
    if key in entity.value:
        entity.value.pop(key)

def copy_region(dir_src, dir_dst, rx_src, rz_src, rx_dst, rz_dst, item_replacements=None, entity_updates=None):
    """
    copy the old region file {dir_src}/r.{rx_src}.{rz_src}.mca
    to the new region file {dir_dst}/r.{rx_dst}.{rz_dst}.mca

    Also Fixes entity positions after copying.
    """
    region_path_src = os.path.join(dir_src, f"r.{rx_src}.{rz_src}.mca")
    region_path_dst = os.path.join(dir_dst, f"r.{rx_dst}.{rz_dst}.mca")
    dx = (rx_dst - rx_src) * 512
    dz = (rz_dst - rz_src) * 512
    dpos = (dx, dz)

    if not copy_file(region_path_src, region_path_dst):
        print(f"*** Could not copy region {region_path_src!r} to {region_path_dst!r}")
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
                if chunk is None:
                	# Chunk does not exist, skip if missing
                	continue
            except:
                # May not exist; skip if missing
                continue

            chunk.body.at_path('Level.xPos').value += dx * 16
            chunk.body.at_path('Level.zPos').value += dz * 16

            if chunk.body.has_path('Level.Entities'):
                # May not exist; skip if missing
                for entity in chunk.body.iter_multipath('Level.Entities[]'):
                    _fixEntity(dpos, {"entity": entity})

            if chunk.body.has_path('Level.TileEntities'):
                # May not exist; skip if missing
                for block_entity in chunk.body.iter_multipath('Level.TileEntities[]'):
                    _fixEntity(dpos, {"entity": block_entity})

            if chunk.body.has_path('Level.TileTicks'):
                # May not exist; skip if missing
                for tile_tick in chunk.body.iter_multipath('Level.TileTicks[]'):
                    _fixEntity(dpos, {"entity": tile_tick})

            if chunk.body.has_path('Level.LiquidTicks'):
                # May not exist; skip if missing
                for liquid_tick in chunk.body.iter_multipath('Level.LiquidTicks[]'):
                    _fixEntity(dpos, {"entity": liquid_tick})

            try:
                region.save_chunk(chunk)
            except:
                print(f'Error saving chunk ({32*rx+cx}, {32*rz+cz}) RegionFile({region_path_dst!r})')
                return False
    return True

def _fixEntity(onMatchArgs, entityDetails):
    dx, dz = onMatchArgs
    entity = entityDetails["entity"]

    nbtPaths = (
        ('x', 'z'),
        ('AX', 'AZ'),
        ('APX', 'APZ'),
        ('BeamTarget.X', 'BeamTarget.Z'),
        ('BoundX', 'BoundZ'),
        ('Brain.memories.{}.value.pos[0]', 'Brain.memories.{}.value.pos[-1]'),
        ('enteredNetherPosition.x', 'enteredNetherPosition.z'),
        ('ExitPortal.X', 'ExitPortal.Z'),
        ('HomePosX', 'HomePosZ'),
        ('Leash.X', 'Leash.Z'),
        ('Pos[0]', 'Pos[2]'),
        ('SleepingX', 'SleepingZ'),
        ('SpawnX', 'SpawnZ'),
        ('TileX', 'TileZ'), # Painting/item frame
        ('TreasurePosX', 'TreasurePosZ'),
        ('TravelPosX', 'TravelPosZ'),
        ('xTile', 'zTile'),
    )

    for nbtPath in nbtPaths:
        if (
            bool(entity.count_multipath(nbtPath[0])) and
            bool(entity.count_multipath(nbtPath[1]))
        ):
            for xTag in entity.iter_multipath(nbtPath[0]):
                xTag.value += dx
            for zTag in entity.iter_multipath(nbtPath[1]):
                zTag.value += dz

    if (entity.has_path("UUIDMost") or entity.has_path("UUIDLeast") or entity.has_path("UUID")):
        pop_if_present(entity, "UUIDMost")
        pop_if_present(entity, "UUIDLeast")
        entity.value["UUID"] = uuid_to_mc_uuid_tag_int_array(uuid.uuid4())
