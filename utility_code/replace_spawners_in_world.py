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
            'id': 'minecraft:stray',
            'mob_CustomName': r'''Tutelary Spirit'''
        },
        'mojangson': r'''{MaxNearbyEntities:4s,RequiredPlayerRange:12s,SpawnCount:2s,SpawnData:{CustomName:"[{\"text\":\"Tutelary Spirit\"}]",Health:60.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:0,Name:"{\"text\":\"§aSoulleather Shoes\"}"},Enchantments:[{lvl:3s,id:"minecraft:depth_strider"}],AttributeModifiers:[{UUIDMost:7540933473533444898L,UUIDLeast:-6717788279730608685L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:0,Name:"{\"text\":\"§aSoulleather Robe\"}"},AttributeModifiers:[{UUIDMost:6471685917605186337L,UUIDLeast:-5725344995972228801L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:0,Name:"{\"text\":\"§aSoulleather Cloak\"}"},AttributeModifiers:[{UUIDMost:-7286025212327409021L,UUIDLeast:-6559093199055774268L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_helmet",Count:1b,tag:{display:{color:0,Name:"{\"text\":\"§aSoulleather Veil\"}"},AttributeModifiers:[{UUIDMost:-5667913726316558953L,UUIDLeast:-7987438630589365482L,Amount:0.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}}],Attributes:[{Base:60.0d,Name:"generic.maxHealth"},{Base:0.3d,Name:"generic.movementSpeed"},{Base:128.0d,Name:"generic.followRange"}],id:"minecraft:stray",Tags:["boss_hidden","boss_addarmor"],HandItems:[{id:"minecraft:stick",Count:1b,tag:{display:{Name:"{\"text\":\"§b§lThaumaturge\\u0027s Greed\"}"},AttributeModifiers:[{UUIDMost:-6890172516491706204L,UUIDLeast:-5786234737523425889L,Amount:13.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},MaxSpawnDelay:800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:400s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Tutelary Spirit\"}]",Health:60.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:0,Name:"{\"text\":\"§aSoulleather Shoes\"}"},Enchantments:[{lvl:3s,id:"minecraft:depth_strider"}],AttributeModifiers:[{UUIDMost:7540933473533444898L,UUIDLeast:-6717788279730608685L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:0,Name:"{\"text\":\"§aSoulleather Robe\"}"},AttributeModifiers:[{UUIDMost:6471685917605186337L,UUIDLeast:-5725344995972228801L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:0,Name:"{\"text\":\"§aSoulleather Cloak\"}"},AttributeModifiers:[{UUIDMost:-7286025212327409021L,UUIDLeast:-6559093199055774268L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_helmet",Count:1b,tag:{display:{color:0,Name:"{\"text\":\"§aSoulleather Veil\"}"},AttributeModifiers:[{UUIDMost:-5667913726316558953L,UUIDLeast:-7987438630589365482L,Amount:0.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}}],Attributes:[{Base:60.0d,Name:"generic.maxHealth"},{Base:0.3d,Name:"generic.movementSpeed"},{Base:128.0d,Name:"generic.followRange"}],id:"minecraft:stray",Tags:["boss_hidden","boss_addarmor"],HandItems:[{id:"minecraft:stick",Count:1b,tag:{display:{Name:"{\"text\":\"§b§lThaumaturge\\u0027s Greed\"}"},AttributeModifiers:[{UUIDMost:-6890172516491706204L,UUIDLeast:-5786234737523425889L,Amount:13.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:drowned',
            'mob_CustomName': r'''Water Wisp'''
        },
        'mojangson': r'''{MaxNearbyEntities:6s,RequiredPlayerRange:16s,SpawnCount:2s,SpawnData:{CustomName:"[{\"text\":\"Water Wisp\"}]",IsBaby:1b,Health:75.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1073407,Name:"{\"text\":\"§aNereid Sandals\"}"},Enchantments:[{lvl:3s,id:"minecraft:depth_strider"}],AttributeModifiers:[{UUIDMost:5225150667289477596L,UUIDLeast:-6080452553714319116L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:9885152,Name:"{\"text\":\"§fCerulean Mage Robes\"}"},AttributeModifiers:[{UUIDMost:-7330304342563666543L,UUIDLeast:-8247513943861980317L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"0b56e5b6-5db6-42fb-b394-90608ac8fcbe",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYmE1ODNmZGIxNmU0Mzk5ZDI4OGE2MmIzOTAxNzNjYWU0YzNiMjQxMGQ1ZDc0N2FlMTE5NDJlMGJjYjU2NjM1ZSJ9fX0="}]}}}}],Attributes:[{Base:75.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"},{Base:0.15d,Name:"generic.movementSpeed"}],id:"minecraft:drowned",Tags:["boss_weaponswitch","boss_invisible"],HandItems:[{id:"minecraft:trident",Count:1b,tag:{Enchantments:[{lvl:17s,id:"minecraft:sharpness"}]}},{id:"minecraft:stick",Count:1b,tag:{display:{Name:"{\"text\":\"§aWand of Storms\"}"},AttributeModifiers:[{UUIDMost:-6561687024932140307L,UUIDLeast:-7292955467971432668L,Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}}]},MaxSpawnDelay:800s,Delay:0s,SpawnRange:4s,MinSpawnDelay:200s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Water Wisp\"}]",IsBaby:1b,Health:75.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:1073407,Name:"{\"text\":\"§aNereid Sandals\"}"},Enchantments:[{lvl:3s,id:"minecraft:depth_strider"}],AttributeModifiers:[{UUIDMost:5225150667289477596L,UUIDLeast:-6080452553714319116L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:9885152,Name:"{\"text\":\"§fCerulean Mage Robes\"}"},AttributeModifiers:[{UUIDMost:-7330304342563666543L,UUIDLeast:-8247513943861980317L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"0b56e5b6-5db6-42fb-b394-90608ac8fcbe",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYmE1ODNmZGIxNmU0Mzk5ZDI4OGE2MmIzOTAxNzNjYWU0YzNiMjQxMGQ1ZDc0N2FlMTE5NDJlMGJjYjU2NjM1ZSJ9fX0="}]}}}}],Attributes:[{Base:75.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"},{Base:0.15d,Name:"generic.movementSpeed"}],id:"minecraft:drowned",Tags:["boss_weaponswitch","boss_invisible"],HandItems:[{id:"minecraft:trident",Count:1b,tag:{Enchantments:[{lvl:17s,id:"minecraft:sharpness"}]}},{id:"minecraft:stick",Count:1b,tag:{display:{Name:"{\"text\":\"§aWand of Storms\"}"},AttributeModifiers:[{UUIDMost:-6561687024932140307L,UUIDLeast:-7292955467971432668L,Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:drowned',
            'mob_CustomName': r'''Inundated Draugr'''
        },
        'mojangson': r'''{MaxNearbyEntities:4s,RequiredPlayerRange:12s,SpawnCount:2s,SpawnData:{CustomName:"[{\"text\":\"Inundated Draugr\"}]",Health:135.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:2502448,Name:"{\"text\":\"§fCloth Shoes\"}"},Enchantments:[{lvl:3s,id:"minecraft:depth_strider"}],AttributeModifiers:[{UUIDMost:8151891606044297994L,UUIDLeast:-7722334274888178576L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:2502448,Name:"{\"text\":\"§fCloth Pants\"}"},AttributeModifiers:[{UUIDMost:-4345728380504357153L,UUIDLeast:-6257690072762414707L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:2502448,Name:"{\"text\":\"§fCloth Shirt\"}"},AttributeModifiers:[{UUIDMost:-5517283433701489063L,UUIDLeast:-7776465610838995910L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"0f438f37-4166-4ce1-9b40-bfab16a7f29f",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvOTUzOWYyNjQ5ZDU0MWM2OGYzZDBmOWQzNzU4ZDkzYzdiYWFjMTcxZTRkNzA5MWE4NGQ4YTM2Mjg5MTQ4YjYyNSJ9fX0="}]}}}}],Attributes:[{Base:135.0d,Name:"generic.maxHealth"},{Base:0.35d,Name:"generic.movementSpeed"},{Base:128.0d,Name:"generic.followRange"}],id:"minecraft:drowned",HandItems:[{id:"minecraft:stone_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§3§lMithril Cleaver\"}"},Enchantments:[{lvl:1s,id:"minecraft:fire_aspect"},{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:-4189142210130457947L,UUIDLeast:-4974667142826157465L,Amount:17.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},MaxSpawnDelay:800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:400s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Inundated Draugr\"}]",Health:135.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:2502448,Name:"{\"text\":\"§fCloth Shoes\"}"},Enchantments:[{lvl:3s,id:"minecraft:depth_strider"}],AttributeModifiers:[{UUIDMost:8151891606044297994L,UUIDLeast:-7722334274888178576L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:2502448,Name:"{\"text\":\"§fCloth Pants\"}"},AttributeModifiers:[{UUIDMost:-4345728380504357153L,UUIDLeast:-6257690072762414707L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:2502448,Name:"{\"text\":\"§fCloth Shirt\"}"},AttributeModifiers:[{UUIDMost:-5517283433701489063L,UUIDLeast:-7776465610838995910L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"0f438f37-4166-4ce1-9b40-bfab16a7f29f",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvOTUzOWYyNjQ5ZDU0MWM2OGYzZDBmOWQzNzU4ZDkzYzdiYWFjMTcxZTRkNzA5MWE4NGQ4YTM2Mjg5MTQ4YjYyNSJ9fX0="}]}}}}],Attributes:[{Base:135.0d,Name:"generic.maxHealth"},{Base:0.35d,Name:"generic.movementSpeed"},{Base:128.0d,Name:"generic.followRange"}],id:"minecraft:drowned",HandItems:[{id:"minecraft:stone_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§3§lMithril Cleaver\"}"},Enchantments:[{lvl:1s,id:"minecraft:fire_aspect"},{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:-4189142210130457947L,UUIDLeast:-4974667142826157465L,Amount:17.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]},Weight:1}]}''',
    },
    {
        'rules': {
            'id': 'minecraft:drowned',
            'mob_CustomName': r'''Drowned Lancer'''
        },
        'mojangson': r'''{MaxNearbyEntities:4s,RequiredPlayerRange:12s,SpawnCount:2s,SpawnData:{CustomName:"[{\"text\":\"Drowned Lancer\"}]",Health:100.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:6252903,Name:"{\"text\":\"§fFur Boots\"}"},Enchantments:[{lvl:3s,id:"minecraft:depth_strider"}],AttributeModifiers:[{UUIDMost:5485816264229864503L,UUIDLeast:-8025614248440623879L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:7372155,Name:"{\"text\":\"§aPlaguehide Pants\"}"},AttributeModifiers:[{UUIDMost:-2740990636941029770L,UUIDLeast:-7105078174313552285L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:7372155,Name:"{\"text\":\"§a§lVinebound Tunic\"}"},AttributeModifiers:[{UUIDMost:-2860069127825963382L,UUIDLeast:-5813863396208373679L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"d11d3a37-8fcb-43e6-a46f-63ebd90f659e",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYzFhNzMyNTI0MDFhNmU5NDZmNjFkYmFjMGUwMjdkMTgzZTBhY2U1ODc1MmZhMTVhNjRkMjQ0OWZjZjUwODdiNyJ9fX0="}]}},display:{}}}],Attributes:[{Base:100.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"}],id:"minecraft:drowned",HandItems:[{id:"minecraft:trident",Count:1b,tag:{display:{Name:"{\"text\":\"Prismatic Pike\"}"},Enchantments:[{lvl:53s,id:"minecraft:sharpness"}]}},{}]},MaxSpawnDelay:800s,Delay:0s,SpawnRange:2s,MinSpawnDelay:400s,SpawnPotentials:[{Entity:{CustomName:"[{\"text\":\"Drowned Lancer\"}]",Health:100.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:6252903,Name:"{\"text\":\"§fFur Boots\"}"},Enchantments:[{lvl:3s,id:"minecraft:depth_strider"}],AttributeModifiers:[{UUIDMost:5485816264229864503L,UUIDLeast:-8025614248440623879L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:7372155,Name:"{\"text\":\"§aPlaguehide Pants\"}"},AttributeModifiers:[{UUIDMost:-2740990636941029770L,UUIDLeast:-7105078174313552285L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:7372155,Name:"{\"text\":\"§a§lVinebound Tunic\"}"},AttributeModifiers:[{UUIDMost:-2860069127825963382L,UUIDLeast:-5813863396208373679L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"d11d3a37-8fcb-43e6-a46f-63ebd90f659e",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYzFhNzMyNTI0MDFhNmU5NDZmNjFkYmFjMGUwMjdkMTgzZTBhY2U1ODc1MmZhMTVhNjRkMjQ0OWZjZjUwODdiNyJ9fX0="}]}},display:{}}}],Attributes:[{Base:100.0d,Name:"generic.maxHealth"},{Base:128.0d,Name:"generic.followRange"}],id:"minecraft:drowned",HandItems:[{id:"minecraft:trident",Count:1b,tag:{display:{Name:"{\"text\":\"Prismatic Pike\"}"},Enchantments:[{lvl:53s,id:"minecraft:sharpness"}]}},{}]},Weight:1}]}''',
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
