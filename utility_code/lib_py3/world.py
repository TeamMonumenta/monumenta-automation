#!/usr/bin/env python3

import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt
from quarry.types.chunk import BlockArray

from lib_py3.block_map import block_map

class World(object):
    """
    An object for editing a world (1.13+).
    Gives methods for editing blocks and areas that
    may cross over chunks or region files.

    The path you provide is expected to contain a level.dat file.
    """
    def __init__(self,path):
        """
        Load a world folder, fetching the list of region files and players that it contains.
        """
        self.path = path
        self.level_dat = nbt.NBTFile.load( os.path.join( path,'level.dat' ) ).root_tag.body
        self.find_region_files()
        self.find_players()

    def find_region_files(self):
        self.region_files = []

        for filename in os.listdir( os.path.join( self.path, 'region' ) ):
            filename_parts = filename.split('.')
            if (
                len(filename_parts) != 4 or
                filename_parts[0] != 'r' or
                filename_parts[3] != 'mca'
            ):
                continue
            try:
                coords = (
                    int( filename_parts[1] ),
                    int( filename_parts[2] )
                )
                self.region_files.append( coords )
            except:
                pass

    def find_players(self):
        self.players = []

        for filename in os.listdir( os.path.join( self.path, 'playerdata' ) ):
            try:
                player = uuid.UUID( filename[:-4] )
                self.players.append( player )
            except:
                pass

    def get_block(self,pos):
        """
        Get the block at position (x,y,z).
        Example block:
        {
            'block': {
                'facing': 'north',
                'waterlogged': 'false',
                'name': 'minecraft:wall_sign'
            },
            'nbt': '{keepPacked:0b,x:-1441,Text4:"{\\"text\\":\\"\\"}",y:2,Text3:"{\\"text\\":\\"\\"}",z:-1444,Text2:"{\\"text\\":\\"\\"}",id:"minecraft:sign",Text1:"{\\"text\\":\\"\\"}"}'
        }

        Fluids are not yet supported
        """
        x,y,z = pos
        # bx,by,bz are block coordinates within the chunk section
        rx, bx = divmod(x, 512)
        by = y
        rz, bz = divmod(z, 512)
        cx, bx = divmod(bx, 16)
        cy, by = divmod(by, 16)
        cz, bz = divmod(bz, 16)

        region_path = os.path.join( self.path, "region", "r.{}.{}.mca".format(rx, rz) )

        with nbt.RegionFile(region_path) as region:
            chunk = region.load_chunk(cx, cz)
            section_not_found = True
            for section in chunk.body.at_path('Level.Sections').value:
                if section.at_path('Y').value == cy:
                    section_not_found = False
                    blocks = BlockArray.from_nbt(section, block_map)

                    result = {'block':blocks[256 * by + 16 * bz + bx]}
                    if chunk.body.has_path('Level.TileEntities'):
                        for tile_entity in chunk.body.at_path('Level.TileEntities').value:
                            if (
                                tile_entity.at_path('x').value == x and
                                tile_entity.at_path('y').value == y and
                                tile_entity.at_path('z').value == z
                            ):
                                result['nbt'] = tile_entity.to_mojangson()
                                break

                    return result
            if section_not_found:
                raise Exception("Chunk section not found")

    def set_block(self,pos,block):
        """
        Set a block at position (x,y,z).
        Example block:
        {'block': {'snowy': 'false', 'name': 'minecraft:grass_block'} }

        In this version:
        - All block properties are mandatory (no defaults are filled in for you)
        - Block NBT cannot be set, but can be read.
        - Existing block NBT for the specified coordinate is cleared.
        - Fluids are not yet supported
        """
        x,y,z = pos
        # bx,by,bz are block coordinates within the chunk section
        rx, bx = divmod(x, 512)
        by = y
        rz, bz = divmod(z, 512)
        cx, bx = divmod(bx, 16)
        cy, by = divmod(by, 16)
        cz, bz = divmod(bz, 16)

        region_path = os.path.join( self.path, "region", "r.{}.{}.mca".format(rx, rz) )

        with nbt.RegionFile(region_path) as region:
            chunk = region.load_chunk(cx, cz)
            for section in chunk.body.at_path('Level.Sections').value:
                if section.value['Y'].value == cy:
                    blocks = BlockArray.from_nbt(section, block_map)
                    blocks[256 * by + 16 * bz + bx] = block['block']

                    if chunk.body.has_path('Level.TileEntities'):
                        NewTileEntities = []
                        for tile_entity in chunk.body.at_path('Level.TileEntities').value:
                            if (
                                tile_entity.at_path('x').value != x or
                                tile_entity.at_path('y').value != y or
                                tile_entity.at_path('z').value != z
                            ):
                                NewTileEntities.append(tile_entity)
                        if len(NewTileEntities) == 0:
                            chunk.body.at_path('Level').value.pop('TileEntities')
                        else:
                            chunk.body.at_path('Level.TileEntities').value = NewTileEntities

                    region.save_chunk(chunk)
                    break
            else:
                raise Exception("Chunk section not found")

    def _bounded_range(self,min_in,max_in,range_start,range_length,divide=1):
        """
        Clip the input so the start and end don't exceed some other range.
        range_start is multiplied by range_length before use
        The output is relative to the start of the range.
        divide allows the range to be scaled to ( range // divide )
        """
        range_length //= divide
        range_start *= range_length

        min_out = min_in//divide - range_start
        max_out = max_in//divide - range_start + 1

        min_out = max( 0, min( min_out, range_length ) )
        max_out = max( 0, min( max_out, range_length ) )

        return range( min_out, max_out )

    def fill_blocks(self,pos1,pos2,block):
        """
        Fill the blocks from pos1 to pos2 (x,y,z).
        Example block:
        {'block': {'snowy': 'false', 'name': 'minecraft:grass_block'} }

        In this version:
        - All block properties are mandatory (no defaults are filled in for you)
        - Block NBT cannot be set, but can be read.
        - Similar to the vanilla /fill command, entities are ignored.
        - Existing block NBT for the specified coordinate is cleared.
        - Fluids are not yet supported
        """
        min_x = min(pos1[0],pos2[0])
        min_y = min(pos1[1],pos2[1])
        min_z = min(pos1[2],pos2[2])

        max_x = max(pos1[0],pos2[0])
        max_y = max(pos1[1],pos2[1])
        max_z = max(pos1[2],pos2[2])

        required_cy_sections = tuple(self._bounded_range(min_y,max_y,0,256,16))

        for rz in range(min_z//512,max_z//512+1):
            for rx in range(min_x//512,max_x//512+1):
                print('- region {},{}'.format(rx,rz))
                region_path = os.path.join( self.path, "region", "r.{}.{}.mca".format(rx, rz) )

                if not os.path.isfile(region_path):
                    raise FileNotFoundError('No such region {},{} in world {}'.format(rx,rz,self.path))

                with nbt.RegionFile(region_path) as region:
                    print('  - cz in {}'.format(self._bounded_range(min_z,max_z,rz,512,16)))
                    for cz in self._bounded_range(min_z,max_z,rz,512,16):
                        print('    - cx in {}'.format(self._bounded_range(min_x,max_x,rx,512,16)))
                        for cx in self._bounded_range(min_x,max_x,rx,512,16):
                            print('      - chunk {},{}'.format(cx,cz))
                            chunk = region.load_chunk(cx, cz)
                            chunk_sections = chunk.body.at_path('Level.Sections').value
                            required_sections_left = set(required_cy_sections)

                            # Handle blocks - eventually fluids, lighting, etc will be handled here too
                            for section in chunk_sections:
                                cy = section.at_path("Y").value
                                if cy not in required_sections_left:
                                    continue
                                required_sections_left.remove(cy)
                                blocks = BlockArray.from_nbt(section, block_map)

                                for by in self._bounded_range(min_y,max_y,cy,16):
                                    for bz in self._bounded_range(min_z,max_z,32*rz+cz,16):
                                        for bx in self._bounded_range(min_x,max_x,32*rx+cx,16):
                                            blocks[256 * by + 16 * bz + bx] = block['block']

                            if len(required_sections_left) != 0:
                                raise KeyError( 'Could not find cy={} in chunk {},{} of region file {},{} in world {}'.format(required_sections_left,cx,cz,rx,rz,self.path) )

                            # Handle tile entities
                            if chunk.body.has_path('Level.TileEntities'):
                                NewTileEntities = []
                                for tile_entity in chunk.body.at_path('Level.TileEntities').value:
                                    tile_x = tile_entity.at_path('x').value
                                    tile_y = tile_entity.at_path('y').value
                                    tile_z = tile_entity.at_path('z').value
                                    if not (
                                        min_x <= tile_x and tile_x <= max_x and
                                        min_y <= tile_y and tile_y <= max_y and
                                        min_z <= tile_z and tile_z <= max_z
                                    ):
                                        NewTileEntities.append(tile_entity)
                                    else:
                                        print('Removing tile entity at {},{},{}, id {}'.format( tile_entity.at_path('x').value, tile_entity.at_path('y').value, tile_entity.at_path('z').value, tile_entity.at_path('id').value ) )
                                if len(NewTileEntities) == 0:
                                    chunk.body.at_path('Level').value.pop('TileEntities')
                                else:
                                    chunk.body.at_path('Level.TileEntities').value = NewTileEntities

                            region.save_chunk(chunk)

