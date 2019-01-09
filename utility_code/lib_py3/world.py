#!/usr/bin/env python3

import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt
from quarry.types.chunk import BlockArray
from quarry.types.buffer import BufferUnderrun

from lib_py3.block_map import block_map
from lib_py3.player import Player
#TODO from lib_py3.scoreboard import Scoreboard

class PlayerIterator(object):
    _world = None
    def __init__(self):
        self._i = -1

    @classmethod
    def _iter_from_world(cls,world):
        result = cls()
        result._world = world
        return result

    def __len__(self):
        return len(self._world.player_paths) + 1

    def __iter__(self):
        return self

    def __next__(self):
        if self._world is None:
            # No world provided, invalid initialization
            raise StopIteration
        if self._i == -1:
            self._i += 1
            return self._world.single_player
        if self._i >= len(self._world.player_paths):
            raise StopIteration
        player_path = self._world.player_paths[self._i]
        self._i += 1
        return Player(player_path)

class BaseChunkEntityIterator(object):
    """
    This is an iterator over basic (non-recursive) entities AND tile entities in the world

    If readonly=False, it will save each chunk it visits that contain entities

    If coordinates are specified, it will only load region files that contain those coordinates
    Otherwise it will iterate over everything world wide

    Only iterates over chunks in regions that could plausibly contain the specified coordinates
    """

    def __init__(self, world, pos1=None, pos2=None, readonly=True):
        self._world = world
        self._readonly = readonly

        if ((pos1 is None) and (not pos2 is None)) or ((pos2 is None) and (not pos1 is None)):
            raise Exception("Only one iteration corner was specified!")

        if (not pos1 is None) and (not pos2 is None):
            self._min_x = min(pos1[0],pos2[0])
            self._min_y = min(pos1[1],pos2[1])
            self._min_z = min(pos1[2],pos2[2])

            self._max_x = max(pos1[0],pos2[0])
            self._max_y = max(pos1[1],pos2[1])
            self._max_z = max(pos1[2],pos2[2])
        else:
            # Compute region boundaries for the world
            xregions = [r[0] for r in world.region_files]
            zregions = [r[1] for r in world.region_files]
            self._min_x = min(xregions) * 512
            self._max_x = max(xregions) * 512
            self._min_y = 0
            self._max_y = 255
            self._min_z = min(zregions) * 512
            self._max_z = max(zregions) * 512

    def __iter__(self):
        """
        Initialize the iterator for use.

        Doing this here instead of in __init__ allows the iterator to potentially be re-used
        """

        self._region = None
        self._chunk = None

        # The _first_run flag is used so that when the first call to __next__ is made, instead
        # of trying to get the next chunk/region it loads the initial ones instead
        self._first_run = True

        return self

    def _next_region(self):
        """
        Iteratively loads the next region to process

        When this returns, either _region is set and valid or StopIteration is raised
        """
        while True:
            if not self._region is None and not self._readonly:
                # Save the current region - maybe nothing to do here?
                self._region = None

            if self._first_run:
                # This was the first call to __next__ - need to load the initial region files
                # and not iterate them just yet
                self._first_run = False
                self._rx = self._min_x//512
                self._rz = self._min_z//512
            else:
                # Get the next region
                self._rx += 1
                if self._rx > self._max_x//512:
                    self._rx = self._min_x//512
                    self._rz += 1

                if self._rz > self._max_z//512:
                    # All done!
                    raise StopIteration

            # Load the next indicated region (_rx/_rz)
            region_path = os.path.join(self._world.path, "region", "r.{}.{}.mca".format(self._rx, self._rz))

            if not os.path.isfile(region_path):
                # This region file isn't present - no reason to keep a reference for saving
                self._region = None

                # Continue iterating over regions to find the next valid one
                continue

            # Calculate which chunks need to be searched - don't waste time on chunks out of range
            self._cx_range = World.bounded_range(self._min_x, self._max_x, self._rx, 512, 16)
            self._cx_idx = 0
            self._cz_range = World.bounded_range(self._min_z, self._max_z, self._rz, 512, 16)
            self._cz_idx = 0

            # If we get to here, region_path is the valid next region file to work with
            self._region = nbt.RegionFile(region_path)

            # Successfully found next region - stop iterating
            break

    def _next_chunk(self):
        """
        Iteratively loads the next chunk to process

        When this returns, either _chunk is set and valid or StopIteration is raised
        """
        while True:
            if not self._chunk is None and not self._readonly:
                # Save the previously edited chunk
                self._region.save_chunk(self._chunk)
                self._chunk = None

            if self._first_run:
                # This was the first call to __next__ - need to load the initial region files
                # and not iterate the chunk index's just yet
                self._next_region()
            else:
                # Get the next chunk
                self._cx_idx += 1
                if self._cx_idx >= len(self._cx_range):
                    self._cx_idx = 0
                    self._cz_idx += 1

            # If the next chunk index is out of range, move to the next region
            if self._cz_idx >= len(self._cz_range):
                # When moving to the next region, can be sure that the ranges are set correctly
                # and can use the index's to get a real chunk in range
                self._next_region()

            # Load the next indicated chunk (_cx/_cz)
            self._chunk = self._region.load_chunk(self._cx_range[self._cx_idx], self._cz_range[self._cz_idx])

            if (
                (self._chunk is None) or
                (((not self._chunk.body.has_path('Level.TileEntities')) or
                  (len(self._chunk.body.at_path('Level.TileEntities').value) == 0)) and
                ((not self._chunk.body.has_path('Level.Entities')) or
                  (len(self._chunk.body.at_path('Level.Entities').value) == 0)))
            ):
                # No entities or tile entities in this chunk - no reason to keep a reference for saving
                self._chunk = None

                # Continue iterating over chunks to find the next one that does have entities
                continue

            # If we get here, this chunk has been loaded and contains some type of entity

            # Chunk contains tile entities
            if self._chunk.body.has_path('Level.TileEntities'):
                # Make note of the tile entities for iterating at the higher level
                self._tile_entities = self._chunk.body.at_path('Level.TileEntities').value
                self._tile_entities_pos = 0

            # Chunk contains regular entities
            if self._chunk.body.has_path('Level.Entities'):
                # Make note of the entities for iterating at the higher level
                self._entities = self._chunk.body.at_path('Level.Entities').value
                self._entities_pos = 0

            # Successfully found next chunk - stop iterating
            break

    def __next__(self):
        """
        Iteratively identifies the next valid tile entity or regular entity and returns it.

        Return value is two things!
            entity - the entity OR tile entity TagCompound
            isTileEntity - True if tile entity, False if entity

        This does the final check to make sure returned entities are in the bounding box
        """
        while True:
            if (
                self._first_run or
                (self._tile_entities_pos >= len(self._tile_entities) and
                 self._entities_pos >= len(self._entities))
            ):
                # Out of tile entities - move to the next chunk with some to process
                self._next_chunk()

            # Still something to iterate - either tile entities or regular entities in this chunk

            # Process tile entities first if haven't finished them yet
            if self._tile_entities_pos < len(self._tile_entities):
                tile_entity = self._tile_entities[self._tile_entities_pos]
                tile_x = tile_entity.at_path('x').value
                tile_y = tile_entity.at_path('y').value
                tile_z = tile_entity.at_path('z').value

                # Increment index so regardless of whether this is in range the next step
                # will find the next tile entity
                self._tile_entities_pos += 1

                if not (
                    self._min_x <= tile_x and tile_x < self._max_x + 1 and
                    self._min_y <= tile_y and tile_y < self._max_y + 1 and
                    self._min_z <= tile_z and tile_z < self._max_z + 1
                ):
                    # This tile entity isn't in the bounding box
                    # Continue iterating until we find one that is
                    continue

                # Found a valid tile entity in range
                return tile_entity, True

            # Tile entities are done but somehow we are still here - so there must be entities to do
            entity = self._entities[self._entities_pos]
            pos = entity.at_path('Pos').value
            x = pos[0].value
            y = pos[1].value
            z = pos[2].value

            # Increment index so regardless of whether this is in range the next step
            # will find the next entity
            self._entities_pos += 1

            if not (
                self._min_x <= x and x < self._max_x + 1 and
                self._min_y <= y and y < self._max_y + 1 and
                self._min_z <= z and z < self._max_z + 1
            ):
                # This entity isn't in the bounding box
                # Continue iterating until we find one that is
                continue

            # Found a valid entity in range
            return entity, False


class RecursiveEntityIterator(object):
    """
    This iterator uses BaseChunkEntityIterator to get entities and tile entities in the world
    Then it recursively iterates over them to find additional entities / tile entities

    Same arguments as BaseChunkEntityIterator:

    If readonly=False, it will save each chunk it visits that contain entities

    If coordinates are specified, it will only load region files that contain those coordinates
    Otherwise it will iterate over everything world wide

    Only iterates over chunks in regions that could plausibly contain the specified coordinates
    """

    def __init__(self, world, pos1=None, pos2=None, readonly=True):
        self._baseiterator = BaseChunkEntityIterator(world, pos1, pos2, readonly)

    def __iter__(self):
        """
        Initialize the iterator for use.

        Doing this here instead of in __init__ allows the iterator to potentially be re-used
        """

        # Initialize the base iterator
        self._baseiterator.__iter__()

        # Use a stack to keep track of what items still need to be processed
        self._work_stack = []

        return self

    def _scan_item_for_work(self, item):
        """
        Looks at an item and if it contains more tile or block entities,
        add them to the _work_stack
        """
        if item.has_path("tag.BlockEntityTag"):
            self._work_stack.append((item.at_path("tag.BlockEntityTag"), True))

        if item.has_path("tag.EntityTag"):
            self._work_stack.append((item.at_path("tag.EntityTag"), False))

    def __next__(self):
        """
        Iterates over entities embedded in an entity.

        Iteration order is depth-first, returning the higher-level object first then using
        a depth-first iterator into nested sub elements

        Return value is two things!
            entity - the entity OR tile entity TagCompound
            is_tile_entity - True if tile entity, False if entity
            source_pos - an (x, y, z) tuple of the original entity's position
        """

        if len(self._work_stack) == 0:
            # No work left to do - get another entity
            entity, is_tile_entity = self._baseiterator.__next__()
            self._work_stack.append((entity, is_tile_entity))

            # Keep track of where the original entity was. This is useful because nested
            # items mostly don't have position tags
            if is_tile_entity:
                if entity.has_path('x') and entity.has_path('y') and entity.has_path('z'):
                    x = entity.at_path('x').value
                    y = entity.at_path('y').value
                    z = entity.at_path('z').value
                    self._source_pos = (x, y, z)
                else:
                    self._source_pos = None
            else:
                if entity.has_path('Pos'):
                    pos = entity.at_path('Pos').value
                    x = pos[0].value
                    y = pos[1].value
                    z = pos[2].value
                    self._source_pos = (x, y, z)
                else:
                    self._source_pos = None


        # Process the next work element on the stack
        current_entity, is_tile_entity = self._work_stack.pop()

        # Add more work to the stack for next time
        if is_tile_entity:
            # Tile entities!
            if current_entity.has_path("SpawnPotentials"):
                for spawn in current_entity.at_path("SpawnPotentials").value:
                    if spawn.has_path("Entity"):
                        self._work_stack.append((spawn.at_path("Entity"), False))

            if current_entity.has_path("SpawnData"):
                self._work_stack.append((current_entity.at_path("SpawnData"), False))

        else:
            # Regular entities!
            if current_entity.has_path("Passengers"):
                for passenger in current_entity.at_path("Passengers").value:
                    self._work_stack.append((passenger, False))

        # Scan items in current entity, and if any are found scan them for nested entities
        ItemIterator.scan_entity_for_items(current_entity, self._scan_item_for_work);

        return current_entity, is_tile_entity, self._source_pos

class ItemIterator(object):
    _single_item_locations = (
        "ArmorItem",
        "Item",
        "RecordItem",
        "SaddleItem",
        "Trident",
    )

    _list_item_locations = (
        "ArmorItems",
        "EnderItems",
        "HandItems",
        "Inventory",
        "Items",
        "Inventory",
    )

    @classmethod
    def scan_entity_for_items(cls, entity_nbt, item_found_func):
        for location in cls._single_item_locations:
            if entity_nbt.has_path(location):
                item_found_func(entity_nbt.at_path(location))

        for location in cls._list_item_locations:
            if entity_nbt.has_path(location):
                for item in entity_nbt.at_path(location).value:
                    item_found_func(item)

        if entity_nbt.has_path("Offers.Recipes"):
            for item in entity_nbt.at_path("Offers.Recipes").value:
                if item.has_path("buy"):
                    item_found_func(item.at_path("buy"))
                if item.has_path("buyB"):
                    item_found_func(item.at_path("buyB"))
                if item.has_path("sell"):
                    item_found_func(item.at_path("sell"))


class World(object):
    """
    An object for editing a world (1.13+).
    Gives methods for editing blocks and areas that
    may cross over chunks or region files.

    The path you provide is expected to contain a level.dat file.
    """
    def __init__(self,path):
        """
        Load a world folder; loading players and region files will occur as needed, though this is half implemented
        """
        self.path = path
        self.level_dat_file = nbt.NBTFile.load( os.path.join( path,'level.dat' ) )
        self.level_dat = self.level_dat_file.root_tag.body
        self.find_region_files()
        self._player_paths = None
        self.find_data_packs()

    def save(self):
        self.level_dat_file.save( os.path.join( self.path, 'level.dat' ) )

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
        self._player_paths = []

        player_data_path = os.path.join( self.path, 'playerdata' )
        if os.path.isdir(player_data_path):
            for filename in os.listdir( player_data_path ):
                try:
                    player = None
                    if filename[-4:] == '.dat':
                        player = uuid.UUID( filename[:-4] )
                    if player:
                        self._player_paths.append( os.path.join( player_data_path, filename ) )
                except:
                    pass

    @property
    def player_paths(self):
        if self._player_paths is None:
            self.find_players()
        return self._player_paths

    @property
    def players(self):
        '''
        Returns an iterator of all players in the world,
        including the singleplayer player.

        The list of players is updated before looping,
        in case any player files were externally edited.

        Usage:
        ```
        for player in world.players:
            player.pos = [0,65,0]
            player.save()
        ```
        '''
        self.find_players()
        return PlayerIterator._iter_from_world(self)

    def entity_iterator(self, pos1=None, pos2=None, readonly=True):
        '''
        Returns an iterator of all entities and tile entities in the world.
        If readonly=True, all chunks containing entities will be saved as
        iteration passes them - meaning you can change them.

        Usage:

        for entity, is_tile_entity in world.tile_entity_iterator():
            if is_tile_entity:
                print("This is a tile entity!")
            else:
                print("This is a regular entity!")
            entity.tree()
        '''
        return RecursiveEntityIterator(self, pos1, pos2, readonly)

    def find_data_packs(self):
        self._enabled_data_packs = []
        self._disabled_data_packs = []

        if self.level_dat.has_path('Data.DataPacks.Disabled'):
            for datapack in self.level_dat.at_path('Data.DataPacks.Disabled').value:
                self._disabled_data_packs.append(datapack.value)

        if self.level_dat.has_path('Data.DataPacks.Enabled'):
            for datapack in self.level_dat.at_path('Data.DataPacks.Enabled').value:
                self._enabled_data_packs.append(datapack.value)

    @property
    def enabled_data_packs(self):
        return list(self._enabled_data_packs)

    @property
    def disabled_data_packs(self):
        return list(self._disabled_data_packs)

    @enabled_data_packs.setter
    def enabled_data_packs(self,other):
        # remove packs to enable from disabled packs
        for pack in self._disabled_data_packs:
            if pack in other:
                self._disabled_data_packs.remove(pack)

        # add no longer enabled packs to disabled packs
        for pack in self._enabled_data_packs:
            if pack not in other:
                self._disabled_data_packs.append(pack)

        # Set enabled packs to desired list
        self._enabled_data_packs = other

    @disabled_data_packs.setter
    def disabled_data_packs(self,other):
        # remove packs to disable from enabled packs
        for pack in self._enabled_data_packs:
            if pack in other:
                self._enabled_data_packs.remove(pack)

        # add no longer disabled packs to enabled packs
        for pack in self._disabled_data_packs:
            if pack not in other:
                self._enabled_data_packs.append(pack)

        # Set disabled packs to desired list
        self._disabled_data_packs = other

    def save_data_packs(self):
        if not self.level_dat.has_path('Data.DataPacks'):
            self.level_dat.at_path('Data').value['DataPacks'] = nbt.TagCompound({})

        if not self.level_dat.has_path('Data.DataPacks.Disabled'):
            self.level_dat.at_path('Data.DataPacks').value['Disabled'] = nbt.TagList({})

        if not self.level_dat.has_path('Data.DataPacks.Enabled'):
            self.level_dat.at_path('Data.DataPacks').value['Enabled'] = nbt.TagList({})

        enabled = []
        disabled = []

        for datapack in self._enabled_data_packs:
            enabled.append( nbt.TagString( datapack ) )

        for datapack in self._disabled_data_packs:
            if datapack not in self._enabled_data_packs:
                disabled.append( nbt.TagString( datapack ) )

        self.level_dat.at_path('Data.DataPacks.Disabled').value = disabled
        self.level_dat.at_path('Data.DataPacks.Enabled').value = enabled

        self.find_data_packs()

    @property
    def single_player(self):
        return Player.from_tag( self.level_dat.at_path('Data.Player') )

    @property
    def spawn(self):
        x = self.level_dat.at_path('Data.SpawnX').value
        y = self.level_dat.at_path('Data.SpawnY').value
        z = self.level_dat.at_path('Data.SpawnZ').value

        return (x,y,z)

    @spawn.setter
    def spawn(self,pos):
        if len(pos) != 3:
            raise IndexError('pos must have 3 entries, xyz')
        paths = ['SpawnX','SpawnY','SpawnZ']
        for i in range(3):
            self.level_dat.at_path( 'Level.' + paths[i] ).value = pos[i]

    def dump_command_blocks(self,pos1,pos2,log=None):
        """
        Finds all command blocks between pos1 and pos2,
        and displays what they contain. (WIP)
        """
        min_x = min(pos1[0],pos2[0])
        min_y = min(pos1[1],pos2[1])
        min_z = min(pos1[2],pos2[2])

        max_x = max(pos1[0],pos2[0])
        max_y = max(pos1[1],pos2[1])
        max_z = max(pos1[2],pos2[2])

        required_cy_sections = tuple(self.bounded_range(min_y,max_y,0,256,16))

        command_blocks = []

        if log:
            log_file = open(log,'w')

        for rz in range(min_z//512,max_z//512+1):
            for rx in range(min_x//512,max_x//512+1):
                region_path = os.path.join( self.path, "region", "r.{}.{}.mca".format(rx, rz) )

                if not os.path.isfile(region_path):
                    continue

                with nbt.RegionFile(region_path) as region:
                    for cz in self.bounded_range(min_z,max_z,rz,512,16):
                        for cx in self.bounded_range(min_x,max_x,rx,512,16):
                            try:
                                chunk = region.load_chunk(cx, cz)

                                if not chunk.body.has_path('Level.TileEntities'):
                                    continue

                                # Load the blocks in the chunk sections now in case we find command block entities
                                chunk_sections = {}
                                for section in chunk.body.at_path('Level.Sections').value:
                                    cy = section.at_path("Y").value
                                    if cy not in required_cy_sections:
                                        continue
                                    chunk_sections[cy] = BlockArray.from_nbt(section, block_map)

                                #blocks[256 * by + 16 * bz + bx] = block['block']

                                for tile_entity in chunk.body.at_path('Level.TileEntities').value:
                                    tile_x = tile_entity.at_path('x').value
                                    tile_y = tile_entity.at_path('y').value
                                    tile_z = tile_entity.at_path('z').value
                                    if not (
                                        tile_entity.at_path('id').value == 'minecraft:command_block' and
                                        min_x <= tile_x and tile_x <= max_x and
                                        min_y <= tile_y and tile_y <= max_y and
                                        min_z <= tile_z and tile_z <= max_z
                                    ):
                                        continue

                                    command_blocks.append(tile_entity)

                                    cy = tile_y // 16

                                    bx = tile_x & 0xf
                                    by = tile_y & 0xf
                                    bz = tile_z & 0xf

                                    block = chunk_sections[cy][256 * by + 16 * bz + bx]
                                    block_id = block['name']
                                    #conditional = block['conditional']
                                    #facing = block['facing']

                                    Command = tile_entity.at_path('Command').value
                                    if tile_entity.has_path('LastOutput'):
                                        LastOutput = tile_entity.at_path('LastOutput').value
                                    else:
                                        LastOutput = ''
                                    if tile_entity.has_path('LastExecution'):
                                        LastExecution = tile_entity.at_path('LastExecution').value
                                    else:
                                        LastExecution = 0

                                    reason = None
                                    if LastExecution <= 559266554:
                                        reason = 'last used 1.12'
                                    elif len(Command) == 0:
                                        reason = 'no command'
                                    elif '"arguement' in LastOutput:
                                        reason = 'bad arguements'
                                    elif '"command.context.here"' in LastOutput:
                                        reason = 'output indicates error'

                                    if reason and log:
                                        # This command block hasn't been updated, or has an error
                                        log_file.write( '{0:>7} {1:>7} {2:>7} {3:<36}{4:<25}{5}\n'.format(tile_x,tile_y,tile_z,block_id,reason,Command) )

                            except BufferUnderrun:
                                # Chunk not loaded
                                pass

        if log:
            log_file.close()
        return(command_blocks)

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

        Liquids are not yet supported
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
        - Liquids are not yet supported
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
                if section.at_path('Y').value == cy:
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

    @classmethod
    def bounded_range(cls, min_in, max_in, range_start, range_length, divide=1):
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

    # TODO: This should be one less level of container - i.e. should just be {'snowy'...}
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
        - Liquids are not yet supported
        """
        min_x = min(pos1[0],pos2[0])
        min_y = min(pos1[1],pos2[1])
        min_z = min(pos1[2],pos2[2])

        max_x = max(pos1[0],pos2[0])
        max_y = max(pos1[1],pos2[1])
        max_z = max(pos1[2],pos2[2])

        required_cy_sections = tuple(self.bounded_range(min_y,max_y,0,256,16))

        for rz in range(min_z//512,max_z//512+1):
            for rx in range(min_x//512,max_x//512+1):
                region_path = os.path.join( self.path, "region", "r.{}.{}.mca".format(rx, rz) )

                if not os.path.isfile(region_path):
                    raise FileNotFoundError('No such region {},{} in world {}'.format(rx,rz,self.path))

                with nbt.RegionFile(region_path) as region:
                    for cz in self.bounded_range(min_z,max_z,rz,512,16):
                        for cx in self.bounded_range(min_x,max_x,rx,512,16):
                            chunk = region.load_chunk(cx, cz)
                            chunk_sections = chunk.body.at_path('Level.Sections').value
                            required_sections_left = set(required_cy_sections)

                            # Handle blocks - eventually liquids, lighting, etc will be handled here too
                            for section in chunk_sections:
                                cy = section.at_path("Y").value
                                if cy not in required_sections_left:
                                    continue
                                required_sections_left.remove(cy)
                                blocks = BlockArray.from_nbt(section, block_map)

                                for by in self.bounded_range(min_y,max_y,cy,16):
                                    for bz in self.bounded_range(min_z,max_z,32*rz+cz,16):
                                        for bx in self.bounded_range(min_x,max_x,32*rx+cx,16):
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
                                if len(NewTileEntities) == 0:
                                    chunk.body.at_path('Level').value.pop('TileEntities')
                                else:
                                    chunk.body.at_path('Level.TileEntities').value = NewTileEntities

                            region.save_chunk(chunk)

    def replace_blocks(self,pos1,pos2,old_blocks,new_block):
        """
        Replace old_blocks from pos1 to pos2 (x,y,z).

        old_blocks is a list of the blocks to replace.
        If an entry in old_blocks leaves out a block state, it will match any value for that state.

        new_block is what those blocks are replaced with.

        Example block:
        {'block': {'snowy': 'false', 'name': 'minecraft:grass_block'} }

        In this version:
        - All block properties are mandatory (no defaults are filled in for you)
        - Block NBT cannot be set, but can be read.
        - Similar to the vanilla /fill command, entities are ignored.
        - Existing block NBT for the specified coordinate is cleared.
        - Liquids are not yet supported
        """
        min_x = min(pos1[0],pos2[0])
        min_y = min(pos1[1],pos2[1])
        min_z = min(pos1[2],pos2[2])

        max_x = max(pos1[0],pos2[0])
        max_y = max(pos1[1],pos2[1])
        max_z = max(pos1[2],pos2[2])

        required_cy_sections = tuple(self.bounded_range(min_y,max_y,0,256,16))

        for rz in range(min_z//512,max_z//512+1):
            for rx in range(min_x//512,max_x//512+1):
                region_path = os.path.join( self.path, "region", "r.{}.{}.mca".format(rx, rz) )

                if not os.path.isfile(region_path):
                    raise FileNotFoundError('No such region {},{} in world {}'.format(rx,rz,self.path))

                with nbt.RegionFile(region_path) as region:
                    for cz in self.bounded_range(min_z,max_z,rz,512,16):
                        for cx in self.bounded_range(min_x,max_x,rx,512,16):
                            chunk = region.load_chunk(cx, cz)
                            chunk_sections = chunk.body.at_path('Level.Sections').value
                            required_sections_left = set(required_cy_sections)

                            # Handle blocks - eventually liquids, lighting, etc will be handled here too
                            for section in chunk_sections:
                                cy = section.at_path("Y").value
                                if cy not in required_sections_left:
                                    continue
                                required_sections_left.remove(cy)
                                blocks = BlockArray.from_nbt(section, block_map)

                                for by in self.bounded_range(min_y,max_y,cy,16):
                                    for bz in self.bounded_range(min_z,max_z,32*rz+cz,16):
                                        for bx in self.bounded_range(min_x,max_x,32*rx+cx,16):
                                            block = blocks[256 * by + 16 * bz + bx]

                                            for old_block in old_blocks:
                                                match = True

                                                for key in old_block['block']:
                                                    if (
                                                        key not in block or
                                                        old_block['block'][key] != block[key]
                                                    ):
                                                        match = False
                                                        break

                                                if not match:
                                                    break

                                                # Replace the block
                                                blocks[256 * by + 16 * bz + bx] = new_block

                                                x = 512*rx + 16*cx + bx
                                                y =          16*cy + by
                                                z = 512*rz + 16*cz + bz

                                                # Handle tile entities
                                                if chunk.body.has_path('Level.TileEntities'):
                                                    NewTileEntities = []
                                                    for tile_entity in chunk.body.at_path('Level.TileEntities').value:
                                                        tile_x = tile_entity.at_path('x').value
                                                        tile_y = tile_entity.at_path('y').value
                                                        tile_z = tile_entity.at_path('z').value
                                                        if not (
                                                            x == tile_x and
                                                            y == tile_y and
                                                            z == tile_z
                                                        ):
                                                            NewTileEntities.append(tile_entity)
                                                    if len(NewTileEntities) == 0:
                                                        chunk.body.at_path('Level').value.pop('TileEntities')
                                                    else:
                                                        chunk.body.at_path('Level.TileEntities').value = NewTileEntities

                            region.save_chunk(chunk)

    def restore_area(self,pos1,pos2,old_world):
        """
        Restore the area in pos1,po2 in this world
        to how it was in old_world at the same coordinates.

        In this version:
        - Restoring an area that's missing in one world or the other results in an error
        - This MAY include subchunks, testing required. In this case, F3+G to show chunk
          borders, the blue lines mark subchunks. Make sure each subchunk has at least
          one block in it, and this should work fine. Air and air variants don't count.
        """
        min_x = min(pos1[0],pos2[0])
        min_y = min(pos1[1],pos2[1])
        min_z = min(pos1[2],pos2[2])

        max_x = max(pos1[0],pos2[0])
        max_y = max(pos1[1],pos2[1])
        max_z = max(pos1[2],pos2[2])

        required_cy_sections = tuple(self.bounded_range(min_y,max_y,0,256,16))

        for rz in range(min_z//512,max_z//512+1):
            for rx in range(min_x//512,max_x//512+1):
                new_region_path = os.path.join( self.path, "region", "r.{}.{}.mca".format(rx, rz) )
                old_region_path = os.path.join( old_world.path, "region", "r.{}.{}.mca".format(rx, rz) )

                if not os.path.isfile(new_region_path):
                    raise FileNotFoundError('No such region {},{} in world {}'.format(rx,rz,self.path))
                if not os.path.isfile(old_region_path):
                    raise FileNotFoundError('No such region {},{} in world {}'.format(rx,rz,old_world.path))

                with nbt.RegionFile(new_region_path) as new_region:
                    with nbt.RegionFile(old_region_path) as old_region:
                        for cz in self.bounded_range(min_z,max_z,rz,512,16):
                            for cx in self.bounded_range(min_x,max_x,rx,512,16):
                                new_chunk = new_region.load_chunk(cx, cz)
                                old_chunk = old_region.load_chunk(cx, cz)
                                """
                                NOTE: loading the old chunk in this way does NOT
                                affect the old world, as long as we don't save
                                the chunk back.
                                No deep copy is required past here.
                                """

                                new_chunk_sections = {}
                                old_chunk_sections = {}

                                for new_chunk_section in new_chunk.body.at_path('Level.Sections').value:
                                    cy = new_chunk_section.at_path("Y").value
                                    if len( self.bounded_range(min_y,max_y,cy,16) ) == 0:
                                        continue
                                    new_chunk_sections[cy] = new_chunk_section

                                for old_chunk_section in old_chunk.body.at_path('Level.Sections').value:
                                    cy = old_chunk_section.at_path("Y").value
                                    if len( self.bounded_range(min_y,max_y,cy,16) ) == 0:
                                        continue
                                    old_chunk_sections[cy] = old_chunk_section

                                old_only_sections = set(old_chunk_sections.keys()).difference(set(new_chunk_sections.keys()))
                                new_only_sections = set(new_chunk_sections.keys()).difference(set(old_chunk_sections.keys()))
                                common_sections = set(old_chunk_sections.keys()).intersection(set(new_chunk_sections.keys()))

                                ################################################
                                # Handle blocks
                                for cy in old_only_sections:
                                    # Copy, deleting blocks if out of bounds
                                    old_section = old_chunk_sections[cy]
                                    old_blocks = BlockArray.from_nbt(old_section, block_map)

                                    for by in set(range(16)).difference(set( self.bounded_range(min_y,max_y,cy,16) )):
                                        for bz in set(range(16)).difference(set( self.bounded_range(min_z,max_z,32*rz+cz,16) )):
                                            for bx in set(range(16)).difference(set( self.bounded_range(min_x,max_x,32*rx+cx,16) )):
                                                index = 256 * by + 16 * bz + bx
                                                old_blocks[index] = {'name': 'minecraft:air'}

                                    new_chunk.body.at_path('Level.Sections').value.append(old_section)

                                for cy in new_only_sections:
                                    # Blocks need deleting if in bounds
                                    new_section = new_chunk_sections[cy]
                                    new_blocks = BlockArray.from_nbt(new_section, block_map)

                                    for by in self.bounded_range(min_y,max_y,cy,16):
                                        for bz in self.bounded_range(min_z,max_z,32*rz+cz,16):
                                            for bx in self.bounded_range(min_x,max_x,32*rx+cx,16):
                                                index = 256 * by + 16 * bz + bx
                                                new_blocks[index] = {'name': 'minecraft:air'}

                                for cy in common_sections:
                                    # copy in-bounds blocks
                                    new_section = new_chunk_sections[cy]
                                    old_section = old_chunk_sections[cy]

                                    new_blocks = BlockArray.from_nbt(new_section, block_map)
                                    old_blocks = BlockArray.from_nbt(old_section, block_map)

                                    new_section.at_path('BlockLight').value = old_section.at_path('BlockLight').value
                                    new_section.at_path('SkyLight').value = old_section.at_path('SkyLight').value

                                    for by in self.bounded_range(min_y,max_y,cy,16):
                                        for bz in self.bounded_range(min_z,max_z,32*rz+cz,16):
                                            for bx in self.bounded_range(min_x,max_x,32*rx+cx,16):
                                                index = 256 * by + 16 * bz + bx
                                                new_blocks[index] = old_blocks[index]

                                ################################################
                                # Handle tile entities, entities, and various tick events
                                for category in (
                                    'Entities',
                                    'TileEntities',
                                    'TileTicks',
                                    'LiquidTicks',
                                ):
                                    NewEntities = []

                                    # Keep anything in bounds in the old chunks
                                    if old_chunk.body.has_path( 'Level.' + category ):
                                        for tile_entity in old_chunk.body.at_path( 'Level.' + category ).value:
                                            if tile_entity.has_path('Pos'):
                                                tile_x = tile_entity.at_path('Pos[0]').value
                                                tile_y = tile_entity.at_path('Pos[1]').value
                                                tile_z = tile_entity.at_path('Pos[2]').value
                                            else:
                                                tile_x = tile_entity.at_path('x').value
                                                tile_y = tile_entity.at_path('y').value
                                                tile_z = tile_entity.at_path('z').value

                                            if (
                                                min_x <= tile_x and tile_x < max_x + 1 and
                                                min_y <= tile_y and tile_y < max_y + 1 and
                                                min_z <= tile_z and tile_z < max_z + 1
                                            ):
                                                NewEntities.append(tile_entity)

                                    # Keep anything out of bounds in the new chunks
                                    if new_chunk.body.has_path( 'Level.' + category ):
                                        for tile_entity in new_chunk.body.at_path( 'Level.' + category ).value:
                                            if tile_entity.has_path('Pos'):
                                                tile_x = tile_entity.at_path('Pos[0]').value
                                                tile_y = tile_entity.at_path('Pos[1]').value
                                                tile_z = tile_entity.at_path('Pos[2]').value
                                            else:
                                                tile_x = tile_entity.at_path('x').value
                                                tile_y = tile_entity.at_path('y').value
                                                tile_z = tile_entity.at_path('z').value

                                            if not (
                                                min_x <= tile_x and tile_x < max_x + 1 and
                                                min_y <= tile_y and tile_y < max_y + 1 and
                                                min_z <= tile_z and tile_z < max_z + 1
                                            ):
                                                NewEntities.append(tile_entity)

                                    if new_chunk.body.has_path( 'Level.' + category ):
                                        if len(NewEntities) == 0:
                                            new_chunk.body.at_path('Level').value.pop( category )
                                        else:
                                            new_chunk.body.at_path( 'Level.' + category ).value = NewEntities
                                    elif len(NewEntities) > 0:
                                        new_chunk.body.at_path( 'Level' ).value[ category ] = nbt.TagList( NewEntities )

                                new_region.save_chunk(new_chunk)

