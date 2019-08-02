#!/usr/bin/env python3

import copy
import os
import json
import random
import sys

this_folder = os.path.dirname(os.path.realpath(__file__))

# temp lib_py3 folder
sys.path.append(os.path.join(this_folder, "../../../"))
from lib_py3.minecraft.datapack.util import TestNumberOrRange

# quarry folder
sys.path.append(os.path.join(this_folder, "../../../../../quarry"))
from quarry.types import nbt

class BaseCondition(object):
    """A loot table condition.

    This is the base class, and is not intended to be used directly, except to get subclasses.
    Subclass names are CaseSensitive, and must match the IDs used by Minecraft itself.
    """
    def __init__(self, condition):
        """Load the condition from a dict.

        A description of the arguements goes here.
        """
        if isinstance(condition, type(self)):
            self._dict = copy.deepcopy(condition._dict)

        elif isinstance(condition, dict):
            self._dict = copy.deepcopy(condition)

        else:
            raise TypeError("Expected condition to be type dict.")

    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented

    def __repr__(self):
        return "{name}({condition})".format(name=self.__class__.__name__, condition=self._dict)

    @classmethod
    def recursive_public_subclasses(cls):
        """Return a dict of subclasses by name, not listing subclasses starting with '_'.

        Should multiple subclasses need to be derived from another subclass,
        a base subclass whose name starts with '_' should be created so
        its children are returned, but not the base subclass itself.
        """
        result = {}

        for subclass in cls.__subclasses__():
            name = subclass.__name__

            # Ignore subclasses that exist only as a parent to other subclasses
            if not name.startswith("_") and not name.startswith("Base"):
                if name in result:
                    raise KeyError("Subclass with the name {!r} appears more than once.".format(name))

                result[name] = subclass

            subsubclasses = subclass.recursive_public_subclasses()

            for name, subsubclass in subsubclasses.items():
                if name in result:
                    raise KeyError("Subclass with the name {!r} appears more than once.".format(name))

                result[name] = subclass

        return result


class BaseConditionList(BaseCondition):
    """Joins conditions from parameter terms with "and"."""
    def __init__(self, condition):
        """Load the condition from a ~~dict~~ list of dicts.

        type(condition["terms"]) == list: A list of conditions to join using 'and'.
        """
        if isinstance(condition, type(self)):
            self._list = copy.deepcopy(condition._list)

        elif isinstance(condition, list):
            self._list = copy.deepcopy(condition)

        else:
            raise TypeError("Expected condition list to be type list.")

        # self._dict is really the list of dicts
        self.conditions = []
        for child_dict in self._list:
            child = load_condition(child_dict)
            self.conditions.append(child)

    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        result = True
        while result:
            result = self.conditions.test(generation_state)
        return result

    def description(self):
        """A description of what this condition requires"""
        result = ["Confirm all of these are true:", []]
        for condition in self.conditions:
            result[1] += condition.description()
        return result


class alternative(BaseConditionList):
    """Joins conditions from parameter terms with "or"."""
    def __init__(self, condition):
        """Load the condition from a ~~dict~~ list of dicts.

        type(condition["terms"]) == list: A list of conditions to join using 'or'.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table.

        TODO Check what happens when no entries are provided
        """
        result = False
        while not result:
            result = self.conditions.test(generation_state)
        return result

    def description(self):
        """A description of what this condition requires"""
        result = ["Confirm any of these are true:", []]
        for condition in self.conditions:
            result[1] += condition.description()
        return result


class block_state_property(BaseCondition):
    """Checks whether the broken block had a specific block state."""
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["block"]) == str: A block ID. Test will fail if broken block doesn't match.
        type(condition["properties"]) == dict: (Optional) A map of block property names to values. All values are strings. Test will fail if broken block doesn't match.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class damage_source_properties(BaseCondition):
    """Check properties of damage source.

    More info needed!
    """
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["properties"]) == dict: map of property:value pairs.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class entity_present(BaseCondition):
    """Returns true if entity is set."""
    def __init__(self, condition):
        """Load the condition from a dict.

        No extra arguements are needed.
        """
        super().__init__(condition)
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class entity_properties(BaseCondition):
    """Test properties of an entity."""
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["entity"]) == str: Specifies the entity to check for the condition. Set to `this` to use the entity that died or the player that gained the advancement, opened the container or broke the block, `killer` for the killer, or `killer_player` for a killer that is a player.

        type(condition["predicate"]) == dict: Predicate applied to location, uses same structure as advancements.
        type(condition["predicate"]["flags"]) == dict: Predicate Flags to be checked.
        type(condition["predicate"]["flags"]["is_on_fire"]) in (True, False): Test whether the entity is or is not on fire.
        type(condition["predicate"]["flags"]["is_sneaking"]) in (True, False): Test whether the entity is or is not sneaking.
        type(condition["predicate"]["flags"]["is_sprinting"]) in (True, False): Test whether the entity is or is not sprinting.
        type(condition["predicate"]["flags"]["is_swimming"]) in (True, False): Test whether the entity is or is not swimming.
        type(condition["predicate"]["flags"]["is_baby"]) in (True, False): Test whether the entity is or is not a baby variant.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class entity_scores(BaseCondition):
    """Test the scoreboard scores of an entity."""
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["entity"]) == str: Specifies the entity to check for the condition. Set to `this` to use the entity that died or the player that gained the advancement, opened the container or broke the block, `killer` for the killer, or `killer_player` for a killer that is a player.
        type(condition["scores"]) == dict: Scores to check. All specified scores must pass for the condition to pass. Keys are objective names.

        type(score) == int: Key name is the objective while the value is the exact score value required for the condition to pass.
        type(score) == dict: Key name is the objective while the value specifies a range of score values required for the condition to pass.

        type(score["min"]) == int: Minimum score.
        type(score["max"]) == int: Maximum score.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class inverted(BaseCondition):
    """Inverts condition from parameter term."""
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["term"]) == dict: The condition to be negated.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class killed_by_player(BaseCondition):
    """Test if a `killer_player` entity is available."""
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["inverse"]) in (True, False): If true, the condition passes if `killer_player` is not available.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class location_check(BaseCondition):
    """Checks if the current location matches."""
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["predicate"]) == dict: Predicate applied to location, uses same structure as advancements.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class match_tool(BaseCondition):
    """Checks the tool used to generate loot."""
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["predicate"]) == dict: Predicate applied to item, uses same structure as advancements.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class random_chance(BaseCondition):
    """Test if a random number 0.0–1.0 is less than a specified value."""
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["chance"]) == float: Success rate as a number 0.0–1.0.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class random_chance_with_looting(BaseCondition):
    """Test if a random number 0.0–1.0 is less than a specified value, affected by the level of Looting on the `killer` entity."""
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["chance"]) == float: Base success rate.
        type(condition["looting_multiplier"]) == float: Looting adjustment to the base success rate. Formula is `chance + (looting_level * looting_multiplier)`.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class survives_explosion(BaseCondition):
    """Returns true with 1/explosion radius probability."""
    def __init__(self, condition):
        """Load the condition from a dict.

        No extra arguements are needed.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class table_bonus(BaseCondition):
    """Passes with probability picked from table, indexed by enchantment level."""
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["enchantment"]) == str: Id of enchantment.
        type(condition["chances"]) == list: List of probabilities for enchantment level, indexed from 0.
        type(condition["chances"][i]) == float: Success rate as a number 0.0–1.0.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class tool_enchantment(BaseCondition):
    """Test the tool's enchantments."""
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["enchantments"]) == list: List of enchantments the tool must have.
        type(condition["enchantments"][i]) == dict: An enchantment.

        type(enchantment["enchantment"]) == str: The enchantment name ID.
        type(enchantment["levels"]) == dict: The level this enchantment has to be.

        type(enchantment["levels"]["min"]) == int: The minimum level.
        type(enchantment["levels"]["max"]) == int: The maximum level.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


class weather_check(BaseCondition):
    """Checks for a current wheather state."""
    def __init__(self, condition):
        """Load the condition from a dict.

        type(condition["raining"]) in (True, False): If true, the condition evaluates to true only if it's raining.
        type(condition["thundering"]) in (True, False): If true, the condition evaluates to false only if it's thundering.
        """
        super().__init__(condition)
        NotImplemented
    
    def test(self, generation_state):
        """Do the test as part of generating loot from a loot table."""
        NotImplemented

    def description(self):
        """A description of what this condition requires"""
        NotImplemented


conditions = BaseCondition.recursive_public_subclasses()

def load_condition(condition):
    """Loads a condition, determining the appropriate type automatically."""
    condition_type = condition['condition']
    condition_class = conditions[condition_type]
    return condition_class(condition)

