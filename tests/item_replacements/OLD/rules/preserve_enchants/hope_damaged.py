#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Rules: Preserve Hope: damaged",
    template_item=r'''{id:"minecraft:zombie_head",tag:{display:{Lore:['{"text":"§8King\'s Valley : Tier II"}'],Name:"{\"text\":\"§rZombie Plushie\"}"},Enchantments:[{lvl:1s,id:"minecraft:protection"}],AttributeModifiers:[]}}''',
    item_under_test=r'''{id:"minecraft:zombie_head",tag:{display:{Lore:['{"text":"§7Hope"}','{"text":"§8King\'s Valley : Tier II"}','{"text":"Infused by Foo_Bar_Baz"}'],Name:"{\"text\":\"§rZombie Plushie\"}"},Enchantments:[{lvl:1s,id:"minecraft:protection"}],AttributeModifiers:[]},Damage:1}''',
    expected_result_item=r'''{id:"minecraft:zombie_head",tag:{display:{Lore:['{"text":"§7Hope"}','{"text":"§8King\'s Valley : Tier II"}','{"text":"Infused by Foo_Bar_Baz"}'],Name:"{\"text\":\"§rZombie Plushie\"}"},Enchantments:[{lvl:1s,id:"minecraft:protection"}],AttributeModifiers:[]},Damage:1}'''
)
test_item.run()

