#!/usr/bin/env python3

import copy
import os
import numpy
import sys

this_folder = os.path.dirname(os.path.realpath(__file__))

sys.path.append(this_folder)
from condition import BaseConditionList
from entry import BaseEntryList

# datapack folder
sys.path.append(os.path.join(this_folder, "../"))
from util import PlaceholderNumberOrRandom

class Pool(object):
    """A loot table pool."""
    def __init__(self, entry):
        """Load the pool from a dict.

        A description of the arguements goes here.
        """
        if isinstance(entry, type(self)):
            self._dict = copy.deepcopy(entry._dict)

        elif isinstance(entry, dict):
            self._dict = copy.deepcopy(entry)

        else:
            raise TypeError("Expected pool to be type dict.")

        self.conditions = BaseConditionList(self._dict.get('conditions', []))
        self.rolls = PlaceholderNumberOrRandom(self._dict['rolls'])
        self.bonus_rolls = PlaceholderNumberOrRandom(self._dict['bonus_rolls'])
        self.entries = BaseEntryList(self._dict.get('entries', []))

    def generate(self, generation_state):
        """Generate a pool entry as part of generating loot from a loot table."""
        if self.conditions.test(generation_state):
            self._generate(generation_state)

    def _generate(self, generation_state):
        """Generate a pool entry after confirming the conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this pool does"""
        NotImplemented

    def __repr__(self):
        return "{name}({pool})".format(name=self.__class__.__name__, pool=self._dict)

