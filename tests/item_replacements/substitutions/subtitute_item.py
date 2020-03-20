#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Substitutions: Substitute the ID and name of items, ignoring other NBT",
    template_item=r'''{id: "minecraft:jungle_sapling", Count: 1b, tag: {display: {Lore: ["§8* Magic Wand *", "§8King's Valley : §eRare", "§7The Black Willows", "§8We need more trees!", "§r", "§7When in main hand:", "§2 4 Attack Speed", "§2 3 Attack Damage"], Name: "{\"text\":\"§2§lChimarian Wand\"}"}, Enchantments: [{lvl: 2s, id: "minecraft:bane_of_arthropods"}, {lvl: 1s, id: "minecraft:fire_aspect"}, {lvl: 3s, id: "minecraft:sharpness"}, {lvl: 2s, id: "minecraft:smite"}]}}''',
    item_under_test=r'''{id: "minecraft:oak_sapling", Count: 1b, tag: {display: {Lore: ["§7Hope", "§8* Magic Wand *", "§8King's Valley : §eRare", "§7The Black Willows", "§8We need more trees!", "Infused by NickNackGus", "§r", "§7When in main hand:", "§2 4 Attack Speed", "§2 3 Attack Damage"], Name: "{\"text\":\"§2§lChimarian Wand\"}"}, Enchantments: [{lvl: 2s, id: "minecraft:bane_of_arthropods"}, {lvl: 1s, id: "minecraft:fire_aspect"}, {lvl: 3s, id: "minecraft:sharpness"}, {lvl: 2s, id: "minecraft:smite"}]}}''',
    expected_result_item=r'''{id: "minecraft:jungle_sapling", Count: 1b, tag: {display: {Lore: ["§7Hope", "§8* Magic Wand *", "§8King's Valley : §eRare", "§7The Black Willows", "§8We need more trees!", "Infused by NickNackGus", "§r", "§7When in main hand:", "§2 4 Attack Speed", "§2 3 Attack Damage"], Name: "{\"text\":\"§2§lChimarian Wand\"}"}, Enchantments: [{lvl: 2s, id: "minecraft:bane_of_arthropods"}, {lvl: 1s, id: "minecraft:fire_aspect"}, {lvl: 3s, id: "minecraft:sharpness"}, {lvl: 2s, id: "minecraft:smite"}]}}'''
)
test_item.run()

