#!/usr/bin/env python3

import os
import sys

from lib_py3.upgrade import upgrade_entity

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt
from quarry.types.text_format import unformat_text

if __name__ == '__main__':
    nbt_to_upgrade = '''{MaxNearbyEntities:6s,RequiredPlayerRange:16s,SpawnCount:4s,SpawnData:{Passengers:[{Passengers:[{BlockState:{Name:"minecraft:lava"},Time:1b,id:"minecraft:falling_block"}],Value:0s,id:"minecraft:experience_orb"}],Health:1.0f,Attributes:[{Base:1.0d,Name:"generic.max_health"}],Silent:1b,id:"minecraft:silverfish",ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:20b,Amplifier:4b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:14b,Amplifier:0b}]},MaxSpawnDelay:800s,Delay:0s,SpawnRange:4s,MinSpawnDelay:200s,SpawnPotentials:[{Entity:{Passengers:[{Passengers:[{BlockState:{Name:"minecraft:lava"},Time:1b,id:"minecraft:falling_block"}],Value:0s,id:"minecraft:experience_orb"}],Health:1.0f,Attributes:[{Base:1.0d,Name:"generic.max_health"}],Silent:1b,id:"minecraft:silverfish",ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:20b,Amplifier:4b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:14b,Amplifier:0b}]},Weight:1}]}'''
    nbt_to_upgrade = nbt.TagCompound.from_mojangson(nbt_to_upgrade)
    upgrade_entity(nbt_to_upgrade, regenerateUUIDs=True)
    print(nbt_to_upgrade.to_mojangson())
