#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib_monumenta import entity_update

"""
Entity update list...more or less a copy of item replacement list,
but I need to update the documentation of both. Item replacement
list documentation is accurate and similar enough for now.

================================================================================
PLEASE NOTE:
This replaces entities AND block entities.
It provides both in the same search, as
- block entities can contain entities (spawners)
- block entities and entities can contain items (not searched here)
- items can contain block entities (shulker boxes, shields/banners...)
- items can contain entities (spawn eggs)

That doesn't even cover commands, but that's a whole nother beast.
Commands can be dumped from command blocks to text files if needed.
================================================================================

Entity update list - this MUST be mutable!

This is an ordered list of update definitions
Each update definition is a list that contains a
    pattern matching list and a list of actions to perform
"""

# Try "init" to show what this list does; you can even
# run this library as a script and skip the other stuff.
#KingsValleyBuild = entity_update.UpdateEntities(["init"],[
KingsValleyBuild = entity_update.UpdateEntities([],[
    [
        {
            "id":"minecraft:spider",
            "name":"Fanged Spider",
        },
        [
            "nbt", "update", ur'''{Health:12.0f,ActiveEffects:[{Ambient:1b,ShowParticles:1b,Duration:1200,Id:16b,Amplifier:0b}],HandItems:[{id:"minecraft:stone_sword",Count:1b,tag:{ench:[{lvl:5s,id:16s}]},Damage:0s},{}]}''',
        ]
    ],
    [
        {
            "nbt":ur'''{Tags:["Elite"]}''',
        },
        [
            "name", "color", '6',
        ]
    ],
    [
        {
            "name_format":u'6',
            "none": {
                "id":"minecraft:villager",
            }
        },
        [
            "nbt", "update", ur'''{Tags:["Elite"]}''',
        ]
    ],
    [
        {
            "id":"minecraft:mob_spawner",
        },
        [
            "nbt", "update", ur'''{Delay:0s}''',
        ]
    ],
    [
        {
            "id":"minecraft:mob_spawner",
            "nbt":ur'''{SpawnData:{Tags:["Elite","FatigueAura"]}}''',
        },
        [
            "nbt", "update", ur'''{SpawnCount:1s,SpawnRange:4s,RequiredPlayerRange:30s,Delay:10s,MinSpawnDelay:32767s,MaxSpawnDelay:32767s,MaxNearbyEntities:30s}''',
        ]
    ],
    [
        {
            "id":"minecraft:mob_spawner",
            "nbt":ur'''{SpawnData:{Tags:["Elite","HungerAura"]}}''',
        },
        [
            "nbt", "update", ur'''{SpawnCount:1s,SpawnRange:4s,RequiredPlayerRange:30s,Delay:10s,MinSpawnDelay:32767s,MaxSpawnDelay:32767s,MaxNearbyEntities:30s}''',
        ]
    ],
    [
        {
            "id":"minecraft:mob_spawner",
            "nbt":ur'''{SpawnData:{Tags:["Elite","SlownessAura"]}}''',
        },
        [
            "nbt", "update", ur'''{SpawnCount:1s,SpawnRange:4s,RequiredPlayerRange:30s,Delay:10s,MinSpawnDelay:32767s,MaxSpawnDelay:32767s,MaxNearbyEntities:30s}''',
        ]
    ],
    [
        {
            "id":"minecraft:mob_spawner",
            "nbt":ur'''{SpawnData:{Tags:["Elite","WeaknessAura"]}}''',
        },
        [
            "nbt", "update", ur'''{SpawnCount:1s,SpawnRange:4s,RequiredPlayerRange:30s,Delay:10s,MinSpawnDelay:32767s,MaxSpawnDelay:32767s,MaxNearbyEntities:30s}''',
        ]
    ],
    [
        {
            "id":"minecraft:wither_skeleton",
            "nbt":ur'''{Tags:["Elite","FatigueAura"]}''',
        },
        [
            "nbt", "update", ur'''{PersistenceRequired:1b,id:"minecraft:wither_skeleton",CustomName:"Harbinger of Fatigue",CustomNameVisible:1b,Tags:["Elite","FatigueAura"],ArmorItems:[{id:"minecraft:golden_boots",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:2359296}}},{id:"minecraft:golden_chestplate",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:skull",Damage:3s,Count:1b,tag:{SkullOwner:{Id:"9eee34ea-2c9f-47a1-98f8-34105af45215",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYTVmMzE3ZmFhOGRjZjEzYTJmYzE4ZWEwYmYwYTA3MzZhNGZmOTVjMjg1MDFiYjFjZmE0MzAyNTQyMjc4ZjhhIn19fQ=="}]}}}}],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{ench:[{id:16s,lvl:10s}]}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{Base:1,Patterns:[{Pattern:"tt",Color:0},{Pattern:"cbo",Color:0},{Pattern:"bt",Color:0},{Pattern:"bts",Color:1},{Pattern:"tts",Color:1}]}}}],ArmorDropChances:[-327.67F,-327.67F,-327.67F,-327.67F],HandDropChances:[-327.67F,-327.67F],Attributes:[{Name:"generic.maxHealth",Base:60.0d},{Name:"generic.movementSpeed",Base:0.21d},{Name:"generic.followRange",Base:25.0d}],Health:60.0f,ActiveEffects:[{Id:11b,Amplifier:0b,Duration:199980}]}''',
        ]
    ],
    [
        {
            "id":"minecraft:wither_skeleton",
            "nbt":ur'''{Tags:["Elite","HungerAura"]}''',
        },
        [
            "nbt", "update", ur'''{PersistenceRequired:1b,id:"minecraft:wither_skeleton",CustomName:"Harbinger of Hunger",CustomNameVisible:1b,Tags:["Elite","HungerAura"],ArmorItems:[{id:"minecraft:golden_boots",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:2359296}}},{id:"minecraft:golden_chestplate",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:skull",Damage:3s,Count:1b,tag:{SkullOwner:{Id:"9eee34ea-2c9f-47a1-98f8-34105af45215",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYTVmMzE3ZmFhOGRjZjEzYTJmYzE4ZWEwYmYwYTA3MzZhNGZmOTVjMjg1MDFiYjFjZmE0MzAyNTQyMjc4ZjhhIn19fQ=="}]}}}}],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{ench:[{id:16s,lvl:10s}]}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{Base:1,Patterns:[{Pattern:"tt",Color:0},{Pattern:"cbo",Color:0},{Pattern:"bt",Color:0},{Pattern:"bts",Color:1},{Pattern:"tts",Color:1}]}}}],ArmorDropChances:[-327.67F,-327.67F,-327.67F,-327.67F],HandDropChances:[-327.67F,-327.67F],Attributes:[{Name:"generic.maxHealth",Base:60.0d},{Name:"generic.movementSpeed",Base:0.21d},{Name:"generic.followRange",Base:25.0d}],Health:60.0f,ActiveEffects:[{Id:11b,Amplifier:0b,Duration:199980}]}''',
        ]
    ],
    [
        {
            "id":"minecraft:wither_skeleton",
            "nbt":ur'''{Tags:["Elite","SlownessAura"]}''',
        },
        [
            "nbt", "update", ur'''{PersistenceRequired:1b,id:"minecraft:wither_skeleton",CustomName:"Harbinger of Slowness",CustomNameVisible:1b,Tags:["Elite","SlownessAura"],ArmorItems:[{id:"minecraft:golden_boots",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:2359296}}},{id:"minecraft:golden_chestplate",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:skull",Damage:3s,Count:1b,tag:{SkullOwner:{Id:"9eee34ea-2c9f-47a1-98f8-34105af45215",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYTVmMzE3ZmFhOGRjZjEzYTJmYzE4ZWEwYmYwYTA3MzZhNGZmOTVjMjg1MDFiYjFjZmE0MzAyNTQyMjc4ZjhhIn19fQ=="}]}}}}],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{ench:[{id:16s,lvl:10s}]}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{Base:1,Patterns:[{Pattern:"tt",Color:0},{Pattern:"cbo",Color:0},{Pattern:"bt",Color:0},{Pattern:"bts",Color:1},{Pattern:"tts",Color:1}]}}}],ArmorDropChances:[-327.67F,-327.67F,-327.67F,-327.67F],HandDropChances:[-327.67F,-327.67F],Attributes:[{Name:"generic.maxHealth",Base:60.0d},{Name:"generic.movementSpeed",Base:0.21d},{Name:"generic.followRange",Base:25.0d}],Health:60.0f,ActiveEffects:[{Id:11b,Amplifier:0b,Duration:199980}]}''',
        ]
    ],
    [
        {
            "id":"minecraft:wither_skeleton",
            "nbt":ur'''{Tags:["Elite","WeaknessAura"]}''',
        },
        [
            "nbt", "update", ur'''{PersistenceRequired:1b,id:"minecraft:wither_skeleton",CustomName:"Harbinger of Weakness",CustomNameVisible:1b,Tags:["Elite","WeaknessAura"],ArmorItems:[{id:"minecraft:golden_boots",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:2359296}}},{id:"minecraft:golden_chestplate",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:skull",Damage:3s,Count:1b,tag:{SkullOwner:{Id:"9eee34ea-2c9f-47a1-98f8-34105af45215",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYTVmMzE3ZmFhOGRjZjEzYTJmYzE4ZWEwYmYwYTA3MzZhNGZmOTVjMjg1MDFiYjFjZmE0MzAyNTQyMjc4ZjhhIn19fQ=="}]}}}}],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{ench:[{id:16s,lvl:10s}]}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{Base:1,Patterns:[{Pattern:"tt",Color:0},{Pattern:"cbo",Color:0},{Pattern:"bt",Color:0},{Pattern:"bts",Color:1},{Pattern:"tts",Color:1}]}}}],ArmorDropChances:[-327.67F,-327.67F,-327.67F,-327.67F],HandDropChances:[-327.67F,-327.67F],Attributes:[{Name:"generic.maxHealth",Base:60.0d},{Name:"generic.movementSpeed",Base:0.21d},{Name:"generic.followRange",Base:25.0d}],Health:60.0f,ActiveEffects:[{Id:11b,Amplifier:0b,Duration:199980}]}''',
        ]
    ],
])

KingsValley = entity_update.UpdateEntities([],[
    KingsValleyBuild,
    [
        {
            "id":"minecraft:hopper_minecart",
        },
        [
            "id", "minecraft:chest_minecart",
        ]
    ],
])


