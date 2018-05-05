#!/usr/bin/env python2.7
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
            "id":"minecraft:mob_spawner",
            "nbt":ur'''{SpawnData:{CustomName:"Buried Remains",id:"minecraft:skeleton"}}''',
        },
        [
            "nbt", "update", ur'''{MaxNearbyEntities:10s,RequiredPlayerRange:16s,SpawnCount:4s,MaxSpawnDelay:300s,Delay:0s,id:"minecraft:mob_spawner",SpawnRange:4s,MinSpawnDelay:100s}''',
        ]
    ],
    [
        {
            "id":"minecraft:skeleton",
            "name":"Buried Remains",
        },
        [
            "nbt", "replace", ur'''{CustomName:"Buried Remains",Passengers:[{Potion:{id:"minecraft:splash_potion",Count:1b,tag:{CustomPotionColor:12566463,CustomPotionEffects:[{Duration:1,Id:7b,Amplifier:0b}],Potion:"minecraft:harming"}},id:"minecraft:potion"}],Health:20.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:11579568}}},{},{},{}],Attributes:[{Base:20,Name:"generic.maxHealth"},{Base:24,Name:"generic.followRange"},{Base:0.15d,Name:"generic.knockbackResistance"},{Base:3,Name:"generic.attackDamage"}],id:"minecraft:skeleton",CustomNameVisible:0b,HandItems:[{id:"minecraft:bone",Count:1b},{id:"minecraft:bone",Count:1b}]}''',
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


