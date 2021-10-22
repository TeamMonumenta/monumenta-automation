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
from lib_py3.common import update_plain_tag

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt
from quarry.types.text_format import unformat_text

class SubstitutionRule(object):
    """Base substitution rule for item replacements, used to preserve and edit data."""
    # Edit this for all new objects:
    name = "Undefined substitution rule"

    def __init__(self):
        """Local data storage"""
        pass

    def process(self, item_meta, item):
        """Edit the item name and ID before doing other replacements.

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

class FixBookTitles(SubstitutionRule):
    name = "Fix book titles"

    def process(self, item_meta, item):
        if item.nbt.has_path('tag.display.Name') or not item.nbt.has_path('tag.title'):
            return
        title = item.tag.at_path('title').value
        item_meta['name'] = unformat_text(parse_name_possibly_json(title))

class FixBrokenSectionSymbols(SubstitutionRule):
    name = "Fix broken section symbols"

    def _fix(self,old_str):
        return old_str.replace(chr(0xfffd), chr(0xa7))

    def process(self, item_meta, item):
        # Name
        if not item.nbt.has_path('tag.display.Name'):
            return
        name = item.tag.at_path('display.Name').value
        new_name = self._fix(name)
        item.tag.at_path('display.Name').value = new_name
        item_meta['name'] = unformat_text(parse_name_possibly_json(new_name))

        # Lore lines
        for lore_line in item.tag.iter_multipath('display.Lore[]'):
            lore = lore_line.value
            new_lore = self._fix(lore)
            lore_line.value = new_lore

class FixDoubleJsonNames(SubstitutionRule):
    name = "Fixed json in json names"

    def process(self, item_meta, item):
        if not item.nbt.has_path('tag.display.Name'):
            return
        name = item.tag.at_path('display.Name').value
        name_json = parse_name_possibly_json(name)
        name_json_json = parse_name_possibly_json(name_json)
        if name_json != name_json_json:
            item.tag.at_path('display.Name').value = name_json
            item_meta['name'] = unformat_text(name_json_json)

class FixEscapedNames(SubstitutionRule):
    name = "Fixed escaped characters in json names"

    def process(self, item_meta, item):
        if not item.nbt.has_path('tag.display.Name'):
            return
        name = item.tag.at_path('display.Name').value
        name = name.replace(r"\\u0027", "'")
        name = name.replace(r"\\u00a7", "§")
        name_json = parse_name_possibly_json(name)
        item.tag.at_path('display.Name').value = name
        item_meta['name'] = unformat_text(name_json)

class FixPlainTag(SubstitutionRule):
    name = "Fix the plain tag"

    def process(self, item_meta, item):
        """Note: This is only useful for items that aren't in the loot tables."""
        if item.nbt.has_path("tag"):
            update_plain_tag(item.nbt.at_path("tag"))

class SubtituteItems(SubstitutionRule):
    name = "Substitute the ID and name of items, ignoring other NBT"

    def __init__(self):
        self.replacements = {}

        for substitution in [
            #["minecraft:example_item_id", "Example Name", "minecraft:new_id", "Example New Name"],
            #["minecraft:example_banned_item", always_equal, "minecraft:new_id", "Example New Name"],

            ["minecraft:bow", "Blazing Crossbow", "minecraft:crossbow", "Blazing Crossbow"],
            ["minecraft:bow", "Heatwave", "minecraft:crossbow", "Heatwave"],
            ["minecraft:bow", "Steel Arbalest", "minecraft:crossbow", "Steel Arbalest"],
            ["minecraft:bow", "Ghastcaller's Gunblade", "minecraft:crossbow", "Ghastcaller's Gunblade"],
            ["minecraft:bow", "Incendiary Inferno", "minecraft:crossbow", "Incendiary Inferno"],
            ["minecraft:bow", "Pirate's Flintlock", "minecraft:crossbow", "Pirate's Flintlock"],
            ["minecraft:bow", "Miner's Flintlock", "minecraft:crossbow", "Miner's Flintlock"],
            ["minecraft:experience_bottle", always_equal, "minecraft:experience_bottle", "Experience Bottle"],
            ["minecraft:bow", "Swiftwood Shortbow", "minecraft:spruce_leaves", "Mistleaf Bracer"],
            ["minecraft:bow", "Swiftwood Longbow", "minecraft:spruce_leaves", "Mistleaf Vambrace"],
            ["minecraft:totem_of_undying", "Cobaltean Charm", "minecraft:compass", "Cobaltean Charm"],
            ["minecraft:chainmail_leggings", "Jorts Of Monshee", "minecraft:chainmail_leggings", "Jorts of Monshee"],
            ["minecraft:stone_sword", "The Frodian Keyblade", "minecraft:stone_sword", "Frodian Keyblade"],
            ["minecraft:golden_helmet", "Rageroot Crown", "minecraft:chainmail_helmet", "Rageroot Crown"],
            ["minecraft:potion", "Wormwood Oil", "minecraft:glass_bottle", "Wormwood Oil"],
            ["minecraft:bone_meal", "Fierce Soul", "minecraft:white_dye", "Fierce Soul"],
            ["minecraft:lapis_lazuli", "Speed Charm", "minecraft:blue_dye", "Speed Charm"],
            ["minecraft:iron_hoe", "Demon's Scar", "minecraft:stone_hoe", "Demon's Scar"],
            ["minecraft:spider_spawn_egg", "Amalgamated Dissonant Energy", "nether_wart_block", "Amalgamated Dissonant Energy"],
            ["minecraft:iron_sword", "Blade of Destiny", "minecraft:stone_sword", "Blade of Destiny"],
            ["minecraft:potion", "Angry Fruit Juice", "minecraft:splash_potion", "Extinguisher"],
            ["minecraft:sunflower", "Despondent Doubloon", "minecraft:gold_nugget", "Despondent Doubloon"],
            ["minecraft:nether_star", "Aurora Shard", "minecraft:quartz", "Aurora Shard"],
            ["minecraft:stone_pickaxe", "Skyfeller", "minecraft:golden_pickaxe", "Skyfeller"],
            ["minecraft:crossbow", "Crimson Chicken", "minecraft:crossbow", "Red Rooster"],
            ["minecraft:sunflower", "Whirpool Coin", "minecraft:sunflower", "Whirlpool Coin"],
            ["minecraft:iron_axe", "Saving Grace", "minecraft:stone_axe", "Saving Grace"],
            ["minecraft:golden_shovel", "Myriad's Rapier", "minecraft:golden_sword", "Myriad's Rapier"],
            ["minecraft:turtle_helmet", "Seadiver's Shell", "minecraft:golden_chestplate", "Seadiver's Shell"],
            ["minecraft:quartz", "Fragment of Remorse", "minecraft:quartz", "Shard of Remorse"],
            ["minecraft:gold_ingot", "Blackflame Hoard", "minecraft:gold_ingot", "Blackflame Emblem"],
            ["minecraft:skeleton_skull", "Valgus' Skull", "minecraft:player_head", "Valgus' Skull"],
            ["minecraft:wooden_sword", "Requiem", "minecraft:jungle_sapling", "Deepdream Roots"],
            ["minecraft:leather_helmet", "Dragon Scale Helm", "minecraft:leather_helmet", "Crimstonian Helm"],
            ["minecraft:leather_chestplate", "Dragon Scale Chestpiece", "minecraft:leather_chestplate", "Crimstonian Chestpiece"],
            ["minecraft:leather_leggings", "Dragon Scale Leggings", "minecraft:leather_leggings", "Crimstonian Leggings"],
            ["minecraft:leather_boots", "Dragon Scale Boots", "minecraft:leather_boots", "Crimstonian Boots"],
            ["minecraft:potion", "Dragon Brew", "minecraft:potion", "Crimstonian Brew"],
            ["minecraft:player_head", "Ender Eyes", "minecraft:player_head", "Gaze of Judgement"],
            ["minecraft:stone_hoe", "Enderwrath", "minecraft:stone_hoe", "Sleepwalker's Sickle"],
            ["minecraft:leather_chestplate", "Bluescale Torso", "minecraft:leather_chestplate", "Warden's Ruin"],
            ["minecraft:stone_sword", "Frostbite", "minecraft:stone_sword", "Cascade"],
            ["minecraft:ink_sac", "Mitten of Madness", "minecraft:golden_hoe", "Mitten of Madness"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag", "minecraft:splash_potion", "Alchemist's Bag"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (0)", "minecraft:splash_potion", "Alchemist's Bag (0)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (1)", "minecraft:splash_potion", "Alchemist's Bag (1)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (2)", "minecraft:splash_potion", "Alchemist's Bag (2)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (3)", "minecraft:splash_potion", "Alchemist's Bag (3)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (4)", "minecraft:splash_potion", "Alchemist's Bag (4)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (5)", "minecraft:splash_potion", "Alchemist's Bag (5)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (6)", "minecraft:splash_potion", "Alchemist's Bag (6)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (7)", "minecraft:splash_potion", "Alchemist's Bag (7)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (8)", "minecraft:splash_potion", "Alchemist's Bag (8)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (9)", "minecraft:splash_potion", "Alchemist's Bag (9)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (10)", "minecraft:splash_potion", "Alchemist's Bag (10)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (11)", "minecraft:splash_potion", "Alchemist's Bag (11)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (12)", "minecraft:splash_potion", "Alchemist's Bag (12)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (13)", "minecraft:splash_potion", "Alchemist's Bag (13)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (14)", "minecraft:splash_potion", "Alchemist's Bag (14)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (15)", "minecraft:splash_potion", "Alchemist's Bag (15)"],
            ["minecraft:flower_banner_pattern", "Alchemist's Bag (16)", "minecraft:splash_potion", "Alchemist's Bag (16)"],
            ["minecraft:wooden_shovel", "Stick Of Beating", "minecraft:wooden_shovel", "Stick of Beating"],
            ["minecraft:leather_chestplate", "Eternal Shroud", "minecraft:leather_chestplate", "Phoenix Shroud"],
            ["minecraft:nether_star", "Ancestral Sigil", "minecraft:firework_star", "Ancestral Sigil"],
            ["minecraft:gold_nugget", "Unlucky Horseshoe (Instant)", "minecraft:gold_nugget", "Unlucky Horseshoe"],
        ]:
            old_id, old_name, new_id, new_name = substitution

            if old_id not in self.replacements:
                self.replacements[old_id] = {}
            id_replacements = self.replacements[old_id]

            id_replacements[old_name] = (new_id, new_name)

    def process(self, item_meta, item):
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

