import sys
import os

from lib_py3.iterators.recursive_entity_iterator import scan_entity_for_items

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

class SchematicEntityIterator(object):
    """
    This iterator iterates over all entities and tile entities in a schematic
    """

    def __init__(self, schematic, readonly=True):
        if readonly:
            self._schematic = schematic.deep_copy()
        else:
            self._schematic = schematic

    def __iter__(self):
        """
        Initialize the iterator for use.

        Doing this here instead of in __init__ allows the iterator to potentially be re-used
        """

        # Initialize the base iterators
        self._tile_entity_iter = None
        self._entity_iter = None
        if self._schematic.has_path("Schematic.TileEntities"):
            self._tile_entity_iter = iter(self._schematic.at_path("Schematic.TileEntities").value)
        if self._schematic.has_path("Schematic.Entities"):
            self._entity_iter = iter(self._schematic.at_path("Schematic.Entities").value)

        # Use a stack to keep track of what items still need to be processed
        # Both players and in-world entities/tile entities share the same stack for simplicity
        # (since they don't happen at the same time - players first, then world)
        #
        # Contents are tuples:
        # (
        #   entity - TagCompound - Might be an entity, tile entity, or player
        #   source_pos - None or (int, int, int) or (double, double, double) - x/y/z
        #   entity_path - List of objects - the path taken to find the object
        # )
        self._work_stack = []

        return self

    def _scan_item_for_work(self, item, arg):
        """
        Looks at an item and if it contains more tile or block entities,
        add them to the _work_stack
        """
        if item.has_path("tag.BlockEntityTag"):
            self._work_stack.append((item.at_path("tag.BlockEntityTag"), arg[0], arg[1]))

        if item.has_path("tag.EntityTag"):
            self._work_stack.append((item.at_path("tag.EntityTag"), arg[0], arg[1]))

    def __next__(self):
        """
        Iterates over entities embedded in an entity.

        Iteration order is depth-first, returning the higher-level object first then using
        a depth-first iterator into nested sub elements

        Return value is:
            entity - the entity OR tile entity TagCompound
            source_pos - an (x, y, z) tuple of the original entity's position (or None)
            entity_path - a list of all the locations traversed to produce the entity
        """

        if len(self._work_stack) == 0:
            # No work left to do - get another entity
            entity = None
            if self._tile_entity_iter is not None:
                try:
                    entity = self._tile_entity_iter.__next__()
                except StopIteration:
                    # Continue to next, and don't try this iterator again
                    self._tile_entity_iter = None
            if entity is None and self._entity_iter is not None:
                # Nothing to catch here - if this throws StopIteration, let it
                entity = self._entity_iter.__next__()
            if entity is None:
                raise StopIteration

            # Keep track of where the original entity was. This is useful because nested
            # items mostly don't have position tags
            if entity.has_path('x') and entity.has_path('y') and entity.has_path('z'):
                x = entity.at_path('x').value
                y = entity.at_path('y').value
                z = entity.at_path('z').value
                source_pos = (x, y, z)
            elif entity.has_path('Pos'):
                pos = entity.at_path('Pos').value
                x = pos[0]
                y = pos[1]
                z = pos[2]
                source_pos = (x, y, z)
            else:
                source_pos = None

            self._work_stack.append((entity, source_pos, []))

        # Process the next work element on the stack
        current_entity, source_pos, entity_path = self._work_stack.pop()

        # Keep track of the path to get here
        entity_path = entity_path.copy()
        entity_path.append(current_entity)

        # Add more work to the stack for next time
        # Tile entities!
        if current_entity.has_path("SpawnPotentials"):
            for spawn in current_entity.at_path("SpawnPotentials").value:
                if spawn.has_path("Entity"):
                    self._work_stack.append((spawn.at_path("Entity"), source_pos, entity_path))

        if current_entity.has_path("SpawnData"):
            self._work_stack.append((current_entity.at_path("SpawnData"), source_pos, entity_path))

        # Regular entities!
        if current_entity.has_path("Passengers"):
            for passenger in current_entity.at_path("Passengers").value:
                self._work_stack.append((passenger, source_pos, entity_path))

        # Scan items in current entity, and if any are found scan them for nested entities
        scan_entity_for_items(current_entity, self._scan_item_for_work, (source_pos, entity_path));

        return current_entity, source_pos, entity_path

class Schematic(object):
    def __init__(self, path: str):
        name = os.path.basename(path)
        self._schematic_name = os.path.splitext(name)[0]

        nbtfile = nbt.NBTFile.load(path)
        self._schematic = nbtfile.root_tag

    @property
    def name(self):
        return self._schematic_name

    def entity_iterator(self, readonly=True):
        '''
        Returns an iterator of all entities and tile entities in the schematic.
        If readonly=False, modifications during iteration will affect the input schematic
        If readonly=True, modifications will not affect the input schematic

        Usage:

        for entity, pos, entity_path in world.tile_entity_iterator():
            entity.tree()
        '''
        return SchematicEntityIterator(self._schematic, readonly)
