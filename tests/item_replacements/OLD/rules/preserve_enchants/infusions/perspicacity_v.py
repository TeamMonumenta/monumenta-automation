#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'../..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Rules: Preserve Perspicacity V",
    template_item=r'''{id: "minecraft:stone_sword", Count: 1b, tag: {HideFlags: 2, display: {Lore: ['{"text":"§8King\'s Valley : §eRare"}', '{"text":"§3King\'s Valley"}', '{"text":""}', '{"text":"§7When in main hand:"}', '{"text":"§2 1.6 Attack Speed"}', '{"text":"§2 5 Attack Damage"}', '{"text":"§9 +1 Armor"}'], Name: "{\"text\":\"§6§lAngelic Sword\"}"}, Enchantments: [{lvl: 2s, id: "minecraft:smite"}, {lvl: 5s, id: "minecraft:unbreaking"}], AttributeModifiers: [{UUIDMost: 69970127574793796L, UUIDLeast: 64342718172429329L, Amount: -2.4d, Slot: "mainhand", AttributeName: "generic.attackSpeed", Operation: 0, Name: "generic.attackSpeed"}, {UUIDMost: 14771070297205314L, UUIDLeast: 58375339796730923L, Amount: 1.0d, Slot: "mainhand", AttributeName: "generic.armor", Operation: 0, Name: "generic.armor"}, {UUIDMost: 13921849192281677L, UUIDLeast: 29424957165321736L, Amount: 4.0d, Slot: "mainhand", AttributeName: "generic.attackDamage", Operation: 0, Name: "generic.attackDamage"}]}}''',
    item_under_test=r'''{id: "minecraft:stone_sword", Count: 1b, tag: {HideFlags: 2, display: {Lore: ['{"text":"§7Perspicacity V"}', '{"text":"§8King\'s Valley : §eRare"}', '{"text":"§3King\'s Valley"}', '{"text":""}', '{"text":"§7When in main hand:"}', '{"text":"§2 1.6 Attack Speed"}', '{"text":"§2 5 Attack Damage"}', '{"text":"§9 +1 Armor"}'], Name: "{\"text\":\"§6§lAngelic Sword\"}"}, Enchantments: [{lvl: 2s, id: "minecraft:smite"}, {lvl: 5s, id: "minecraft:unbreaking"}], AttributeModifiers: [{UUIDMost: 69970127574793796L, UUIDLeast: 64342718172429329L, Amount: -2.4d, Slot: "mainhand", AttributeName: "generic.attackSpeed", Operation: 0, Name: "generic.attackSpeed"}, {UUIDMost: 14771070297205314L, UUIDLeast: 58375339796730923L, Amount: 1.0d, Slot: "mainhand", AttributeName: "generic.armor", Operation: 0, Name: "generic.armor"}, {UUIDMost: 13921849192281677L, UUIDLeast: 29424957165321736L, Amount: 4.0d, Slot: "mainhand", AttributeName: "generic.attackDamage", Operation: 0, Name: "generic.attackDamage"}]}}''',
    expected_result_item=r'''{id: "minecraft:stone_sword", Count: 1b, tag: {HideFlags: 2, display: {Lore: ['{"text":"§7Perspicacity V"}', '{"text":"§8King\'s Valley : §eRare"}', '{"text":"§3King\'s Valley"}', '{"text":""}', '{"text":"§7When in main hand:"}', '{"text":"§2 1.6 Attack Speed"}', '{"text":"§2 5 Attack Damage"}', '{"text":"§9 +1 Armor"}'], Name: "{\"text\":\"§6§lAngelic Sword\"}"}, Enchantments: [{lvl: 2s, id: "minecraft:smite"}, {lvl: 5s, id: "minecraft:unbreaking"}], AttributeModifiers: [{UUIDMost: 69970127574793796L, UUIDLeast: 64342718172429329L, Amount: -2.4d, Slot: "mainhand", AttributeName: "generic.attackSpeed", Operation: 0, Name: "generic.attackSpeed"}, {UUIDMost: 14771070297205314L, UUIDLeast: 58375339796730923L, Amount: 1.0d, Slot: "mainhand", AttributeName: "generic.armor", Operation: 0, Name: "generic.armor"}, {UUIDMost: 13921849192281677L, UUIDLeast: 29424957165321736L, Amount: 4.0d, Slot: "mainhand", AttributeName: "generic.attackDamage", Operation: 0, Name: "generic.attackDamage"}]}}'''
)
test_item.run()

