#
# Recursive iterator for entities / tile entities everywhere in the world
#

import sys
import os
import re
import json
from uuid import UUID

from lib_py3.iterators.base_chunk_entity_iterator import BaseChunkEntityIterator
from lib_py3.iterators.iterator_interface import recursive_entity_iterator

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.text_format import unformat_text
from quarry.types.text_format import ansify_text

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
        self._world = world
        self._pos1 = pos1
        self._pos2 = pos2
        self._readonly = readonly
        self._no_players = no_players
        self._players_only = players_only

        self._iter = recursive_entity_iterator(self._world, self._pos1, self._pos2, self._readonly, self._no_players, self._players_only)

    def __iter__(self):
        """
        Initialize the iterator for use.

        Doing this here instead of in __init__ allows the iterator to potentially be re-used
        """
        self._iter = recursive_entity_iterator(self._world, self._pos1, self._pos2, self._readonly, self._no_players, self._players_only)

        return self

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
        return self._iter.__next__()
