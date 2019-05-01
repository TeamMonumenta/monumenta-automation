#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.base_test import ReplacementTest

test_item = ReplacementTest(
    test_name="Rules: Abort if there's no lore text",
    template_item=r'''{id:"minecraft:compass",tag:{display:{Lore:["§fLeft click to display active quest","§fRight click to cycle quests and objectives","§fShift + Right click to view local respawn timers"],Name:"{\"text\":\"§6§lQuest Compass\"}"}}}''',
    item_under_test=r'''{id:"minecraft:compass",tag:{display:{Name:"{\"text\":\"§6§lQuest Compass\"}"}}}''',
    expected_result_item=r'''{id:"minecraft:compass",tag:{display:{Name:"{\"text\":\"§6§lQuest Compass\"}"}}}'''
)
test_item.test()

