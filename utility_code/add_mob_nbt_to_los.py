#!/usr/bin/env python3

import sys
import os
from lib_py3.library_of_souls import LibraryOfSouls

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

from quarry.types.nbt import TagCompound

los = LibraryOfSouls("souls_database.json")
los.upgrade_all()

#lines = [
#    r'''{id:"minecraft:phantom",CustomName:"\"Night Terror\"",Health:50.0f,Size:6,Attributes:[{Base:50.0d,Name:"generic.maxHealth"},{Base:100.0d,Name:"generic.followRange"}],Tags:["boss_chargerstrong","boss_targetplayer"],HandItems:[{id:"minecraft:arrow",Count:1b,tag:{display:{Name:"\"Phantom Fang\""},AttributeModifiers:[{UUIDMost:-6498451240576266699L,UUIDLeast:-6858106810304442920L,Amount:12.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
#    r'''{id:"minecraft:magma_cube",CustomName:"{\"text\":\"World Ender\"}",Health:1000.0f,Attributes:[{Base:1000.0d,Name:"generic.maxHealth"}],Size:1}''',
#]
#
#for line in lines:
#    mobnbt = TagCompound.from_mojangson(line)
#    try:
#        name = los.add_soul(mobnbt)
#        print(f"Added {name}")
#    except Exception as e:
#        print(e)
#

los.save()
