#!/usr/bin/env python3

import copy
import math
import os
import sys

class GenerationState(object):
    """The state of the loot being generated."""
    def __init__(self, target=None, source='generic', player=None, tool=None, entity=None, block=None):
        """Establish the destination and conditions to generate loot.

        target is the container loot is put in, or None to drop on the ground.
        source is a string like 'loot' or 'kill'
        """
        self.target = target
        self.source = source
        self.player = player
        self.tool = tool
        self.entity = entity
        self.block = block

    def description(self):
        """A description of what the generation state is."""
        NotImplemented

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

