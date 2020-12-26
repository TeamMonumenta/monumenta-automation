#!/usr/bin/env python3

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
            'id': 'minecraft:silverfish',
            'mob_CustomName': r'''Firefish'''
        },
        'mojangson': r'''{MaxNearbyEntities:6s,RequiredPlayerRange:12s,SpawnCount:1s,SpawnData:{CustomName:"{\"text\":\"Firefish\"}",Health:30.0f,Fire:9999s,Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],id:"minecraft:silverfish",ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:8640000,Id:12b,Amplifier:0b}],Tags:["boss_infested"],HandItems:[{id:"minecraft:diamond_sword",Count:1b,tag:{Enchantments:[{lvl:1s,id:"minecraft:fire_aspect"}],AttributeModifiers:[{UUIDMost:-1609236631565678652L,UUIDLeast:-7544331711960737524L,Amount:6.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-3802968361034625470L,UUIDLeast:-8795518285071425824L,Amount:0.2d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{}]},MaxSpawnDelay:800s,Delay:0s,SpawnRange:4s,MinSpawnDelay:200s,SpawnPotentials:[{Entity:{CustomName:"{\"text\":\"Firefish\"}",Health:30.0f,Fire:9999s,Attributes:[{Base:30.0d,Name:"generic.maxHealth"}],id:"minecraft:silverfish",ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:8640000,Id:12b,Amplifier:0b}],Tags:["boss_infested"],HandItems:[{id:"minecraft:diamond_sword",Count:1b,tag:{Enchantments:[{lvl:1s,id:"minecraft:fire_aspect"}],AttributeModifiers:[{UUIDMost:-1609236631565678652L,UUIDLeast:-7544331711960737524L,Amount:6.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-3802968361034625470L,UUIDLeast:-8795518285071425824L,Amount:0.2d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}},{}]},Weight:1}]}''',
    },
]


def usage():
    sys.exit("Usage: {} <--world /path/to/world> [--logfile <stdout|stderr|path>] [--pos1 x,y,z --pos2 x,y,z] [--dry-run]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:l:d", ["world=", "logfile=", "pos1=", "pos2=", "dry-run"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
logfile = 'stdout'
dry_run = False
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
