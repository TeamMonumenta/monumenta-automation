#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Rules: Preserve Crossbow Item: Empty",
    template_item=r'''{id: "minecraft:crossbow", tag: {Charged: 1b, Damage: 0, display: {Name: '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"white","text":"Simple Crossbow"}],"text":""}', Lore: ['{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"dark_gray","text":"King\'s Valley : Tier I"}],"text":""}', '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gray","text":""}],"text":""}', '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gray","text":"When in main hand:"}],"text":""}', '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"dark_green","text":" 9 Projectile Damage"}],"text":""}', '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"dark_green","text":" 1 Projectile Speed"}],"text":""}']}, ChargedProjectiles: [{id: "minecraft:arrow", Count: 1b}]}, Count: 1b}''',
    item_under_test=r'''{id: "minecraft:crossbow", tag: {Charged: 0b, Damage: 0, display: {Name: '{"text":"Simple Crossbow"}', Lore: ['{"text":"Replace me."}']}, ChargedProjectiles: []}, Count: 1b}''',
    expected_result_item=r'''{id: "minecraft:crossbow", tag: {Charged: 0b, Damage: 0, display: {Name: '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"white","text":"Simple Crossbow"}],"text":""}', Lore: ['{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"dark_gray","text":"King\'s Valley : Tier I"}],"text":""}', '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gray","text":""}],"text":""}', '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gray","text":"When in main hand:"}],"text":""}', '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"dark_green","text":" 9 Projectile Damage"}],"text":""}', '{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"dark_green","text":" 1 Projectile Speed"}],"text":""}']}, ChargedProjectiles: []}, Count: 1b}'''
)
test_item.run()

