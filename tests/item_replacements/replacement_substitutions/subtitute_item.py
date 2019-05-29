#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.base_test import ReplacementTest

test_item = ReplacementTest(
    test_name="Substitutions: Substitute the ID and name of items, ignoring other NBT",
    template_item=r'''{id: "minecraft:quartz", tag: {HideFlags: 1, display: {Lore: ["§7Worth 8 Enchanted Cystalline Shards"], Name: "{\"text\":\"§8§lLegacy Compressed Crystalline Shard\"}"}, Enchantments: [{lvl: 1s, id: "minecraft:infinity"}]}}''',
    item_under_test=r'''{id: "minecraft:quartz", Count: 3b, tag: {HideFlags: 1, display: {Lore: ["§7Worth 8 Enchanted Cystalline Shards"], Name: "{\"text\":\"§b§lCompressed Crystalline Shard\"}"}, Enchantments: [{lvl: 1s, id: "minecraft:infinity"}]}}''',
    expected_result_item=r'''{id: "minecraft:quartz", Count: 3b, tag: {HideFlags: 1, display: {Lore: ["§7Worth 8 Enchanted Cystalline Shards"], Name: "{\"text\":\"§8§lLegacy Compressed Crystalline Shard\"}"}, Enchantments: [{lvl: 1s, id: "minecraft:infinity"}]}}'''
)
test_item.test()

