#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Rules: Preserve Shield Banner: Added Pattern",
    template_item=r'''{id:"minecraft:shield",tag:{display:{Lore:['{"text":"§8King\'s Valley : Tier II"}'],Name:"{\"text\":\"§fTest Shield\"}"}}}''',
    item_under_test=r'''{id:"minecraft:shield",tag:{display:{Lore:['{"text":"§8King\'s Valley : Tier II"}'],Name:"{\"text\":\"§fTest Shield\"}"},BlockEntityTag:{id:"minecraft:banner",Patterns:[{Pattern:"bri",Color:13}],Base:9}}}''',
    expected_result_item=r'''{id:"minecraft:shield",tag:{display:{Lore:['{"text":"§8King\'s Valley : Tier II"}'],Name:"{\"text\":\"§fTest Shield\"}"},BlockEntityTag:{Patterns:[{Pattern:"bri",Color:13}],Base:9}}}'''
)
test_item.run()

