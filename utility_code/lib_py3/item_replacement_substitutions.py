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

class substitution_rule(object):
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

substitution_rules = []

class fix_broken_section_symbols(substitution_rule):
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

substitution_rules.append(fix_broken_section_symbols())

class fix_double_json_names(substitution_rule):
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

substitution_rules.append(fix_double_json_names())

class subtitute_items(substitution_rule):
    name = "Substitute the ID and name of items, ignoring other NBT"

    def __init__(self):
        self.replacements = {}

        for substitution in [
            #["minecraft:example_item_id", "Example Name", "minecraft:new_id", "Example New Name"],
            #["minecraft:example_banned_item", always_equal, "minecraft:new_id", "Example New Name"],

            #["minecraft:prismarine_shard", "Crystalline Shard", "minecraft:prismarine_shard", "Crystalline Shard"],
            ["minecraft:prismarine_crystals", "Enchanted Crystalline Shard", "minecraft:prismarine_crystals", "Compressed Crystalline Shard"],
            ["minecraft:quartz", "Compressed Crystalline Shard", "minecraft:quartz", "Legacy Crystalline Shard"],
            ["minecraft:nether_star", "Purified Crystalline Shard", "minecraft:nether_star", "Hyper Crystalline Shard"],

            ["minecraft:golden_chestplate", "Lemurian Vestements", "minecraft:golden_chestplate", "Lemurian Vestments"],
            ["minecraft:golden_chestplate", "Stalwart Curiass", "minecraft:golden_chestplate", "Stalwart Cuirass"],
            ["minecraft:golden_chestplate", "Patinated Curiass", "minecraft:golden_chestplate", "Patinated Cuirass"],

            ["minecraft:stone_pickaxe", "Pyromancer's Staff", "minecraft:blaze_rod", "Pyromancer's Staff"],
            ["minecraft:cooked_rabbit", " Cooked Zombie Meat", "minecraft:cooked_rabbit", "Cooked Zombie Meat"],

            ["minecraft:golden_helmet", "Legionnaire's Helmet", "minecraft:chainmail_helmet", "Legionnaire's Helmet"],
            ["minecraft:golden_chestplate", "Legionnaire's Chestplate", "minecraft:chainmail_chestplate", "Legionnaire's Chestplate"],
            ["minecraft:golden_leggings", "Legionnaire's Leggings", "minecraft:chainmail_leggings", "Legionnaire's Leggings"],
            ["minecraft:golden_boots", "Legionnaire's Boots", "minecraft:chainmail_boots", "Legionnaire's Boots"],
            ["minecraft:leather_helmet", "Incindiary Hood", "minecraft:leather_helmet", "Incendiary Hood"],
            ["minecraft:leather_chestplate", "Incindiary Cloak", "minecraft:leather_chestplate", "Incendiary Cloak"],
            ["minecraft:leather_leggings", "Incindiary Pants", "minecraft:leather_leggings", "Incendiary Pants"],
            ["minecraft:leather_boots", "Incindiary Boots", "minecraft:leather_boots", "Incendiary Boots"],
            ["minecraft:golden_leggings", "Bladedancer's Sabatons", "minecraft:golden_leggings", "Bladedancer's Greaves"],
            ["minecraft:golden_boots", "Bladedancer's Boots", "minecraft:golden_boots", "Bladedancer's Sabatons"],
            ["minecraft:golden_chestplate", "Oracle's Vestements", "minecraft:golden_chestplate", "Oracle's Vestments"],
            ["minecraft:leather_helmet", "Viridian Scale Hat", "minecraft:chainmail_helmet", "Viridian Scale Hat"],
            ["minecraft:leather_chestplate", "Viridian Scale Tunic", "minecraft:chainmail_chestplate", "Viridian Scale Tunic"],
            ["minecraft:leather_leggings", "Viridian Scale Robes", "minecraft:chainmail_leggings", "Viridian Scale Robes"],
            ["minecraft:leather_boots", "Viridian Scale Slippers", "minecraft:chainmail_boots", "Viridian Scale Slippers"],
            ["minecraft:iron_sword", "Rootstrike", "minecraft:stone_sword", "Rootstrike"],
            ["minecraft:chainmail_boots", "Steel Sabatons", "minecraft:iron_boots", "Steel Sabatons"],
            ["minecraft:chainmail_leggings", "Sunblessed Leggings", "minecraft:golden_leggings", "Sunblessed Leggings"],
            ["minecraft:golden_helmet", "Excavator's Hardlamp", "minecraft:iron_helmet", "Excavator's Hardlamp"],
            ["minecraft:iron_pickaxe", "The Earthshaker", "minecraft:golden_pickaxe", "The Earthshaker"],

            # UGHHHH
            ["minecraft:iron_helmet", "True Frost Giant's Crown", "minecraft:iron_helmet", "Frost Giant's Crown"],
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

substitution_rules.append(subtitute_items())

