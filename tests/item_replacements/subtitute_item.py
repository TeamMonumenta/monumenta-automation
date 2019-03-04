#!/usr/bin/env python3

from base_test import ReplacementTest

test_los_combustible = ReplacementTest(
    test_name="Substitute one item for another",
    template_item=r'''{id:"minecraft:compass",tag:{display:{Lore:["§fLeft click to display active quest","§fRight click to cycle quests and objectives","§fShift + Right click to view local respawn timers"],Name:"{\"text\":\"§6§lQuest Compass\"}"}}}''',
    item_under_test=r'''{id:"minecraft:trident",tag:{display:{Lore:["Items with no lore get skipped"],Name:"{\"text\":\"Dinglehopper\"}"}}}''',
    expected_result_item=r'''{id:"minecraft:compass",tag:{display:{Lore:["§fLeft click to display active quest","§fRight click to cycle quests and objectives","§fShift + Right click to view local respawn timers"],Name:"{\"text\":\"§6§lQuest Compass\"}"}}}'''
)
test_los_combustible.test()

