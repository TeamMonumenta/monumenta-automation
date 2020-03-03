#
# Iterator for entities / tile entities stored in region files (without recursion)
#

import os

from quarry.types import nbt

from lib_py3.common import bounded_range

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

        self._regions = set(world.region_files)

        if (not pos1 is None) and (not pos2 is None):
            self._min_x = min(pos1[0],pos2[0])
            self._min_y = min(pos1[1],pos2[1])
            self._min_z = min(pos1[2],pos2[2])

            self._max_x = max(pos1[0],pos2[0])
            self._max_y = max(pos1[1],pos2[1])
            self._max_z = max(pos1[2],pos2[2])

            newregions = set()
            for region in self._regions:
                if (region[0] >= self._min_x // 512
                    and region[0] <= self._max_x // 512
                    and region[1] >= self._min_z // 512
                    and region[1] <= self._max_z // 512):

                    newregions.add(region)

            self._regions = newregions
        else:
            # Compute region boundaries for the world
            xregions = [r[0] for r in world.region_files]
            zregions = [r[1] for r in world.region_files]
            self._min_x = min(xregions) * 512
            self._max_x = (max(xregions) + 1) * 512
            self._min_y = 0
            self._max_y = 255
            self._min_z = min(zregions) * 512
            self._max_z = (max(zregions) + 1) * 512

            # Use the original / unmodified region list

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

            if len(self._regions) <= 0:
                # All done!
                raise StopIteration

            self._rx, self._rz = self._regions.pop()

            # Load the next indicated region (_rx/_rz)
            region_path = os.path.join(self._world.path, "region", "r.{}.{}.mca".format(self._rx, self._rz))

            if not os.path.isfile(region_path):
                # This region file isn't present - no reason to keep a reference for saving
                self._region = None

                # Continue iterating over regions to find the next valid one
                continue

            # Calculate which chunks need to be searched - don't waste time on chunks out of range
            self._cx_range = bounded_range(self._min_x, self._max_x, self._rx, 512, 16)
            self._cx_idx = 0
            self._cz_range = bounded_range(self._min_z, self._max_z, self._rz, 512, 16)
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
                self._first_run = False
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

            # Always zero the work to do first when loading a new chunk with something to do
            self._tile_entities = []
            self._tile_entities_pos = 0
            self._entities = []
            self._entities_pos = 0

            # Chunk contains tile entities
            if self._chunk.body.has_path('Level.TileEntities'):
                # Make note of the tile entities for iterating at the higher level
                self._tile_entities = self._chunk.body.at_path('Level.TileEntities').value

            # Chunk contains regular entities
            if self._chunk.body.has_path('Level.Entities'):
                # Make note of the entities for iterating at the higher level
                self._entities = self._chunk.body.at_path('Level.Entities').value

            # Successfully found next chunk - stop iterating
            break

    def __next__(self):
        """
        Iteratively identifies the next valid tile entity or regular entity and returns it.

        Return value:
            entity - the entity OR tile entity TagCompound

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
                return tile_entity

            # Tile entities are done but somehow we are still here - so there must be entities to do
            entity = self._entities[self._entities_pos]

            # Increment index so regardless of whether this is in range the next step
            # will find the next entity
            self._entities_pos += 1

            if not entity.has_path('Pos'):
                # ????
                # This is a real problem - something has broken the entity to not have a position tag at all
                # Pretty sure this entity will be effectively removed from the world. No reason to iterate it here
                continue

            pos = entity.at_path('Pos').value
            x = pos[0].value
            y = pos[1].value
            z = pos[2].value

            if not (
                self._min_x <= x and x < self._max_x + 1 and
                self._min_y <= y and y < self._max_y + 1 and
                self._min_z <= z and z < self._max_z + 1
            ):
                # This entity isn't in the bounding box
                # Continue iterating until we find one that is
                continue

            # Found a valid entity in range
            return entity

