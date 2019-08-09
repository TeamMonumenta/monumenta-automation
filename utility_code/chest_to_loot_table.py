#!/usr/bin/python3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

shard,x,y,z=('region_2',-1400,39,-1517)

rx,rz=x//512,z//512
cx,cz=(x%512)//16,(z%512)//16

try:
    region = nbt.RegionFile('/home/epic/project_epic/{0}/Project_Epic-{0}/region/r.{1}.{2}.mca'.format(shard,rx,rz))
    chunk = region.load_chunk(cx,cz)

    for tile_entity in chunk.body.at_path('Level.TileEntities').value:
        if (
            x == tile_entity.at_path('x').value and
            y == tile_entity.at_path('y').value and
            z == tile_entity.at_path('z').value
        ):
            # TODO Do stuff here
            result = tile_entity
            result.tree()

except:
    print("An exception has occured. Are you sure your coordinates and shard name are correct?")

