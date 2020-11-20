#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name=r"""Substitutions: Fixed simple json names ("\"Example\"")""",
    template_item=r'''{id:"minecraft:golden_sword",tag:{display:{Lore:['{"text":"§7Radiant"}','{"text":"§7Hope"}','{"text":"§8King\'s Valley : §4Artifact"}','{"text":"§l"}','{"text":"§7When in main hand:"}','{"text":"§7 1.6 Attack Speed"}','{"text":"§7 3 Attack Damage"}'],Name:"{\"text\":\"§e§l§nLight of Salvation\"}"}}}''',
    item_under_test=r'''{id:"minecraft:golden_sword",tag:{display:{Lore:['{"text":"§7Radiant"}','{"text":"§7Hope"}','{"text":"§7Festive"}','{"text":"§8King\'s Valley : §4Artifact"}','{"text":"Decorated by Combustible"}','{"text":"§l"}','{"text":"§7When in main hand:"}','{"text":"§7 1.6 Attack Speed"}','{"text":"§7 3 Attack Damage"}','{"text":"* Soulbound to Combustible *"}'],Name:"\"§e§l§nLight of Salvation\""}}}''',
    expected_result_item=r'''{id:"minecraft:golden_sword",tag:{display:{Lore:['{"text":"§7Radiant"}','{"text":"§7Hope"}','{"text":"§7Festive"}','{"text":"§8King\'s Valley : §4Artifact"}','{"text":"Decorated by Combustible"}','{"text":"§l"}','{"text":"§7When in main hand:"}','{"text":"§7 1.6 Attack Speed"}','{"text":"§7 3 Attack Damage"}','{"text":"* Soulbound to Combustible *"}'],Name:"{\"text\":\"§e§l§nLight of Salvation\"}"}}}'''
)
test_item.run()

