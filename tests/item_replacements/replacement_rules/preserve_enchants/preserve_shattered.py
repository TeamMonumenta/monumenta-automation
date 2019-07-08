#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.base_test import ReplacementTest

test_item = ReplacementTest(
    test_name="Rules: Preserve Shattered",
    template_item=r'''{id:"minecraft:golden_chestplate",tag:{display:{Lore:["§7Hope","§8King's Valley : §6§lEpic"],Name:"{\"text\":\"§b§l§nKing\\u0027s Warden\"}"},Enchantments:[{lvl:2s,id:"minecraft:blast_protection"},{lvl:1s,id:"minecraft:mending"},{lvl:3s,id:"minecraft:protection"}],AttributeModifiers:[{UUIDMost:348118L,UUIDLeast:433148L,Amount:5.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:96224L,UUIDLeast:26892L,Amount:2.0d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"}]}}''',
    item_under_test=r'''{id:"minecraft:golden_chestplate",Count:1b,tag:{display:{Lore:["§7Hope","§8King's Valley : §6§lEpic","§4§l* SHATTERED *","§4Maybe a Master Repairman","§4could reforge it..."],Name:"{\"text\":\"§b§l§nKing\\u0027s Warden\"}"},Enchantments:[{lvl:2s,id:"minecraft:blast_protection"},{lvl:1s,id:"minecraft:mending"},{lvl:3s,id:"minecraft:protection"}],AttributeModifiers:[{UUIDMost:348118L,UUIDLeast:433148L,Amount:5.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:96224L,UUIDLeast:26892L,Amount:2.0d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"}]}}''',
    expected_result_item=r'''{id:"minecraft:golden_chestplate",Count:1b,tag:{display:{Lore:["§7Hope","§8King's Valley : §6§lEpic","§4§l* SHATTERED *","§4Maybe a Master Repairman","§4could reforge it..."],Name:"{\"text\":\"§b§l§nKing\\u0027s Warden\"}"},Enchantments:[{lvl:2s,id:"minecraft:blast_protection"},{lvl:1s,id:"minecraft:mending"},{lvl:3s,id:"minecraft:protection"}],AttributeModifiers:[{UUIDMost:348118L,UUIDLeast:433148L,Amount:5.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:96224L,UUIDLeast:26892L,Amount:2.0d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"}]}}'''
)
test_item.test()

