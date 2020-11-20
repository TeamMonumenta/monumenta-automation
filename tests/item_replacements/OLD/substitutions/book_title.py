#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Substitutions: Book Titles",
    template_item=r'''{id:"minecraft:written_book",tag:{pages:['{"text":"Baz"}'],title:"Foo",author:"NickNackGus",display:{Name:'{"text":"Foo"}',Lore:['{"text":"a"}']},resolved:1b}}''',
    item_under_test=r'''{id:"minecraft:written_book",tag:{pages:['{"text":"Bar"}'],title:"Foo",author:"NickNackGus",resolved:1b}}''',
    expected_result_item=r'''{id:"minecraft:written_book",tag:{pages:['{"text":"Baz"}'],title:"Foo",author:"NickNackGus",display:{Name:'{"text":"Foo"}',Lore:['{"text":"a"}']},resolved:1b}}'''
)
test_item.run()

