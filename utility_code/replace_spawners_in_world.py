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
            'id': 'minecraft:drowned',
            'mob_CustomName': r'''Camouflaged Swarmer'''
        },
        'mojangson': r'''{MaxNearbyEntities:4s,RequiredPlayerRange:12s,SpawnCount:5s,SpawnData:{CustomName:"[{\"text\":\"Camouflaged Swarmer\"}]",IsBaby:1b,Health:45.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:8737041,Name:"{\"text\":\"§fLeafweave Sandals\"}"},AttributeModifiers:[{UUIDMost:-382133999706684619L,UUIDLeast:-6317337915334863574L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:8737041,Name:"{\"text\":\"§fLeafweave Trousers\"}"},AttributeModifiers:[{UUIDMost:859917323600545817L,UUIDLeast:-8778870212998811052L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:chainmail_chestplate",Count:1b,tag:{display:{Name:"{\"text\":\"§2§lLeafveil Shroud\"}"},AttributeModifiers:[{UUIDMost:8219733933951370485L,UUIDLeast:-5084087028162377544L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:jungle_leaves",Count:1b}],Attributes:[{Base:45.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"},{Base:0.21d,Name:"generic.movementSpeed"}],id:"minecraft:drowned",HandItems:[{id:"minecraft:wooden_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§fLiving Thorn\"}"},AttributeModifiers:[{UUIDMost:-3881071891453163442L,UUIDLeast:-4702150977003512039L,Amount:12.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},MaxSpawnDelay:800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:400s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Camouflaged Swarmer\"}]",IsBaby:1b,Health:45.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:8737041,Name:"{\"text\":\"§fLeafweave Sandals\"}"},AttributeModifiers:[{UUIDMost:-382133999706684619L,UUIDLeast:-6317337915334863574L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:8737041,Name:"{\"text\":\"§fLeafweave Trousers\"}"},AttributeModifiers:[{UUIDMost:859917323600545817L,UUIDLeast:-8778870212998811052L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:chainmail_chestplate",Count:1b,tag:{display:{Name:"{\"text\":\"§2§lLeafveil Shroud\"}"},AttributeModifiers:[{UUIDMost:8219733933951370485L,UUIDLeast:-5084087028162377544L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:jungle_leaves",Count:1b}],Attributes:[{Base:45.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"},{Base:0.21d,Name:"generic.movementSpeed"}],id:"minecraft:drowned",HandItems:[{id:"minecraft:wooden_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§fLiving Thorn\"}"},AttributeModifiers:[{UUIDMost:-3881071891453163442L,UUIDLeast:-4702150977003512039L,Amount:12.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:phantom',
            'mob_CustomName': r'''Bloated Phantom'''
        },
        'mojangson': r'''{MaxNearbyEntities:4s,RequiredPlayerRange:12s,SpawnCount:5s,SpawnData:{Passengers:[{CustomName:"[{\"text\":\"Bloated Phantom\"}]",Health:27.0f,Size:2,Attributes:[{Base:27.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"}],id:"minecraft:phantom",HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{display:{Name:"[{\"text\":\"Swift Bite\",\"italic\":false}]"},AttributeModifiers:[{UUIDMost:7760838378018586847L,UUIDLeast:-6265449433678749048L,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}],Health:1.0f,Attributes:[{Base:1.0d,Name:"generic.maxHealth"}],Silent:1b,id:"minecraft:vex",ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:20b,Amplifier:4b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:14b,Amplifier:0b}]},MaxSpawnDelay:800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:400s,SpawnPotentials:[{Entity:{Passengers:[{CustomName:"[{\"text\":\"Bloated Phantom\"}]",Health:27.0f,Size:2,Attributes:[{Base:27.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"}],id:"minecraft:phantom",HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{display:{Name:"[{\"text\":\"Swift Bite\",\"italic\":false}]"},AttributeModifiers:[{UUIDMost:7760838378018586847L,UUIDLeast:-6265449433678749048L,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}],Health:1.0f,Attributes:[{Base:1.0d,Name:"generic.maxHealth"}],Silent:1b,id:"minecraft:vex",ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:20b,Amplifier:4b},{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:100,Id:14b,Amplifier:0b}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:silverfish',
            'mob_CustomName': r'''Unyielding Silverfish'''
        },
        'mojangson': r'''{MaxNearbyEntities:4s,RequiredPlayerRange:12s,SpawnCount:5s,SpawnData:{CustomName:"[{\"text\":\"Unyielding Silverfish\"}]",Health:54.0f,Attributes:[{Base:54.0d,Name:"generic.maxHealth"},{Base:1.0d,Name:"generic.knockbackResistance"},{Base:128.0d,Name:"generic.followRange"}],id:"minecraft:silverfish",HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{display:{Name:"{\"italic\":false,\"text\":\"Grave Nibble\"}"},AttributeModifiers:[{UUIDMost:521411499802511775L,UUIDLeast:-7101535124109311188L,Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},MaxSpawnDelay:800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:400s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Unyielding Silverfish\"}]",Health:54.0f,Attributes:[{Base:54.0d,Name:"generic.maxHealth"},{Base:1.0d,Name:"generic.knockbackResistance"},{Base:128.0d,Name:"generic.followRange"}],id:"minecraft:silverfish",HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{display:{Name:"{\"italic\":false,\"text\":\"Grave Nibble\"}"},AttributeModifiers:[{UUIDMost:521411499802511775L,UUIDLeast:-7101535124109311188L,Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:ocelot',
            'mob_CustomName': r'''Rabid Ocelot'''
        },
        'mojangson': r'''{MaxNearbyEntities:4s,RequiredPlayerRange:12s,SpawnCount:5s,SpawnData:{AgeLocked:1b,CustomName:"[{\"text\":\"Rabid Ocelot\"}]",Health:45.0f,Attributes:[{Base:45.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"},{Base:0.2d,Name:"generic.movementSpeed"}],id:"minecraft:ocelot",Tags:["boss_targetplayer"],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{display:{Name:"{\"italic\":false,\"text\":\"Fangs\"}"},AttributeModifiers:[{UUIDMost:-8960180552131130808L,UUIDLeast:-5455308468062322858L,Amount:5.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},MaxSpawnDelay:800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:400s,SpawnPotentials:[{Entity:{AgeLocked:1b,CustomName:"[{\"text\":\"Rabid Ocelot\"}]",Health:45.0f,Attributes:[{Base:45.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"},{Base:0.2d,Name:"generic.movementSpeed"}],id:"minecraft:ocelot",Tags:["boss_targetplayer"],HandItems:[{id:"minecraft:golden_sword",Count:1b,tag:{display:{Name:"{\"italic\":false,\"text\":\"Fangs\"}"},AttributeModifiers:[{UUIDMost:-8960180552131130808L,UUIDLeast:-5455308468062322858L,Amount:5.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},Weight:1}]}''',
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

def recurse_add_mob(lst, entity):
    if entity.has_path('SpawnPotentials[0]'):
        lst.value += list(entity.at_path('SpawnPotentials').value)
        for mob in entity.at_path('SpawnPotentials').value:
            recurse_add_mob(lst, mob)
    if entity.has_path('SpawnData'):
        lst.value.append(entity.at_path('SpawnData'))
        recurse_add_mob(lst, entity.at_path('SpawnData'))
    if entity.has_path('Passengers[0]'):
        lst.value += list(entity.at_path('Passengers').value)
        for mob in entity.at_path('Passengers').value:
            recurse_add_mob(lst, mob)

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
        recurse_add_mob(spawner_mobs, entity)

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
