#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Rules: Preserve Armor Color: Turtle Helm",
    template_item=r'''{id:"minecraft:leather_helmet",tag:{Enchantments:[{lvl:1s,id:"minecraft:respiration"},{lvl:2s,id:"minecraft:blast_protection"}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"{\"text\":\"§fTurtle Helm\"}"},AttributeModifiers:[{UUIDMost:260399L,UUIDLeast:803793L,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}}''',
    item_under_test=r'''{id:"minecraft:leather_helmet",tag:{Enchantments:[{lvl:1s,id:"minecraft:respiration"},{lvl:2s,id:"minecraft:blast_protection"}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:16777215,Name:"{\"text\":\"§fTurtle Helm\"}"},AttributeModifiers:[{UUIDMost:260399L,UUIDLeast:803793L,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}}''',
    expected_result_item=r'''{id:"minecraft:leather_helmet",tag:{Enchantments:[{lvl:1s,id:"minecraft:respiration"},{lvl:2s,id:"minecraft:blast_protection"}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:16777215,Name:"{\"text\":\"§fTurtle Helm\"}"},AttributeModifiers:[{UUIDMost:260399L,UUIDLeast:803793L,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}}'''
)
test_item.run()

