#!/usr/bin/env python3

import copy
import os
import random
import sys

this_folder = os.path.dirname(os.path.realpath(__file__))

sys.path.append(this_folder)
from condition import BaseConditionList

# datapack folder
sys.path.append(os.path.join(this_folder, "../"))
from util import PlaceholderNumberOrRandom

# quarry folder
sys.path.append(os.path.join(this_folder, "../../../../../quarry"))
from quarry.types import nbt

class BaseFunction(object):
    """A loot table function.

    This is the base class, and is not intended to be used directly, except to get subclasses.
    Subclass names are CaseSensitive, and must match the IDs used by Minecraft itself.
    """
    def __init__(self, function):
        """Load the function from a dict.

        A description of the arguements goes here.
        """
        if isinstance(function, type(self)):
            self._dict = copy.deepcopy(function._dict)

        elif isinstance(function, dict):
            self._dict = copy.deepcopy(function)

        else:
            raise TypeError("Expected function to be type dict.")

        self.conditions = BaseConditionList(self._dict.get("conditions", []))

    def run(self, item_stack, generation_state):
        """Run the function as part of generating loot from a loot table."""
        if self.conditions.test(generation_state):
            self._run(item_stack, generation_state)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented

    def __repr__(self):
        return "{name}({function})".format(name=self.__class__.__name__, function=self._dict)

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


class BaseFunctionList(BaseFunction):
    """A list of functions to run in order."""
    def __init__(self, function):
        """Load the function list from a ~~dict~~ list of dicts."""
        if isinstance(function, type(self)):
            self._list = copy.deepcopy(function._list)

        elif isinstance(function, list):
            self._list = copy.deepcopy(function)

        else:
            raise TypeError("Expected function list to be type list.")

        self.conditions = BaseConditionList(self._dict.get("conditions", []))

        self.functions = []
        for subfunction in self._list:
            self.functions.append(load_function(subfunction))

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        for function in self.functions:
            function.run(item_stack, generation_state)

    def description(self):
        """A description of what this function does"""
        result = ["Run the following functions:", []]
        for function in self.functions:
            result[1] += function.description()
        return result

    def __repr__(self):
        return "{name}({function})".format(name=self.__class__.__name__, function=self._dict)


class apply_bonus(BaseFunction):
    """Applies a predefined bonus formula.

    This information is new in 1.14 and is not proven right yet. Use with caution.
    """
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["enchantment"]) == str: Enchantment ID used for level calculation.
        type(function_dict["formula"]) == str: Can be `binomial_with_bonus_count` for a biominal distribution (with `n=level + extra`, `p=probability`), `uniform_bonus_count` for uniform distribution (from `0` to `level * bonusMultiplier`), or `ore_drops` for a special function used for ore drops in the vanilla game `(count * (max(0, random(0..1) - 1) + 1))`. (The wiki mentions these formulas don't make sense; they may be incorrect.)
        type(function_dict["parameters"]) == dict: Values required for the formula.

        type(function_dict["parameters"]["extra"]) == int: 
        type(function_dict["parameters"]["probability"]) == float: 
        type(function_dict["parameters"]["bonusMultiplier"]) == float: 
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class copy_name(BaseFunction):
    """For loot table type 'block', copies a block entity's `CustomName` tag into the item's `display.Name` tag."""
    def __init__(self, function):
        """Load the function from a dict.

        function_dict["source"] == "block_entity":  Needs to be set to 'block_entity'.
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class copy_nbt(BaseFunction):
    """Copies nbt to the item's `tag` tag."""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["source"]) == str: Specifies the source. Set to `block_entity` for the block entity of the destroyed block, `this` to use the entity that died or the player that gained the advancement, opened the container or broke the block, `killer` for the killer, or `killer_player` for a killer that is a player.

        type(function_dict["ops"]) == list: A list of copy operations.
        type(function_dict["ops"][i]) == dict: An operation

        type(operation["source"]) == str: The nbt path to copy from.
        type(operation["target"]) == str: The nbt path to copy to, starting from the item's `tag` tag.
        type(operation["op"]) == str: Can be `replace` to replace any existing contents of the target, `append` to append to a list, or `merge` to merge into a compound tag.
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class enchant_randomly(BaseFunction):
    """Enchants the item with one randomly-selected enchantment. The level of the enchantment, if applicable, will be random."""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["enchantments"]) == list: List of enchantment names to choose from. If omitted, all enchantments applicable to the item will be possible.
        type(function_dict["enchantments"][i]) == str
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class enchant_with_levels(BaseFunction):
    """Enchants the item, with the specified enchantment level (roughly equivalent to using an enchantment table at that level)."""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["treasure"]) in (True, False): Determines whether treasure enchantments are allowed on this item.

        type(function_dict["levels"]) == int: Specifies the exact enchantment level to use.
        type(function_dict["levels"]) == dict: Specifies a random enchantment level within a range.

        type(function_dict["levels"]["min"]) == int: Minimum level to use.
        type(function_dict["levels"]["max"]) == int: Maximum level to use.
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class exploration_map(BaseFunction):
    """Converts an empty map into an explorer map leading to a nearby generated structure."""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["destination"]) == str: The type of generated structure to locate. Accepts any of the `StructureType`s used by the /locate command (case insensitive).
        type(function_dict["decoration"]) == str: The icon used to mark the destination on the map. Accepts any of the map icon text IDs (case insensitive). If `mansion` or `monument` is used, the color of the lines on the item texture will change to match the corresponding explorer map.
        type(function_dict["zoom"]) == int: The zoom level of the resulting map. Defaults to 2.
        type(function_dict["search_radius"]) == int: The size, in chunks, of the area to search for structures. The area checked is square, not circular. Radius 0 causes only the current chunk to be searched, radius 1 causes the current chunk and eight adjacent chunks to be searched, and so on. Defaults to 50.
        type(function_dict["skip_existing_chunks"]) in (True, False): Don't search in chunks that have already been generated. Defaults to true.
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class explosion_decay(BaseFunction):
    """For loot tables of type 'block', removes some items from a stack, if there was an explosion. Each item has a chance of 1/explosion radius to be lost."""
    def __init__(self, function):
        """Load the function from a dict.

        No extra arguements are needed.
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class fill_player_head(BaseFunction):
    """Adds required item tags of a player head"""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["entity"]) == str: Specifies an entity to be used for the player head. Set to `this` to use the entity that died or the player that gained the advancement, opened the container or broke the block, `killer` for the killer, or `killer_player` for a killer that is a player.
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class furnace_smelt(BaseFunction):
    """Smelts the item as it would be in a furnace. Used in combination with the `entity_properties` condition to cook food from animals on death."""
    def __init__(self, function):
        """Load the function from a dict.

        No extra arguements are needed.
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class limit_count(BaseFunction):
    """Limits the count of an item stack."""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["limit"]) == int: Specifies the exact limit to use.
        type(function_dict["limit"]) == dict: Specifies a random limit within a range.

        type(function_dict["limit"]["min"]) == int: Minimum limit to use.
        type(function_dict["limit"]["max"]) == int: Maximum limit to use.
        """
        super().__init__(function)

        if "limit" not in self._dict:
            raise KeyError("No limit specified in limit_count function.")

        self._limit = PlaceholderNumberOrRandom(self._dict["limit"], rand_float=False)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        count = item_stack.count
        limit = self._limit()

        item_stack.count = min(count, limit)

    def description(self):
        """A description of what this function does"""
        return ["Limit item count to no more than ".format(self._limit.description())]


class looting_enchant(BaseFunction):
    """Adjusts the stack size based on the level of the Looting enchantment on the `killer` entity."""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["count"]) == int: Specifies an exact number of additional items per level of looting.
        type(function_dict["count"]) == dict: Specifies a random number (within a range) of additional items per level of looting. Note the random number generated may be fractional, and will be rounded after multiplying by the looting level.

        type(function_dict["count"]["min"]) == int: Minimum increase.
        type(function_dict["count"]["max"]) == int: Maximum increase.

        type(function_dict["limit"]) == int: Specifies the maximum amount of items in the stack after the looting calculation. If the value is 0, no limit is applied.
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class set_attributes(BaseFunction):
    """Add attribute modifiers to the item.

    Oh boy... This isn't getting added any time soon. This should be handled in an Attributes class.
    """
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["modifiers"]) == list
        type(function_dict["modifiers"][i]) == str: A modifier

        type(modifier["name"]) == str: Name of the modifier
        type(modifier["attribute"]) == str: The name of the attribute this modifier is to act upon.
        type(modifier["operation"]) == str: Must be either "addition", "multiply_base" or "multiply_total".

        type(modifier["amount"]) == int: Specifies the exact amount of change of the modifier.
        type(modifier["amount"]) == dict: Specifies a random amount within a range.

        type(modifier["amount"]["min"]) == int: Minimum amount.
        type(modifier["amount"]["max"]) == int: Maximum amount.

        type(modifier["id"]) == str: Optional : UUID of the modifier following. If none specified, a new UUID will be generated.

        type(modifier["slot"]) == str: Slots the item must be in for the modifier to take effect, this value can be one of the following : "mainhand", "offhand", "feet", "legs", "chest", or "head".
        type(modifier["slot"]) == list: One of the listed slots will be chosen randomly.
        type(modifier["slot"][i]) == str: One of the following : "mainhand", "offhand", "feet", "legs", "chest", or "head".
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class set_contents(BaseFunction):
    """For loot tables of type 'block', sets the contents of a container block item to a list of entries."""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["entries"]) == list: The entries to use as contents. (Oh boy, this sounds recursive...)
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class set_count(BaseFunction):
    """Sets the count of an item stack."""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["count"]) == int: Specifies the exact stack size to set.
        type(function_dict["count"]) == dict: Specifies a random stack size within a range.

        type(function_dict["count"]["min"]) == int: Minimum stack size.
        type(function_dict["count"]["max"]) == int: Maximum stack size.
        """
        super().__init__(function)

        if "count" not in self._dict:
            raise KeyError("No count specified in set_count function.")

        self._count = PlaceholderNumberOrRandom(self._dict["count"], rand_float=False)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        item_stack.count = self._count()

    def description(self):
        """A description of what this function does"""
        return ["Set item count to {}".format(self._count.description())]


class set_damage(BaseFunction):
    """Sets the item's damage value (durability) for tools."""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["damage"]) == float: Specifies the damage fraction to set (1.0 is undamaged, 0.0 is zero durability left).
        type(function_dict["damage"]) == dict: Specifies a random damage fraction within a range.

        type(function_dict["damage"]["min"]) == float: Minimum value.
        type(function_dict["damage"]["max"]) == float: Maximum value.
        """
        super().__init__(function)

        if "damage" not in self._dict:
            raise KeyError("No damage specified in set_damage function.")

        self._damage = PlaceholderNumberOrRandom(self._dict["damage"], rand_float=True)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        item_stack.damage = self._damage()

    def description(self):
        """A description of what this function does"""
        return ["Set item damage to {} out of 1.0 durability remaining".format(self._damage.description())]


class set_lore(BaseFunction):
    """Adds lore to the item"""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["lore"]) == list: List of JSON text components. Each list entry represents one line of the lore.
        type(function_dict["entity"]) == str: Specifies the entity to act as the source `@s` in the JSON text component. Set to `this` to use the entity that died or the player that gained the advancement, opened the container or broke the block, `killer` for the killer, or `killer_player` for a killer that is a player.
        type(function_dict["replace"]) in (True, False): If true, replaces all existing lines of lore, if false appends the list.
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class set_name(BaseFunction):
    """Adds display name of the item."""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["name"]) == str: A simple name like with an anvil.
        type(function_dict["name"]) == dict or list: A JSON text component name, allowing color, translations, etc.

        type(function_dict["entity"]): Specifies an entity to act as source `@s` in the JSON text component. Set to `this` to use the entity that died or the player that gained the advancement, opened the container or broke the block, `killer` for the killer, or `killer_player` for a killer that is a player.
        """
        super().__init__(function)

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        NotImplemented

    def description(self):
        """A description of what this function does"""
        NotImplemented


class set_nbt(BaseFunction):
    """Adds NBT data to the item."""
    def __init__(self, function):
        """Load the function from a dict.

        type(function_dict["tag"]) == str: Tag string to add, similar to those used by commands. Note that the first bracket is required and quotation marks need to be escaped using a backslash (`\`).
        """
        super().__init__(function)

        if "tag" not in self._dict:
            raise KeyError("No tag specified in set_nbt function.")

        if not isinstance(self._dict["tag"], str):
            raise TypeError("Tag must be a mojangson string.")

        # This is to check for errors and speed up reuse of this operation.
        self._tag_bin = nbt.from_mojangson(self._dict["tag"]).to_bytes()

    def _run(self, item_stack, generation_state):
        """Run the function after confirming its conditions are met."""
        item_stack.tag = nbt.from_bytes(self._tag_bin)

    def description(self):
        """A description of what this function does"""
        return ["Set item NBT to {}".format(self._dict["tag"])]


functions = BaseFunction.recursive_public_subclasses()

def load_function(function):
    """Loads a function, determining the appropriate type automatically."""
    function_type = function['function']
    function_class = functions[function_type]
    return function_class(function)

