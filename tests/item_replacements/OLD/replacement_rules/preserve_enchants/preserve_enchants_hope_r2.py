#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.base_test import ReplacementTest

test_item = ReplacementTest(
    test_name="Rules: Preserve Hope: r2",
    template_item=r'''{id:"minecraft:iron_leggings",tag:{display:{Lore:['{"text":"§8Celsian Isles : §2Relic"}','{"text":"§6Bounty Ship"}','{"text":"§8Strength and resolve are the only"}','{"text":"§8things that endure in the Chillwind Tundra."}'],Name:"{\"text\":\"§b§lFrost Knight\\u0027s Greaves\"}"},Enchantments:[{lvl:2s,id:"minecraft:projectile_protection"},{lvl:1s,id:"minecraft:protection"},{lvl:2s,id:"minecraft:unbreaking"}],AttributeModifiers:[{UUIDMost:-8378714422707533333L,UUIDLeast:-6089825513335937437L,Amount:8.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:2235858673608444385L,UUIDLeast:-6934852202355861425L,Amount:3.0d,Slot:"legs",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:7759640557228478141L,UUIDLeast:-5673807078112448756L,Amount:-0.1d,Slot:"legs",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}}}''',
    item_under_test=r'''{id:"minecraft:iron_leggings",tag:{display:{Lore:['{"text":"§7Hope"}','"text":"§8Celsian Isles : §2Relic"}','{"text":"§6Bounty Ship","§8Strength and resolve are the only"}','{"text":"§8things that endure in the Chillwind Tundra."}','{"text":"Infused by Spy21DD"}'],Name:"{\"text\":\"§b§lFrost Knight\\u0027s Greaves\"}"},Enchantments:[{lvl:2s,id:"minecraft:projectile_protection"},{lvl:1s,id:"minecraft:protection"},{lvl:2s,id:"minecraft:unbreaking"}],AttributeModifiers:[{UUIDMost:-8378714422707533333L,UUIDLeast:-6089825513335937437L,Amount:8.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:2235858673608444385L,UUIDLeast:-6934852202355861425L,Amount:3.0d,Slot:"legs",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:7759640557228478141L,UUIDLeast:-5673807078112448756L,Amount:-0.1d,Slot:"legs",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}}}''',
    expected_result_item=r'''{id:"minecraft:iron_leggings",tag:{display:{Lore:['{"text":"§7Hope"}','{"text":"§8Celsian Isles : §2Relic"}','{"text":"§6Bounty Ship"}','{"text":"§8Strength and resolve are the only"}','{"text":"§8things that endure in the Chillwind Tundra."}','{"text":"Infused by Spy21DD"}'],Name:"{\"text\":\"§b§lFrost Knight\\u0027s Greaves\"}"},Enchantments:[{lvl:2s,id:"minecraft:projectile_protection"},{lvl:1s,id:"minecraft:protection"},{lvl:2s,id:"minecraft:unbreaking"}],AttributeModifiers:[{UUIDMost:-8378714422707533333L,UUIDLeast:-6089825513335937437L,Amount:8.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:2235858673608444385L,UUIDLeast:-6934852202355861425L,Amount:3.0d,Slot:"legs",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:7759640557228478141L,UUIDLeast:-5673807078112448756L,Amount:-0.1d,Slot:"legs",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}}}'''
)
test_item.test()

