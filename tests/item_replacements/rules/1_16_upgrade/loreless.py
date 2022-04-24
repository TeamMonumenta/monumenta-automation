#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Rules: Loreless",
    template_item=r'''{id: "minecraft:bone", tag: {Enchantments: [{id: "minecraft:fire_aspect", lvl: 5s}], plain: {display: {Name: "Charm of C'Zanil", Lore: ["Regeneration I", "King's Valley : Enhanced Rare", "Ephemeral Corridors", "The souls scream, yearning to be released."]}}, HideFlags: 1, AttributeModifiers: [{Name: "Modifier", Amount: 2.0d, Operation: 0, UUID: [I; -1, -96511059, -1, -1762056], Slot: "offhand", AttributeName: "minecraft:generic.max_health"}, {Name: "Modifier", Amount: 0.07d, Operation: 1, UUID: [I; 1902081872, -210811010, -1877467335, -1473527034], Slot: "offhand", AttributeName: "minecraft:generic.movement_speed"}], display: {Name: '{"extra":[{"bold":true,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gold","text":"Charm of C\'Zanil"}],"text":""}', Lore: ['{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gray","text":"Regeneration I"}],"text":""}', '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"dark_gray","text":"King\'s Valley : "},{"bold":true,"italic":false,"color":"yellow","text":"Enhanced Rare"}],"text":""}', '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"red","text":"Ephemeral Corridors"}],"text":""}', '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"dark_gray","text":"The souls scream, yearning to be released."}],"text":""}']}}, Count: 1b}''',
    item_under_test=r'''{id: "minecraft:bone", tag: {Damage: 150, Enchantments: [{id: "minecraft:fire_aspect", lvl: 5s}], display: {Name: '"Charm of C\'Zanil"'}}, Count: 1b}''',
    expected_result_item=r'''{id: "minecraft:bone", tag: {Damage: 150, Enchantments: [{id: "minecraft:fire_aspect", lvl: 5s}], display: {Name: '"Charm of C\'Zanil"'}, plain: {display: {Name: "Charm of C'Zanil"}}}, Count: 1b}'''
)
test_item.run()

