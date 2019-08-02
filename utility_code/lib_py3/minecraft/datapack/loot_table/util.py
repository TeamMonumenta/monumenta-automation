#!/usr/bin/env python3

import copy
import math
import os
import sys

class GenerationState(object):
    """The state of the loot being generated."""
    source_descriptions = {
        "fish": "Loot generating from fishing.",
        "kill": "Loot generating from slain entity.",
        "loot": "Loot generating from container or generic source.",
        "mine": "Loot generating from broken block.",
    }

    def __init__(self, target=None, source="loot", player=None, tool=None, entity=None, block=None):
        """Establish the destination and conditions to generate loot.

        target is the container loot is put in, or None to drop on the ground.
        source is one of: 'fish', 'kill', 'loot', 'mine'
        """
        if source not in self.source_descriptions.keys():
            raise KeyError("Invalid loot source {}. Must be one of {}.".format(source, list(self.source_descriptions.keys())))

        self.target = target
        self.source = source
        self.player = player
        self.tool = tool
        self.entity = entity
        self.block = block

    def description(self):
        """A description of what the generation state is."""
        result = []

        result.append(self.source_descriptions.get(self.source, self.source_descriptions["loot"]))

        if self.target is not None:
            result.append("Dropping items on the ground.")

        if self.player is not None:
            raise NotImplemented
            result.append(repr(self.player)) # TODO Make this use a nicer description.

        if self.tool is not None:
            result.append(repr(self.tool)) # TODO Make this use a nicer description.

        if self.entity is not None:
            result.append(repr(self.entity)) # TODO Make this use a nicer description.

        if self.block is not None:
            result.append(repr(self.block)) # TODO Make this use a nicer description.

        return result

    def __repr__(self):
        return "{name}(target={target}, source={source}, player={player}, tool={tool}, entity={entity}, block={block})".format(
            name=self.__class__.__name__,
            target=self.target,
            source=self.source,
            player=self.player,
            tool=self.tool,
            entity=self.entity,
            block=self.block,
        )

