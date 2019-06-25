#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.base_test import ReplacementTest

test_item = ReplacementTest(
    test_name="Substitutions: Substitute the ID and name of items, ignoring other NBT",
    template_item=r'''{id: "minecraft:nether_star",tag:{display:{Lore:["§7Worth 64 Compressed Crystalline Shards"],Name:"{\"text\":\"§b§lHyper Crystalline Shard\"}"}}}''',
    item_under_test=r'''{id: "minecraft:nether_star",Count:3b,tag:{display:{Lore:["§7Worth 8 Compressed Crystalline Shards"],Name:"{\"text\":\"§b§lPurified Crystalline Shard\"}"}}}''',
    expected_result_item=r'''{id: "minecraft:nether_star",Count:3b,tag:{display:{Lore:["§7Worth 64 Compressed Crystalline Shards"],Name:"{\"text\":\"§b§lHyper Crystalline Shard\"}"}}}'''
)
test_item.test()

