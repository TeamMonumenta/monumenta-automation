#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.base_test import ReplacementTest

test_item = ReplacementTest(
    test_name="Substitutions: Substitute the ID and name of items, ignoring other NBT",
    template_item=r'''{id: "minecraft:jungle_sapling",tag:{Enchantments:[{lvl:3s,id:"minecraft:sharpness"},{lvl:2s,id:"minecraft:smite"},{lvl:2s,id:"minecraft:bane_of_arthropods"},{lvl:1s,id:"minecraft:fire_aspect"}],display:{Lore:["§8King's Valley : §eRare","§7The Black Willows","§8We need more trees!","§8* Magic Wand *"],Name:"{\"text\":\"§2§lChimarian Wand\"}"}}}''',
    item_under_test=r'''{id: "minecraft:oak_sapling",tag:{Enchantments:[{lvl:3s,id:"minecraft:sharpness"},{lvl:2s,id:"minecraft:smite"},{lvl:2s,id:"minecraft:bane_of_arthropods"},{lvl:1s,id:"minecraft:fire_aspect"}],display:{Lore:["§8King's Valley : §eRare","§7The Black Willows","§8We need more trees!","§8* Magic Wand *"],Name:"{\"text\":\"§2§lChimarian Wand\"}"}}}''',
    expected_result_item=r'''{id: "minecraft:jungle_sapling",tag:{Enchantments:[{lvl:3s,id:"minecraft:sharpness"},{lvl:2s,id:"minecraft:smite"},{lvl:2s,id:"minecraft:bane_of_arthropods"},{lvl:1s,id:"minecraft:fire_aspect"}],display:{Lore:["§8King's Valley : §eRare","§7The Black Willows","§8We need more trees!","§8* Magic Wand *"],Name:"{\"text\":\"§2§lChimarian Wand\"}"}}}'''
)
test_item.test()

