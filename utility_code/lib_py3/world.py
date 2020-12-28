import math
import numbers
import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt
from quarry.types.chunk import BlockArray
from quarry.types.buffer import BufferUnderrun

from lib_py3.block_map import block_map
from lib_py3.common import bounded_range, get_entity_uuid
from lib_py3.iterators.item_iterator import ItemIterator
from lib_py3.iterators.recursive_entity_iterator import RecursiveEntityIterator
from lib_py3.iterators.base_chunk_entity_iterator import BaseChunkEntityIterator
from lib_py3.player import Player
from lib_py3.scoreboard import Scoreboard

class World(object):
    """
    An object for editing a world (1.13+).
    Gives methods for editing blocks and areas that
    may cross over chunks or region files.

    The path you provide is expected to contain a level.dat file.
    """
    def __init__(self, path):
        """
        Load a world folder; loading players and region files will occur as needed, though this is half implemented
        """
        self.path = path
        self.level_dat_file = nbt.NBTFile.load(os.path.join(path, 'level.dat'))
        self.level_dat = self.level_dat_file.root_tag.body
        self._player_paths = None
        self._scoreboard = None
        self.find_data_packs()

    def save(self):
        self.level_dat_file.save(os.path.join(self.path, 'level.dat'))

    def find_players(self):
        self._player_paths = []

        player_data_path = os.path.join(self.path, 'playerdata')
        if os.path.isdir(player_data_path):
            for filename in os.listdir(player_data_path):
                try:
                    player = None
                    if filename.endswith('.dat'):
                        player = uuid.UUID(filename[:-4])
                    if player:
                        full_path = os.path.join(player_data_path, filename)
                        if os.path.getsize(full_path) <= 0:
                            continue
                        self._player_paths.append(full_path)
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
        for player in world.players():
            player.pos = [0, 65, 0]
            player.save()
        ```
        '''
        self.find_players()
        if self.level_dat.has_path('Data.Player'):
            yield Player.from_tag(self.level_dat.at_path('Data.Player'))
        for player_path in self._player_paths:
            yield Player(player_path)

    def entity_iterator(self, pos1=None, pos2=None, readonly=True, no_players=False, players_only=False):
        '''
        Returns an iterator of all entities and tile entities in the world.
        If readonly=False, all chunks containing entities will be saved as
        iteration passes them - meaning you can modify the entities returned

        Usage:

        for entity, pos, entity_path in world.entity_iterator():
            entity.tree()
        '''
        return RecursiveEntityIterator(self, pos1=pos1, pos2=pos2, readonly=readonly, no_players=no_players, players_only=players_only)

    def base_entity_iterator(self, pos1=None, pos2=None, readonly=True):
        '''
        Returns an iterator of all entities and tile entities in the world.
        If readonly=False, all chunks containing entities will be saved as
        iteration passes them - meaning you can modify the entities returned

        Note that this version is not recursive; each yielded item will just
        be a single top-level entity.

        Usage:

        for entity: TagCompound in world.base_entity_iterator():
            entity.tree()
        '''
        return BaseChunkEntityIterator(self, pos1=pos1, pos2=pos2, readonly=readonly)

    def entity_uuids(self):
        """
        Return a list of UUIDs found in this world.
        Used for pruning scores of dead entities.
        """
        uuids = set()
        for entity, source_pos, entity_path in self.entity_iterator():
            entity_uuid = get_entity_uuid(entity)
            if entity_uuid is not None:
                uuids.add(str(entity_uuid))

        return uuids

    def items(self, pos1=None, pos2=None, readonly=True, no_players=False, players_only=False):
        '''
        Returns an iterator of all items in the world.
        If readonly=False, all chunks will be saved as
        iteration passes them - meaning you can modify the items returned

        Usage:

        for item, pos in world.items():
            item.tree()
        '''
        return ItemIterator(self, pos1=pos1, pos2=pos2, readonly=readonly, no_players=no_players, players_only=players_only)

    def find_data_packs(self):
        self._enabled_data_packs = []
        self._disabled_data_packs = []

        if self.level_dat.has_path('Data.DataPacks.Disabled'):
            for datapack in self.level_dat.iter_multipath('Data.DataPacks.Disabled[]'):
                self._disabled_data_packs.append(datapack.value)

        if self.level_dat.has_path('Data.DataPacks.Enabled'):
            for datapack in self.level_dat.iter_multipath('Data.DataPacks.Enabled[]'):
                self._enabled_data_packs.append(datapack.value)

    @property
    def enabled_data_packs(self):
        return list(self._enabled_data_packs)

    @property
    def disabled_data_packs(self):
        return list(self._disabled_data_packs)

    @enabled_data_packs.setter
    def enabled_data_packs(self, other):
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
    def disabled_data_packs(self, other):
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

    # Note - this only saves datapacks to the loaded version of level.dat
    # Caller must also call World.save() to commit this back to the disk
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
            enabled.append(nbt.TagString(datapack))

        for datapack in self._disabled_data_packs:
            if datapack not in self._enabled_data_packs:
                disabled.append(nbt.TagString(datapack))

        self.level_dat.at_path('Data.DataPacks.Disabled').value = disabled
        self.level_dat.at_path('Data.DataPacks.Enabled').value = enabled

        self.find_data_packs()

    @property
    def single_player(self):
        return Player.from_tag(self.level_dat.at_path('Data.Player'))

    @property
    def spawn(self):
        x = self.level_dat.at_path('Data.SpawnX').value
        y = self.level_dat.at_path('Data.SpawnY').value
        z = self.level_dat.at_path('Data.SpawnZ').value

        return (x, y, z)

    @spawn.setter
    def spawn(self, pos):
        if len(pos) != 3:
            raise IndexError('pos must have 3 entries, xyz')
        paths = ['SpawnX', 'SpawnY', 'SpawnZ']
        for i in range(3):
            self.level_dat.at_path(f'Level.{paths[i]}').value = pos[i]

    @property
    def scoreboard(self):
        if not self._scoreboard:
            self._scoreboard = Scoreboard(os.path.join(self.path, "data", "scoreboard.dat"))
        return self._scoreboard


    # TODO: This should be one less level of container - i.e. should just be {'snowy'...}
    def fill_blocks(self, pos1, pos2, block):
        """
        Fill the blocks from pos1 to pos2 (x, y, z).
        Example block:
        {'block': {'snowy': 'false', 'name': 'minecraft:grass_block'} }

        In this version:
        - All block properties are mandatory (no defaults are filled in for you)
        - Block NBT cannot be set, but can be read.
        - Similar to the vanilla /fill command, entities are ignored.
        - Existing block NBT for the specified coordinate is cleared.
        - Liquids are not yet supported
        """
        min_x = min(pos1[0], pos2[0])
        min_y = min(pos1[1], pos2[1])
        min_z = min(pos1[2], pos2[2])

        max_x = max(pos1[0], pos2[0])
        max_y = max(pos1[1], pos2[1])
        max_z = max(pos1[2], pos2[2])

        required_cy_sections = tuple(bounded_range(min_y, max_y, 0, 256, 16))

        for rz in range(min_z//512, max_z//512+1):
            for rx in range(min_x//512, max_x//512+1):
                region_path = os.path.join(self.path, "region", f"r.{rx}.{rz}.mca")

                if not os.path.isfile(region_path):
                    raise FileNotFoundError(f'No such region {rx},{rz} in world {self.path}')

                with nbt.RegionFile(region_path) as region:
                    for cz in bounded_range(min_z, max_z, rz, 512, 16):
                        for cx in bounded_range(min_x, max_x, rx, 512, 16):
                            chunk = region.load_chunk(cx, cz)
                            required_sections_left = set(required_cy_sections)

                            # Handle blocks - eventually liquids, lighting, etc will be handled here too
                            for section in chunk.body.iter_multipath('Level.Sections[]'):
                                cy = section.at_path("Y").value
                                if cy not in required_sections_left:
                                    continue
                                required_sections_left.remove(cy)
                                blocks = BlockArray.from_nbt(section, block_map)

                                for by in bounded_range(min_y, max_y, cy, 16):
                                    for bz in bounded_range(min_z, max_z, 32*rz+cz, 16):
                                        for bx in bounded_range(min_x, max_x, 32*rx+cx, 16):
                                            blocks[256 * by + 16 * bz + bx] = block['block']

                            if len(required_sections_left) != 0:
                                raise KeyError(f'Could not find cy={required_sections_left} in chunk {cx},{cz} of region file {rx},{rz} in world {self.path}')

                            # Handle tile entities
                            if chunk.body.has_path('Level.TileEntities'):
                                NewTileEntities = []
                                for tile_entity in chunk.body.iter_multipath('Level.TileEntities[]'):
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

    def replace_blocks(self, pos1, pos2, old_blocks, new_block):
        """
        Replace old_blocks from pos1 to pos2 (x, y, z).

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
        min_x = min(pos1[0], pos2[0])
        min_y = min(pos1[1], pos2[1])
        min_z = min(pos1[2], pos2[2])

        max_x = max(pos1[0], pos2[0])
        max_y = max(pos1[1], pos2[1])
        max_z = max(pos1[2], pos2[2])

        required_cy_sections = tuple(bounded_range(min_y, max_y, 0, 256, 16))

        for rz in range(min_z//512, max_z//512+1):
            for rx in range(min_x//512, max_x//512+1):
                region_path = os.path.join(self.path, "region", f"r.{rx}.{rz}.mca")

                if not os.path.isfile(region_path):
                    raise FileNotFoundError(f'No such region {rx},{rz} in world {self.path}')

                with nbt.RegionFile(region_path) as region:
                    for cz in bounded_range(min_z, max_z, rz, 512, 16):
                        for cx in bounded_range(min_x, max_x, rx, 512, 16):
                            chunk = region.load_chunk(cx, cz)
                            required_sections_left = set(required_cy_sections)

                            # Handle blocks - eventually liquids, lighting, etc will be handled here too
                            for section in chunk.body.iter_multipath('Level.Sections[]'):
                                cy = section.at_path("Y").value
                                if cy not in required_sections_left:
                                    continue
                                required_sections_left.remove(cy)
                                blocks = BlockArray.from_nbt(section, block_map)

                                for by in bounded_range(min_y, max_y, cy, 16):
                                    for bz in bounded_range(min_z, max_z, 32*rz+cz, 16):
                                        for bx in bounded_range(min_x, max_x, 32*rx+cx, 16):
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
                                                    for tile_entity in chunk.body.iter_multipath('Level.TileEntities[]'):
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

    def restore_chunks(self, old_world, chunk_coords):
        """Restore chunks from an old world into a new world.

        chunk_coords is an iterable of cx,cz tuples.
        """
        # Speed up processing by handling one region file at a time.
        chunks_by_region = {}
        for cx, cz in chunk_coords:
            rx, cx = divmod(cx, 32)
            rz, cz = divmod(cz, 32)
            region = (rx, rz)
            chunk = (cx, cz)

            if region not in chunks_by_region:
                chunks_by_region[region] = []
            chunks_by_region[region].append(chunk)

        for rx, rz in chunks_by_region:
            new_region_path = os.path.join(self.path, "region", f"r.{rx}.{rz}.mca")
            old_region_path = os.path.join(old_world.path, "region", f"r.{rx}.{rz}.mca")

            if not os.path.isfile(new_region_path):
                raise FileNotFoundError(f'No such region {rx},{rz} in world {self.path}')
            if not os.path.isfile(old_region_path):
                raise FileNotFoundError(f'No such region {rx},{rz} in world {old_world.path}')

            with nbt.RegionFile(new_region_path) as new_region:
                with nbt.RegionFile(old_region_path) as old_region:
                    for cx, cz in chunks_by_region[(rx, rz)]:
                        new_region.restore_chunk(old_region, cx, cz)

    def restore_area(self, pos1, pos2, old_world):
        """
        Restore the area in pos1, po2 in this world
        to how it was in old_world at the same coordinates.

        In this version:
        - Restoring an area that's missing in one world or the other results in an error
        - This MAY include subchunks, testing required. In this case, F3+G to show chunk
          borders, the blue lines mark subchunks. Make sure each subchunk has at least
          one block in it, and this should work fine. Air and air variants don't count.
        """
        min_x = min(pos1[0], pos2[0])
        min_y = min(pos1[1], pos2[1])
        min_z = min(pos1[2], pos2[2])

        max_x = max(pos1[0], pos2[0])
        max_y = max(pos1[1], pos2[1])
        max_z = max(pos1[2], pos2[2])

        required_cy_sections = tuple(bounded_range(min_y, max_y, 0, 256, 16))

        for rz in range(min_z//512, max_z//512+1):
            for rx in range(min_x//512, max_x//512+1):
                new_region_path = os.path.join(self.path, "region", f"r.{rx}.{rz}.mca")
                old_region_path = os.path.join(old_world.path, "region", f"r.{rx}.{rz}.mca")

                if not os.path.isfile(new_region_path):
                    raise FileNotFoundError(f'No such region {rx},{rz} in world {self.path}')
                if not os.path.isfile(old_region_path):
                    raise FileNotFoundError(f'No such region {rx},{rz} in world {old_world.path}')

                with nbt.RegionFile(new_region_path) as new_region:
                    with nbt.RegionFile(old_region_path) as old_region:
                        for cz in bounded_range(min_z, max_z, rz, 512, 16):
                            for cx in bounded_range(min_x, max_x, rx, 512, 16):
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

                                for new_chunk_section in new_chunk.body.iter_multipath('Level.Sections[]'):
                                    cy = new_chunk_section.at_path("Y").value
                                    if len(bounded_range(min_y, max_y, cy, 16)) == 0:
                                        continue
                                    new_chunk_sections[cy] = new_chunk_section

                                for old_chunk_section in old_chunk.body.iter_multipath('Level.Sections[]'):
                                    cy = old_chunk_section.at_path("Y").value
                                    if len(bounded_range(min_y, max_y, cy, 16)) == 0:
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

                                    for by in set(range(16)).difference(set(bounded_range(min_y, max_y, cy, 16))):
                                        for bz in set(range(16)).difference(set(bounded_range(min_z, max_z, 32*rz+cz, 16))):
                                            for bx in set(range(16)).difference(set(bounded_range(min_x, max_x, 32*rx+cx, 16))):
                                                index = 256 * by + 16 * bz + bx
                                                old_blocks[index] = {'name': 'minecraft:air'}

                                    new_chunk.body.at_path('Level.Sections').value.append(old_section)

                                for cy in new_only_sections:
                                    # Blocks need deleting if in bounds
                                    new_section = new_chunk_sections[cy]
                                    new_blocks = BlockArray.from_nbt(new_section, block_map)

                                    for by in bounded_range(min_y, max_y, cy, 16):
                                        for bz in bounded_range(min_z, max_z, 32*rz+cz, 16):
                                            for bx in bounded_range(min_x, max_x, 32*rx+cx, 16):
                                                index = 256 * by + 16 * bz + bx
                                                new_blocks[index] = {'name': 'minecraft:air'}

                                for cy in common_sections:
                                    # copy in-bounds blocks
                                    new_section = new_chunk_sections[cy]
                                    old_section = old_chunk_sections[cy]

                                    new_blocks = BlockArray.from_nbt(new_section, block_map)
                                    old_blocks = BlockArray.from_nbt(old_section, block_map)

                                    # TODO: This seems at least partially broken in 1.15
                                    # new_section.at_path('BlockLight').value = old_section.at_path('BlockLight').value
                                    # new_section.at_path('SkyLight').value = old_section.at_path('SkyLight').value

                                    for by in bounded_range(min_y, max_y, cy, 16):
                                        for bz in bounded_range(min_z, max_z, 32*rz+cz, 16):
                                            for bx in bounded_range(min_x, max_x, 32*rx+cx, 16):
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
                                    if old_chunk.body.has_path(f'Level.{category}'):
                                        for tile_entity in old_chunk.body.iter_multipath(f'Level.{category}[]'):
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
                                    if new_chunk.body.has_path(f'Level.{category}'):
                                        for tile_entity in new_chunk.body.iter_multipath(f'Level.{category}[]'):
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

                                    if new_chunk.body.has_path(f'Level.{category}'):
                                        if len(NewEntities) == 0:
                                            new_chunk.body.at_path('Level').value.pop(category)
                                        else:
                                            new_chunk.body.at_path(f'Level.{category}').value = NewEntities
                                    elif len(NewEntities) > 0:
                                        new_chunk.body.at_path('Level').value[category] = nbt.TagList(NewEntities)

                                new_region.save_chunk(new_chunk)
