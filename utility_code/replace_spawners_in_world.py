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
            'mob_CustomName': r'''Land Guardian'''
        },
        'mojangson': r'''{MaxNearbyEntities:6s,RequiredPlayerRange:16s,SpawnCount:4s,SpawnData:{Health:20.0f,Attributes:[{Base:20.0d,Name:"generic.maxHealth"},{Base:32.0d,Name:"generic.followRange"},{Base:7.0d,Name:"generic.attackDamage"}],HandItems:[{},{}],CustomName:"{\"text\":\"Land Guardian\"}",WorldUUIDMost:-1041596277173696703L,ArmorItems:[{},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:2659451,Name:"{\"italic\":false,\"text\":\"land_guardian_chestplate\"}"},AttributeModifiers:[{UUIDMost:7343286061065781312L,UUIDLeast:-7821914282794956699L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"4005cac1-a16a-45aa-9e72-7fb514335717",Properties:{textures:[{Signature:"KioAh3QPaT8hPDYPstWRQtZm4jW9zP7yzcgoG2GVpRTnAaMrBBsPOK+TD53KqASmv30no8sIMbMd1lWla01Bq96a2HtiP0GYKgE0XYxe7e2WFv/4W9rpJv0Usf/YZiQKTlkZm/ixWZjhBbdyTML3jPLkOq8wDbPVHK7qRxx0TGGuslKlKfkmqgoYYMy3HhSsghbSv/Wpx5g65w2aqVKvJl26mMzdL70FW3x/6fSua1Z3GzFY3EHTAn3xGlQFAlA7l2nm6R1/OinCZ2BOIDJWQiPNmG4udWRZQcbl3vtR3SSiWe4vR2I060D4M7X6ntGFne27zpqxfSo+lXsgUbsU5vbNzeAGCmkQiXniTszVHSyP6tBT6peordjBza9LLLsnEj0g7Yb8c8aIS4D7sjQmB8xlc+JCBcjOiPY+SoXwNDGwfxaFqhYTAPLamLFWD1GcsJDPqG5VaatiWeGNDgzntkxPzZLRqSMQjNoT9EUSXaWSWDETaC92krkiG9LcEnX/iwllbisv3YbU1IGVoMo2bd2njcz8ggXjmAv7LmZd4nkXDgw7vGQyonw24+VpHt5KIb06I7dNxdq1iJ/tXf+89JWUALgRbMjNxYd3+jx4sdMw4xwgatGRx9WjQCLvWH0ENhriU5PEDqEWhCNo5x/BQ8iUAApDoz3CG6LB2p+Z5+0=",Value:"eyJ0aW1lc3RhbXAiOjE0OTk5NzU4NjA0MDUsInByb2ZpbGVJZCI6IjQwMDVjYWMxYTE2YTQ1YWE5ZTcyN2ZiNTE0MzM1NzE3IiwicHJvZmlsZU5hbWUiOiJNSEZfR3VhcmRpYW4iLCJzaWduYXR1cmVSZXF1aXJlZCI6dHJ1ZSwidGV4dHVyZXMiOnsiU0tJTiI6eyJ1cmwiOiJodHRwOi8vdGV4dHVyZXMubWluZWNyYWZ0Lm5ldC90ZXh0dXJlLzkzMmMyNDUyNGM4MmFiM2IzZTU3YzIwNTJjNTMzZjEzZGQ4YzBiZWI4YmRkMDYzNjliYjI1NTRkYTg2YzEyMyJ9fX0="}]},Name:"MHF_Guardian"},Enchantments:[{lvl:2s,id:"minecraft:thorns"}]}}],id:"minecraft:drowned",WorldUUIDLeast:-7560693509725274339L,ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:99999999,Id:14b,Amplifier:0b}]},MaxSpawnDelay:800s,Delay:0s,SpawnRange:6s,MinSpawnDelay:400s,SpawnPotentials:[{Entity:{Health:20.0f,Attributes:[{Base:20.0d,Name:"generic.maxHealth"},{Base:32.0d,Name:"generic.followRange"},{Base:7.0d,Name:"generic.attackDamage"}],HandItems:[{},{}],CustomName:"{\"text\":\"Land Guardian\"}",WorldUUIDMost:-1041596277173696703L,ArmorItems:[{},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:2659451,Name:"{\"italic\":false,\"text\":\"land_guardian_chestplate\"}"},AttributeModifiers:[{UUIDMost:7343286061065781312L,UUIDLeast:-7821914282794956699L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"4005cac1-a16a-45aa-9e72-7fb514335717",Properties:{textures:[{Signature:"KioAh3QPaT8hPDYPstWRQtZm4jW9zP7yzcgoG2GVpRTnAaMrBBsPOK+TD53KqASmv30no8sIMbMd1lWla01Bq96a2HtiP0GYKgE0XYxe7e2WFv/4W9rpJv0Usf/YZiQKTlkZm/ixWZjhBbdyTML3jPLkOq8wDbPVHK7qRxx0TGGuslKlKfkmqgoYYMy3HhSsghbSv/Wpx5g65w2aqVKvJl26mMzdL70FW3x/6fSua1Z3GzFY3EHTAn3xGlQFAlA7l2nm6R1/OinCZ2BOIDJWQiPNmG4udWRZQcbl3vtR3SSiWe4vR2I060D4M7X6ntGFne27zpqxfSo+lXsgUbsU5vbNzeAGCmkQiXniTszVHSyP6tBT6peordjBza9LLLsnEj0g7Yb8c8aIS4D7sjQmB8xlc+JCBcjOiPY+SoXwNDGwfxaFqhYTAPLamLFWD1GcsJDPqG5VaatiWeGNDgzntkxPzZLRqSMQjNoT9EUSXaWSWDETaC92krkiG9LcEnX/iwllbisv3YbU1IGVoMo2bd2njcz8ggXjmAv7LmZd4nkXDgw7vGQyonw24+VpHt5KIb06I7dNxdq1iJ/tXf+89JWUALgRbMjNxYd3+jx4sdMw4xwgatGRx9WjQCLvWH0ENhriU5PEDqEWhCNo5x/BQ8iUAApDoz3CG6LB2p+Z5+0=",Value:"eyJ0aW1lc3RhbXAiOjE0OTk5NzU4NjA0MDUsInByb2ZpbGVJZCI6IjQwMDVjYWMxYTE2YTQ1YWE5ZTcyN2ZiNTE0MzM1NzE3IiwicHJvZmlsZU5hbWUiOiJNSEZfR3VhcmRpYW4iLCJzaWduYXR1cmVSZXF1aXJlZCI6dHJ1ZSwidGV4dHVyZXMiOnsiU0tJTiI6eyJ1cmwiOiJodHRwOi8vdGV4dHVyZXMubWluZWNyYWZ0Lm5ldC90ZXh0dXJlLzkzMmMyNDUyNGM4MmFiM2IzZTU3YzIwNTJjNTMzZjEzZGQ4YzBiZWI4YmRkMDYzNjliYjI1NTRkYTg2YzEyMyJ9fX0="}]},Name:"MHF_Guardian"},Enchantments:[{lvl:2s,id:"minecraft:thorns"}]}}],id:"minecraft:drowned",WorldUUIDLeast:-7560693509725274339L,ActiveEffects:[{Ambient:1b,ShowIcon:1b,ShowParticles:1b,Duration:99999984,Id:14b,Amplifier:0b}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:drowned',
            'mob_CustomName': r'''Water Spirit'''
        },
        'mojangson': r'''{MaxNearbyEntities:12s,RequiredPlayerRange:16s,SpawnCount:10s,SpawnData:{IsBaby:1b,Health:10.0f,Attributes:[{Base:10.0d,Name:"generic.maxHealth"},{Base:0.18d,Modifiers:[{UUIDMost:-5082757096938257406L,UUIDLeast:-4891139119377885130L,Amount:0.5d,Operation:1,Name:"Baby speed boost"}],Name:"generic.movementSpeed"},{Base:32.0d,Name:"generic.followRange"}],HandItems:[{id:"minecraft:diamond_hoe",Count:1b,tag:{HideFlags:1,display:{Name:"{\"italic\":false,\"text\":\"Aqueous Scythe\"}"},Enchantments:[{lvl:1s,id:"minecraft:aqua_affinity"}],AttributeModifiers:[{UUIDMost:-6299659404845825479L,UUIDLeast:-7746443255638769651L,Amount:3.5d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{id:"minecraft:diamond_hoe",Count:1b,tag:{HideFlags:1,Enchantments:[{lvl:1s,id:"minecraft:aqua_affinity"}],AttributeModifiers:[{UUIDMost:462633899168646156L,UUIDLeast:-6256128536084544333L,Amount:0.0d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}}],CustomName:"{\"text\":\"Water Spirit\"}",WorldUUIDMost:-1041596277173696703L,ArmorItems:[{},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:33023,Name:"{\"italic\":false,\"text\":\"water_spirit_chestplate\"}"},AttributeModifiers:[{UUIDMost:-5799195600123901260L,UUIDLeast:-4717379432341202162L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"0b582b1b-8de8-4b5f-bfc6-d2585b318186",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvNWM3ZWNiZmQ2ZDMzZTg3M2ExY2Y5YTkyZjU3ZjE0NjE1MmI1MmQ5ZDczMTE2OTQ2MDI2NzExMTFhMzAyZiJ9fX0="}]}}}}],id:"minecraft:drowned",WorldUUIDLeast:-7560693509725274339L,ActiveEffects:[{Ambient:0b,ShowIcon:0b,ShowParticles:0b,Duration:99999999,Id:14b,Amplifier:0b}]},MaxSpawnDelay:400s,Delay:0s,SpawnRange:6s,MinSpawnDelay:350s,SpawnPotentials:[{Entity:{IsBaby:1b,Health:10.0f,Attributes:[{Base:10.0d,Name:"generic.maxHealth"},{Base:0.18d,Modifiers:[{UUIDMost:-5082757096938257406L,UUIDLeast:-4891139119377885130L,Amount:0.5d,Operation:1,Name:"Baby speed boost"}],Name:"generic.movementSpeed"},{Base:32.0d,Name:"generic.followRange"}],HandItems:[{id:"minecraft:diamond_hoe",Count:1b,tag:{HideFlags:1,display:{Name:"{\"italic\":false,\"text\":\"Aqueous Scythe\"}"},Enchantments:[{lvl:1s,id:"minecraft:aqua_affinity"}],AttributeModifiers:[{UUIDMost:-6299659404845825479L,UUIDLeast:-7746443255638769651L,Amount:3.5d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{id:"minecraft:diamond_hoe",Count:1b,tag:{HideFlags:1,Enchantments:[{lvl:1s,id:"minecraft:aqua_affinity"}],AttributeModifiers:[{UUIDMost:462633899168646156L,UUIDLeast:-6256128536084544333L,Amount:0.0d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}}],CustomName:"{\"text\":\"Water Spirit\"}",WorldUUIDMost:-1041596277173696703L,ArmorItems:[{},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:33023,Name:"{\"italic\":false,\"text\":\"water_spirit_chestplate\"}"},AttributeModifiers:[{UUIDMost:-5799195600123901260L,UUIDLeast:-4717379432341202162L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"0b582b1b-8de8-4b5f-bfc6-d2585b318186",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvNWM3ZWNiZmQ2ZDMzZTg3M2ExY2Y5YTkyZjU3ZjE0NjE1MmI1MmQ5ZDczMTE2OTQ2MDI2NzExMTFhMzAyZiJ9fX0="}]}}}}],id:"minecraft:drowned",WorldUUIDLeast:-7560693509725274339L,ActiveEffects:[{Ambient:0b,ShowIcon:0b,ShowParticles:0b,Duration:99999999,Id:14b,Amplifier:0b}]},Weight:1}]}''',
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
