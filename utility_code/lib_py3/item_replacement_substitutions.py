#!/usr/bin/env python3

import os
import sys

import json
import traceback

from lib_py3.common import always_equal
from lib_py3.common import eprint
from lib_py3.common import get_item_name_from_nbt
from lib_py3.common import parse_name_possibly_json
from lib_py3.common import unformat_text

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt
from quarry.types.text_format import unformat_text

class SubstitutionRule(object):
    """
    Base substitution rule for item replacements, used to preserve and edit data.
    """
    # Edit this for all new objects:
    name = "Undefined substitution rule"

    def __init__(self):
        """
        Local data storage
        """
        pass

    def process(self, item_meta, item):
        """
        Read the item details.
        Edit item name and ID here, and it will change
        which item NBT is used for replacements.
        """
        pass

    @classmethod
    def recursive_public_subclasses(cls):
        """Return a list of initialized subclasses, not listing subclasses starting with '_'.

        Should multiple subclasses need to be derived from another subclass,
        a base subclass whose name starts with '_' should be created so
        its children are returned, but not the base subclass itself.
        """
        result = []

        for subclass in cls.__subclasses__():
            name = subclass.__name__

            # Ignore subclasses that exist only as a parent to other subclasses
            if not name.startswith("_"):
                result.append(subclass())

            result += subclass.recursive_public_subclasses()

        return result

substitution_rules = []

################################################################################
# Substitution rules begin

class FixBrokenSectionSymbols(SubstitutionRule):
    name = "Fix broken section symbols"

    def _fix(self,old_str):
        return old_str.replace(chr(0xfffd), chr(0xa7))

    def process(self, item_meta, item):
        # Name
        if not item.has_path('tag.display.Name'):
            return
        name = item.at_path('tag.display.Name').value
        new_name = self._fix(name)
        item.at_path('tag.display.Name').value = new_name
        item_meta['name'] = unformat_text(parse_name_possibly_json(new_name))

        # Lore lines
        if item.has_path('tag.display.Lore'):
            for lore_line in item.at_path('tag.display.Lore').value:
                lore = lore_line.value
                new_lore = self._fix(lore)
                lore_line.value = new_lore

class FixDoubleJsonNames(SubstitutionRule):
    name = "Fixed json in json names"

    def process(self, item_meta, item):
        try:
            if not item.has_path('tag.display.Name'):
                return
            name = item.at_path('tag.display.Name').value
            name_json = parse_name_possibly_json(name)
            name_json_json = parse_name_possibly_json(name_json)
            if name_json != name_json_json:
                item.at_path('tag.display.Name').value = name_json
                item_meta['name'] = unformat_text(name_json_json)
        except:
            pass

class SubtituteItems(SubstitutionRule):
    name = "Substitute the ID and name of items, ignoring other NBT"

    def __init__(self):
        self.replacements = {}

        for substitution in [
            #["minecraft:example_item_id", "Example Name", "minecraft:new_id", "Example New Name"],
            #["minecraft:example_banned_item", always_equal, "minecraft:new_id", "Example New Name"],

            ["minecraft:potion", "Antidote", "minecraft:splash_potion", "Antidote"],
            ["minecraft:oak_sapling", "Chimarian Wand", "minecraft:jungle_sapling", "Chimarian Wand"],
            ["minecraft:potion", "Ellixir of the Jaguar", "minecraft:potion", "Elixir of the Jaguar"],
            ["minecraft:golden_chestplate", "Eternal Curiass", "minecraft:golden_chestplate", "Eternal Cuirass"],
            ["minecraft:wooden_shovel", "Graceful Spade", "minecraft:stone_shovel", "Graceful Spade"],
            ["minecraft:stone_shovel", "Pyromancer's Staff", "minecraft:blaze_rod", "Pyromancer's Staff"],
            ["minecraft:leather_helmet", "Starborn Cap", "minecraft:leather_helmet", "Starborn Cap"],
            ["minecraft:potion", "Waycrstal Extract", "minecraft:potion", "Waycrystal Extract"],
            ["minecraft:nether_wart_block", "Nightmare Key", "minecraft:nether_wart_block", "Reverie Key"],
            ["minecraft:dark_oak_leaves", "Bonus Key", "minecraft:dark_oak_leaves", "Willows Key"],
            ["minecraft:iron_bars", "Old Labs Key", "minecraft:iron_bars", "Alchemy Labs Key"],
            ["minecraft:player_head", "Aquiren's Head", "minecraft:player_head", "Aqurien's Head"],
            ["minecraft:dark_oak_leaves", "Willows Key", "minecraft:mossy_cobblestone", "Black Willows Key"],
            ["minecraft:nether_wart_block", "Reverie Key", "minecraft:nether_wart_block", "Malevolent Reverie Key"],
            ["minecraft:white_stained_glass", "White Key", "minecraft:white_concrete", "White Wool Key"],
            ["minecraft:orange_stained_glass", "Orange Key", "minecraft:orange_concrete", "Orange Wool Key"],
            ["minecraft:magenta_stained_glass", "Magenta Key", "minecraft:magenta_concrete", "Magenta Wool Key"],
            ["minecraft:light_blue_stained_glass", "Light Blue Key", "minecraft:light_blue_concrete", "Light Blue Wool Key"],
            ["minecraft:yellow_stained_glass", "Yellow Key", "minecraft:yellow_concrete", "Yellow Wool Key"],
            ["minecraft:lime_stained_glass", "Lime Key", "minecraft:lime_concrete", "Lime Wool Key"],
            ["minecraft:pink_stained_glass", "Pink Key", "minecraft:pink_concrete", "Pink Wool Key"],
            ["minecraft:gray_stained_glass", "Gray Key", "minecraft:gray_concrete", "Gray Wool Key"],
            ["minecraft:light_gray_stained_glass", "Light Gray Key", "minecraft:light_gray_concrete", "Light Gray Wool Key"],
            ["minecraft:cyan_stained_glass", "Cyan Key", "minecraft:cyan_concrete", "Cyan Wool Key"],
            ["minecraft:stone_shovel", "Greyskull's Spellcaster", "minecraft:bone", "Greyskull's Spellcaster"],
            ["minecraft:prismarine_crystals", "Shifting Crystals", "minecraft:quartz", "Shifting Crystals"],
            ["minecraft:leather_leggings", "Sports Leggings", "minecraft:leather_leggings", "Yoga Pants"],
            ["minecraft:iron_sword", "Dutiful Blade", "minecraft:stone_sword", "Dutiful Blade"],
        ]:
            old_id, old_name, new_id, new_name = substitution

            if old_id not in self.replacements:
                self.replacements[old_id] = {}
            id_replacements = self.replacements[old_id]

            id_replacements[old_name] = (new_id, new_name)

    def process(self, item_meta, item):
        if not item.has_path('tag.display.Name'):
            return

        old_id = item_meta['id']
        old_name = item_meta['name']

        # This way around so always_equal works
        for replaceable_id in self.replacements.keys():
            if replaceable_id == old_id:
                # This way around so always_equal works
                for replaceable_name in self.replacements[replaceable_id].keys():
                    if replaceable_name == old_name:
                        new_id, new_name = self.replacements[replaceable_id][replaceable_name]

                        item_meta['id'] = new_id
                        item_meta['name'] = new_name

################################################################################
# Substitution rules end

substitution_rules = SubstitutionRule.recursive_public_subclasses()

