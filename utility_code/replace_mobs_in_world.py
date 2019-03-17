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
        'mojangson': r'''{CustomName:"{\"text\":\"Pirate Archer\"}",Health:30.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:4673362,Name:"{\"text\":\"§bPirateBoots\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:4673362,Name:"{\"text\":\"§bPiratePants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:6192150,Name:"{\"text\":\"§bPirateChest\"}"}}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"1165dfc5-ebc2-44ee-aee2-cfc3c4e115ab",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvN2M0NjUzODZiYmU5ZmFmMTQzN2FmNjM3N2Q2NjczNWRjNWExNWVhNWNlZGYyNmJkOTVmZDNmZTY2YjNhZmNkIn19fQ=="}]}},display:{Name:"{\"text\":\"Pirate Girl\"}"}}}],Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],id:"minecraft:skeleton",HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§bSteelwood Bow\"}"},Enchantments:[{lvl:2s,id:"minecraft:power"}],Damage:0}},{id:"minecraft:tipped_arrow",Count:1b,tag:{Potion:"minecraft:weakness"}}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:zombie',
            'CustomName': 'Pirate Swordsman'
        },
        'mojangson': r'''{CustomName:"{\"text\":\"Pirate Swordsman\"}",Health:40.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:4673362,Name:"{\"text\":\"§bPirateBoots\"}"},Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:4673362,Name:"{\"text\":\"§bPiratePants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:6192150,Name:"{\"text\":\"§bPirateChest\"}"}}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"99b222b4-9770-4154-8589-bae30d73b68d",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvZTBjZjhjYWViNWI4OTYxODg4YmQ4NmZhOTgzNjk0YmYxNTFmOWEzZTU1NzVjZGQwNDA5MDYzMWZlZTUwYmNjNiJ9fX0="}]}},display:{Name:"{\"text\":\"Villager Pirate\"}"}}}],Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],id:"minecraft:zombie",HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§7§lArachnidruid Cutlass\"}"},Enchantments:[{lvl:2s,id:"minecraft:sharpness"}]}},{}]}''',
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
        'mojangson': r'''{CustomName:"{\"text\":\"Animated Crystal\"}",IsBaby:0b,Health:40.0f,ArmorItems:[{},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:12772533,Name:"{\"text\":\"§fCloth Shirt\"}"},AttributeModifiers:[{UUIDMost:270399L,UUIDLeast:903793L,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"c46f476b-d3ef-45d5-975b-6bb2bcc7c9f6",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMjI4ZGQzZDliODFjYzlmOTZhNGMxMWZlMTNiMDc5NDk0ZjI3ZmM1YjkzM2M0ZjA4MzNmNjU2NDQ3MmVlMTYwOSJ9fX0="}]}},display:{Name:"{\"text\":\"§fcrystal_melee_helmet\"}"}}}],Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],id:"minecraft:zombie",ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:17280000,Id:14b,Amplifier:0b}],Tags:["boss_charger"],HandItems:[{id:"minecraft:iron_shovel",Count:1b,tag:{Enchantments:[{lvl:1s,id:"minecraft:knockback"},{lvl:1s,id:"minecraft:fire_aspect"}],display:{Name:"{\"text\":\"§fCrystal Spear\"}"},Damage:0,AttributeModifiers:[{UUIDMost:4790688300322801738L,UUIDLeast:-5487926069810695271L,Amount:10.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
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
