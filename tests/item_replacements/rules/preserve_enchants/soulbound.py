#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from lib.item_test import ItemTest

test_item = ItemTest(
    test_name="Rules: Preserve Soulbound",
    template_item=r'''{id:"minecraft:golden_sword",tag:{Unbreakable:1,HideFlags:2,Enchantments:[{lvl:2s,id:"minecraft:efficiency"},{lvl:1s,id:"minecraft:knockback"},{lvl:1s,id:"minecraft:fire_aspect"}],display:{Lore:["§7Radiant","§7Hope","§8King's Valley : §4Artifact","§l","§7When in main hand:","§7 1.6 Attack Speed","§7 3 Attack Damage"],Name:"{\"text\":\"§e§l§nLight of Salvation\"}"},AttributeModifiers:[{UUIDMost:4598269408375358984L,UUIDLeast:-7980334193493528635L,Amount:0.0d,AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-3549468348533027207L,UUIDLeast:-5101475887946467451L,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:-8751945831914649559L,UUIDLeast:-7565408329895997931L,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}}''',
    item_under_test=r'''{id:"minecraft:golden_sword",tag:{Unbreakable:1,HideFlags:2,Enchantments:[{lvl:2s,id:"minecraft:efficiency"},{lvl:1s,id:"minecraft:knockback"},{lvl:1s,id:"minecraft:fire_aspect"}],display:{Lore:["§7Radiant","§7Hope","§8King's Valley : §4Artifact","§l","§7When in main hand:","§7 1.6 Attack Speed","§7 3 Attack Damage","* Soulbound to Combustible *"],Name:"{\"text\":\"§e§l§nLight of Salvation\"}"},AttributeModifiers:[{UUIDMost:4598269408375358984L,UUIDLeast:-7980334193493528635L,Amount:0.0d,AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-3549468348533027207L,UUIDLeast:-5101475887946467451L,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:-8751945831914649559L,UUIDLeast:-7565408329895997931L,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}}''',
    expected_result_item=r'''{id:"minecraft:golden_sword",tag:{Unbreakable:1,HideFlags:2,Enchantments:[{lvl:2s,id:"minecraft:efficiency"},{lvl:1s,id:"minecraft:knockback"},{lvl:1s,id:"minecraft:fire_aspect"}],display:{Lore:["§7Radiant","§7Hope","§8King's Valley : §4Artifact","§l","§7When in main hand:","§7 1.6 Attack Speed","§7 3 Attack Damage","* Soulbound to Combustible *"],Name:"{\"text\":\"§e§l§nLight of Salvation\"}"},AttributeModifiers:[{UUIDMost:4598269408375358984L,UUIDLeast:-7980334193493528635L,Amount:0.0d,AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-3549468348533027207L,UUIDLeast:-5101475887946467451L,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:-8751945831914649559L,UUIDLeast:-7565408329895997931L,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}}'''
)
test_item.run()

