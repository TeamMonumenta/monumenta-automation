#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Rules: Preserve Shield Banner: Removed",
    template_item=r'''{id:"minecraft:shield",tag:{HideFlags:32,BlockEntityTag:{Patterns:[{Pattern:"hh",Color:12},{Pattern:"hhb",Color:12},{Pattern:"bri",Color:8},{Pattern:"bri",Color:12},{Pattern:"bo",Color:8}],Base:15},Enchantments:[{lvl:2s,id:"minecraft:unbreaking"}],display:{Lore:['{"text":"§8King\'s Valley : Tier III"}'],Name:"{\"text\":\"§fHardened Shield\"}"}}}''',
    item_under_test=r'''{id:"minecraft:shield",tag:{HideFlags:32,Enchantments:[{lvl:2s,id:"minecraft:unbreaking"}],display:{Lore:['{"text":"§8King\'s Valley : Tier III"}'],Name:"{\"text\":\"§fHardened Shield\"}"}}}''',
    expected_result_item=r'''{id:"minecraft:shield",tag:{HideFlags:32,Enchantments:[{lvl:2s,id:"minecraft:unbreaking"}],display:{Lore:['{"text":"§8King\'s Valley : Tier III"}'],Name:"{\"text\":\"§fHardened Shield\"}"}}}'''
)
test_item.run()

