#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Rules: Preserve Hope",
    template_item=r'''{id:"minecraft:zombie_head",tag:{display:{Lore:["§8King's Valley : Tier II"],Name:"{\"text\":\"§rZombie Plushy\"}"},Enchantments:[{lvl:1s,id:"minecraft:protection"}],AttributeModifiers:[]}}''',
    item_under_test=r'''{id:"minecraft:zombie_head",tag:{display:{Lore:["§7Hope","§8King's Valley : Tier II","Infused by Foo_Bar_Baz"],Name:"{\"text\":\"§rZombie Plushy\"}"},Enchantments:[{lvl:1s,id:"minecraft:protection"}],AttributeModifiers:[]}}''',
    expected_result_item=r'''{id:"minecraft:zombie_head",tag:{display:{Lore:["§7Hope","§8King's Valley : Tier II","Infused by Foo_Bar_Baz"],Name:"{\"text\":\"§rZombie Plushy\"}"},Enchantments:[{lvl:1s,id:"minecraft:protection"}],AttributeModifiers:[]}}'''
)
test_item.run()
