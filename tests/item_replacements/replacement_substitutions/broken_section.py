#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.base_test import ReplacementTest

test_item = ReplacementTest(
    test_name="Substitutions: Fix broken section symbols",
    template_item=r'''{id:"minecraft:golden_sword",tag:{display:{Lore:["§7Radiant","§7Hope","§8King's Valley : §4Artifact","§l","§7When in main hand:","§7 1.6 Attack Speed","§7 3 Attack Damage"],Name:"{\"text\":\"§e§l§nLight of Salvation\"}"}}}''',
    item_under_test=r'''{id:"minecraft:golden_sword",tag:{display:{Lore:["�7Radiant","�7Hope","�7Festive","�8King's Valley : �4Artifact","Infused by Combustible","�l","�7When in main hand:","�7 1.6 Attack Speed","�7 3 Attack Damage","* Soulbound to Combustible *"],Name:"{\"text\":\"�e�l�nLight of Salvation\"}"}}}''',
    expected_result_item=r'''{id:"minecraft:golden_sword",tag:{display:{Lore:["§7Radiant","§7Hope","§7Festive","§8King's Valley : §4Artifact","Decorated by Combustible","§l","§7When in main hand:","§7 1.6 Attack Speed","§7 3 Attack Damage","* Soulbound to Combustible *"],Name:"{\"text\":\"§e§l§nLight of Salvation\"}"}}}'''
)
test_item.test()

