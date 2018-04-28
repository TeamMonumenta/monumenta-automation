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

# Immovable team fix
KingsValleyImmovable = entity_update.UpdateEntities([],[
    [
        {
            "id":"minecraft:villager",
            "none":[
                {
                    "nbt":ur'''{Tags:["Mariya"]}''',
                }
            ]
        },
        [
            "nbt", "update", ur'''{Team:"IMMOVABLE_NPCS"}''',
        ]
    ],
])


# Try "init" to show what this list does; you can even
# run this library as a script and skip the other stuff.
#KingsValleyBuild = entity_update.UpdateEntities(["init"],[
KingsValleyBuild = entity_update.UpdateEntities([],[
    [
        {
            "tag":[u"lite"],
        },
        [
            "tag", [u"!lite"],
        ]
    ],
    [
        {
            "id":"minecraft:mob_spawner",
            "nbt":ur'''{SpawnData:{CustomName:"Infernal Archer",id:"minecraft:skeleton"}}''',
        },
        [
            "nbt", "update", ur'''{MaxNearbyEntities:8s,RequiredPlayerRange:16s,SpawnCount:2s,MaxSpawnDelay:600s,Delay:0s,id:"minecraft:mob_spawner",SpawnRange:4s,MinSpawnDelay:500s}''',
        ]
    ],
    [
        {
            "id":"minecraft:skeleton",
            "name":"Infernal Archer",
        },
        [
            "nbt", "replace", ur'''{ArmorDropChances:[-327.67f,-327.67f,-327.67f,-327.67f],CustomName:"Infernal Archer",Health:24.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:7667712}}},{id:"minecraft:chainmail_leggings",Count:1b},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:7667712}}},{id:"minecraft:skull",Count:1b,tag:{SkullOwner:{Id:"7db94d06-a33c-44ac-963b-6258c3bd70c9",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvOTgyMzJiZGQ2NmJkOTlhMzdlNjM0MzZhMDQ3NjczNWVjNGY4NGRjOTg4NTE2NjE1MGIzODJhZGE3NTdmIn19fQ=="}]}}},Damage:3}],Attributes:[{Base:24,Name:"generic.maxHealth"},{Base:0.2d,Name:"generic.movementSpeed"},{Base:25,Name:"generic.followRange"}],HandDropChances:[-327.67f,-327.67f],id:"minecraft:skeleton",ActiveEffects:[{Duration:199980,Id:12,Amplifier:0}],HandItems:[{id:"minecraft:bow",Count:1b,tag:{ench:[{lvl:1,id:48},{lvl:2,id:49},{lvl:2,id:50}]}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{Patterns:[{Pattern:"sc",Color:11},{Pattern:"mc",Color:1},{Pattern:"flo",Color:0},{Pattern:"bts",Color:1},{Pattern:"tts",Color:1}],Base:14}}}]}''',
        ]
    ],
    [
        {
            "id":"minecraft:mob_spawner",
            "nbt":ur'''{SpawnData:{id:"minecraft:vex",CustomName:"Seeker"}}''',
        },
        [
            "nbt", "update", ur'''{MaxNearbyEntities:8s,RequiredPlayerRange:18s,SpawnCount:3s,MaxSpawnDelay:4000s,Delay:0s,id:"minecraft:mob_spawner",SpawnRange:4s,MinSpawnDelay:2000s}''',
        ]
    ],
    [
        {
            "id":"minecraft:vex",
            "name":"Seeker",
        },
        [
            "nbt", "replace", ur'''{ArmorDropChances:[0.085f,0.085f,0.085f,-327.67f],CustomName:"Seeker",Health:6.0f,ArmorItems:[{},{},{},{id:"minecraft:skull",Count:1b,tag:{SkullOwner:{Id:"75c53779-1669-4fe7-8b3c-59d7b6439b5e",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYTdiOTg4MjdkOTc5Mzg1NTE0YTkzNmY5YTU5Njg4MmQzMmQ4ZWY3NTY3ZTdkOWE1MjM5NzgyZjk0NWU2OGIwIn19fQ=="}]}}},Damage:3}],Fire:20000,Attributes:[{Base:6,Name:"generic.maxHealth"},{Base:25,Name:"generic.followRange"}],HandDropChances:[-327.67f,-327.67f],id:"minecraft:vex",ActiveEffects:[{Duration:199980,Id:2,Amplifier:0}],HandItems:[{id:"minecraft:stone_sword",Count:1b},{id:"minecraft:stone_sword",Count:1b}]}''',
        ]
    ],
    [
        {
            "any":[
                {"name":'Air Wraith'},
                {"name":'Earth Wraith'},
                {"name":'Flame Wraith'},
                {"name":'Water Wraith'},
                {
                    "name":'Ghost',
                    "tag":["Elite"],
                },
            ]
        },
        [
            "tag", ["Elite","Invisible"],
        ]
    ],
    [ # That space was going to drive me nuts
        {
            "name":" Skeletal Abomination",
        },
        [
            "name", "set", "Skeletal Abomination",
        ]
    ],
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
            "name":"Harbinger of Fatigue",
        },
        [
            "nbt", "replace", ur'''{PersistenceRequired:1b,id:"minecraft:wither_skeleton",CustomName:"Harbinger of Fatigue",CustomNameVisible:1b,Tags:["Elite","FatigueAura"],ArmorItems:[{id:"minecraft:golden_boots",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:2359296}}},{id:"minecraft:golden_chestplate",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:skull",Damage:3s,Count:1b,tag:{SkullOwner:{Id:"9eee34ea-2c9f-47a1-98f8-34105af45215",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYTVmMzE3ZmFhOGRjZjEzYTJmYzE4ZWEwYmYwYTA3MzZhNGZmOTVjMjg1MDFiYjFjZmE0MzAyNTQyMjc4ZjhhIn19fQ=="}]}}}}],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{ench:[{id:16s,lvl:10s}]}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{Base:1,Patterns:[{Pattern:"tt",Color:0},{Pattern:"cbo",Color:0},{Pattern:"bt",Color:0},{Pattern:"bts",Color:1},{Pattern:"tts",Color:1}]}}}],ArmorDropChances:[-327.67F,-327.67F,-327.67F,-327.67F],HandDropChances:[-327.67F,-327.67F],Attributes:[{Name:"generic.maxHealth",Base:60.0d},{Name:"generic.movementSpeed",Base:0.21d},{Name:"generic.followRange",Base:25.0d}],Health:60.0f,ActiveEffects:[{Id:11b,Amplifier:0b,Duration:199980}]}''',
        ]
    ],
    [
        {
            "id":"minecraft:wither_skeleton",
            "name":"Harbinger of Hunger",
        },
        [
            "nbt", "replace", ur'''{PersistenceRequired:1b,id:"minecraft:wither_skeleton",CustomName:"Harbinger of Hunger",CustomNameVisible:1b,Tags:["Elite","HungerAura"],ArmorItems:[{id:"minecraft:golden_boots",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:2359296}}},{id:"minecraft:golden_chestplate",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:skull",Damage:3s,Count:1b,tag:{SkullOwner:{Id:"9eee34ea-2c9f-47a1-98f8-34105af45215",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYTVmMzE3ZmFhOGRjZjEzYTJmYzE4ZWEwYmYwYTA3MzZhNGZmOTVjMjg1MDFiYjFjZmE0MzAyNTQyMjc4ZjhhIn19fQ=="}]}}}}],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{ench:[{id:16s,lvl:10s}]}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{Base:1,Patterns:[{Pattern:"tt",Color:0},{Pattern:"cbo",Color:0},{Pattern:"bt",Color:0},{Pattern:"bts",Color:1},{Pattern:"tts",Color:1}]}}}],ArmorDropChances:[-327.67F,-327.67F,-327.67F,-327.67F],HandDropChances:[-327.67F,-327.67F],Attributes:[{Name:"generic.maxHealth",Base:60.0d},{Name:"generic.movementSpeed",Base:0.21d},{Name:"generic.followRange",Base:25.0d}],Health:60.0f,ActiveEffects:[{Id:11b,Amplifier:0b,Duration:199980}]}''',
        ]
    ],
    [
        {
            "id":"minecraft:wither_skeleton",
            "name":"Harbinger of Slowness",
        },
        [
            "nbt", "replace", ur'''{PersistenceRequired:1b,id:"minecraft:wither_skeleton",CustomName:"Harbinger of Slowness",CustomNameVisible:1b,Tags:["Elite","SlownessAura"],ArmorItems:[{id:"minecraft:golden_boots",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:2359296}}},{id:"minecraft:golden_chestplate",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:skull",Damage:3s,Count:1b,tag:{SkullOwner:{Id:"9eee34ea-2c9f-47a1-98f8-34105af45215",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYTVmMzE3ZmFhOGRjZjEzYTJmYzE4ZWEwYmYwYTA3MzZhNGZmOTVjMjg1MDFiYjFjZmE0MzAyNTQyMjc4ZjhhIn19fQ=="}]}}}}],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{ench:[{id:16s,lvl:10s}]}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{Base:1,Patterns:[{Pattern:"tt",Color:0},{Pattern:"cbo",Color:0},{Pattern:"bt",Color:0},{Pattern:"bts",Color:1},{Pattern:"tts",Color:1}]}}}],ArmorDropChances:[-327.67F,-327.67F,-327.67F,-327.67F],HandDropChances:[-327.67F,-327.67F],Attributes:[{Name:"generic.maxHealth",Base:60.0d},{Name:"generic.movementSpeed",Base:0.21d},{Name:"generic.followRange",Base:25.0d}],Health:60.0f,ActiveEffects:[{Id:11b,Amplifier:0b,Duration:199980}]}''',
        ]
    ],
    [
        {
            "id":"minecraft:wither_skeleton",
            "name":"Harbinger of Weakness",
        },
        [
            "nbt", "replace", ur'''{PersistenceRequired:1b,id:"minecraft:wither_skeleton",CustomName:"Harbinger of Weakness",CustomNameVisible:1b,Tags:["Elite","WeaknessAura"],ArmorItems:[{id:"minecraft:golden_boots",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:2359296}}},{id:"minecraft:golden_chestplate",Count:1b,tag:{ench:[{id:0s,lvl:2s},{id:4s,lvl:4s}]}},{id:"minecraft:skull",Damage:3s,Count:1b,tag:{SkullOwner:{Id:"9eee34ea-2c9f-47a1-98f8-34105af45215",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYTVmMzE3ZmFhOGRjZjEzYTJmYzE4ZWEwYmYwYTA3MzZhNGZmOTVjMjg1MDFiYjFjZmE0MzAyNTQyMjc4ZjhhIn19fQ=="}]}}}}],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{ench:[{id:16s,lvl:10s}]}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{Base:1,Patterns:[{Pattern:"tt",Color:0},{Pattern:"cbo",Color:0},{Pattern:"bt",Color:0},{Pattern:"bts",Color:1},{Pattern:"tts",Color:1}]}}}],ArmorDropChances:[-327.67F,-327.67F,-327.67F,-327.67F],HandDropChances:[-327.67F,-327.67F],Attributes:[{Name:"generic.maxHealth",Base:60.0d},{Name:"generic.movementSpeed",Base:0.21d},{Name:"generic.followRange",Base:25.0d}],Health:60.0f,ActiveEffects:[{Id:11b,Amplifier:0b,Duration:199980}]}''',
        ]
    ],
    # Save these for last; don't want to forget to handle Elites properly, do we?
    [
        {
            "id":"minecraft:villager",
            "none":[
                {
                    "nbt":ur'''{Tags:["Mariya"]}''',
                }
            ]
        },
        [
            "nbt", "update", ur'''{Team:"IMMOVABLE_NPCS"}''',
        ]
    ],
    [
        {
            "tag":[u"Elite"],
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
            "tag", [u"Elite"],
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


