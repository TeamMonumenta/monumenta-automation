#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Rules: Abort if there's no lore text",
    template_item=r'''{id:"minecraft:compass",tag:{display:{Lore:['{"text":"§fLeft click to display active quest"}','{"text":"§fRight click to cycle quests and objectives"}','{"text":"§fShift + Right click to view local respawn timers"}'],Name:"{\"text\":\"§6§lQuest Compass\"}"}}}''',
    item_under_test=r'''{id:"minecraft:compass",tag:{display:{Name:"{\"text\":\"§6§lQuest Compass\"}"}}}''',
    expected_result_item=r'''{id:"minecraft:compass",tag:{display:{Name:"{\"text\":\"§6§lQuest Compass\"}"}}}'''
)
test_item.run()

