#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Rules: Preserve Hope: pre-enchanted",
    template_item=r'''{id:"minecraft:golden_chestplate",tag:{display:{Lore:['{"text":"§7Hope"}','{"text":"§8King\'s Valley : §6§lEpic"}'],Name:"{\"text\":\"§b§l§nKing\\u0027s Warden\"}"},Enchantments:[{lvl:1s,id:"minecraft:mending"},{lvl:3s,id:"minecraft:protection"},{lvl:2s,id:"minecraft:blast_protection"}],AttributeModifiers:[{UUIDMost:96224L,UUIDLeast:26892L,Amount:2.0d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:348118L,UUIDLeast:433148L,Amount:5.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}}''',
    item_under_test=r'''{id:"minecraft:golden_chestplate",tag:{display:{Lore:['{"text":"§7Hope"}','{"text":"§8King\'s Valley : §6§lEpic"}'],Name:"{\"text\":\"§b§l§nKing\\u0027s Warden\"}"},Enchantments:[{lvl:1s,id:"minecraft:mending"},{lvl:3s,id:"minecraft:protection"},{lvl:2s,id:"minecraft:blast_protection"}],AttributeModifiers:[{UUIDMost:96224L,UUIDLeast:26892L,Amount:2.0d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:348118L,UUIDLeast:433148L,Amount:5.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}}''',
    expected_result_item=r'''{id:"minecraft:golden_chestplate",tag:{display:{Lore:['{"text":"§7Hope"}','{"text":"§8King\'s Valley : §6§lEpic"}'],Name:"{\"text\":\"§b§l§nKing\\u0027s Warden\"}"},Enchantments:[{lvl:1s,id:"minecraft:mending"},{lvl:3s,id:"minecraft:protection"},{lvl:2s,id:"minecraft:blast_protection"}],AttributeModifiers:[{UUIDMost:96224L,UUIDLeast:26892L,Amount:2.0d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:348118L,UUIDLeast:433148L,Amount:5.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}}'''
)
test_item.run()

