#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Substitutions: Fix escaped names",
    template_item=r'''{id:"minecraft:golden_sword",tag:{display:{Lore:['{"text":"§7Radiant"}','{"text":"§7Hope"}','{"text":"§8King\'s Valley : §4Artifact"}','{"text":"§l"}','{"text":"§7When in main hand:"}','{"text":"§7 1.6 Attack Speed"}','{"text":"§7 3 Attack Damage"}'],Name:'{"text":"§e§l§nTest\'s Item"}'}}}''',
    item_under_test=r'''{id:"minecraft:golden_sword",tag:{display:{Lore:['{"text":"\\u00a77Radiant"}','{"text":"\\u00a77Hope"}','{"text":"\\u00a77Festive"}','{"text":"\\u00a78King\'s Valley : \\u00a74Artifact"}','{"text":"Decorated by Combustible"}','{"text":"\\u00a7l"}','{"text":"\\u00a77When in main hand:"}','{"text":"\\u00a77 1.6 Attack Speed"}','{"text":"\\u00a77 3 Attack Damage"}','{"text":"* Soulbound to Combustible *"}'],Name:'{"text":"\\u00a7e\\u00a7l\\u00a7nTest\\u0027s Item"}'}}}''',
    expected_result_item=r'''{id:"minecraft:golden_sword",tag:{display:{Lore:['{"text":"§7Radiant"}','{"text":"§7Hope"}','{"text":"§7Festive"}','{"text":"§8King\'s Valley : §4Artifact"}','{"text":"Decorated by Combustible"}','{"text":"§l"}','{"text":"§7When in main hand:"}','{"text":"§7 1.6 Attack Speed"}','{"text":"§7 3 Attack Damage"}','{"text":"* Soulbound to Combustible *"}'],Name:'{"text":"§e§l§nTest\'s Item"}'}}}'''
)
test_item.run()

