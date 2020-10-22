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
        self.find_region_files()
        self._player_paths = None
        self._scoreboard = None
        self.find_data_packs()

    def save(self):
        self.level_dat_file.save(os.path.join(self.path, 'level.dat'))

    def find_region_files(self):
        self.region_files = []

        for filename in os.listdir(os.path.join(self.path, 'region')):
            filename_parts = filename.split('.')
            if (
                len(filename_parts) != 4 or
                filename_parts[0] != 'r' or
                filename_parts[3] != 'mca'
            ):
                continue
            try:
                coords = (
                    int(filename_parts[1]),
                    int(filename_parts[2])
                )
                self.region_files.append(coords)
            except:
                pass

    def iter_region_files(self, min_x=None, min_z=None, max_x=None, max_z=None):
        """Iterate over region files, optionally within a range.

        min/max_x/z may be any real value in blocks, inclusive to inclusive.
        yields (rx, rz, full_region_file_path)
        """
        regions_dir = os.path.join(self.path, 'region')
        if not os.path.isdir(regions_dir):
            # Region file folder does not exist
            return

        for filename in os.listdir(regions_dir):
            filename_parts = filename.split('.')
            if (
                len(filename_parts) != 4 or
                filename_parts[0] != 'r' or
                filename_parts[3] != 'mca'
            ):
                continue

            try:
                rx = int(filename_parts[1])
                rz = int(filename_parts[2])
            except ValueError:
                continue

            if ((isinstance(min_x, numbers.Real) and rx < int(min_x)//512) or
                (isinstance(min_z, numbers.Real) and rz < int(min_z)//512) or
                (isinstance(max_x, numbers.Real) and int(max_x)//512 < rx) or
                (isinstance(max_z, numbers.Real) and int(max_z)//512 < rz)):
                continue

            yield (rx, rz, os.path.join(regions_dir, filename))

    def iter_regions(self, min_x=None, min_z=None, max_x=None, max_z=None):
        """Iterate over regions, optionally within a range.

        min/max_x/z may be any real value in blocks, inclusive.
        yields nbt.RegionFile
        """
        for rx, rz, region_file in self.iter_region_files(min_x, min_z, max_x, max_z):
            yield (rx, rz, nbt.RegionFile(region_file))

    def iter_chunks(self, min_x=None, min_z=None, max_x=None, max_z=None):
        """Iterate over chunks, optionally within a range.

        min/max_x/z may be any real value in blocks, inclusive.
        Saving is left to the calling function.
        yields (cx, cz, chunk_NBT, save_callback)
        """
        if min_x is None and min_z is None and max_x is None and max_z is None:
            # Compute region boundaries for the world
            xregions = [r[0] for r in self.region_files]
            zregions = [r[1] for r in self.region_files]

            min_x = min(xregions) * 512
            max_x = (max(xregions) + 1) * 512
            min_z = min(zregions) * 512
            max_z = (max(zregions) + 1) * 512
        elif min_x is None or min_z is None or max_x is None or max_z is None:
            raise Exception("Only one iteration corner was specified!")

        min_cx = int(min_x)//16
        min_cz = int(min_z)//16
        max_cx = int(max_x)//16
        max_cz = int(max_z)//16

        for rx, rz, region in self.iter_regions(min_x, min_z, max_x, max_z):
            min_cx_in_r = max(min_cx - 32*rx, 0)
            max_cx_in_r = min(max_cx - 32*rx, 31)
            min_cz_in_r = max(min_cz - 32*rz, 0)
            max_cz_in_r = min(max_cz - 32*rz, 31)

            for cz_in_r in range(min_cz_in_r, max_cz_in_r+1):
                cz = 32*rz + cz_in_r
                for cx_in_r in range(min_cx_in_r, max_cx_in_r+1):
                    cx = 32*rx + cx_in_r

                    chunk = region.load_chunk(cx_in_r, cz_in_r)
                    if chunk is not None:
                        yield (cx, cz, chunk.body, lambda : region.save_chunk(chunk))

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
                        self._player_paths.append(os.path.join(player_data_path, filename))
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

        for entity, pos, entity_path in world.tile_entity_iterator():
            entity.tree()
        '''
        return RecursiveEntityIterator(self, pos1=pos1, pos2=pos2, readonly=readonly, no_players=no_players, players_only=players_only)

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

    def prune(self):
        """
        Prune this world of region files that are 100% empty, meaning:
        - No entities
        - No block entities
        - No block light
        - No blocks other than air
        - It otherwise fails to load at all.
        Everything else is left intact.
        """
        regions_scanned = 0
        deleted = 0
        print("Deleting completely empty region files:")
        for region_coord in self.region_files:
            print("Scanned {}/{} region files.".format(regions_scanned, len(self.region_files)))
            regions_scanned += 1
            confirmed_valid = False
            rx, rz = region_coord

            region_path = os.path.join(self.path, "region", f"r.{rx}.{rz}.mca")

            if not os.path.isfile(region_path):
                continue

            with nbt.RegionFile(region_path) as region:
                for cz in range(0, 32):
                    if confirmed_valid:
                        break

                    for cx in range(0, 32):
                        if confirmed_valid:
                            break

                        try:
                            chunk = region.load_chunk(cx, cz)
                            chunk_sections = chunk.body.at_path('Level.Sections').value
                        except:
                            continue

                        # Check if there are entities (fast check)
                        if chunk.body.count_multipath('Level.Entities[]') > 0:
                            confirmed_valid = True
                            break

                        # Check if there are tile entities (fast check)
                        if chunk.body.count_multipath('Level.TileEntities[]') > 0:
                            confirmed_valid = True
                            break

                        for section in chunk_sections:
                            # TODO: Needs updating for 1.15
                            # # Check block light > 0
                            # for block_light in section.iter_multipath('BlockLight[]'):
                            #     if block_light > 0:
                            #         confirmed_valid = True
                            #         break
                            #
                            # if confirmed_valid:
                            #     break

                            # Check for non-air block
                            # This is an expensive check, keep it low priority

                            # TODO: This try is sketchy
                            try:
                                blocks = BlockArray.from_nbt(section, block_map)
                                for block in blocks:
                                    if block['name'] != "minecraft:air":
                                        confirmed_valid = True
                                        break
                            except IndexError:
                                print("Warning: unable to iterate blocks. Assuming region is valid")
                                confirmed_valid = True

            if not confirmed_valid:
                deleted += 1
                os.remove(region_path)
                print("- Completely empty; deleted.")

        print(f"Scanned {regions_scanned}/{len(self.region_files)} region files.")
        self.find_region_files()
        print(f"Deleted {deleted} empty region files.")

    @property
    def scoreboard(self):
        if not self._scoreboard:
            self._scoreboard = Scoreboard(os.path.join(self.path, "data", "scoreboard.dat"))
        return self._scoreboard

    def dump_command_blocks(self, pos1, pos2, log=None):
        """
        Finds all command blocks between pos1 and pos2,
        and displays what they contain. (WIP)
        """
        min_x = min(pos1[0], pos2[0])
        min_y = min(pos1[1], pos2[1])
        min_z = min(pos1[2], pos2[2])

        max_x = max(pos1[0], pos2[0])
        max_y = max(pos1[1], pos2[1])
        max_z = max(pos1[2], pos2[2])

        required_cy_sections = tuple(bounded_range(min_y, max_y, 0, 256, 16))

        command_blocks = []

        if log:
            log_file = open(log, 'w')

        for rz in range(min_z//512, max_z//512+1):
            for rx in range(min_x//512, max_x//512+1):
                region_path = os.path.join(self.path, "region", f"r.{rx}.{rz}.mca")

                if not os.path.isfile(region_path):
                    continue

                with nbt.RegionFile(region_path) as region:
                    for cz in bounded_range(min_z, max_z, rz, 512, 16):
                        for cx in bounded_range(min_x, max_x, rx, 512, 16):
                            try:
                                chunk = region.load_chunk(cx, cz)

                                if not chunk.body.has_path('Level.TileEntities'):
                                    continue

                                # Load the blocks in the chunk sections now in case we find command block entities
                                chunk_sections = {}
                                for section in chunk.body.iter_multipath('Level.Sections[]'):
                                    cy = section.at_path("Y").value
                                    if cy not in required_cy_sections:
                                        continue
                                    chunk_sections[cy] = BlockArray.from_nbt(section, block_map)

                                #blocks[256 * by + 16 * bz + bx] = block['block']

                                for tile_entity in chunk.body.iter_multipath('Level.TileEntities[]'):
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
                                        log_file.write('{tile_x:>7} {tile_y:>7} {tile_z:>7} {block_id:<36}{reason:<25}{Command}\n')

                            except BufferUnderrun:
                                # Chunk not loaded
                                pass

        if log:
            log_file.close()
        return(command_blocks)

    def get_block(self, pos):
        """
        Get the block at position (x, y, z).
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
        x, y, z = (int(pos[0]), int(pos[1]), int(pos[2]))
        # bx, by, bz are block coordinates within the chunk section
        rx, bx = divmod(x, 512)
        by = y
        rz, bz = divmod(z, 512)
        cx, bx = divmod(bx, 16)
        cy, by = divmod(by, 16)
        cz, bz = divmod(bz, 16)

        region_path = os.path.join(self.path, "region", f"r.{rx}.{rz}.mca")

        with nbt.RegionFile(region_path) as region:
            chunk = region.load_chunk(cx, cz)
            section_not_found = True
            for section in chunk.body.iter_multipath('Level.Sections[]'):
                if section.at_path('Y').value == cy:
                    section_not_found = False
                    blocks = BlockArray.from_nbt(section, block_map)

                    result = {'block':blocks[256 * by + 16 * bz + bx]}
                    if chunk.body.has_path('Level.TileEntities'):
                        for tile_entity in chunk.body.iter_multipath('Level.TileEntities[]'):
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

    def set_block(self, pos, block):
        """
        Set a block at position (x, y, z).
        Example block:
        {'block': {'snowy': 'false', 'name': 'minecraft:grass_block'} }

        In this version:
        - All block properties are mandatory (no defaults are filled in for you)
        - Block NBT cannot be set, but can be read.
        - Existing block NBT for the specified coordinate is cleared.
        - Liquids are not yet supported
        """
        x, y, z = pos
        # bx, by, bz are block coordinates within the chunk section
        rx, bx = divmod(x, 512)
        by = y
        rz, bz = divmod(z, 512)
        cx, bx = divmod(bx, 16)
        cy, by = divmod(by, 16)
        cz, bz = divmod(bz, 16)

        region_path = os.path.join(self.path, "region", f"r.{rx}.{rz}.mca")

        with nbt.RegionFile(region_path) as region:
            chunk = region.load_chunk(cx, cz)
            for section in chunk.body.iter_multipath('Level.Sections[]'):
                if section.at_path('Y').value == cy:
                    blocks = BlockArray.from_nbt(section, block_map)
                    blocks[256 * by + 16 * bz + bx] = block['block']

                    if chunk.body.has_path('Level.TileEntities'):
                        NewTileEntities = []
                        for tile_entity in chunk.body.iter_multipath('Level.TileEntities[]'):
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
