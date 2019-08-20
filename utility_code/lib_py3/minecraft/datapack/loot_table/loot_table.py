#!/usr/bin/env python3

import copy
import os
import numpy
import sys

this_folder = os.path.dirname(os.path.realpath(__file__))

sys.path.append(this_folder)
from pool import Pool

class LootTable(object):
    """A loot table."""
    type_descriptions = {
        'empty': """Generates no items.""",
        'entity': """Generates items from an entity.""",
        'block': """Generates items from a block.""",
        'chest': """Generates items from a chest.""",
        'fishing': """Generates items from fishing.""",
        'advancement_reward': """Generates items from an advancement reward.""",
        'generic': """Generates items from any source."""
    }

    def __init__(self, loot_table):
        """Load the loot table from a dict.

        A description of the arguements goes here.
        """
        if isinstance(entry, type(self)):
            self._dict = copy.deepcopy(entry._dict)

        elif isinstance(entry, dict):
            self._dict = copy.deepcopy(entry)

        else:
            raise TypeError("Expected loot table to be type dict.")

        self.type = self._dict.get('type', 'generic')
        self.pools = [Pool(pool) for pool in self._dict.get('pools', [])]

    def generate(self, generation_state):
        """Generate a pool entry as part of generating loot from a loot table."""
        if self.conditions.test(generation_state):
            self._generate(generation_state)

    def _generate(self, generation_state):
        """Generate a pool entry after confirming the conditions are met."""
        if len(self.entries) == 0:
            # Generate nothing
            return

        # There is at least one entry to generate
        luck = 0 # TODO Get this from generation state
        rolls = self.rolls + bonus_rolls * luck
        weights = [max(0, entry.get_weight(generation_state)) for entry in self.entries]
        total_weight = sum(weights)

        if total_weight == 0:
            # Nothing would generate
            return

        for entry in random.choice(self.entries, replace=True, size=rolls, p=[vote/total_votes for vote in vote_scores]):
            # TODO see what happens when an entry fails; re-roll?
            entry.generate(generation_state)

    def description(self):
        """A description of what this pool does"""
        NotImplemented

    def __repr__(self):
        return "{name}({pool})".format(name=self.__class__.__name__, pool=self._dict)

