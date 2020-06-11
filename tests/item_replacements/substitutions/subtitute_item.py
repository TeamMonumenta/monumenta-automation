#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Substitutions: Substitute the ID and name of items, ignoring other NBT",
    template_item=r'''{id: "minecraft:crossbow", Count: 1b, tag: {display: {Lore: ['{"text":"Test"}'], Name: "{\"text\":\"Blazing Crossbow\"}"}}}''',
    item_under_test=r'''{id: "minecraft:bow", Count: 1b, tag: {display: {Lore: ['{"text":"Test"}'], Name: "{\"text\":\"Blazing Crossbow\"}"}}}''',
    expected_result_item=r'''{id: "minecraft:crossbow", Count: 1b, tag: {display: {Lore: ['{"text":"Test"}'], Name: "{\"text\":\"Blazing Crossbow\"}"}}}'''
)
test_item.run()

