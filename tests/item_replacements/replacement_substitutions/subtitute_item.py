#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.base_test import ReplacementTest

test_los_combustible = ReplacementTest(
    test_name="Substitutions: Substitute the ID and name of items, ignoring other NBT",
    template_item=r'''{id:"minecraft:compass",tag:{display:{Lore:["§fLeft click to display active quest","§fRight click to cycle quests and objectives","§fShift + Right click to view local respawn timers"],Name:"{\"text\":\"§6§lQuest Compass\"}"}}}''',
    item_under_test=r'''{id:"minecraft:trident",tag:{display:{Lore:["Items with no lore get skipped"],Name:"{\"text\":\"Dinglehopper\"}"}}}''',
    expected_result_item=r'''{id:"minecraft:compass",tag:{display:{Lore:["§fLeft click to display active quest","§fRight click to cycle quests and objectives","§fShift + Right click to view local respawn timers"],Name:"{\"text\":\"§6§lQuest Compass\"}"}}}'''
)
test_los_combustible.test()

