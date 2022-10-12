#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Substitutions: Loreless: Frosted Potion",
    template_item=r'''{id:"minecraft:potion",tag:{AttributeModifiers:[{Amount:1.0d,AttributeName:"minecraft:generic.armor_toughness",Name:"MMDummy",Operation:2,UUID:[I;-1329892836,1717257533,-2052729597,949077985]}],CustomPotionColor:11387104,Enchantments:[{lvl:1s,id:"minecraft:power"}],HideFlags:103,Monumenta:{Stock:{Effects:[{EffectDuration:4800,EffectStrength:0.15d,EffectType:"Slow"}]}},Potion:"minecraft:mundane",display:{Lore:['{"text":""}','{"italic":false,"color":"gray","text":"When Consumed:"}','{"italic":false,"color":"#d02e28","extra":[{"italic":false,"color":"dark_gray","text":"(4:00)"}],"text":"-15% Speed "}'],Name:'{"bold":true,"italic":false,"underlined":false,"color":"#afc2e3","text":"Frosted Potion"}'},plain:{display:{Lore:["","When Consumed:","-15% Speed (4:00)"],Name:"Frosted Potion"}}}}''',
    item_under_test=r'''{Count:1b,Slot:6b,id:"minecraft:potion",tag:{Potion:"minecraft:long_slowness",display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#afc2e3","text":"Frosted Potion"}'}}}''',
    expected_result_item=r'''{Count:1b,Slot:6b,id:"minecraft:potion",tag:{AttributeModifiers:[{Amount:1.0d,AttributeName:"minecraft:generic.armor_toughness",Name:"MMDummy",Operation:2,UUID:[I;-1329892836,1717257533,-2052729597,949077985]}],CustomPotionColor:11387104,Enchantments:[{lvl:1s,id:"minecraft:power"}],HideFlags:103,Monumenta:{Stock:{Effects:[{EffectDuration:4800,EffectStrength:0.15d,EffectType:"Slow"}]}},Potion:"minecraft:mundane",display:{Lore:['{"text":""}','{"italic":false,"color":"gray","text":"When Consumed:"}','{"italic":false,"color":"#d02e28","extra":[{"italic":false,"color":"dark_gray","text":"(4:00)"}],"text":"-15% Speed "}'],Name:'{"bold":true,"italic":false,"underlined":false,"color":"#afc2e3","text":"Frosted Potion"}'},plain:{display:{Lore:["","When Consumed:","-15% Speed (4:00)"],Name:"Frosted Potion"}}}}'''
)
test_item.run()
