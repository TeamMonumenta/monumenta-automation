#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.base_test import ReplacementTest

test_item = ReplacementTest(
    test_name="Substitutions: Substitute the ID and name of items, ignoring other NBT",
    template_item=r'''{id:"minecraft:anvil",tag:{display:{Name:"{\"text\":\"§aRepair Anvil\"}"}}}''',
    item_under_test=r'''{id:"minecraft:damaged_anvil",tag:{display:{Name:"{\"text\":\"§aNarsen Anvil\"}"}}}''',
    expected_result_item=r'''{id:"minecraft:anvil",tag:{display:{Name:"{\"text\":\"§aRepair Anvil\"}"}}}'''
)
test_item.test()

