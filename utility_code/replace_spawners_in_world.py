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

spawners_to_replace = [
    {
        'rules': {
            'id': 'minecraft:guardian',
            'mob_CustomName': r'''Debuff Phaser'''
        },
        'mojangson': r'''{MaxNearbyEntities:6s,RequiredPlayerRange:12s,SpawnCount:1s,MaxSpawnDelay:1800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:1800s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Debuff Phaser\"}]",Passengers:[{CustomName:"[{\"text\":\"Ocean\\u0027s Antidote\"}]",Potion:{id:"minecraft:splash_potion",Count:1b,tag:{CustomPotionEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:200,Id:3b,Amplifier:9b}],Potion:"minecraft:empty",display:{Name:"[{\"text\":\"Ocean\\u0027s Blessing\",\"italic\":false}]"}}},id:"minecraft:potion"}],Health:68.0f,Attributes:[{Base:10.0d,Name:"generic.attackDamage"},{Base:68.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"}],Silent:1b,id:"minecraft:guardian",Tags:["boss_debuffhit","Elite"]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:drowned',
            'mob_CustomName': r'''Skewer Fisherman'''
        },
        'mojangson': r'''{MaxNearbyEntities:6s,RequiredPlayerRange:12s,SpawnCount:1s,MaxSpawnDelay:1800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:1800s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Skewer Fisherman\",\"color\":\"gold\"}]",Passengers:[{CustomName:"[{\"text\":\"Undead Fisherman\\u0027s Tonic\"}]",Potion:{id:"minecraft:splash_potion",Count:1b,tag:{CustomPotionEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:600,Id:1b,Amplifier:1b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:1,Id:7b,Amplifier:1b}],Potion:"minecraft:empty",display:{Name:"{\"italic\":false,\"text\":\"Undead Fisherman\\u0027s Tonic\"}"}}},id:"minecraft:potion"}],Health:135.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{Enchantments:[{lvl:3s,id:"minecraft:depth_strider"}],display:{color:4409980},AttributeModifiers:[{UUIDMost:-8776597148285647765L,UUIDLeast:-9206484756231977365L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:4409980},AttributeModifiers:[{UUIDMost:1188612004481876511L,UUIDLeast:-5821744835140493444L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:16725301,Name:"{\"text\":\"§rTlaxan Priest Robe\"}"},AttributeModifiers:[{UUIDMost:6244128172798787786L,UUIDLeast:-8468974444263739158L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_helmet",Count:1b,tag:{display:{color:16725301,Name:"{\"text\":\"§d§lFisherman\\u0027s Cap\"}"},AttributeModifiers:[{UUIDMost:-8226535867445522848L,UUIDLeast:-5390949661264407625L,Amount:0.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}}],Attributes:[{Base:128.0d,Name:"generic.followRange"},{Base:135.0d,Name:"generic.maxHealth"},{Base:0.35d,Name:"generic.movementSpeed"}],PersistenceRequired:1b,id:"minecraft:drowned",Tags:["Elite","aura_slowness"],HandItems:[{id:"minecraft:trident",Count:1b,tag:{display:{Name:"{\"italic\":false,\"text\":\"Barbed Skewer\"}"}}},{id:"minecraft:fishing_rod",Count:1b,tag:{display:{Name:"{\"text\":\"§aMermaid\\u0027s Touch\"}"}}}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:spider',
            'mob_CustomName': r'''Rageroot Arachnid'''
        },
        'mojangson': r'''{MaxNearbyEntities:6s,RequiredPlayerRange:12s,SpawnCount:1s,MaxSpawnDelay:1800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:1800s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Rageroot Arachnid\",\"color\":\"gold\"}]",Health:180.0f,Attributes:[{Base:180.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"},{Base:0.3d,Name:"generic.movementSpeed"}],PersistenceRequired:1b,id:"minecraft:spider",Tags:["Elite"],HandItems:[{id:"minecraft:iron_axe",Count:1b,tag:{display:{Name:"{\"italic\":false,\"text\":\"Sharpened Fangs\"}"},AttributeModifiers:[{UUIDMost:-558721672100425944L,UUIDLeast:-8124267424213379293L,Amount:16.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:creeper',
            'mob_CustomName': r'''Rageroot Creeper'''
        },
        'mojangson': r'''{MaxNearbyEntities:6s,RequiredPlayerRange:12s,SpawnCount:1s,MaxSpawnDelay:1800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:1800s,SpawnPotentials:[{Entity:{Fuse:15s,CustomName:"[{\"text\":\"Rageroot Creeper\",\"color\":\"gold\"}]",Health:90.0f,Attributes:[{Base:90.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"}],PersistenceRequired:1b,id:"minecraft:creeper",ExplosionRadius:6b,Tags:["Elite","boss_volatile"]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:stray',
            'mob_CustomName': r'''Antediluvian Aquamancer'''
        },
        'mojangson': r'''{MaxNearbyEntities:6s,RequiredPlayerRange:12s,SpawnCount:1s,MaxSpawnDelay:1800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:1800s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Antediluvian Aquamancer\",\"color\":\"gold\"}]",Health:68.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:5212828,Name:"{\"text\":\"§fFur Boots\"}"},Enchantments:[{lvl:1s,id:"minecraft:depth_strider"}],AttributeModifiers:[{UUIDMost:5386322013538897733L,UUIDLeast:-8998162946674457598L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:5415325,Name:"{\"text\":\"§fCerulean Mage Robes\"}"},AttributeModifiers:[{UUIDMost:-1995641301730177409L,UUIDLeast:-5515609166516412329L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:7126421,Name:"{\"text\":\"§fCerulean Mage Robes\"}"},AttributeModifiers:[{UUIDMost:-631563309361249866L,UUIDLeast:-8025764122455886580L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"aebaed94-875d-427a-9d9b-c44390fbd8ba",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvOGQ4OGZhNzRkYzkyZWUxMDQ0NmVmYjg2YWQ1YzZjOTVhMzk4ZTMxMjU5Y2RlNTIxYWE3MzIyZWY5MmRjMjEzYiJ9fX0="}]}},display:{}}}],Attributes:[{Base:68.0d,Name:"generic.maxHealth"},{Base:0.225d,Name:"generic.movementSpeed"},{Base:128.0d,Name:"generic.followRange"}],PersistenceRequired:1b,id:"minecraft:stray",Tags:["boss_rejuvenation","Elite"],HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§8§lShadow\\u0027s Flames\"}"},Enchantments:[{lvl:30s,id:"minecraft:power"}]}},{id:"minecraft:tipped_arrow",Count:64b,tag:{CustomPotionEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:2b,Amplifier:1b}],Potion:"minecraft:empty"}}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:wither_skeleton',
            'mob_CustomName': r'''Prismatic Guardian'''
        },
        'mojangson': r'''{MaxNearbyEntities:6s,RequiredPlayerRange:12s,SpawnCount:1s,MaxSpawnDelay:1800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:1800s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Prismatic Guardian\",\"color\":\"gold\"}]",Health:270.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:7138262,Name:"{\"text\":\"§fMolten Boots\"}"},Enchantments:[{lvl:3s,id:"minecraft:depth_strider"}],AttributeModifiers:[{UUIDMost:-944856366505046841L,UUIDLeast:-6105144497961504631L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:7138262,Name:"{\"text\":\"§fMolten Pants\"}"},AttributeModifiers:[{UUIDMost:3888304676118810404L,UUIDLeast:-4807977090837825753L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:7138262,Name:"{\"text\":\"§fMolten Cloak\"}"},AttributeModifiers:[{UUIDMost:-1910290038600611430L,UUIDLeast:-6235118465610640621L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{}],Attributes:[{Base:270.0d,Name:"generic.maxHealth"},{Base:1.0d,Name:"generic.knockbackResistance"},{Base:0.275d,Name:"generic.movementSpeed"},{Base:128.0d,Name:"generic.followRange"}],PersistenceRequired:1b,id:"minecraft:wither_skeleton",Tags:["Elite","boss_charger"],HandItems:[{id:"minecraft:iron_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§aPerilous Zweihander\"}"},AttributeModifiers:[{UUIDMost:2778343276251138293L,UUIDLeast:-6183743212280026582L,Amount:22.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:guardian',
            'mob_CustomName': r'''Sodden Corpse'''
        },
        'mojangson': r'''{MaxNearbyEntities:6s,RequiredPlayerRange:12s,SpawnCount:1s,MaxSpawnDelay:1800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:1800s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Sodden Corpse\",\"color\":\"gold\"}]",Passengers:[{CustomName:"[{\"text\":\"Corpse Possessor\",\"color\":\"gold\"}]",Health:100.0f,Attributes:[{Base:100.0d,Name:"generic.maxHealth"},{Base:0.3d,Name:"generic.movementSpeed"},{Base:128.0d,Name:"generic.followRange"},{Base:20.0d,Name:"generic.attackDamage"}],Silent:1b,id:"minecraft:guardian",Tags:["Elite"]}],Health:225.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:6252903,Name:"{\"text\":\"§fBandit\\u0027s Boots\"}"},Enchantments:[{lvl:3s,id:"minecraft:depth_strider"}],AttributeModifiers:[{UUIDMost:8283392819243862858L,UUIDLeast:-6761338060964078388L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:7372155,Name:"{\"text\":\"§fScoundrel\\u0027s Trousers\"}"},AttributeModifiers:[{UUIDMost:6854348570093242073L,UUIDLeast:-6580178524329005905L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:10072236,Name:"{\"text\":\"§fBrigand\\u0027s Tunic\"}"},AttributeModifiers:[{UUIDMost:3612403347900943719L,UUIDLeast:-7666735338925091412L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{}],Attributes:[{Base:225.0d,Name:"generic.maxHealth"},{Base:0.4d,Name:"generic.movementSpeed"},{Base:128.0d,Name:"generic.followRange"}],PersistenceRequired:1b,id:"minecraft:drowned",Tags:["Elite"],HandItems:[{id:"minecraft:iron_hoe",Count:1b,tag:{display:{Name:"{\"text\":\"§fSeawater Razor\"}"},AttributeModifiers:[{UUIDMost:-8486678022247201685L,UUIDLeast:-8518554479247957116L,Amount:17.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'mob_CustomName': r'''Bandit Archer'''
        },
        'mojangson': r'''{MaxNearbyEntities:6s,RequiredPlayerRange:12s,SpawnCount:2s,MaxSpawnDelay:800s,Delay:0s,SpawnRange:4s,MinSpawnDelay:600s,SpawnPotentials:[{Entity:{CustomName:"{\"text\":\"Bandit Archer\"}",ArmorItems:[{id:"minecraft:leather_boots",tag:{display:{color:6704179}},Count:1b},{id:"minecraft:leather_leggings",tag:{display:{color:7955020}},Count:1b},{id:"minecraft:leather_chestplate",tag:{display:{color:6704179}},Count:1b},{id:"minecraft:player_head",tag:{SkullOwner:{Id:"f778d9a1-3995-4be4-8853-d2c788e94230",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYTE4YjkyOTM4MWFiNWZiZWIwY2NiNzFkM2ZjYjhlMzk2MzJlMjUyZmI1NDQxNzFiYzBlNTc3YmMwYjFkIn19fQ=="}]}},display:{Name:"{\"text\":\"Bandit\"}"}},Count:1b}],id:"minecraft:skeleton",HandItems:[{id:"minecraft:bow",tag:{},Count:1b},{id:"minecraft:shield",tag:{},Count:1b}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:guardian',
            'mob_CustomName': r'''Phaser Assassin'''
        },
        'mojangson': r'''{MaxNearbyEntities:6s,RequiredPlayerRange:12s,SpawnCount:1s,MaxSpawnDelay:1800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:1800s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Phaser Assassin\",\"color\":\"gold\"}]",Health:90.0f,Attributes:[{Base:90.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"},{Base:15.0d,Name:"generic.attackDamage"}],PersistenceRequired:1b,id:"minecraft:guardian",Tags:["Elite"]},Weight:1}]}''',
    },
]

def usage():
    sys.exit("Usage: {} <--world /path/to/world> [--logfile <stdout|stderr|path>] [--pos1 x,y,z --pos2 x,y,z] [--dry-run] [--interactive]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:l:di", ["world=", "logfile=", "pos1=", "pos2=", "dry-run", "interactive"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
logfile = 'stdout'
dry_run = False
interactive = False
pos1 = None
pos2 = None

for o, a in opts:
    if o in ("-w", "--world"):
        world_path = a
    elif o in ("-l", "--logfile"):
        logfile = a
    elif o in ("--pos1"):
        try:
            split = a.split(",")
            pos1 = (int(split[0]), int(split[1]), int(split[2]))
        except:
            eprint("Invalid --pos1 argument")
            usage()
    elif o in ("--pos2"):
        try:
            split = a.split(",")
            pos2 = (int(split[0]), int(split[1]), int(split[2]))
        except:
            eprint("Invalid --pos2 argument")
            usage()
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
elif ((pos1 is not None) and (pos2 is None)) or ((pos1 is None) and (pos2 is not None)):
    eprint("--pos1 and --pos2 must be specified (or neither specified)!")
    usage()

world = World(world_path)

log_handle = None
if logfile == "stdout":
    log_handle = sys.stdout
elif logfile == "stderr":
    log_handle = sys.stderr
elif logfile is not None:
    log_handle = open(logfile, 'w')

clean_replacements = []
for replacement in spawners_to_replace:
    if (
        replacement['rules'].get('mob_CustomName', None) is None
        and ('mob_HandItems' not in replacement['rules']
             or (replacement['rules']['mob_HandItems'] is not None and
                 replacement['rules']['mob_HandItems'][0] is None and
                 replacement['rules']['mob_HandItems'][1] is None))
    ):
        # Can only potentially replace if mob_CustomName or mob_HandItems rule is specified and valid
        print("!!! Can only potentially replace if mob_CustomName or mob_HandItems rule is specified and valid:")
        print(replacement)
        continue

    clean_replacements.append(replacement)

spawners_to_replace = clean_replacements

if dry_run:
    print("!!! Running in DRY RUN / READ ONLY mode")

replacements_log = {}
for entity, source_pos, entity_path in world.entity_iterator(pos1=pos1, pos2=pos2, readonly=dry_run):
    ### Update entities
    for replacement in spawners_to_replace:
        if not (
            entity.has_path('id')
            and entity.at_path('id').value == "minecraft:mob_spawner"
            and (
                entity.has_path('SpawnPotentials[0]')
                or entity.has_path('SpawnData')
            )
        ):
            # Not a valid spawner
            continue

        spawner_mobs = nbt.TagList([])
        if entity.has_path('SpawnPotentials[0]'):
            spawner_mobs.value += list(entity.at_path('SpawnPotentials').value)
        if entity.has_path('SpawnData'):
            spawner_mobs.value.append(entity.at_path('SpawnData'))

        # The spawner doesn't match if there are no mobs
        matches = False

        if interactive:
            variables = globals().copy()
            variables.update(locals())
            shell = code.InteractiveConsole(variables)
            shell.interact()

        for mob in spawner_mobs.value:
            if not mob.has_path('id'):
                continue

            # Assume a mob matches until proven otherwise
            matches = True

            if (
                replacement['rules'].get('mob_id', None) is not None
                # Already checked that mob has an ID
                and mob.at_path('id').value != replacement['rules']['mob_id']
            ):
                # This mob doesn't match; matches = False in case this was the last mob
                matches = False
                continue

            if (
                replacement['rules'].get('mob_CustomName', None) is not None
                and (
                    not mob.has_path('CustomName')
                    or parse_name_possibly_json(mob.at_path('CustomName').value) != replacement['rules']['mob_CustomName']
                )
            ):
                # This mob doesn't match; matches = False in case this was the last mob
                matches = False
                continue

            if 'mob_HandItems' in replacement['rules']:
                if replacement['rules']['mob_HandItems'] is not None and not mob.has_path('HandItems'):
                    # There is a non-none rule but the mob has no hand items - not a match
                    matches = False
                    continue

                if replacement['rules']['mob_HandItems'] is None and mob.has_path('HandItems'):
                    # Replacement specifies mob with no hand items but this mob has some - not a match
                    matches = False
                    continue

                if replacement['rules']['mob_HandItems'] is not None and mob.has_path('HandItems'):
                    hand_items = get_named_hand_items(entity)
                    if hand_items != replacement['rules']['mob_HandItems']:
                        # Replacement and mob both have hand items - but they don't match
                        matches = False
                        continue

        if not matches:
            continue

        # Replace this spawner
        log_handle.write("\n")
        log_handle.write("    MERGING:  {}\n".format(replacement['mojangson']))
        log_handle.write("    INTO:     {}\n".format(entity.to_mojangson()))
        log_handle.write("    AT:       {}\n".format(get_debug_string_from_entity_path(entity_path)))

        tag_to_merge = nbt.TagCompound.from_mojangson(replacement['mojangson'])
        entity.update(tag_to_merge)

        log_handle.write("    RESULT:   {}\n".format(entity.to_mojangson()))
        log_handle.write("\n")


if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
    log_handle.close()

eprint("Done")
