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
            "tag":[u"!Mariya"],
        },
        [
            "tag", [u"IMMOVABLE_NPCS"],
        ]
    ],
])


# Try "init" to show what this list does; you can even
# run this library as a script and skip the other stuff.
#KingsValleyBuild = entity_update.UpdateEntities(["init"],[
KingsValleyBuild = entity_update.UpdateEntities([],[
    [ # Data types are less strict when comparing with our code, but be careful of tags that are (or should be!) missing in spawners; Pos, Motion, Rotation, UUID, anything with Spigot/Bukkit, WorldUUID, Fire, OnGround, etc. Basically just take out everything that isn't needed.
        {
            "id":"minecraft:zombie",
            "nbt":ur'''{Health:15.0f,CustomName:"Mansion Wraith"}''',
        },
        [
            "name", "set", ur"Soulleather Banshee",
        ]
    ],
    [ # TODO needs fix; will delete other attributes because attributes are stored as a list!
        {
            "name":"Mansion Wraith"
        },
        [
            "nbt", "update", ur'''{Attributes:[{Base:20.0d,Name:"generic.maxHealth"},{Base:1.0d,Name:"generic.knockbackResistance"},{Base:0.24d,Name:"generic.movementSpeed"},{Base:2.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:35.0d,Name:"generic.followRange"},{Base:3.0d,Name:"generic.attackDamage"}],Health:20.0f}''',
        ]
    ],
    [ # TODO double check data types when setting here; NBT will break if the types are set wrong (ie attributes need to be type Double {0.0d})
        {
            "name":"Animated Potions"
        },
        [
            "id", "minecraft:creeper",
            "nbt", "replace", ur'''{CustomName:"Animated Potions",Health:15f,ExplosionRadius:0b,Fuse:30s,Tags:["boss_invisible"],Passengers:[{id:"minecraft:potion",Passengers:[{id:"minecraft:potion",Passengers:[{id:"minecraft:potion",Passengers:[{id:"minecraft:potion",Potion:{id:"minecraft:splash_potion",Count:1b,tag:{Potion:"minecraft:water",CustomPotionColor:3684408,CustomPotionEffects:[{Id:7b,Amplifier:2b,Duration:20}]}}}],Potion:{id:"minecraft:splash_potion",Count:1b,tag:{Potion:"minecraft:water",CustomPotionColor:6381921,CustomPotionEffects:[{Id:18b,Amplifier:0b,Duration:600}]}}}],Potion:{id:"minecraft:splash_potion",Count:1b,tag:{Potion:"minecraft:water",CustomPotionColor:10066329,CustomPotionEffects:[{Id:2b,Amplifier:1b,Duration:600}]}}}],Potion:{id:"minecraft:splash_potion",Count:1b,tag:{Potion:"minecraft:water",CustomPotionColor:13092807,CustomPotionEffects:[{Id:15b,Amplifier:0b,Duration:100}]}}}],Attributes:[{Name:generic.maxHealth,Base:15d},{Name:generic.movementSpeed,Base:0.33d}]}''',
        ]
    ],
    [
        {
            "name":"Tidal Terror",
        },
        [
            "nbt", "update", ur'''{Fuse:35s}''',
        ]
    ],
    # Save these for last; don't want to forget to handle Elites properly, do we?
    KingsValleyImmovable,
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


