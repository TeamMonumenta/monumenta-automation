#
# Recursive iterator for entities / tile entities everywhere in the world
#

import sys
import os
import re
import json
from uuid import UUID

from lib_py3.iterators.base_chunk_entity_iterator import BaseChunkEntityIterator

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.text_format import unformat_text
from quarry.types.text_format import ansify_text

_single_item_locations = (
    "ArmorItem",
    "Book",
    "ChargedProjectiles", # Crossbows
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
)

def get_name(name, ansii_colors=False):
    name = re.sub(r"\\u0027", "'", name)
    name = re.sub(r"\\u00a7", "§", name)

    # If the name is JSON, parse it down to just the name text
    try:
        name_json = json.loads(name)
        if "text" in name_json:
            name = name_json["text"]
    except:
        pass

    if ansii_colors:
        name = ansify_text(name, show_section=False)
    else:
        name = unformat_text(name)

    return name


def get_debug_string_from_entity_path(entity_path, ansii_colors=False):
    debug_string = ""
    if entity_path is None:
        return "None"

    for location in entity_path:
        if len(debug_string) > 0:
            debug_string += " -> "

        if location.has_path("playerGameType"):
            # This is a player
            uuidint = ((location.at_path("UUIDMost").value & 0xffffffffffffffff) << 64) | (location.at_path("UUIDLeast").value & 0xffffffffffffffff)
            debug_string += "player:" + str(UUID(int=uuidint))
        elif location.has_path("SpawnPotentials"):
            debug_string += "spawner"
            if location.has_path("Pos"):
                debug_string += "  {} {} {}".format(location.at_path("Pos").value[0], location.at_path("Pos").value[1], location.at_path("Pos").value[2])
        elif location.has_path("id"):
            # Not a player
            debug_string += location.at_path("id").value.replace("minecraft:","")

            if location.has_path("Pos"):
                debug_string += "  {} {} {}".format(location.at_path("Pos").value[0].value, location.at_path("Pos").value[1].value, location.at_path("Pos").value[2].value)

            if location.has_path("x"):
                debug_string += "  {} {} {}".format(location.at_path("x").value, location.at_path("y").value, location.at_path("z").value)

            if location.has_path("CustomName"):
                name = get_name(location.at_path("CustomName").value, ansii_colors)

                # Don't print names of things that are just "@" (commands do this a lot apparently)
                if name != "@":
                    debug_string += "  " + name

            if location.has_path("tag.display.Name"):
                name = get_name(location.at_path("tag.display.Name").value, ansii_colors)
                debug_string += "  " + name


    return debug_string

# Scans through an entity's NBT and calls item_found_func(item, arg) for each item found
def scan_entity_for_items(entity_nbt, item_found_func, arg):
    for location in _single_item_locations:
        if entity_nbt.has_path(location):
            item_found_func(entity_nbt.at_path(location), arg)

    for location in _list_item_locations:
        if entity_nbt.has_path(location):
            for item in entity_nbt.at_path(location).value:
                item_found_func(item, arg)

    if entity_nbt.has_path("Offers.Recipes"):
        for item in entity_nbt.at_path("Offers.Recipes").value:
            if item.has_path("buy"):
                item_found_func(item.at_path("buy"), arg)
            if item.has_path("buyB"):
                item_found_func(item.at_path("buyB"), arg)
            if item.has_path("sell"):
                item_found_func(item.at_path("sell"), arg)

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

    def __init__(self, world, pos1=None, pos2=None, readonly=True, no_players=False, players_only=False):
        self._player_iterator = world.players
        self._players_only = players_only
        if not self._players_only:
            self._baseiterator = BaseChunkEntityIterator(world, pos1=pos1, pos2=pos2, readonly=readonly)
        self._readonly = readonly
        self._no_players = no_players

    def __iter__(self):
        """
        Initialize the iterator for use.

        Doing this here instead of in __init__ allows the iterator to potentially be re-used
        """

        # Initialize the player iterator
        self._player_iterator.__iter__()

        # The player who is currently being iterated
        self._player = None

        # Players are iterated first! Keep track of whether they are done.
        # If no_players is set, there are no players to iterate
        self._players_done = self._no_players

        # Initialize the base iterator
        if not self._players_only:
            self._baseiterator.__iter__()

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

        if not self._players_done:
            if len(self._work_stack) == 0:
                if self._player is not None and not self._readonly:
                    # Need to save the previous player
                    self._player.save()
                    self._player = None

                try:
                    # Attempt to get the next player
                    self._player = self._player_iterator.__next__()

                    # Players are just another entity!
                    self._work_stack.append((self._player.player_tag, None, []))

                except StopIteration:
                    # No more players to iterate

                    # Recurse (only should ever happen once)
                    self._players_done = True
                    return self.__next__()

        #
        # NOTE (this is complicated!)
        #
        # If we are still iterating players (_players_done = False), the above
        # code will trigger and guarantee that there is *something* on the work
        # stack - either a player or a tile entity within their inventory
        #
        # That means that the below code to iterate the world will never run
        # while there is still player work to do. Both player and world objects
        # share the exact same tile entity/entity processing
        #

        if len(self._work_stack) == 0 and self._players_only:
            # Only doing players - done
            raise StopIteration

        if len(self._work_stack) == 0:
            # No work left to do - get another entity
            entity = self._baseiterator.__next__()

            # Keep track of where the original entity was. This is useful because nested
            # items mostly don't have position tags
            if entity.has_path('x') and entity.has_path('y') and entity.has_path('z'):
                x = entity.at_path('x').value
                y = entity.at_path('y').value
                z = entity.at_path('z').value
                source_pos = (x, y, z)
            elif entity.has_path('Pos'):
                pos = entity.at_path('Pos').value
                x = pos[0].value
                y = pos[1].value
                z = pos[2].value
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
        if current_entity.has_path("Bees"):
            self._work_stack.append((current_entity.at_path("Bees"), source_pos, entity_path))

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
