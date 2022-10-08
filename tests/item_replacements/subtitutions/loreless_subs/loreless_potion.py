#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Substitutions: Loreless: Matching potion",
    template_item=r'''{id:"minecraft:potion",tag:{AttributeModifiers:[{Amount:1.0d,AttributeName:"minecraft:generic.armor_toughness",Name:"MMDummy",Operation:2,UUID:[I;-1016107944,1547518597,-1657039478,-306805767]}],CustomPotionColor:14192676,Enchantments:[{id:"minecraft:power",lvl:1s}],HideFlags:103,Monumenta:{Stock:{Effects:[{EffectDuration:6000,EffectStrength:1.0d,EffectType:"Haste"},{EffectDuration:100,EffectStrength:1.0d,EffectType:"Nausea"}]}},Potion:"minecraft:mundane",display:{Lore:['{"text":""}','{"italic":false,"color":"gray","text":"When Consumed:"}','{"italic":false,"color":"#4ac2e5","extra":[{"italic":false,"color":"dark_gray","text":"(5:00)"}],"text":"Haste I "}','{"italic":false,"color":"#d02e28","extra":[{"italic":false,"color":"dark_gray","text":"(0:05)"}],"text":"Nausea "}'],Name:'{"bold":true,"italic":false,"underlined":false,"color":"#c6c2b6","text":"Worker\'s Pale Ale"}'},plain:{display:{Lore:["","When Consumed:","Haste I (5:00)","Nausea (0:05)"],Name:"Worker's Pale Ale"}}}}''',
    item_under_test=r'''{Count:1b,Slot:13b,id:"minecraft:potion",tag:{CustomPotionColor:14192676,CustomPotionEffects:[{Ambient:1b,Amplifier:0b,Duration:100,Id:9b,ShowIcon:1b,ShowParticles:1b},{Ambient:1b,Amplifier:0b,Duration:3600,Id:3b,ShowIcon:1b,ShowParticles:1b}],Potion:"minecraft:mundane",display:{Name:'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"white","text":"Worker\'s Pale Ale"}],"text":""}'},plain:{display:{Name:"Worker's Pale Ale"}}}}''',
    expected_result_item=r'''{Count:1b,Slot:13b,id:"minecraft:potion",tag:{AttributeModifiers:[{Amount:1.0d,AttributeName:"minecraft:generic.armor_toughness",Name:"MMDummy",Operation:2,UUID:[I;-1016107944,1547518597,-1657039478,-306805767]}],CustomPotionColor:14192676,Enchantments:[{id:"minecraft:power",lvl:1s}],HideFlags:103,Monumenta:{Stock:{Effects:[{EffectDuration:6000,EffectStrength:1.0d,EffectType:"Haste"},{EffectDuration:100,EffectStrength:1.0d,EffectType:"Nausea"}]}},Potion:"minecraft:mundane",display:{Lore:['{"text":""}','{"italic":false,"color":"gray","text":"When Consumed:"}','{"italic":false,"color":"#4ac2e5","extra":[{"italic":false,"color":"dark_gray","text":"(5:00)"}],"text":"Haste I "}','{"italic":false,"color":"#d02e28","extra":[{"italic":false,"color":"dark_gray","text":"(0:05)"}],"text":"Nausea "}'],Name:'{"bold":true,"italic":false,"underlined":false,"color":"#c6c2b6","text":"Worker\'s Pale Ale"}'},plain:{display:{Lore:["","When Consumed:","Haste I (5:00)","Nausea (0:05)"],Name:"Worker's Pale Ale"}}}}'''
)
test_item.run()
