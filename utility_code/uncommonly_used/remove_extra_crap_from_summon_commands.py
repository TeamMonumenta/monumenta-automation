#!/usr/bin/env python3

# For interactive shell
import readline
import code

import sys
import os
import getopt
import re
from pprint import pprint

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from quarry.types import nbt

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


mobs = [
    r'''{HurtByTimestamp:0,Leashed:0b,IsBaby:1b,Health:8.0f,Bukkit.updateLevel:2,Attributes:[{Base:8.0d,Name:"generic.maxHealth"}],Silent:1b,OnGround:1b,Dimension:0,PortalCooldown:0,AbsorptionAmount:0.0f,CustomName:"{\"text\":\"§dAnimated Text\"}",CanBreakDoors:0b,WorldUUIDMost:-1041596277173696703L,ArmorItems:[{},{},{},{id:"minecraft:book",Count:1b,tag:{display:{Name:"{\"text\":\"§b§lTome of Aquatic Shards\"}"},Enchantments:[{lvl:1s,id:"minecraft:power"}],AttributeModifiers:[{UUIDMost:-7795826339782442390L,UUIDLeast:-8977556070605263741L,Amount:2.0d,Slot:"head",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}}],DeathLootTable:"minecraft:empty",Spigot.ticksLived:271,Tags:["boss_gray_swarm"],WorldUUIDLeast:-7560693509725274339L,ActiveEffects:[{Ambient:0b,ShowIcon:0b,ShowParticles:0b,Duration:199709,Id:14b,Amplifier:0b}]}''',
    r'''{HurtByTimestamp:0,Leashed:0b,Health:50.0f,Bukkit.updateLevel:2,Attributes:[{Base:50.0d,Name:"generic.maxHealth"}],OnGround:1b,Dimension:0,PortalCooldown:0,AbsorptionAmount:0.0f,HandItems:[{id:"minecraft:stone_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§5§lErebus\"}"},AttributeModifiers:[{UUIDMost:4546668228276800624L,UUIDLeast:-9220563185721679875L,Amount:0.2d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:2132509948532640819L,UUIDLeast:-4693094300401352144L,Amount:14.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{id:"minecraft:fermented_spider_eye",Count:1b,tag:{HideFlags:1,display:{Name:"{\"text\":\"§c§lDemonic Heart\"}"}}}],CustomName:"{\"text\":\"Conjured Demon\"}",WorldUUIDMost:-1041596277173696703L,ArmorItems:[{id:"minecraft:diamond_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§bSummoner2Boots\"}"},Damage:0}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:13915937,Name:"{\"text\":\"§bSummoner2Pants\"}"},Damage:0}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:11546150,Name:"{\"text\":\"§bSummoner2Chest\"}"},Damage:0}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"a7024851-83e4-3575-8a62-20405cf05aa3",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvZGRlNTU2OWUzM2YzNzVhYWEyM2U5MTc2ZjkxZjE5MmMzNDUyOTNlMjgyMjc1NjdjNzMwYzY2NmYzOGI4ZGUifX19"}]}}}}],Spigot.ticksLived:511,WorldUUIDLeast:-7560693509725274339L}''',
    r'''{HurtByTimestamp:0,Leashed:0b,Health:50.0f,Bukkit.updateLevel:2,Attributes:[{Base:50.0d,Name:"generic.maxHealth"}],OnGround:1b,Dimension:0,PortalCooldown:0,AbsorptionAmount:0.0f,HandItems:[{id:"minecraft:stone_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§6§lSoulcrusher\"}"},Damage:0,AttributeModifiers:[{UUIDMost:-4664142119989130575L,UUIDLeast:-7207479895603301059L,Amount:1.0d,Slot:"mainhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-9164396771939824792L,UUIDLeast:-6052235485526131778L,Amount:14.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-433896928173994138L,UUIDLeast:-8859177146029034537L,Amount:0.05d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{id:"minecraft:redstone",Count:1b,tag:{display:{Name:"{\"text\":\"§4§lCorrupted Malevolence\"}"}}}],CustomName:"{\"text\":\"Conjured Golem\"}",WorldUUIDMost:-1041596277173696703L,ArmorItems:[{id:"minecraft:chainmail_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§bSummonerBoots\"}"},Damage:0}},{id:"minecraft:chainmail_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§9§lIronscale Leggings\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:11546150,Name:"{\"text\":\"§bSummoner2Chest\"}"},Damage:0}},{id:"minecraft:leather_helmet",Count:1b,tag:{display:{color:9468004,Name:"{\"text\":\"§c§lSacrifice\\u0027s Scalp\"}"},Damage:0}}],Spigot.ticksLived:92,WorldUUIDLeast:-7560693509725274339L}''',
    r'''{HurtByTimestamp:0,Leashed:0b,IsBaby:1b,Health:8.0f,Bukkit.updateLevel:2,Attributes:[{Base:8.0d,Name:"generic.maxHealth"}],Silent:1b,OnGround:1b,Dimension:0,PortalCooldown:0,AbsorptionAmount:0.0f,CustomName:"{\"text\":\"§eScarab\"}",CanBreakDoors:0b,WorldUUIDMost:-1041596277173696703L,ArmorItems:[{},{},{},{id:"minecraft:brown_mushroom",Count:1b,tag:{display:{Name:"{\"text\":\"§eScarab Teeth\"}"},AttributeModifiers:[{UUIDMost:6479497315394079057L,UUIDLeast:-5714715579073658916L,Amount:2.0d,Slot:"head",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}}],DeathLootTable:"minecraft:empty",Spigot.ticksLived:271,Tags:["boss_gray_swarm"],WorldUUIDLeast:-7560693509725274339L,ActiveEffects:[{Ambient:0b,ShowIcon:0b,ShowParticles:0b,Duration:199709,Id:14b,Amplifier:0b}]}''',
]

for mob in mobs:
    entity = nbt.TagCompound.from_mojangson(mob)
    remove_tags_from_spawner_entity(entity, None, None)
    print(entity.to_mojangson())
