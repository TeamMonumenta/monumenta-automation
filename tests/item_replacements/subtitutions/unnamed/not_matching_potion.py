#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Substitutions: Unnamed: Not matching potion",
    template_item=r'''{id:"minecraft:splash_potion",tag:{Potion:"minecraft:strong_healing",display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#c21e56","text":"Healing Vial"}'},plain:{display:{Name:'Healing Vial'}}}}''',
    item_under_test=r'''{Count:1b,Slot:1b,id:"minecraft:splash_potion",tag:{Potion:"minecraft:not_healing"}}''',
    expected_result_item=r'''{Count:1b,Slot:1b,id:"minecraft:splash_potion",tag:{Potion:"minecraft:not_healing"}}'''
)
test_item.run()
