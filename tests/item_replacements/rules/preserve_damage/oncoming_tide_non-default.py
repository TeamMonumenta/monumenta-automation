#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Rules: Preserve Damage: Oncoming Tide, non-default damage",
    template_item=r'''{id:"minecraft:bow",tag:{HideFlags:2,display:{Lore:['{"text":"§8King\'s Valley : Uncommon"}','{"text":"§l"}','{"text":"§7When in either hand:"}','{"text":"§9 +7% Speed"}'],Name:"{\"text\":\"§b§lOncoming Tide\"}"},Enchantments:[{lvl:1s,id:"minecraft:punch"},{lvl:1s,id:"minecraft:mending"}],Damage:377,AttributeModifiers:[{UUIDMost:1004903320127294777L,UUIDLeast:-6735527447459109365L,Amount:0.07d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:5006830818721221879L,UUIDLeast:-8510586944847453132L,Amount:0.07d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}}''',
    item_under_test=r'''{id:"minecraft:bow",tag:{HideFlags:2,display:{Lore:['{"text":"§8King\'s Valley : Uncommon"}','{"text":"§l"}','{"text":"§7When in either hand:"}','{"text":"§9 +7% Speed"}'],Name:"{\"text\":\"§b§lOncoming Tide\"}"},Enchantments:[{lvl:1s,id:"minecraft:punch"},{lvl:1s,id:"minecraft:mending"}],Damage:15,AttributeModifiers:[{UUIDMost:1004903320127294777L,UUIDLeast:-6735527447459109365L,Amount:0.07d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:5006830818721221879L,UUIDLeast:-8510586944847453132L,Amount:0.07d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}}''',
    expected_result_item=r'''{id:"minecraft:bow",tag:{HideFlags:2,display:{Lore:['{"text":"§8King\'s Valley : Uncommon"}','{"text":"§l"}','{"text":"§7When in either hand:"}','{"text":"§9 +7% Speed"}'],Name:"{\"text\":\"§b§lOncoming Tide\"}"},Enchantments:[{lvl:1s,id:"minecraft:punch"},{lvl:1s,id:"minecraft:mending"}],Damage:15,AttributeModifiers:[{UUIDMost:1004903320127294777L,UUIDLeast:-6735527447459109365L,Amount:0.07d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:5006830818721221879L,UUIDLeast:-8510586944847453132L,Amount:0.07d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}}'''
)
test_item.run()

