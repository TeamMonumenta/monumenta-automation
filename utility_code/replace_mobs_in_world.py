#!/usr/bin/env python3

# For interactive shell
import readline
import code

import sys
import os
import getopt
import re
from pprint import pprint

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path
from lib_py3.common import eprint, parse_name_possibly_json, get_named_hand_items
from lib_py3.world import World

def pop_if_present(spawner_entity, entity_path, log_handle, key):
    if isinstance(spawner_entity, nbt.TagCompound) and key in spawner_entity.value:
        if log_handle is not None:
            log_handle.write("Popping '{}' from spawner entity at {}\n".format(key, get_debug_string_from_entity_path(entity_path)))
        spawner_entity.value.pop(key)

def remove_tags_from_spawner_entity(spawner_entity, entity_path, log_handle):
    pop_if_present(spawner_entity, entity_path, log_handle, 'Pos')
    pop_if_present(spawner_entity, entity_path, log_handle, 'Leashed')
    pop_if_present(spawner_entity, entity_path, log_handle, 'Air')
    pop_if_present(spawner_entity, entity_path, log_handle, 'OnGround')
    pop_if_present(spawner_entity, entity_path, log_handle, 'Dimension')
    pop_if_present(spawner_entity, entity_path, log_handle, 'Rotation')
    pop_if_present(spawner_entity, entity_path, log_handle, 'WorldUUIDMost')
    pop_if_present(spawner_entity, entity_path, log_handle, 'WorldUUIDLeast')
    pop_if_present(spawner_entity, entity_path, log_handle, 'HurtTime')
    pop_if_present(spawner_entity, entity_path, log_handle, 'HurtByTimestamp')
    pop_if_present(spawner_entity, entity_path, log_handle, 'FallFlying')
    pop_if_present(spawner_entity, entity_path, log_handle, 'PortalCooldown')
    pop_if_present(spawner_entity, entity_path, log_handle, 'FallDistance')
    pop_if_present(spawner_entity, entity_path, log_handle, 'DeathTime')
    pop_if_present(spawner_entity, entity_path, log_handle, 'HandDropChances')
    pop_if_present(spawner_entity, entity_path, log_handle, 'ArmorDropChances')
    pop_if_present(spawner_entity, entity_path, log_handle, 'CanPickUpLoot')
    pop_if_present(spawner_entity, entity_path, log_handle, 'Bukkit.updateLevel')
    pop_if_present(spawner_entity, entity_path, log_handle, 'Spigot.ticksLived')
    pop_if_present(spawner_entity, entity_path, log_handle, 'Paper.AAAB')
    pop_if_present(spawner_entity, entity_path, log_handle, 'Paper.Origin')
    pop_if_present(spawner_entity, entity_path, log_handle, 'Paper.FromMobSpawner')
    pop_if_present(spawner_entity, entity_path, log_handle, 'Team')

    # Recurse over passengers
    if (spawner_entity.has_path('Passengers')):
        remove_tags_from_spawner_entity(spawner_entity.at_path('Passengers'), entity_path, log_handle)

def remove_tags_from_entities_in_spawner(entity, entity_path, log_handle):
    '''
    Checks if this entity is a spawner - and if so, removes junk tags from its SpawnPotentials and SpawnData
    Safe to give any entity - will do nothing if not a spawner
    '''
    # Remove position tags from mobs in spawners
    if entity.has_path('SpawnPotentials'):
        for nested_entity in entity.at_path('SpawnPotentials').value:
            if nested_entity.has_path('Entity'):
                remove_tags_from_spawner_entity(nested_entity.at_path('Entity'), entity_path, log_handle)
    if entity.has_path("SpawnData"):
        remove_tags_from_spawner_entity(entity.at_path("SpawnData"), entity_path, log_handle)

mobs_to_replace = [
    # V1 replacements on xyz date
    {
        'rules': {
            'id': 'minecraft:zombie_pigman',
            'CustomName': '§6Kreepa Kultist'
        },
        'mojangson': r'''{Anger:9999s,CustomName:"{\"text\":\"Kreepa Kultist\"}",Health:40.0f,ArmorItems:[{id:"minecraft:iron_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§bKreepaIronBoots\"}"}}},{id:"minecraft:iron_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§bKreepaIronPants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:8398884,Name:"{\"text\":\"§bKreepaChest\"}"}}},{id:"minecraft:creeper_head",Count:1b,tag:{display:{Name:"{\"text\":\"§bKreepaHead\"}"}}}],Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],id:"minecraft:zombie_pigman",HandItems:[{id:"minecraft:stone_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§bPoison Ivy\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:-3110836741443598160L,UUIDLeast:-9119148225133807228L,Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': '§6Kreepa Marskman'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"Kreepa Marksman\"}",Health:30.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:8398884,Name:"{\"text\":\"§bKreepaBoots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:8398884,Name:"{\"text\":\"§bKreepaPants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"§bKreepaChest2\"}"}}},{id:"minecraft:creeper_head",Count:1b,tag:{display:{Name:"{\"text\":\"§bKreepaHead\"}"}}}],Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],id:"minecraft:skeleton",HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§bSoulvenom Bow\"}"},Enchantments:[{lvl:1s,id:"minecraft:punch"},{lvl:4s,id:"minecraft:power"}],Damage:0}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:blaze',
            'CustomName': 'Enraged Blaze'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"Radiant Blaze\"}",Health:30.0f,Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],id:"minecraft:blaze",Tags:["boss_fireball"]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Pyro Miner'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"Pyro Miner\"}",Health:40.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:5643800,Name:"{\"text\":\"§fInfernal Boots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:5643800,Name:"{\"text\":\"§fInfernal Pants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:5643800,Name:"{\"text\":\"§fInfernal Tunic\"}"}}},{id:"minecraft:leather_helmet",Count:1b,tag:{display:{color:3416859,Name:"{\"text\":\"§fBurnt Helm\"}"}}}],Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],id:"minecraft:skeleton",Tags:["boss_blockbreak"],HandItems:[{id:"minecraft:iron_pickaxe",Count:1b,tag:{display:{Name:"{\"text\":\"§bBasanite Miner\\u0027s Pick\"}"},Damage:0,AttributeModifiers:[{UUIDMost:6439584543901370625L,UUIDLeast:-5460530576207987635L,Amount:9.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'Mage Defender'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"Mage Defender\"}",Health:40.0f,ArmorItems:[{id:"minecraft:chainmail_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§bAquamarineBoots\"}"}}},{id:"minecraft:chainmail_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§bAquamarinePants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:3287104,Name:"{\"text\":\"§1§lVoidguard\"}"}}},{}],Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],id:"minecraft:zombie",HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§bArcane Deathbringer\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:6490429914453657687L,UUIDLeast:-7163478804406197079L,Amount:8.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'CustomName': '§6Enraged Captain'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"§6Enraged Captain\"}",Health:70.0f,ArmorItems:[{id:"minecraft:iron_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§fEnragedCaptainBoots\"}"},Enchantments:[{lvl:3s,id:"minecraft:fire_protection"}],Damage:0}},{id:"minecraft:chainmail_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§fEnragedCaptainPants\"}"},Damage:0}},{id:"minecraft:iron_chestplate",Count:1b,tag:{display:{Name:"{\"text\":\"§fEnragedCaptainChest\"}"},Enchantments:[{lvl:4s,id:"minecraft:projectile_protection"}],Damage:0}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"8a5020df-1921-45a9-9346-3e376b122865",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvNmVkMzExOTU0MDJmODNhMDI5ZGNiYzA5MDUzNmEyNDRkOGNiMjU1MmE4OWIzZGZmZWZmM2Y5ZjUzZjRlNTIzOCJ9fX0="}]}},display:{Name:"{\"text\":\"§fEnragedCaptainHead\"}"}}}],Attributes:[{Base:70.0d,Name:"generic.maxHealth"}],id:"minecraft:wither_skeleton",Tags:["Elite","boss_charger"],HandItems:[{id:"minecraft:iron_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§fEnraged Captain\\u0027s Axe\"}"},Enchantments:[{lvl:3s,id:"minecraft:sharpness"},{lvl:1s,id:"minecraft:knockback"}]}},{id:"minecraft:shield",Count:1b,tag:{display:{Name:"{\"text\":\"§fEnraged Captain\\u0027s Shield\"}"}}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': '§6Master Scavenger'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"§6Master Scavenger\"}",Health:90.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"§bScavengerBoots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:5251875,Name:"{\"text\":\"§bScavengerPants\"}"}}},{id:"minecraft:chainmail_chestplate",Count:1b,tag:{Enchantments:[{lvl:4s,id:"minecraft:projectile_protection"},{lvl:4s,id:"minecraft:blast_protection"}],display:{Name:"{\"text\":\"§bScavengerChest\"}"},Damage:0}},{}],Attributes:[{Base:90.0d,Name:"generic.maxHealth"}],id:"minecraft:skeleton",Tags:["boss_charger","Elite"],HandItems:[{id:"minecraft:stone_hoe",Count:1b,tag:{display:{Name:"{\"text\":\"§bScavenger\\u0027s Scythe\"}"},Enchantments:[{lvl:5s,id:"minecraft:sharpness"}],AttributeModifiers:[{UUIDMost:3528639911520192138L,UUIDLeast:-5188345177487516701L,Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Scavenger Marksman'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"Scavenger Marksman\"}",Health:30.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§bScavengerMarkBoots\"}"},Damage:0}},{id:"minecraft:chainmail_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§bScavengerAssasinPants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:15100703,Name:"{\"text\":\"§bScavengerMarkChest\"}"}}},{}],Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],id:"minecraft:skeleton",HandItems:[{id:"minecraft:bow",Count:1b,tag:{Enchantments:[{lvl:1s,id:"minecraft:punch"},{lvl:3s,id:"minecraft:power"}],display:{Name:"{\"text\":\"§bSoulvenom Bow\"}"},Damage:0}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie_villager',
            'CustomName': 'Feyrune Defender'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"Feyrune Defender\"}",Health:35.0f,ArmorItems:[{id:"minecraft:chainmail_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyruneDefenderBoots\"}"},Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:4345646,Name:"{\"text\":\"§fFeyruneDefenderPants\"}"},Damage:0}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:7646748,Name:"{\"text\":\"§fFeyruneDefenderChest\"}"},Damage:0}},{}],Attributes:[{Base:35.0d,Name:"generic.maxHealth"},{Base:1.0d,Name:"generic.knockbackResistance"}],id:"minecraft:zombie_villager",HandItems:[{id:"minecraft:wooden_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyrune Defender\\u0027s Axe\"}"},Enchantments:[{lvl:1s,id:"minecraft:unbreaking"},{lvl:1s,id:"minecraft:knockback"}]}},{id:"minecraft:golden_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyruneDefenderAxe2\"}"},Damage:0}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'Feyrune Swarmer'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"Feyrune Swarmer\"}",IsBaby:1b,Health:10.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"§fFeyruneSwarmerV1Boots\"}"},Damage:0}},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{Enchantments:[{lvl:1s,id:"minecraft:fire_protection"}],display:{color:8439583,Name:"{\"text\":\"§fFeyruneSwarmerV1Chest\"}"},Damage:0}},{id:"minecraft:dark_oak_leaves",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyruneSwarmerV1Head\"}"}}}],Attributes:[{Base:10.0d,Name:"generic.maxHealth"}],id:"minecraft:zombie",HandItems:[{id:"minecraft:stick",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyrune Swarmer Staff\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:-8758235605642295191L,UUIDLeast:-9179479420119590084L,Amount:-0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:3763681251137896589L,UUIDLeast:-8226037626211480689L,Amount:4.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{id:"minecraft:azure_bluet",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyruneSwarmerV1Flower\"}"}}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'book'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"Feyrune Minion\"}",IsBaby:1b,Health:10.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"§fFeyruneSwarmerV2Boots\"}"}}},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:6192150,Name:"{\"text\":\"§fFeyruneSwarmerV2Chest\"}"},Enchantments:[{lvl:1s,id:"minecraft:fire_protection"}],Damage:0}},{id:"minecraft:dark_oak_leaves",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyruneSwarmerV2Head\"}"}}}],Attributes:[{Base:10.0d,Name:"generic.maxHealth"}],id:"minecraft:zombie",HandItems:[{id:"minecraft:stick",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyrune Swarmer Staff\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:-8758235605642295191L,UUIDLeast:-9179479420119590084L,Amount:-0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:3763681251137896589L,UUIDLeast:-8226037626211480689L,Amount:4.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{id:"minecraft:blue_orchid",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyruneSwarmerV2Flower\"}"}}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'Spore Swarmer'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"Spore Swarmer\"}",Passengers:[{Potion:{id:"minecraft:splash_potion",Count:1b,tag:{Potion:"minecraft:harming"}},id:"minecraft:potion"}],IsBaby:1b,Health:10.0f,ArmorItems:[{id:"minecraft:chainmail_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§bSporeSwarmerBoots\"}"}}},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:4673362,Name:"{\"text\":\"§bSporeSwarmerChest\"}"}}},{id:"minecraft:red_mushroom_block",Count:1b}],Attributes:[{Base:10.0d,Name:"generic.maxHealth"}],id:"minecraft:zombie",HandItems:[{id:"minecraft:brown_mushroom",Count:1b,tag:{AttributeModifiers:[{UUIDMost:3986171858156734267L,UUIDLeast:-8071532259608096167L,Amount:5.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Pirate Archer'
        },
        'mojangson': r'''{id:"minecraft:skeleton",CustomName:"{\"text\":\"Pirate Archer\"}",Health:30.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:4673362,Name:"{\"text\":\"§bPirateBoots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:4673362,Name:"{\"text\":\"§bPiratePants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:6192150,Name:"{\"text\":\"§bPirateChest\"}"}}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"1165dfc5-ebc2-44ee-aee2-cfc3c4e115ab",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvN2M0NjUzODZiYmU5ZmFmMTQzN2FmNjM3N2Q2NjczNWRjNWExNWVhNWNlZGYyNmJkOTVmZDNmZTY2YjNhZmNkIn19fQ=="}]}},display:{Name:"{\"text\":\"Pirate Girl\"}"}}}],Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§bSteelwood Bow\"}"},Enchantments:[{lvl:2s,id:"minecraft:power"}],Damage:0}},{id:"minecraft:tipped_arrow",Count:1b,tag:{CustomPotionEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:120,Id:18b,Amplifier:0b}],Potion:"minecraft:empty"}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'Pirate Swordsman'
        },
        'mojangson': r'''{id:"minecraft:zombie",CustomName:"{\"text\":\"Pirate Swordsman\"}",Health:30.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:4673362,Name:"{\"text\":\"§bPirateBoots\"}"},Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:4673362,Name:"{\"text\":\"§bPiratePants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:6192150,Name:"{\"text\":\"§bPirateChest\"}"}}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"99b222b4-9770-4154-8589-bae30d73b68d",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvZTBjZjhjYWViNWI4OTYxODg4YmQ4NmZhOTgzNjk0YmYxNTFmOWEzZTU1NzVjZGQwNDA5MDYzMWZlZTUwYmNjNiJ9fX0="}]}},display:{Name:"{\"text\":\"Villager Pirate\"}"}}}],Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§7§lArachnidruid Cutlass\"}"},Enchantments:[{lvl:2s,id:"minecraft:sharpness"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'CustomName': '§6Pirate Captain'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"§6Pirate Captain\"}",Health:90.0f,ArmorItems:[{id:"minecraft:golden_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§bPirateCaptainBoots\"}"}}},{id:"minecraft:chainmail_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§bPirateCaptainPants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:6192150,Name:"{\"text\":\"§bPirateCaptainChest\"}"}}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"8c365419-8c9b-4886-b796-21261e38a473",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvN2FlODIzZTFhYzc0YmNlMGZkYzM2MWYyZWM1NDk3ZDg4NDU4ZmZlZTRhN2VjMzcwM2JlMzY5Zjg2ZTI4Nzc4YiJ9fX0="}]}},display:{Name:"{\"text\":\"Pirate\"}"}}}],Attributes:[{Base:90.0d,Name:"generic.maxHealth"}],id:"minecraft:wither_skeleton",Tags:["Elite"],HandItems:[{id:"minecraft:iron_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§bPirate\\u0027s Hatchet\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"},{lvl:1s,id:"minecraft:fire_aspect"}],AttributeModifiers:[{UUIDMost:-2318795613139877656L,UUIDLeast:-6636823588444154371L,Amount:9.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie_pigman',
            'HandItems': ["'§bBlazing Soul'", "'§bBlazing Soul'"],
        },
        'mojangson': r'''{id:"minecraft:zombie_pigman",Anger:3297s,CustomName:"{\"text\":\"Fire Imp\"}",IsBaby:1b,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:5643800,Name:"{\"text\":\"§fInfernal Boots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:5643800,Name:"{\"text\":\"§fInfernal Pants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:5643800,Name:"{\"text\":\"§fInfernal Tunic\"}"}}},{}],HandItems:[{id:"minecraft:blaze_powder",Count:1b,tag:{display:{Name:"{\"text\":\"§bBlazing Soul\"}"},Enchantments:[{lvl:1s,id:"minecraft:fire_aspect"}],AttributeModifiers:[{UUIDMost:-2899840319788137997L,UUIDLeast:-6474403868551417057L,Amount:5.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:6643163485254798509L,UUIDLeast:-9135644038788542450L,Amount:-0.08d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{id:"minecraft:blaze_powder",Count:1b,tag:{display:{Name:"{\"text\":\"§bBlazing Soul\"}"},Enchantments:[{lvl:1s,id:"minecraft:fire_aspect"}],AttributeModifiers:[{UUIDMost:-2899840319788137997L,UUIDLeast:-6474403868551417057L,Amount:5.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:6643163485254798509L,UUIDLeast:-9135644038788542450L,Amount:-0.08d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Crystal Marksman'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"Crystal Marksman\"}",Health:30.0f,ArmorItems:[{},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:12172255,Name:"{\"text\":\"§fCloth Shirt\"}"},Damage:0,AttributeModifiers:[{UUIDMost:270399L,UUIDLeast:903793L,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"bc49eab7-0e56-4e0d-953d-c545868955ed",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvY2FiYjUxZjU5NDgxMTMyNTQ1YjUwZTQ3NWU3NjYyMzljNzljNjI0ZTliOTZhYjNhMGFjYjJhZjMwMWQ5NmM3OSJ9fX0="}]}},display:{Name:"{\"text\":\"§fcrystal_archer_helmet\"}"}}}],Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],id:"minecraft:skeleton",ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:17280000,Id:14b,Amplifier:0b}],HandItems:[{id:"minecraft:bow",Count:1b,tag:{Enchantments:[{lvl:4s,id:"minecraft:power"}],display:{Name:"{\"text\":\"§fCrystal Longbow\"}"},Damage:0}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Silver Chariot Knight'
        },
        'mojangson': r'''{Attributes:[{Base:40.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],id:"minecraft:skeleton",Health:40.0f,HandItems:[{id:"minecraft:iron_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§fBluesteel Longsword\"}"},Enchantments:[{lvl:1s,id:"minecraft:unbreaking"}],AttributeModifiers:[{UUIDMost:6705566393807683648L,UUIDLeast:-6789050455259027767L,Amount:6.5d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}],CustomName:"{\"text\":\"Silver Chariot Knight\"}",ArmorItems:[{id:"minecraft:iron_boots",Count:1b,tag:{display:{Name:"{\"text\":\"Silver chariot boots\"}"},Enchantments:[{lvl:3s,id:"minecraft:feather_falling"}],Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"Silver chariot legs\"}"},Enchantments:[{lvl:3s,id:"minecraft:blast_protection"}],Damage:0}},{id:"minecraft:iron_chestplate",Count:1b,tag:{display:{Name:"{\"text\":\"Silver chariot chest\"}"},Enchantments:[{lvl:2s,id:"minecraft:blast_protection"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"d21362d7-3ea6-4e89-843b-2ce986317414",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvZjkyNWU3NTI0OGU3MjllNjBlYzZmYjVkMzAxNmQ1MmQ3ODliMWQ2OTY3MTE0MjM1YjUxMDcxOGRhZGRkIn19fQ=="}]}},display:{Name:"{\"text\":\"Knight Helmet\"}"}}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'Animated Crystal'
        },
        'mojangson': r'''{id:"minecraft:zombie",CustomName:"{\"text\":\"Animated Crystal\"}",IsBaby:0b,Health:40.0f,ArmorItems:[{},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:12772533,Name:"{\"text\":\"§fCloth Shirt\"}"}}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"c46f476b-d3ef-45d5-975b-6bb2bcc7c9f6",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMjI4ZGQzZDliODFjYzlmOTZhNGMxMWZlMTNiMDc5NDk0ZjI3ZmM1YjkzM2M0ZjA4MzNmNjU2NDQ3MmVlMTYwOSJ9fX0="}]}},display:{Name:"{\"text\":\"§fcrystal_melee_helmet\"}"}}}],Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:17280000,Id:14b,Amplifier:0b}],Tags:["boss_charger"],HandItems:[{id:"minecraft:iron_shovel",Count:1b,tag:{Enchantments:[{lvl:1s,id:"minecraft:knockback"},{lvl:1s,id:"minecraft:fire_aspect"}],display:{Name:"{\"text\":\"§fCrystal Spear\"}"},Damage:0,AttributeModifiers:[{UUIDMost:4790688300322801738L,UUIDLeast:-5487926069810695271L,Amount:10.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },

    # V2 replacements, pink & miscellaneous standardization
    {
        'rules': {
            'id': 'minecraft:creeper',
            'CustomName': 'Landmine'
        },
        'mojangson': r'''{id:"minecraft:creeper",Fuse:20,Motion:[0.0d,1.0d,0.0d],CustomName:"{\"text\":\"Landmine\"}",ignited:1,Glowing:1b,CustomNameVisible:1}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'Nightmare Cultist'
        },
        'mojangson': r'''{id:"minecraft:zombie",Attributes:[{Base:0.2d,Name:"generic.movementSpeed"},{Base:2.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:35.0d,Name:"generic.followRange"},{Base:7.0d,Name:"generic.attackDamage"},{Base:0.08852623664344506d,Name:"zombie.spawnReinforcements"},{Base:0.5d,Name:"generic.knockbackResistance"},{Base:26.0d,Name:"generic.maxHealth"}],Invulnerable:0b,PersistenceRequired:0b,Health:30.0f,HandItems:[{id:"minecraft:ender_eye",tag:{Enchantments:[{lvl:1,id:"minecraft:knockback"},{lvl:1,id:"minecraft:fire_aspect"}]},Count:1b},{}],Passengers:[{shake:0b,xTile:0,Potion:{id:"minecraft:splash_potion",tag:{CustomPotionEffects:[{ShowParticles:0b,Duration:30,Id:25,Amplifier:30}]},Count:1b},inGround:0b,Invulnerable:0b,ownerName:"",zTile:0,yTile:0,id:"minecraft:potion"}],CustomName:"{\"text\":\"Nightmare Cultist\"}",CanBreakDoors:0b,ArmorItems:[{},{},{id:"minecraft:leather_chestplate",tag:{display:{color:3473469}},Count:1b},{id:"minecraft:player_head",tag:{SkullOwner:{Id:"c8354db9-fc75-4011-989a-013471e7aa84",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYWVjM2ZmNTYzMjkwYjEzZmYzYmNjMzY4OThhZjdlYWE5ODhiNmNjMThkYzI1NDE0N2Y1ODM3NGFmZTliMjFiOSJ9fX0="}]}}},Count:1b}],WorldActiveEffects:[{Ambient:0b,ShowParticles:0b,Duration:199999252,Id:14b,Amplifier:1b}],CustomNameVisible:1b}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': '§6Archmage'
        },
        'mojangson': r'''{id:"minecraft:zombie",CustomName:"{\"text\":\"§6Archmage\"}",IsBaby:0,Health:70.0f,ArmorItems:[{id:"minecraft:leather_boots",tag:{display:{color:2368548}},Count:1b},{id:"minecraft:golden_leggings",tag:{Enchantments:[{lvl:4,id:"minecraft:fire_protection"},{lvl:4,id:"minecraft:feather_falling"},{lvl:4,id:"minecraft:blast_protection"},{lvl:4,id:"minecraft:projectile_protection"}]},Count:1b},{id:"minecraft:leather_chestplate",tag:{display:{color:2368548}},Count:1b},{id:"minecraft:player_head",tag:{SkullOwner:{Id:"36216b27-bea8-4e2b-98ce-0e664427dd53",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvNmQzMjc0YjFkN2M5Yjg0ZTc4NTZkOWFhNzYzZWQ5ODY1ZWUyMzFlNjFjNDc5ODU5YjUxYmJjOGE4ZjVlNmNiIn19fQ=="}]}}},Count:1b}],Attributes:[{Base:70,Name:"generic.maxHealth"},{Base:0.28d,Name:"generic.movementSpeed"},{Base:0.0f,Name:"zombie.spawnReinforcements"},{Base:30,Name:"generic.followRange"}],Tags:["Elite"],ActiveEffects:[{Duration:199980,Id:13,Amplifier:0}],HandItems:[{id:"minecraft:stick",tag:{Enchantments:[{lvl:12,id:"minecraft:sharpness"},{lvl:2,id:"minecraft:knockback"},{lvl:3,id:"minecraft:fire_aspect"}]},Count:1b},{id:"minecraft:book",tag:{Enchantments:[{lvl:1,id:"minecraft:protection"}]},Count:1b}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie_pigman',
            'CustomName': '§6Mutated Abomination'
        },
        'mojangson': r'''{id:"minecraft:zombie_pigman",Anger:32767,CustomName:"{\"text\":\"§6Mutated Abomination\"}",IsBaby:0,Health:80.0f,ArmorItems:[{id:"minecraft:leather_boots",tag:{display:{color:3436544},Enchantments:[{lvl:4,id:"minecraft:blast_protection"}]},Count:1b},{},{id:"minecraft:leather_chestplate",tag:{display:{color:3436544},Enchantments:[{lvl:4,id:"minecraft:blast_protection"}]},Count:1b},{}],Attributes:[{Base:80,Name:"generic.maxHealth"},{Base:12,Name:"generic.attackDamage"},{Base:30,Name:"generic.followRange"}],Tags:["Elite"],ActiveEffects:[{Duration:199980,Id:8,Amplifier:0}],HandItems:[{id:"minecraft:stick",Count:1b},{id:"minecraft:stick",Count:1b}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Lost Soul'
        },
        'mojangson': r'''{id:"minecraft:skeleton",CustomName:"{\"text\":\"Lost Soul\"}",Health:1.0f,ArmorItems:[{},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:11579568}}},{id:"minecraft:skeleton_skull",Count:1b}],Attributes:[{Base:1,Name:"generic.maxHealth"}],DeathLootTable:"minecraft:empty",ActiveEffects:[{Duration:20000000,Id:14b,Amplifier:0b}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'CustomName': 'Serpensia Lord'
        },
        'mojangson': r'''{id:"minecraft:wither_skeleton",Passengers:[{Potion:{id:"minecraft:splash_potion",Count:1b,tag:{CustomPotionColor:28676,CustomPotionEffects:[{Duration:200,Id:18b,Amplifier:0b},{Duration:200,Id:19b,Amplifier:0b}],Potion:"minecraft:water"}},id:"minecraft:potion"}],CustomName:"{\"text\":\"Serpensia Lord\",\"color\":\"gold\"}",Health:32.0f,ArmorItems:[{},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:4812118}}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"0ae5e2a1-babb-4ec3-81da-e08efdc3ced2",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvZDQ4NjFkYTViYTM3NmM5ZDk3ZWQ4ODEzZmNiMjQ3M2IwZjVkYTEyNzc5NzI2ZDhiNWJkYzVlZmIyOTUyMTM4In19fQ=="}]}}}}],Attributes:[{Base:32,Name:"generic.maxHealth"},{Base:16,Name:"generic.followRange"},{Base:0.25d,Name:"generic.movementSpeed"}],Tags:["Elite"],ActiveEffects:[{ShowParticles:1b,Duration:20000000,Id:14b,Amplifier:0b}],HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"Venom\",\"color\":\"white\"}"},Enchantments:[{lvl:1,id:"minecraft:power"}]}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{Patterns:[{Pattern:"bt",Color:13},{Pattern:"tt",Color:13},{Pattern:"mr",Color:15}],Base:15}}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'CustomName': 'Quetzal Priest'
        },
        'mojangson': r'''{id:"minecraft:wither_skeleton",CustomName:"{\"text\":\"Quetzal Priest\",\"color\":\"gold\"}",Health:32.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:41215},Enchantments:[{lvl:2,id:"minecraft:feather_falling"},{lvl:1,id:"minecraft:projectile_protection"}]}},{id:"minecraft:golden_leggings",Count:1b,tag:{Enchantments:[{lvl:3,id:"minecraft:protection"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:41215},Enchantments:[{lvl:1,id:"minecraft:projectile_protection"}]}},{id:"minecraft:cyan_banner",Count:1b,tag:{BlockEntityTag:{Patterns:[{Pattern:"tt",Color:4},{Pattern:"mr",Color:4},{Pattern:"flo",Color:9}],Base:9}}}],Attributes:[{Base:32,Name:"generic.maxHealth"},{Base:16,Name:"generic.followRange"},{Base:0.25d,Name:"generic.movementSpeed"}],Tags:["Elite"],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{Enchantments:[{lvl:1,id:"minecraft:sharpness"},{lvl:1,id:"minecraft:knockback"}]}},{id:"minecraft:bone",Count:1b}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:vindicator',
            'CustomName': 'Harmonic Adherent'
        },
        'mojangson': r'''{id:"minecraft:vindicator",CustomName:"{\"text\":\"Harmonic Adherent\"}",Health:35.0f,Attributes:[{Base:35.0d,Name:"generic.maxHealth"}],Team:"mobs",HandItems:[{id:"minecraft:stone_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§fObsidian Blade\"}"},AttributeModifiers:[{Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:iron_golem',
            'CustomName': '§6Dissonant Sentinel'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"§6Dissonant Sentinel\"}",Health:120.0f,Attributes:[{Base:120.0d,Name:"generic.maxHealth"}],Team:"mobs",id:"minecraft:iron_golem",Tags:["boss_targetplayer","Elite","boss_blockbreak","boss_projimmune","boss_charger"]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'HandItems': ["'§fViridian Hunter'", None],
        },
        'mojangson': r'''{id:"minecraft:skeleton",Attributes:[{Base:30.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,PersistenceRequired:0b,Team:"mobs",Health:30.0f,HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§fViridian Hunter\"}"},Enchantments:[{lvl:4s,id:"minecraft:power"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'CustomName': 'Harmonic Keeper'
        },
        'mojangson': r'''{id:"minecraft:wither_skeleton",CustomName:"{\"text\":\"Harmonic Keeper\"}",Health:45.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:7567221}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:7567221}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:7567221}}},{id:"minecraft:chiseled_stone_bricks",Count:1b}],Attributes:[{Base:45.0d,Name:"generic.maxHealth"}],Team:"mobs",HandItems:[{id:"minecraft:iron_axe",Count:1b,tag:{HideFlags:1,display:{Name:"{\"text\":\"§2§lWrath of the Mountain\"}"}}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:iron_golem',
            'CustomName': '§6Harmonic Sentinel'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"§6Harmonic Sentinel\"}",Health:120.0f,Attributes:[{Base:120.0d,Name:"generic.maxHealth"}],Team:"mobs",id:"minecraft:iron_golem",Tags:["boss_targetplayer","Elite","boss_blockbreak","boss_blockbreak","boss_stomp","boss_projimmune"]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': '§6Master Scavenger'
        },
        'mojangson': r'''{id:"minecraft:skeleton",HurtByTimestamp:0,Attributes:[{Base:90.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,FallDistance:0.0f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:1b,Spigot.ticksLived:221,Tags:["Elite","boss_charger"],Motion:[0.0d,-0.0784000015258789d,0.0d],Leashed:0b,Health:90.0f,Bukkit.updateLevel:2,LeftHanded:0b,Paper.AAAB:[-704.6249754083491d,87.0d,-1615.658277927043d,-704.0249753845072d,88.99000000953674d,-1615.058277903201d],Air:300s,OnGround:1b,Dimension:0,Rotation:[11.738251f,3.9602158f],HandItems:[{id:"minecraft:stone_hoe",Count:1b,tag:{display:{Name:"{\"text\":\"§bScavenger\\u0027s Scythe\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:3528639911520192138L,UUIDLeast:-5188345177487516701L,Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-7218190296710885949L,UUIDLeast:-6433239892790551973L,Amount:0.5d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],CustomName:"{\"text\":\"§6Master Scavenger\"}",Pos:[-704.3249753964282d,87.0d,-1615.358277915122d],Fire:-1s,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"§bScavengerBoots\"}"},Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:5251875,Name:"{\"text\":\"§bScavengerPants\"}"},Damage:0}},{id:"minecraft:chainmail_chestplate",Count:1b,tag:{Enchantments:[{lvl:4s,id:"minecraft:blast_protection"},{lvl:4s,id:"minecraft:projectile_protection"}],display:{Name:"{\"text\":\"§bScavengerChest\"}"},Damage:0}},{}],CanPickUpLoot:0b,DeathLootTable:"epic:r2/mobs/master_scavenger",HurtTime:0s,Paper.FromMobSpawner:1b,WorldUUIDLeast:-7560693509725274339L,Paper.Origin:[-703.3779677421893d,88.0d,-1619.9158697405255d]}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'CustomName': '§6Pirate Captain'
        },
        'mojangson': r'''{id:"minecraft:wither_skeleton",HurtByTimestamp:0,Attributes:[{Base:90.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,FallDistance:0.0f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:0b,Spigot.ticksLived:199,Tags:["Elite"],Motion:[0.0d,-0.0784000015258789d,0.0d],Leashed:0b,Health:90.0f,Bukkit.updateLevel:2,LeftHanded:0b,Paper.AAAB:[-710.7728633686679d,87.0d,-1620.845200422513d,-710.0728633805888d,89.40000009536743d,-1620.145200434434d],Air:300s,OnGround:1b,Dimension:0,Rotation:[113.55947f,0.0f],HandItems:[{id:"minecraft:iron_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§bPirate\\u0027s Hatchet\"}"},Enchantments:[{lvl:1s,id:"minecraft:fire_aspect"},{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:-2318795613139877656L,UUIDLeast:-6636823588444154371L,Amount:9.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],CustomName:"{\"text\":\"§6Pirate Captain\"}",Pos:[-710.4228633746284d,87.0d,-1620.4952004284735d],Fire:-1s,ArmorItems:[{id:"minecraft:golden_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§bPirateCaptainBoots\"}"},Damage:0}},{id:"minecraft:chainmail_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§bPirateCaptainPants\"}"},Damage:0}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:6192150,Name:"{\"text\":\"§bPirateCaptainChest\"}"},Damage:0}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"8c365419-8c9b-4886-b796-21261e38a473",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvN2FlODIzZTFhYzc0YmNlMGZkYzM2MWYyZWM1NDk3ZDg4NDU4ZmZlZTRhN2VjMzcwM2JlMzY5Zjg2ZTI4Nzc4YiJ9fX0="}]}},display:{Name:"{\"text\":\"Pirate\"}"}}}],CanPickUpLoot:0b,DeathLootTable:"epic:r2/mobs/pirate_captain",HurtTime:0s,Paper.FromMobSpawner:1b,WorldUUIDLeast:-7560693509725274339L,Paper.Origin:[-710.4228633746284d,88.0d,-1620.4952004284735d]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': '§6Feyrune Marksman'
        },
        'mojangson': r'''{id:"minecraft:skeleton",HurtByTimestamp:0,Attributes:[{Base:70.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,FallDistance:0.0f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:0b,Spigot.ticksLived:16,Tags:["Elite"],Motion:[0.0d,-0.0784000015258789d,0.0d],Leashed:0b,Health:70.0f,Bukkit.updateLevel:2,LeftHanded:0b,Paper.AAAB:[-717.7613117082317d,87.0d,-1618.18891282507d,-717.1613116843898d,88.99000000953674d,-1617.5889128012282d],Air:52s,OnGround:1b,Dimension:0,Rotation:[144.45146f,0.0f],HandItems:[{id:"minecraft:bow",Count:1b,tag:{Enchantments:[{lvl:4s,id:"minecraft:power"}],display:{Name:"{\"text\":\"§fFeyrune Marksman\\u0027s Bow\"}"},Damage:0}},{id:"minecraft:jungle_sapling",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyruneMarksmanSapling\"}"}}}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],CustomName:"{\"text\":\"§6Feyrune Marksman\"}",Pos:[-717.4613116963108d,87.0d,-1617.888912813149d],Fire:-1s,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:5465909,Name:"{\"text\":\"§fFeyruneMarksmanBoots\"}"},Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:7315738,Name:"{\"text\":\"§fFeyruneMarksmanPants\"}"},Damage:0}},{id:"minecraft:chainmail_chestplate",Count:1b,tag:{Enchantments:[{lvl:2s,id:"minecraft:projectile_protection"},{lvl:1s,id:"minecraft:protection"}],display:{Name:"{\"text\":\"§fFeyruneMarksmanChest\"}"},Damage:0}},{id:"minecraft:jungle_leaves",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyruneMarksmanHead\"}"}}}],CanPickUpLoot:0b,DeathLootTable:"epic:r2/mobs/feyrune_marksman",HurtTime:0s,Paper.FromMobSpawner:1b,WorldUUIDLeast:-7560693509725274339L,Paper.Origin:[-717.4613116963108d,87.0d,-1617.888912813149d]}''',
    },
    {
        'rules': {
            'id': 'minecraft:enderman',
            'CustomName': 'Spectral Enderman'
        },
        'mojangson': r'''{id:"minecraft:enderman",CustomName:"{\"text\":\"Spectral Enderman\"}",Health:40.0f,Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:1728000000,Id:24b,Amplifier:0b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:1728000000,Id:14b,Amplifier:0b}],Tags:["boss_targetplayer"],HandItems:[{id:"minecraft:stone_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§bSpectral Slicer\"}"},Enchantments:[{lvl:1s,id:"minecraft:fire_aspect"}],Damage:0,AttributeModifiers:[{UUIDMost:6758313694813700880L,UUIDLeast:-7432768362308561981L,Amount:6.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'Nature Elemental'
        },
        'mojangson': r'''{id:"minecraft:zombie",CustomName:"{\"text\":\"Nature Elemental\"}",Health:40.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:14256852,Name:"{\"text\":\"§bSpringBoots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:6192150,Name:"{\"text\":\"§bSpringPants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:14256852,Name:"{\"text\":\"§bSpringChest\"}"}}},{id:"minecraft:leather_helmet",Count:1b,tag:{display:{color:16383998,Name:"{\"text\":\"§bSpringHelm\"}"}}}],Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],HandItems:[{id:"minecraft:golden_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§bAxe of Spring\"}"},AttributeModifiers:[{UUIDMost:2964310904583110856L,UUIDLeast:-8850808570329176908L,Amount:6.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Frigid Assassin'
        },
        'mojangson': r'''{id:"minecraft:skeleton",CustomName:"{\"text\":\"Frigid Assassin\"}",Health:25.0f,ArmorItems:[{id:"minecraft:chainmail_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§bFrigidBoots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:10531071,Name:"{\"text\":\"§fSky Mage Robe\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:1073407,Name:"{\"text\":\"§aNereid Tunic\"}"}}},{id:"minecraft:chainmail_helmet",Count:1b,tag:{display:{Name:"{\"text\":\"§bFrigidHelm\"}"}}}],Attributes:[{Base:25.0d,Name:"generic.maxHealth"}],Tags:["boss_tpbehind"],HandItems:[{id:"minecraft:diamond_hoe",Count:1b,tag:{display:{Name:"{\"text\":\"§bFrigid Scythe\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:-1377635467568722567L,UUIDLeast:-6236399593913355141L,Amount:9.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'Feyrune Swarmer'
        },
        'mojangson': r'''{id:"minecraft:zombie",CustomName:"{\"text\":\"Feyrune Swarmer\"}",IsBaby:1b,Health:10.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"§fFeyruneSwarmerV1Boots\"}"},Damage:0}},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{Enchantments:[{lvl:1s,id:"minecraft:fire_protection"}],display:{color:8439583,Name:"{\"text\":\"§fFeyruneSwarmerV1Chest\"}"},Damage:0}},{id:"minecraft:dark_oak_leaves",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyruneSwarmerV1Head\"}"}}}],Attributes:[{Base:10.0d,Name:"generic.maxHealth"}],HandItems:[{id:"minecraft:stick",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyrune Swarmer Staff\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:1608078254659488666L,UUIDLeast:-6932078456909392358L,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{id:"minecraft:azure_bluet",Count:1b,tag:{display:{Name:"{\"text\":\"§fFeyruneSwarmerV1Flower\"}"}}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'CustomName': '§6Silver Dreadnaught'
        },
        'mojangson': r'''{id:"minecraft:wither_skeleton",HurtByTimestamp:0,Attributes:[{Base:90.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,FallDistance:0.0f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:0b,Spigot.ticksLived:334,Tags:["boss_charger","Elite"],Motion:[0.0d,-0.0784000015258789d,0.0d],Leashed:0b,Health:90.0f,Bukkit.updateLevel:2,LeftHanded:0b,Air:300s,OnGround:1b,Dimension:0,Rotation:[0.0f,0.0f],HandItems:[{id:"minecraft:stone_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§b§lSilver Knight\\u0027s Hammer\"}"},Enchantments:[{lvl:2s,id:"minecraft:smite"},{lvl:1s,id:"minecraft:sharpness"},{lvl:1s,id:"minecraft:mending"}],Damage:0}},{}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],CustomName:"{\"text\":\"§6Silver Dreadnaught\"}",Fire:-1s,ArmorItems:[{id:"minecraft:iron_boots",Count:1b,tag:{display:{Name:"{\"text\":\"Silver chariot boots\"}"},Enchantments:[{lvl:7s,id:"minecraft:feather_falling"}],Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"Silver chariot legs\"}"},Enchantments:[{lvl:3s,id:"minecraft:blast_protection"}],Damage:0}},{id:"minecraft:iron_chestplate",Count:1b,tag:{display:{Name:"{\"text\":\"Silver chariot chest\"}"},Enchantments:[{lvl:2s,id:"minecraft:blast_protection"}],Damage:0}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"4c1fec3d-13ce-4b28-aaa5-f6708ae47f99",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvNWY4YWViY2Y0YjcyZDczZDFkNWRjM2NjYmRlZDUzMmNlNGVjM2Q1ODVjZTcyMTU0YzQyMjI5NjM4YjQ1YzRkZSJ9fX0="}]}},display:{Name:"{\"text\":\"Knight Helmet\"}"}}}],CanPickUpLoot:0b,HurtTime:0s,WorldUUIDLeast:-7560693509725274339L}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'Bone Cult Assassin'
        },
        'mojangson': r'''{id:"minecraft:zombie",CustomName:"{\"text\":\"Bone Cult Assassin\"}",Health:25.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:13684991,Name:"{\"text\":\"§b§lZephyric Sandals\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:16383998,Name:"{\"text\":\"§bBonePants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:10329495,Name:"{\"text\":\"§bBonesChest\"}"}}},{}],Attributes:[{Base:25.0d,Name:"generic.maxHealth"}],Tags:["boss_tpbehind"],HandItems:[{id:"minecraft:stone_hoe",Count:1b,tag:{display:{Name:"{\"text\":\"§bBone Scythe\"}"},AttributeModifiers:[{UUIDMost:-1732030607911925132L,UUIDLeast:-8862348590511379083L,Amount:9.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:1973469405162917330L,UUIDLeast:-8482276659341838830L,Amount:0.2d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie_pigman',
            'CustomName': '§6Charred Foreman'
        },
        'mojangson': r'''{id:"minecraft:zombie_pigman",CustomName:"{\"text\":\"§6Charred Foreman\"}",Health:90.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:5643800,Name:"{\"text\":\"§fInfernal Boots\"}"}}},{id:"minecraft:golden_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§bBasanitePants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:5643800,Name:"{\"text\":\"§fInfernal Tunic\"}"}}},{}],Attributes:[{Base:90.0d,Name:"generic.maxHealth"}],Tags:["Elite","boss_flamenova","boss_fireball"],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§bBasanite Spellblade\"}"},AttributeModifiers:[{UUIDMost:-5443655948128206615L,UUIDLeast:-8115751551700471969L,Amount:10.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{id:"minecraft:magma_cream",Count:1b,tag:{display:{Name:"{\"text\":\"§bBasanite Magma\"}"}}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Unstable Archer'
        },
        'mojangson': r'''{id:"minecraft:skeleton",CustomName:"{\"text\":\"Unstable Archer\"}",Health:30.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:16195840,Name:"{\"text\":\"§fInfernal Boots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:10506272,Name:"{\"text\":\"§aHardened Leather Pants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:10506272,Name:"{\"text\":\"§aHardened Leather Tunic\"}"}}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"9c705b74-b966-40a8-852b-9eb71288e37d",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvNWVkYjZmZDc0OWU5NWIyZGQwZDI0OTVhODU2MTdiNWFlZjNiNDc2NDE3Yzg1OWJmMzRjNDU0NzdhZTY4MSJ9fX0="}]}},display:{Name:"{\"text\":\"§finfested_villager_head\"}"}}}],Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§fCorrupted Steelsiege\"}"},Enchantments:[{lvl:4s,id:"minecraft:power"},{lvl:1s,id:"minecraft:flame"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie_pigman',
            'CustomName': 'Fire Imp'
        },
        'mojangson': r'''{id:"minecraft:zombie_pigman",Anger:3297s,CustomName:"{\"text\":\"Fire Imp\"}",IsBaby:1b,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:5643800,Name:"{\"text\":\"§fInfernal Boots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:5643800,Name:"{\"text\":\"§fInfernal Pants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:5643800,Name:"{\"text\":\"§fInfernal Tunic\"}"}}},{}],HandItems:[{id:"minecraft:blaze_powder",Count:1b,tag:{display:{Name:"{\"text\":\"§bBlazing Soul\"}"},Enchantments:[{lvl:1s,id:"minecraft:fire_aspect"}],AttributeModifiers:[{UUIDMost:-2899840319788137997L,UUIDLeast:-6474403868551417057L,Amount:5.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:6643163485254798509L,UUIDLeast:-9135644038788542450L,Amount:-0.08d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{id:"minecraft:blaze_powder",Count:1b,tag:{display:{Name:"{\"text\":\"§bBlazing Soul\"}"},Enchantments:[{lvl:1s,id:"minecraft:fire_aspect"}],AttributeModifiers:[{UUIDMost:-2899840319788137997L,UUIDLeast:-6474403868551417057L,Amount:5.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:6643163485254798509L,UUIDLeast:-9135644038788542450L,Amount:-0.08d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:ghast',
            'CustomName': 'Shrieking Apparition'
        },
        'mojangson': r'''{id:"minecraft:ghast",CustomName:"{\"text\":\"Shrieking Apparition\"}",Health:26.0f,Attributes:[{Base:26.0d,Name:"generic.maxHealth"}],Team:"mobs",ExplosionPower:3}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie_villager',
            'CustomName': 'Cursed Miner'
        },
        'mojangson': r'''{id:"minecraft:zombie_villager",Profession:3,CustomName:"{\"text\":\"Cursed Miner\"}",Health:40.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:10065039,Name:"{\"text\":\"§fBurnt Boots\"}"},Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:10065039,Name:"{\"text\":\"§fBurnt Leggings\"}"},Damage:0}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:10065039,Name:"{\"text\":\"§fBurnt Cloak\"}"},Damage:0}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"f49cfedb-b943-444a-a4ea-9e67c3e2367b",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvZGU1OWYzYjE1NTRkOWMwMmRjOGEyMTllMjU4ZDEzNjNjODhmNzI3OGM0NTI2MjYzODA0ZWFjNDZjNWQ1NyJ9fX0="}]}},display:{Name:"{\"text\":\"Miner\"}"}}}],Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],HandItems:[{id:"minecraft:golden_pickaxe",Count:1b,tag:{display:{Name:"{\"text\":\"§bCursed Pickaxe\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"},{lvl:13s,id:"minecraft:sharpness"}],Damage:0}},{id:"minecraft:redstone",Count:1b,tag:{AttributeModifiers:[{UUIDMost:3187929739390766823L,UUIDLeast:-7012500192929918795L,Amount:0.2d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:ghast',
            'CustomName': 'Manipulated Ghast'
        },
        'mojangson': r'''{id:"minecraft:ghast",CustomName:"{\"text\":\"Manipulated Ghast\"}",Passengers:[{CustomName:"{\"text\":\"Airborne Scourge\"}",Health:26.0f,ArmorItems:[{id:"minecraft:string",Count:1b,tag:{display:{Name:"{\"text\":\"Generic phantom 1\"}"},AttributeModifiers:[{UUIDMost:1784323748451274166L,UUIDLeast:-8041570111476416582L,Amount:0.1d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-6371339278188132964L,UUIDLeast:-7998758353134359446L,Amount:6.0d,Slot:"feet",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{},{},{}],Attributes:[{Base:26.0d,Name:"generic.maxHealth"}],id:"minecraft:phantom",Tags:["custom"]}],Health:22.0f,Attributes:[{Base:22.0d,Name:"generic.maxHealth"}],ExplosionPower:3,HandItems:[{id:"minecraft:string",Count:1b,tag:{display:{Name:"{\"text\":\"Generic blaze1\"}"},AttributeModifiers:[{UUIDMost:-5698604123419097876L,UUIDLeast:-9150926501413543855L,Amount:12.0d,Slot:"mainhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:spider',
            'CustomName': 'Flamekissed Arachno'
        },
        'mojangson': r'''{id:"minecraft:spider",HurtByTimestamp:0,Attributes:[{Base:32.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.28d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,FallDistance:0.0784f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:0b,Spigot.ticksLived:185,Motion:[0.05609046718294944d,-0.1552320045166016d,0.018696940428116298d],Leashed:0b,Health:32.0f,Bukkit.updateLevel:2,LeftHanded:0b,Air:300s,OnGround:0b,Dimension:0,HandItems:[{id:"minecraft:iron_sword",Count:1b,tag:{ench:[{lvl:1,id:19},{lvl:1,id:20}]},Damage:0s},{}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],CustomName:"{\"text\":\"Flamekissed Arachno\"}",Fire:9814s,ArmorItems:[{},{},{},{}],CanPickUpLoot:0b,HurtTime:0s,WorldUUIDLeast:-7560693509725274339L,ActiveEffects:[{Ambient:0b,ShowParticles:1b,Duration:22035,Id:12b,Amplifier:0b},{Ambient:0b,ShowParticles:0b,Duration:22035,Id:8b,Amplifier:1b},{Ambient:0b,ShowParticles:0b,Duration:22035,Id:11b,Amplifier:0b}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': '§6Stoneborn Immortal'
        },
        'mojangson': r'''{id:"minecraft:zombie",ArmorDropChances:[-327.67f,-327.67f,-327.67f,-327.67f],CustomName:"{\"text\":\"§6Stoneborn Immortal\"}",IsBaby:0,Health:30.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:10395294},Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:6191160},Damage:0}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:10395294},Damage:0}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"86d08d4a-3cc6-46fa-61cf-c54d58373c70",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYzk4ZDNjMzFmOWJjNTc1Mzk4MzdkMTc2NTdiOWJhZTczNWE4OTZmMWEwNzc4MTZlZDk1NzU3YzE1NDJhYTMifX19"}]}}}}],Attributes:[{Base:30,Name:"generic.maxHealth"},{Base:0.21d,Name:"generic.movementSpeed"},{Base:0.0f,Name:"zombie.spawnReinforcements"},{Base:60,Name:"generic.followRange"}],HandDropChances:[-327.67f,-327.67f],Tags:["Elite"],ActiveEffects:[{Duration:1999980,Id:5,Amplifier:0},{Duration:1999980,Id:11,Amplifier:4}],HandItems:[{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{id:"minecraft:banner",Patterns:[{Pattern:"tt",Color:7},{Pattern:"cs",Color:7},{Pattern:"flo",Color:7},{Pattern:"gru",Color:7}],Base:8},Enchantments:[{lvl:10,id:"minecraft:sharpness"}],Damage:0}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{id:"minecraft:banner",Patterns:[{Pattern:"tt",Color:7},{Pattern:"cs",Color:7},{Pattern:"flo",Color:7},{Pattern:"gru",Color:7}],Base:8},Enchantments:[{lvl:10,id:"minecraft:sharpness"}],Damage:0}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:vex',
            'CustomName': '§6Shieldbreaker Sprite'
        },
        'mojangson': r'''{id:"minecraft:vex",CustomName:"{\"text\":\"Shieldbreaker Sprite\",\"color\":\"gold\"}",Attributes:[{Base:50,Name:"generic.followRange"}],Tags:["Elite"],HandItems:[{id:"minecraft:golden_axe",Count:1b,tag:{Enchantments:[{lvl:2,id:"minecraft:knockback"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:vex',
            'CustomName': 'Shieldbreaker Sprite'
        },
        'mojangson': r'''{id:"minecraft:vex",CustomName:"{\"text\":\"Shieldbreaker Sprite\",\"color\":\"gold\"}",Attributes:[{Base:50,Name:"generic.followRange"}],Tags:["Elite"],HandItems:[{id:"minecraft:golden_axe",Count:1b,tag:{Enchantments:[{lvl:2,id:"minecraft:knockback"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:creeper',
            'CustomName': 'Pineapple Creeper'
        },
        'mojangson': r'''{id:"minecraft:creeper",Passengers:[{Particle:"happy_villager",Radius:0.5d,Duration:25,id:"minecraft:area_effect_cloud",Age:0,Tags:["effect_cloud"]},{Small:1,ArmorItems:[{},{},{},{id:"minecraft:player_head",tag:{SkullOwner:{Id:"f0a7a8e2-1188-b578-1ea7-1ec6951094d0",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvOTdkN2M1NzNlZDU2MDc3MjU1ZDJhOWY1ODNmMTIxNjg0N2E4ZDQ1NTM3NzVjOGY1ODkzM2M0NWJmODZhOWVjIn19fQ=="}]}}},Count:1b}],Pose:{RightArm:[0.0f,0.0f,17.0f],Head:[180.0f,0.0f,0.0f],LeftArm:[0.0f,0.0f,343.0f]},NoBasePlate:1,id:"minecraft:armor_stand",Marker:1b,Invisible:1,ShowArms:1,Tags:["rider","pineapple"],HandItems:[{id:"minecraft:jungle_leaves",Count:1b},{id:"minecraft:jungle_leaves",Count:1b}]}],CustomName:"{\"text\":\"Pineapple Creeper\"}",Health:20.0f,Attributes:[{Base:20.0d,Name:"generic.maxHealth"},{Base:0.3d,Name:"generic.movementSpeed"}],ExplosionRadius:4b,CustomNameVisible:0}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'CustomName': '§6Golem of Decay'
        },
        'mojangson': r'''{id:"minecraft:wither_skeleton",CustomName:"{\"text\":\"§6Golem of Decay\"}",Health:100.0f,ArmorItems:[{id:"minecraft:golden_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§bFallBoots\"}"},Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:16425045,Name:"{\"text\":\"§bFallPants\"}"},Damage:0}},{id:"minecraft:chainmail_chestplate",Count:1b,tag:{display:{Name:"{\"text\":\"§bDecayChest\"}"},Damage:0}},{}],Attributes:[{Base:100.0d,Name:"generic.maxHealth"}],Tags:["aura_hunger","Elite"],HandItems:[{id:"minecraft:golden_shovel",Count:1b,tag:{display:{Name:"{\"text\":\"§bLeaf Digger\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:-321792617466279460L,UUIDLeast:-5913668740073679520L,Amount:12.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{id:"minecraft:fern",Count:1b}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': '§6Frozen Guard'
        },
        'mojangson': r'''{id:"minecraft:skeleton",CustomName:"{\"text\":\"§6Frozen Guard\"}",Health:45.0f,ArmorItems:[{id:"minecraft:chainmail_boots",tag:{display:{Name:"{\"text\":\"FrozenCitizenBoots_E\"}"}},Count:1b},{id:"minecraft:leather_leggings",tag:{display:{color:7702406,Name:"{\"text\":\"FrozenCitizenPants_E\"}"}},Count:1b},{id:"minecraft:leather_chestplate",tag:{display:{color:7702406,Name:"{\"text\":\"FrozenCitizenChest_E\"}"}},Count:1b},{id:"minecraft:player_head",tag:{SkullOwner:{Id:"3776820c-7098-42f8-864a-a8997c0f5b47",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvNDBmNzU4NWZlZjBkZWUwNDFmMzNhNjc5MTFkNzlmOTVhZDkwYzdkYjFmMmVjNTAxNTZmMzUzY2Y5NDFkYWY3MiJ9fX0="}]}}},Count:1b}],Fire:-1s,Attributes:[{Base:45.0d,Name:"generic.maxHealth"},{Base:4.0d,Name:"generic.armor"}],Invulnerable:0b,PersistenceRequired:0b,LeftHanded:0b,AbsorptionAmount:0.0f,Tags:["Elite","aura_slowness"],HandItems:[{id:"minecraft:stone_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§fIce Shiv\"}"},Enchantments:[{lvl:8s,id:"minecraft:sharpness"}]}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{id:"minecraft:banner",Base:7},Damage:0}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'CustomName': '§6Duke of Frost'
        },
        'mojangson': r'''{id:"minecraft:wither_skeleton",CustomName:"{\"text\":\"§6Duke of Frost\"}",Health:75.0f,ArmorItems:[{id:"minecraft:iron_boots",Count:1b,tag:{display:{Name:"{\"text\":\"FrostKnightBoots\"}"},Enchantments:[{lvl:2s,id:"minecraft:feather_falling"},{lvl:2s,id:"minecraft:fire_protection"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:11198694,Name:"{\"text\":\"§fGlacial Trousers\"}"},Enchantments:[{lvl:2s,id:"minecraft:unbreaking"},{lvl:1s,id:"minecraft:projectile_protection"},{lvl:2s,id:"minecraft:protection"}],AttributeModifiers:[{UUIDMost:-6220321283308304534L,UUIDLeast:-7046124410738595557L,Amount:2.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-5590101535826884820L,UUIDLeast:-5975264218032950413L,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:11198694,Name:"{\"text\":\"§rGlacial Chestplate\"}"},Enchantments:[{lvl:2s,id:"minecraft:unbreaking"},{lvl:1s,id:"minecraft:projectile_protection"},{lvl:2s,id:"minecraft:protection"}],AttributeModifiers:[{UUIDMost:2064313145065688627L,UUIDLeast:-6431352151458895290L,Amount:2.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_helmet",Count:1b,tag:{display:{color:65493,Name:"{\"text\":\"§b§lKismet\\u0027s Blessing\"}"},Enchantments:[{lvl:2s,id:"minecraft:projectile_protection"}]}}],Attributes:[{Base:75.0d,Name:"generic.maxHealth"}],ActiveEffects:[{Ambient:1b,ShowParticles:1b,Duration:72000,Id:10b,Amplifier:0b},{Ambient:1b,ShowParticles:1b,Duration:72000,Id:2b,Amplifier:7b},{Ambient:1b,ShowParticles:1b,Duration:72000,Id:1b,Amplifier:5b}],HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§fBow of the Great Blizzard\"}"},Enchantments:[{lvl:5s,id:"minecraft:power"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'CustomName': '§6Smuggler Leader'
        },
        'mojangson': r'''{id:"minecraft:wither_skeleton",CustomName:"{\"text\":\"§6Smuggler Leader\"}",Health:90.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:6305568,Name:"{\"text\":\"§aHardened Leather Boots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:6305568,Name:"{\"text\":\"§aHardened Leather Pants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:6305568,Name:"{\"text\":\"§aHardened Leather Tunic\"}"}}},{}],Attributes:[{Base:90.0d,Name:"generic.maxHealth"}],Tags:["Elite","charger"],HandItems:[{id:"minecraft:stone_hoe",Count:1b,tag:{display:{Name:"{\"text\":\"§bRuffian\\u0027s Scythe\"}"},Enchantments:[{lvl:5s,id:"minecraft:sharpness"}],AttributeModifiers:[{UUIDMost:-527754898800293601L,UUIDLeast:-6419796000351238753L,Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:6058306957502661420L,UUIDLeast:-8008453641933767453L,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'Smuggler Assassin'
        },
        'mojangson': r'''{id:"minecraft:zombie",CustomName:"{\"text\":\"Smuggler Assassin\"}",Health:25.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:6305568,Name:"{\"text\":\"§aHardened Leather Boots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:6305568,Name:"{\"text\":\"§aHardened Leather Pants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:6305568,Name:"{\"text\":\"§aHardened Leather Tunic\"}"}}},{}],Attributes:[{Base:25.0d,Name:"generic.maxHealth"}],Tags:["tpbehind"],HandItems:[{id:"minecraft:iron_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§bSmuggler\\u0027s Sword\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"},{lvl:3s,id:"minecraft:sharpness"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': '§6Winery Defender'
        },
        'mojangson': r'''{id:"minecraft:zombie",CustomName:"{\"text\":\"§6Winery Defender\"}",IsBaby:1b,Health:60.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:7393328,Name:"{\"text\":\"§fHobnailed Boots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:7393328,Name:"{\"text\":\"§fHobnailed Leggings\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:8439583,Name:"{\"text\":\"§a§lVinebound Tunic\"}"}}},{}],Attributes:[{Base:60.0d,Name:"generic.maxHealth"}],Tags:["Elite"],HandItems:[{id:"minecraft:stick",Count:1b,tag:{display:{Name:"{\"text\":\"§bStudent\\u0027s Wand\"}"},Enchantments:[{lvl:2s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:2727385767052724336L,UUIDLeast:-6639409340661554772L,Amount:10.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{id:"minecraft:totem_of_undying",Count:1b,tag:{display:{Name:"{\"text\":\"§bStalwart Idol\"}"}}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'HandItems': ["'§fEnraged Captain's Axe'", "'§bHawk's Talon'"],
        },
        'mojangson': r'''{id:"minecraft:skeleton",CustomName:"{\"text\":\"§6Lighthouse Defender\"}",Health:75.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:4521728,Name:"{\"text\":\"§2§lBoots of Vitality\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:10506272,Name:"{\"text\":\"§aHardened Leather Pants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:10506272,Name:"{\"text\":\"§aHardened Leather Tunic\"}"}}},{}],Attributes:[{Base:75.0d,Name:"generic.maxHealth"}],Tags:["Elite","boss_weaponswitch","boss_charger"],HandItems:[{id:"minecraft:iron_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§fEnraged Captain\\u0027s Axe\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"},{lvl:1s,id:"minecraft:sharpness"}],Damage:0}},{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§bHawk\\u0027s Talon\"}"},Enchantments:[{lvl:3s,id:"minecraft:power"}],Damage:0}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:husk',
            'CustomName': '§6Snow Raider General'
        },
        'mojangson': r'''{id:"minecraft:husk",HurtByTimestamp:0,Attributes:[{Base:90.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.23000000417232513d,Name:"generic.movementSpeed"},{Base:2.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:35.0d,Name:"generic.followRange"},{Base:3.0d,Name:"generic.attackDamage"},{Base:0.003505449877311974d,Name:"zombie.spawnReinforcements"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,InWaterTime:-1,FallDistance:0.0f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:0b,Spigot.ticksLived:114,Tags:["Elite"],Motion:[0.0d,-0.0784000015258789d,0.0d],Leashed:0b,Health:90.0f,Bukkit.updateLevel:2,LeftHanded:0b,Air:300s,OnGround:1b,Dimension:0,Rotation:[0.0f,0.0f],HandItems:[{id:"minecraft:stone_sword",Count:1b,tag:{HideFlags:1,display:{Name:"{\"text\":\"§aBrutal Longsword\"}"},Enchantments:[{lvl:13s,id:"minecraft:sharpness"}]}},{}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],CustomName:"{\"text\":\"§6Snow Raider General\"}",CanBreakDoors:0b,Fire:-1s,ArmorItems:[{id:"minecraft:iron_boots",Count:1b,tag:{display:{Name:"{\"text\":\"SnowBanditBoots_E\"}"},Damage:0}},{id:"minecraft:iron_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"SnowBanditGreaves\"}"},Damage:0}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:5271712,Name:"{\"text\":\"SnowBanditChest_E\"}"},Enchantments:[{lvl:1s,id:"minecraft:protection"},{lvl:2s,id:"minecraft:projectile_protection"}],Damage:0}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"8836c064-ecaa-413b-99af-dc6ca1bde8e1",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYWE4Y2ExMWQ4YjZmYmZmZjYwNDQyMmViOTg4ZGRiZjkyZmZlYTEwMTA5ZTYyYmNkNjM1NzA3ZWIzN2E4NCJ9fX0="}]}},display:{Name:"{\"text\":\"Man\"}"},AttributeModifiers:[{UUIDMost:-2568949878646291902L,UUIDLeast:-7939972146680390007L,Amount:0.15d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}}],CanPickUpLoot:0b,DeathLootTable:"minecraft:empty",HurtTime:0s,WorldUUIDLeast:-7560693509725274339L,DrownedConversionTime:-1}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'CustomName': '§6Runebound Guardian'
        },
        'mojangson': r'''{id:"minecraft:wither_skeleton",CustomName:"{\"text\":\"§6Runebound Guardian\"}",Health:90.0f,ArmorItems:[{id:"minecraft:chainmail_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§bRuneboundBoots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:16369622,Name:"{\"text\":\"§bMarblePants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:16369622,Name:"{\"text\":\"§bMarbleChest\"}"}}},{id:"minecraft:chiseled_quartz_block",Count:1b}],Attributes:[{Base:90.0d,Name:"generic.maxHealth"}],Tags:["Elite","boss_flamenova"],HandItems:[{id:"minecraft:iron_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§bBlade of Marble\"}"},Enchantments:[{lvl:2s,id:"minecraft:fire_aspect"},{lvl:1s,id:"minecraft:knockback"}],Damage:0,AttributeModifiers:[{UUIDMost:1014543144579123431L,UUIDLeast:-8532948561401745245L,Amount:15.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie_pigman',
            'CustomName': 'Marble Guardian'
        },
        'mojangson': r'''{id:"minecraft:zombie_pigman",Anger:32767s,CustomName:"{\"text\":\"Marble Guardian\"}",Health:40.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:16369622,Name:"{\"text\":\"§bMarbleBoots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:16369622,Name:"{\"text\":\"§bMarblePants\"}"}}},{id:"minecraft:iron_chestplate",Count:1b,tag:{display:{Name:"{\"text\":\"§bRuneboundChest\"}"}}},{id:"minecraft:smooth_quartz",Count:1b}],Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],HandItems:[{id:"minecraft:quartz",Count:1b,tag:{display:{Name:"{\"text\":\"§bMarble Malice\"}"},Enchantments:[{lvl:1s,id:"minecraft:fire_aspect"}],AttributeModifiers:[{UUIDMost:-3038290024543992035L,UUIDLeast:-7447551154585303322L,Amount:8.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': '§6Magmatic Marksman'
        },
        'mojangson': r'''{id:"minecraft:skeleton",CustomName:"{\"text\":\"§6Magmatic Marksman\"}",Health:75.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:7352328,Name:"{\"text\":\"§fBurnt Boots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:7352328,Name:"{\"text\":\"§fBurnt Leggings\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:7352328,Name:"{\"text\":\"§fBurnt Cloak\"}"}}},{id:"minecraft:chainmail_helmet",Count:1b,tag:{display:{Name:"{\"text\":\"§4§lHellborn Crown\"}"}}}],Attributes:[{Base:75.0d,Name:"generic.maxHealth"}],Tags:["boss_fireball"],HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§bDemonbreath\"}"},Enchantments:[{lvl:3s,id:"minecraft:power"},{lvl:1s,id:"minecraft:flame"},{lvl:1s,id:"minecraft:punch"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'HandItems': ["'fComposite Bow'", None],
        },
        'mojangson': r'''{id:"minecraft:skeleton",Health:30.0f,Fire:-1s,Attributes:[{Base:30.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,PersistenceRequired:0b,LeftHanded:0b,AbsorptionAmount:0.0f,HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§fComposite Bow\"}"},Enchantments:[{lvl:3s,id:"minecraft:power"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:spider',
            'CustomName': 'Shieldcrusher Spiders'
        },
        'mojangson': r'''{id:"minecraft:spider",CustomName:"{\"text\":\"Shieldcrusher Spider\"}",Health:24.0f,Attributes:[{Base:24,Name:"generic.maxHealth"}],HandDropChances:[-327.67f,0.085f],ActiveEffects:[{Duration:222220,Id:26,Amplifier:0}],HandItems:[{id:"minecraft:wooden_axe",tag:{AttributeModifiers:[{UUIDMost:339242,UUIDLeast:52922,Amount:2,AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"}]},Count:1b},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:spider',
            'CustomName': 'Shieldcrusher Spider'
        },
        'mojangson': r'''{id:"minecraft:spider",CustomName:"{\"text\":\"Shieldcrusher Spider\"}",Health:24.0f,Attributes:[{Base:24,Name:"generic.maxHealth"}],HandDropChances:[-327.67f,0.085f],ActiveEffects:[{Duration:222220,Id:26,Amplifier:0}],HandItems:[{id:"minecraft:wooden_axe",tag:{AttributeModifiers:[{UUIDMost:339242,UUIDLeast:52922,Amount:2,AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"}]},Count:1b},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie_villager',
            'CustomName': 'Son of the Frost'
        },
        'mojangson': r'''{id:"minecraft:zombie_villager",HurtByTimestamp:494,Attributes:[{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.28d,Name:"generic.movementSpeed"},{Base:2.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:35.0d,Name:"generic.followRange"},{Base:3.0d,Name:"generic.attackDamage"},{Base:0.04554001988740193d,Name:"zombie.spawnReinforcements"},{Base:30.0d,Name:"generic.maxHealth"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,FallDistance:0.0f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:0b,Spigot.ticksLived:651,ConversionTime:-1,Motion:[0.0d,-0.0784000015258789d,0.0d],Leashed:0b,Health:30.0f,Bukkit.updateLevel:2,LeftHanded:0b,Air:300s,OnGround:1b,Dimension:0,HandItems:[{id:"minecraft:iron_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§fFrozen Sword\"}"},Enchantments:[{lvl:1s,id:"minecraft:unbreaking"}],Damage:0}},{id:"minecraft:white_tulip",Count:1b}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],Profession:4,CustomName:"{\"text\":\"Son of the Frost\"}",CanBreakDoors:0b,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:9237759},Damage:0}},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:9237759},Damage:0}},{id:"minecraft:ice",Count:1b}],Fire:-1s,CanPickUpLoot:0b,HurtTime:0s,WorldUUIDLeast:-7560693509725274339L,CustomNameVisible:0b}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Bone Cult Shaman'
        },
        'mojangson': r'''{id:"minecraft:skeleton",CustomName:"{\"text\":\"Bone Cult Shaman\"}",Health:30.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:13684991,Name:"{\"text\":\"§b§lZephyric Sandals\"}"}}},{id:"minecraft:chainmail_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§9§lIronscale Leggings\"}"}}},{id:"minecraft:chainmail_chestplate",Count:1b,tag:{display:{Name:"{\"text\":\"§bBoneRobes\"}"}}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"c659cdd4-e436-4977-a6a7-d5518ebecfbb",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMWFlMzg1NWY5NTJjZDRhMDNjMTQ4YTk0NmUzZjgxMmE1OTU1YWQzNWNiY2I1MjYyN2VhNGFjZDQ3ZDMwODEifX19"}]}},display:{Name:"{\"text\":\"§4§lTlaxan Mask\"}"}}}],Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],Tags:["boss_medicall"],HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§bQuetzalcoatl\\u0027s Wrath\"}"},Enchantments:[{lvl:2s,id:"minecraft:power"}],Damage:0}},{id:"minecraft:tipped_arrow",Count:1b,tag:{Potion:"minecraft:harming"}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:enderman',
            'CustomName': 'Spectral Enderman'
        },
        'mojangson': r'''{id:"minecraft:enderman",CustomName:"{\"text\":\"Spectral Enderman\"}",Health:40.0f,Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:1728000000,Id:24b,Amplifier:0b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:1728000000,Id:14b,Amplifier:0b}],Tags:["boss_targetplayer"],HandItems:[{id:"minecraft:stone_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§bSpectral Slicer\"}"},Enchantments:[{lvl:1s,id:"minecraft:fire_aspect"}],AttributeModifiers:[{UUIDMost:-5959315156678718861L,UUIDLeast:-8083021445480028083L,Amount:8.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'CustomName': '§6Frozen Arcanist'
        },
        'mojangson': r'''{id:"minecraft:wither_skeleton",CustomName:"{\"text\":\"§6Frozen Arcanist\"}",Health:90.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1073407,Name:"{\"text\":\"§aNereid Sandals\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:1073407,Name:"{\"text\":\"§aNereid Leggings\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:1481884,Name:"{\"text\":\"§9§lAntimatter Chestplate\"}"}}},{}],Attributes:[{Base:90.0d,Name:"generic.maxHealth"}],Tags:["Elite","boss_handswap"],ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:99999999,Id:11b,Amplifier:0b}],HandItems:[{id:"minecraft:ender_eye",Count:1b,tag:{display:{Name:"{\"text\":\"§bFrozenArcanistEnderEye\"}"},Enchantments:[{lvl:2s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:-5351288644228789145L,UUIDLeast:-7420281802652659757L,Amount:10.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{id:"minecraft:ender_pearl",Count:1b,tag:{display:{Name:"{\"text\":\"§bFrozenArcanistEnderEye\"}"},AttributeModifiers:[{UUIDMost:3855067632032696055L,UUIDLeast:-8818995474034523850L,Amount:6.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-2744434347783405358L,UUIDLeast:-8375395871970178544L,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': '§6Tundra Spellslinger'
        },
        'mojangson': r'''{id:"minecraft:skeleton",HurtByTimestamp:0,Attributes:[{Base:40.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,FallDistance:0.0f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:0b,Spigot.ticksLived:1795,Motion:[0.0d,-0.0784000015258789d,0.0d],Leashed:0b,Health:40.0f,Bukkit.updateLevel:2,LeftHanded:0b,Air:300s,OnGround:1b,Dimension:0,HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§fLiving Bow\"}"},Enchantments:[{lvl:2s,id:"minecraft:power"},{lvl:1s,id:"minecraft:mending"},{lvl:1s,id:"minecraft:punch"}],Damage:0}},{id:"minecraft:potion",Count:1b,tag:{Potion:"minecraft:slow_falling"}}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],CustomName:"{\"text\":\"Tundra Spellslinger\"}",Fire:-1s,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:16777215,Name:"{\"text\":\"§aSoulleather Shoes\"}"},Enchantments:[{lvl:1s,id:"minecraft:mending"},{lvl:2s,id:"minecraft:protection"},{lvl:1s,id:"minecraft:vanishing_curse"}],Damage:0}},{id:"minecraft:chainmail_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"SnowBanditPants\"}"},Damage:0}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:16777215,Name:"{\"text\":\"§aSoulleather Cloak\"}"},Enchantments:[{lvl:1s,id:"minecraft:mending"},{lvl:2s,id:"minecraft:protection"},{lvl:1s,id:"minecraft:vanishing_curse"}],Damage:0}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"e92c1950-2fa6-4a5b-a1f4-c4ca9eb04402",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMTZlYTMwM2E3MzQ5ZWY4YmI3N2M5NDNlYWIyM2JiNmRlYmMyNTNhOGZlNjk5YmMzYjE1ZmZkMzBlZjliMjYifX19"}]}},display:{Name:"{\"text\":\"Assassin\"}"}}}],CanPickUpLoot:0b,HurtTime:0s,WorldUUIDLeast:-7560693509725274339L,ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:70553,Id:1b,Amplifier:0b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:70553,Id:12b,Amplifier:0b}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Tundra Spellslinger'
        },
        'mojangson': r'''{id:"minecraft:skeleton",HurtByTimestamp:0,Attributes:[{Base:40.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,FallDistance:0.0f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:0b,Spigot.ticksLived:1795,Motion:[0.0d,-0.0784000015258789d,0.0d],Leashed:0b,Health:40.0f,Bukkit.updateLevel:2,LeftHanded:0b,Air:300s,OnGround:1b,Dimension:0,HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§fLiving Bow\"}"},Enchantments:[{lvl:2s,id:"minecraft:power"},{lvl:1s,id:"minecraft:mending"},{lvl:1s,id:"minecraft:punch"}],Damage:0}},{id:"minecraft:potion",Count:1b,tag:{Potion:"minecraft:slow_falling"}}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],CustomName:"{\"text\":\"Tundra Spellslinger\"}",Fire:-1s,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:16777215,Name:"{\"text\":\"§aSoulleather Shoes\"}"},Enchantments:[{lvl:1s,id:"minecraft:mending"},{lvl:2s,id:"minecraft:protection"},{lvl:1s,id:"minecraft:vanishing_curse"}],Damage:0}},{id:"minecraft:chainmail_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"SnowBanditPants\"}"},Damage:0}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:16777215,Name:"{\"text\":\"§aSoulleather Cloak\"}"},Enchantments:[{lvl:1s,id:"minecraft:mending"},{lvl:2s,id:"minecraft:protection"},{lvl:1s,id:"minecraft:vanishing_curse"}],Damage:0}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"e92c1950-2fa6-4a5b-a1f4-c4ca9eb04402",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMTZlYTMwM2E3MzQ5ZWY4YmI3N2M5NDNlYWIyM2JiNmRlYmMyNTNhOGZlNjk5YmMzYjE1ZmZkMzBlZjliMjYifX19"}]}},display:{Name:"{\"text\":\"Assassin\"}"}}}],CanPickUpLoot:0b,HurtTime:0s,WorldUUIDLeast:-7560693509725274339L,ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:70553,Id:1b,Amplifier:0b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:70553,Id:12b,Amplifier:0b}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:enderman',
            'CustomName': '§6Unchained Experiment'
        },
        'mojangson': r'''{id:"minecraft:enderman",CustomName:"{\"text\":\"§6Unchained Experiment\"}",Health:40.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{Enchantments:[{lvl:10s,id:"minecraft:fire_protection"}],Damage:0,AttributeModifiers:[{UUIDMost:4603514513408019067L,UUIDLeast:-7946737575686475072L,Amount:3.0d,Slot:"feet",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:1960082888142045239L,UUIDLeast:-8379815847399625656L,Amount:-0.15d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{},{},{}],Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],Team:"mobs",ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:99999,Id:14b,Amplifier:0b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:99999,Id:24b,Amplifier:0b}],Tags:["Elite","boss_blockbreak","boss_targetplayer"]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Viridian Archer'
        },
        'mojangson': r'''{id:"minecraft:skeleton",CustomName:"{\"text\":\"Viridian Archer\"}",Health:28.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1105920,Name:"{\"text\":\"§aViridian Mage Robes\"}"},Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:1105920,Name:"{\"text\":\"§aViridian Mage Robes\"}"},Damage:0}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:1105920,Name:"{\"text\":\"§aViridian Mage Robes\"}"},Damage:0}},{id:"minecraft:leather_helmet",Count:1b,tag:{display:{color:1105920,Name:"{\"text\":\"§aViridian Mage Hat\"}"}}}],Attributes:[{Base:28.0d,Name:"generic.maxHealth"}],Team:"mobs",HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§3§lSwiftwood Shortbow\"}"},Enchantments:[{lvl:3s,id:"minecraft:power"}],Damage:0}},{id:"minecraft:tipped_arrow",Count:1b,tag:{CustomPotionEffects:[{Ambient:0b,ShowIcon:1b,ShowParticles:1b,Duration:60,Id:1b,Amplifier:4b},{Ambient:0b,ShowIcon:1b,ShowParticles:1b,Duration:60,Id:4b,Amplifier:3b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:60,Id:19b,Amplifier:0b}],Potion:"minecraft:empty"}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:vindicator',
            'CustomName': 'Lunatic Cultist'
        },
        'mojangson': r'''{id:"minecraft:vindicator",CustomName:"{\"text\":\"Gibbering Cultist\"}",Health:40.0f,Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],HandDropChances:[0.0f,0.0f],HandItems:[{id:"minecraft:stone_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§4§lCorrupted Watcher\\u0027s Sword\"}"},Enchantments:[{lvl:5s,id:"minecraft:sharpness"}],Damage:0}},{id:"minecraft:book",Count:1b,tag:{HideFlags:2,display:{Name:"{\"text\":\"§5§lTome of Arcane Horrors\"}"}}}]}''',
    },

    ################################################################################
    # RL Sunken Temple
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'Guardian Brawler'
        },
        'mojangson': r'''{id:"minecraft:silverfish",Passengers:[{CustomName:"{\"text\":\"Guardian Brawler\"}",ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{Enchantments:[{lvl:2s,id:"minecraft:depth_strider"}],display:{color:9161413}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:9161413}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:9161413}}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"4005cac1-a16a-45aa-9e72-7fb514335717",Properties:{textures:[{Signature:"PRszFbJki+hf7k/LnfNAwqzVYyxvkdO0fzqEBMvnoYI/1AK0CPSEls9p8t5vCLYO3je2j0FtMj362hLZN+bhdg7X/f+m7+NJ8GqhXKY5jr3/+H3RbDEpfSBygNqKuABz3I0zyuXzb8OzJsReOWoWp+8AePKw0p4ct+AGhuM27+86u+2fSoXpYr3zJw/N0TmEcKmFFPaTLrVFI348ZkuPQIwsAm3JY81QCo6YyEI+O4oMlKaTav8lNccD8g1s8WHyc02Su+pfEmarqf9cg7365Mx3DFbRUW6VrNXCKboRn+Q/IjUvxxOqx9tx3qQRJsHxuFgq6T/HAboMLNxhQMd2KeOGBo/lOteok5TtUdQi89fYuLhz4SQV0WBNy2bfZ9amMuc9IyYBNxbTh3RSsFwcRt66IorlJVjzK3xi6nVprSBMECW0tTCFMyXcLwrc/bnZPz0P/jNuTG3EyNq+2L91tIfOkKtt55I/vdNqO2ukXsV6peJkRZ2m2DJ2d72IZzr34hbI5q3nDGGlC7118Cb+74Tee/eeZO7UcztZmgVDONRX0AF7sqtSozp8JGlKaUmwTTABrrIMLx2XDdwWsXYGkLoikG1NZea8TohblzTEZIrpnbyNVNxSuKzyAcyzNhwX74+3uLtWj8EB7yKDKU/PXjVpcG+ZvaRLKkNo23XO8g0=",Value:"eyJ0aW1lc3RhbXAiOjE0OTk0OTAwODM4NjIsInByb2ZpbGVJZCI6IjQwMDVjYWMxYTE2YTQ1YWE5ZTcyN2ZiNTE0MzM1NzE3IiwicHJvZmlsZU5hbWUiOiJNSEZfR3VhcmRpYW4iLCJzaWduYXR1cmVSZXF1aXJlZCI6dHJ1ZSwidGV4dHVyZXMiOnsiU0tJTiI6eyJ1cmwiOiJodHRwOi8vdGV4dHVyZXMubWluZWNyYWZ0Lm5ldC90ZXh0dXJlLzkzMmMyNDUyNGM4MmFiM2IzZTU3YzIwNTJjNTMzZjEzZGQ4YzBiZWI4YmRkMDYzNjliYjI1NTRkYTg2YzEyMyJ9fX0="}]},Name:"MHF_Guardian"}}}],id:"minecraft:drowned",HandItems:[{id:"minecraft:stone_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§fPrismarine Axe\"}"},AttributeModifiers:[{UUIDMost:-7576342528069448003L,UUIDLeast:-5159379555572510812L,Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{id:"minecraft:shield",Count:1b,tag:{BlockEntityTag:{id:"minecraft:banner",Patterns:[{Pattern:"gru",Color:15},{Pattern:"bt",Color:15}],Base:11}}}]}],Health:1.0f,Attributes:[{Base:1.0d,Name:"generic.maxHealth"}],Silent:1b,ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:20b,Amplifier:4b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:14b,Amplifier:0b}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Elder Archer'
        },
        'mojangson': r'''{id:"minecraft:skeleton",CustomName:"{\"text\":\"Elder Archer\"}",Health:20.0f,ArmorItems:[{id:"minecraft:leather_boots",tag:{display:{color:16774619}},Count:1b},{id:"minecraft:leather_leggings",tag:{display:{color:16774619},Enchantments:[{lvl:2s,id:"minecraft:thorns"}]},Count:1b},{id:"minecraft:leather_chestplate",tag:{display:{color:16774619}},Count:1b},{id:"minecraft:player_head",tag:{SkullOwner:{Id:"e56a8749-8a4a-40cc-9ded-3c90f8ae8c63",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMWM3OTc0ODJhMTRiZmNiODc3MjU3Y2IyY2ZmMWI2ZTZhOGI4NDEzMzM2ZmZiNGMyOWE2MTM5Mjc4YjQzNmIifX19"}]}}},Count:1b}],Attributes:[{Base:20.0d,Name:"generic.maxHealth"}],Tags:["boss_float"],HandItems:[{id:"minecraft:bow",Count:1b,tag:{Enchantments:[{lvl:3,id:"minecraft:power"}],Damage:0}},{id:"minecraft:tipped_arrow",Count:1b,tag:{Potion:"minecraft:slow_falling"}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:guardian',
            'CustomName': 'Mindfaser'
        },
        'mojangson': r'''{id:"minecraft:guardian",Passengers:[{Potion:{id:"minecraft:lingering_potion",tag:{CustomPotionEffects:[{Duration:550,Id:13,Amplifier:0}]},Count:1},id:"minecraft:potion"}],CustomName:"{\"text\":\"Mindfaser\"}",Health:12.0f,Attributes:[{Base:12,Name:"generic.maxHealth"},{Base:10,Name:"generic.attackDamage"}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Spirit of the drowned'
        },
        'mojangson': r'''{id:"minecraft:silverfish",Passengers:[{CustomName:"{\"text\":\"Spirit of the Drowned\"}",Health:6.0f,ArmorItems:[{id:"minecraft:chainmail_boots",Count:1b,tag:{Enchantments:[{lvl:3s,id:"minecraft:depth_strider"}],AttributeModifiers:[{UUIDMost:6015052308714310336L,UUIDLeast:-5136869337687873999L,Amount:0.2d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{},{id:"minecraft:chainmail_chestplate",Count:1b,tag:{Enchantments:[{lvl:1s,id:"minecraft:fire_protection"},{lvl:5s,id:"minecraft:respiration"}],Damage:0}},{}],Attributes:[{Base:6.0d,Name:"generic.maxHealth"}],id:"minecraft:drowned",ActiveEffects:[{ShowParticles:0b,Duration:222220,Id:14,Amplifier:0}],HandItems:[{id:"minecraft:stone_sword",Count:1b,tag:{Enchantments:[{lvl:3s,id:"minecraft:sharpness"}]}},{}]}],Health:1.0f,Attributes:[{Base:1.0d,Name:"generic.maxHealth"}],Silent:1b,ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:20b,Amplifier:4b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:14b,Amplifier:0b}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:creeper',
            'CustomName': 'Tidal Terror'
        },
        'mojangson': r'''{id:"minecraft:creeper",Fuse:15s,CustomName:"{\"text\":\"Tidal Terror\"}",powered:0b,Health:16.0f,ArmorItems:[{id:"minecraft:leather_boots",tag:{Enchantments:[{lvl:1,id:"minecraft:depth_strider"}]},Count:1b},{},{},{}],Attributes:[{Base:16,Name:"generic.maxHealth"},{Base:0.28d,Name:"generic.movementSpeed"}],ExplosionRadius:3b,ActiveEffects:[{Duration:800,Id:13,Amplifier:0}]}''',
    },
    # RL Sunken Temple
    ################################################################################

    ################################################################################
    # Gray mobs
    {
        'rules': {
            'id': 'minecraft:ghast',
            'CustomName': 'Dessicated Ghast'
        },
        'mojangson': r'''{id:"minecraft:ghast",CustomName:"{\"text\":\"Dessicated Ghast\"}",Health:25.0f,Attributes:[{Base:25.0d,Name:"generic.maxHealth"}],ExplosionPower:2}''',
    },
    {
        'rules': {
            'id': 'minecraft:witch',
            'CustomName': '§6Insectomancer'
        },
        'mojangson': r'''{id:"minecraft:witch",CustomName:"{\"text\":\"§6Insectomancer\"}",Health:70.0f,Attributes:[{Base:70.0d,Name:"generic.maxHealth"}],Tags:["Elite","boss_gray_summ_bug"]}''',
    },
    {
        'rules': {
            'id': 'minecraft:evoker',
            'CustomName': '§6Golem Conjurer'
        },
        'mojangson': r'''{id:"minecraft:evoker",HurtByTimestamp:0,Attributes:[{Base:70.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.5d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:12.0d,Modifiers:[{UUIDMost:-6061386258842106171L,UUIDLeast:-8973333721991499206L,Amount:-0.05375743401508224d,Operation:1,Name:"Random spawn bonus"}],Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,FallDistance:0.0f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:0b,SpellTicks:0,Spigot.ticksLived:376,Tags:["Elite","boss_gray_summ_golem"],Motion:[0.0d,-0.0784000015258789d,0.0d],Leashed:0b,Health:70.0f,Bukkit.updateLevel:2,LeftHanded:0b,Air:300s,OnGround:1b,Dimension:0,Rotation:[124.45302f,-40.0f],HandItems:[{id:"minecraft:stick",Count:1b,tag:{display:{Name:"{\"text\":\"§6Corrupted Staff\"}"},Enchantments:[{lvl:1s,id:"minecraft:power"}]}},{id:"minecraft:totem_of_undying",Count:1b,tag:{display:{Name:"{\"text\":\"§6§lIdol of Immortality\"}"}}}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],CustomName:"{\"text\":\"§6Golem Conjurer\"}",Pos:[-955.5d,57.0d,-1569.5d],Fire:-1s,ArmorItems:[{},{},{},{}],CanPickUpLoot:0b,HurtTime:0s,WorldUUIDLeast:-7560693509725274339L,CustomNameVisible:0b}''',
    },
    {
        'rules': {
            'id': 'minecraft:evoker',
            'CustomName': '§6Demon Conjurer'
        },
        'mojangson': r'''{id:"minecraft:evoker",HurtByTimestamp:0,Attributes:[{Base:70.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.5d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:12.0d,Modifiers:[{UUIDMost:2007171504040069592L,UUIDLeast:-6845276924738347140L,Amount:-0.020605684567772134d,Operation:1,Name:"Random spawn bonus"}],Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,FallDistance:0.0f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:0b,SpellTicks:0,Spigot.ticksLived:418,Tags:["Elite","boss_gray_summ_demon"],Motion:[0.0d,-0.0784000015258789d,0.0d],Leashed:0b,Health:70.0f,Bukkit.updateLevel:2,LeftHanded:1b,Air:300s,OnGround:1b,Dimension:0,Rotation:[125.80794f,-40.0f],HandItems:[{id:"minecraft:stone_shovel",Count:1b,tag:{display:{Name:"{\"text\":\"§aPyromancer\\u0027s Staff\"}"},Enchantments:[{lvl:1s,id:"minecraft:power"}]}},{id:"minecraft:totem_of_undying",Count:1b,tag:{display:{Name:"{\"text\":\"§e§lTotem of the Veil\"}"}}}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],CustomName:"{\"text\":\"§6Demon Conjurer\"}",Pos:[-955.5d,57.0d,-1567.5d],Fire:-1s,ArmorItems:[{},{},{},{}],CanPickUpLoot:0b,HurtTime:0s,WorldUUIDLeast:-7560693509725274339L,CustomNameVisible:0b}''',
    },
    {
        'rules': {
            'id': 'minecraft:witch',
            'CustomName': '§6Bibliomancer'
        },
        'mojangson': r'''{id:"minecraft:witch",CustomName:"{\"text\":\"§6Bibliomancer\"}",Health:70.0f,Attributes:[{Base:70.0d,Name:"generic.maxHealth"}],Tags:["Elite","boss_gray_summ_book"]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Desiccated Terror'
        },
        'mojangson': r'''{id:"minecraft:skeleton",HurtByTimestamp:0,Attributes:[{Base:45.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,FallDistance:0.0f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:1b,Spigot.ticksLived:3604,Motion:[0.0d,-0.0784000015258789d,0.0d],Leashed:0b,Health:45.0f,Bukkit.updateLevel:2,LeftHanded:0b,Air:300s,OnGround:1b,Dimension:0,Rotation:[0.0f,0.0f],HandItems:[{id:"minecraft:iron_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§fSkullcrusher\"}"},AttributeModifiers:[{UUIDMost:6532206609118478368L,UUIDLeast:-8955621743513098640L,Amount:0.8d,Slot:"mainhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-1685987466123654650L,UUIDLeast:-5383834777761010495L,Amount:15.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-463252452232638665L,UUIDLeast:-4687319287056168669L,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],CustomName:"{\"text\":\"Desiccated Terror\"}",Pos:[-955.5d,57.0d,-1559.5d],Fire:-1s,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"§bGrayBoots\"}"},Damage:0}},{id:"minecraft:chainmail_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§9§lIronscale Leggings\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"§bGrayChest2\"}"},Damage:0}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"5554d596-e473-49d7-b6d4-6e7fad49a9f2",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvZmZkOWM2ZjFkYzQ5Njc3NTUyNTk1YjZlODJmMTI5Njc3OGZiMGJkZDNlMGJjN2MxNTQwODRlYTJlMzMxNDRmIn19fQ=="}]}},display:{Name:"{\"text\":\"§bGrayMummyHead2\"}"}}}],CanPickUpLoot:0b,HurtTime:0s,WorldUUIDLeast:-7560693509725274339L}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Desiccated Brute'
        },
        'mojangson': r'''{id:"minecraft:skeleton",HurtByTimestamp:4615,Attributes:[{Base:45.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,FallFlying:0b,PortalCooldown:0,AbsorptionAmount:0.0f,FallDistance:0.0f,DeathTime:0s,WorldUUIDMost:-1041596277173696703L,HandDropChances:[-200.1f,-200.1f],PersistenceRequired:1b,Spigot.ticksLived:16363,Motion:[0.0d,-0.0784000015258789d,0.0d],Leashed:0b,Health:45.0f,Bukkit.updateLevel:2,Silent:1b,LeftHanded:0b,Air:300s,OnGround:1b,Dimension:0,Rotation:[0.0f,2.2923818f],HandItems:[{id:"minecraft:stone_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§fObsidian Blade\"}"},AttributeModifiers:[{UUIDMost:-2483446473759634744L,UUIDLeast:-7254151480308536732L,Amount:10.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-1575746377282469550L,UUIDLeast:-7704976322174616712L,Amount:0.05d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{}],ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f],CustomName:"{\"text\":\"Desiccated Brute\"}",Pos:[-955.3024929396968d,57.0d,-1557.2220994220675d],Fire:-1s,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"§bGrayBoots\"}"},Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:7567221,Name:"{\"text\":\"§bGrayPants\"}"},Damage:0}},{id:"minecraft:chainmail_chestplate",Count:1b,tag:{display:{Name:"{\"text\":\"§7§lWhispering Chains\"}"}}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"8f7c0c5b-720f-4944-8481-b0f7931f303f",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvM2U5MWU5NTgyMmZlOThjYzVhNTY1OGU4MjRiMWI4Y2YxNGQ0ZGU5MmYwZTFhZjI0ODE1MzcyNDM1YzllYWI2In19fQ=="}]}},display:{Name:"{\"text\":\"§bGrayMummyHead\"}"}}}],CanPickUpLoot:0b,HurtTime:0s,WorldUUIDLeast:-7560693509725274339L}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie_villager',
            'CustomName': 'Desiccated Husk'
        },
        'mojangson': r'''{id:"minecraft:zombie_villager",Profession:3,CustomName:"{\"text\":\"Desiccated Husk\"}",Health:30.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"§bGrayBoots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:7567221,Name:"{\"text\":\"§bGrayPants\"}"},Damage:0}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:7567221,Name:"{\"text\":\"§bGrayChest\"}"}}},{id:"minecraft:leather_helmet",Count:1b,tag:{display:{color:9468004,Name:"{\"text\":\"§c§lSacrifice\\u0027s Scalp\"}"}}}],Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],HandItems:[{id:"minecraft:yellow_glazed_terracotta",Count:1b,tag:{AttributeModifiers:[{UUIDMost:6017016372753615690L,UUIDLeast:-7901936291116754037L,Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-6310810371670782814L,UUIDLeast:-6820282009554906307L,Amount:0.12d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'CustomName': 'Desiccated Bowman'
        },
        'mojangson': r'''{id:"minecraft:skeleton",CustomName:"{\"text\":\"Desiccated Bowman\"}",Health:30.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1908001,Name:"{\"text\":\"§bGrayBoots\"}"},Damage:0}},{id:"minecraft:chainmail_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§9§lIronscale Leggings\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:7567221,Name:"{\"text\":\"§bGrayChest\"}"},Damage:0}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"8f7c0c5b-720f-4944-8481-b0f7931f303f",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvM2U5MWU5NTgyMmZlOThjYzVhNTY1OGU4MjRiMWI4Y2YxNGQ0ZGU5MmYwZTFhZjI0ODE1MzcyNDM1YzllYWI2In19fQ=="}]}},display:{Name:"{\"text\":\"§bGrayMummyHead\"}"}}}],Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§6§lScarab\\u0027s Bane\"}"},Enchantments:[{lvl:1s,id:"minecraft:flame"},{lvl:3s,id:"minecraft:power"}],Damage:0}},{id:"minecraft:tipped_arrow",Count:1b,tag:{CustomPotionEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:120,Id:14b,Amplifier:0b}],Potion:"minecraft:empty"}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:drowned',
            'CustomName': 'Sopping Cadaver'
        },
        'mojangson': r'''{id:"minecraft:drowned",CustomName:"{\"text\":\"Sopping Cadaver\"}",Health:28.0f,ArmorItems:[{},{id:"minecraft:chainmail_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§9§lIronscale Leggings\"}"},Damage:0}},{id:"minecraft:chainmail_chestplate",Count:1b,tag:{display:{Name:"{\"text\":\"§7§lWhispering Chains\"}"}}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"17673802-79e3-4a1b-9350-d416924a583b",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvNDRiYjI2MjdiMmRmODg0MjRmM2Q2MDY3NDk3ZGQyMzAzOWM1ODI2OTI5NTllYTE2NDhiYzc2YzFhOGNlYTgwIn19fQ=="}]}},display:{Name:"{\"text\":\"§bWaterCorpseHead\"}"}}}],Attributes:[{Base:28.0d,Name:"generic.maxHealth"}],HandItems:[{id:"minecraft:trident",Count:1b,tag:{display:{Name:"{\"text\":\"§fPrismarine Pike\"}"},Damage:0}},{}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:creeper',
            'CustomName': 'Unstable Revenant'
        },
        'mojangson': r'''{id:"minecraft:creeper",CustomName:"{\"text\":\"Unstable Revenant\"}",powered:1b,Health:28.0f,Attributes:[{Base:28.0d,Name:"generic.maxHealth"}],ExplosionRadius:3b,Tags:["boss_invisible","boss_volatile"]}''',
    },
    {
        'rules': {
            'id': 'minecraft:creeper',
            'CustomName': 'Unstable Atrocity'
        },
        'mojangson': r'''{id:"minecraft:creeper",CustomName:"{\"text\":\"Unstable Atrocity\"}",Health:28.0f,Attributes:[{Base:28.0d,Name:"generic.maxHealth"}],ExplosionRadius:4b,Tags:["boss_volatile"]}''',
    },
    {
        'rules': {
            'id': 'minecraft:blaze',
            'CustomName': 'Disembodied Soul'
        },
        'mojangson': r'''{id:"minecraft:blaze",CustomName:"{\"text\":\"Disembodied Soul\"}",Health:30.0f,Attributes:[{Base:30.0d,Name:"generic.maxHealth"}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:spider',
            'CustomName': 'Venomous Tarantula'
        },
        'mojangson': r'''{id:"minecraft:spider",CustomName:"{\"text\":\"Venomous Tarantula\"}",Health:30.0f,Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],Tags:["boss_witherhit"],HandItems:[{id:"minecraft:string",Count:1b,tag:{AttributeModifiers:[{UUIDMost:8950014472550895615L,UUIDLeast:-8091237055434418498L,Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
    # Gray mobs
    ################################################################################
]

def usage():
    sys.exit("Usage: {} <--world /path/to/world> [--logfile <stdout|stderr|path>] [--dry-run] [--interactive]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:l:di", ["world=", "logfile=", "dry-run", "interactive"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
logfile = 'stdout'
dry_run = False
interactive = False

for o, a in opts:
    if o in ("-w", "--world"):
        world_path = a
    elif o in ("-l", "--logfile"):
        logfile = a
    elif o in ("-d", "--dry-run"):
        dry_run = True
    elif o in ("-i", "--interactive"):
        interactive = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None:
    eprint("--world must be specified!")
    usage()

world = World(world_path)

log_handle = None
if logfile == "stdout":
    log_handle = sys.stdout
elif logfile == "stderr":
    log_handle = sys.stderr
elif logfile is not None:
    log_handle = open(logfile, 'w')

# Just in case the replacements themselves have junk tags...
clean_mobs_to_replace = []
for replacement in mobs_to_replace:
    entity = nbt.TagCompound.from_mojangson(replacement['mojangson'])
    remove_tags_from_spawner_entity(entity, None, log_handle)
    replacement['mojangson'] = entity.to_mojangson()
    clean_mobs_to_replace.append(replacement)
mobs_to_replace = clean_mobs_to_replace

replacements_log = {}
for entity, source_pos, entity_path in world.entity_iterator(readonly=dry_run):
    ### Apply fixes common to all spawners
    remove_tags_from_entities_in_spawner(entity, entity_path, log_handle)

    # Prime spawners
    if entity.has_path("Delay"):
        entity.at_path("Delay").value = 0

    # Remove pigs
    if entity.has_path('SpawnPotentials'):
        new_potentials = []
        for nested_entity in entity.at_path('SpawnPotentials').value:
            if nested_entity.has_path('Entity.id') and nested_entity.at_path('Entity.id').value == "minecraft:pig":
                log_handle.write("Removing pig from SpawnPotentials at {}\n".format(get_debug_string_from_entity_path(entity_path)))
            else:
                new_potentials.append(nested_entity)
        entity.at_path('SpawnPotentials').value = new_potentials
    if entity.has_path("SpawnData.id") and entity.at_path("SpawnData.id").value == "minecraft:pig":
        log_handle.write("Removing pig Spawndata at {}\n".format(get_debug_string_from_entity_path(entity_path)))
        entity.value.pop("SpawnData")

    ### Update entities
    for replacement in mobs_to_replace:
        if entity.has_path('id') and entity.at_path('id').value == replacement['rules']['id']:
            matches = False

            if interactive:
                variables = globals().copy()
                variables.update(locals())
                shell = code.InteractiveConsole(variables)
                shell.interact()

            if (('CustomName' in replacement['rules'] and replacement['rules']['CustomName'] is not None) or
                ('HandItems' in replacement['rules'] and ((replacement['rules']['HandItems'][0] is not None) or
                                                          (replacement['rules']['HandItems'][1] is not None)))):
                # Can only potentially replace if 'CustomName' or 'HandItems' rule specified and valid
                matches = True

            if 'CustomName' in replacement['rules']:
                # This rule has a 'CustomName' field - fail if the mob does not have a name or the name doesn't match
                if not entity.has_path('CustomName'):
                    matches = False

                else:
                    name = parse_name_possibly_json(entity.at_path('CustomName').value)

                    if name != replacement['rules']['CustomName']:
                        matches = False

            if 'HandItems' in replacement['rules']:
                # This rule has a 'HandItems' field - fail if the mob does not have HandItems or the names of them don't both match
                if not entity.has_path('HandItems'):
                    matches = False

                else:
                    hand_items = get_named_hand_items(entity)

                    if hand_items != replacement['rules']['HandItems']:
                        matches = False

            if matches:
                # Replace this entity
                log_handle.write("\n")
                log_handle.write("    TO:    {}\n".format(replacement['mojangson']))
                log_handle.write("    FROM:  {}\n".format(entity.to_mojangson()))
                log_handle.write("    AT:    {}\n".format(get_debug_string_from_entity_path(entity_path)))
                log_handle.write("\n")

                entity.value = nbt.TagCompound.from_mojangson(replacement['mojangson']).value



if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
    log_handle.close()

eprint("Done")
