#!/usr/bin/env python3

# For interactive shell
import readline
import code

import sys
import os
import getopt

from lib_py3.mob_replacement_manager import MobReplacementManager, remove_unwanted_spawner_tags
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path
from lib_py3.common import eprint
from lib_py3.world import World
from lib_py3.library_of_souls import LibraryOfSouls
from lib_py3.schematic import Schematic

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

def is_entity_in_spawner(entity_path: [nbt.TagCompound]) -> bool:
    contains_spawner = False
    last = False
    for element in entity_path:
        if element.has_path("SpawnPotentials"):
            contains_spawner = True
            last = True
        else:
            last = False

    return contains_spawner and not last

custom_replace_rules_for_later = [
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'HandItems': ["'§fEnraged Captain's Axe'", "'§bHawk's Talon'"],
        },
        'mojangson': r'''{id:"minecraft:skeleton",CustomName:"{\"text\":\"§6Lighthouse Defender\"}",Health:75.0f,ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:4521728,Name:"{\"text\":\"§2§lBoots of Vitality\"}"}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:10506272,Name:"{\"text\":\"§aHardened Leather Pants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:10506272,Name:"{\"text\":\"§aHardened Leather Tunic\"}"}}},{}],Attributes:[{Base:75.0d,Name:"generic.maxHealth"}],Tags:["Elite","boss_weaponswitch","boss_charger"],HandItems:[{id:"minecraft:iron_axe",Count:1b,tag:{display:{Name:"{\"text\":\"§fEnraged Captain\\u0027s Axe\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"},{lvl:1s,id:"minecraft:sharpness"}],Damage:0}},{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§bHawk\\u0027s Talon\"}"},Enchantments:[{lvl:3s,id:"minecraft:power"}],Damage:0}}]}''',
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
            'id': 'minecraft:wither_skeleton',
            # Note this typo'd name!
            'CustomName': '6Frost Moon Brute'
        },
        'mojangson': r'''{id:"minecraft:wither_skeleton",Health:100.0f,Attributes:[{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.5d,Name:"generic.knockbackResistance"},{Base:100.0d,Name:"generic.maxHealth"},{Base:32.0d,Name:"generic.followRange"}],LeftHanded:1b,OnGround:1b,HandItems:[{id:"minecraft:iron_sword",Count:1b,tag:{display:{Name:"{\"italic\":false,\"text\":\"Dual Frost Greatsword\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:-3834667671152932107L,UUIDLeast:-6852958939107637417L,Amount:17.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{id:"minecraft:iron_sword",Count:1b,tag:{display:{Name:"{\"italic\":false,\"text\":\"Dual Frost Greatsword\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:-3834667671152932107L,UUIDLeast:-6852958939107637417L,Amount:17.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}}],CustomName:"[{\"text\":\"Frost Moon Brute\",\"color\":\"gold\"}]",ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:60395,Name:"{\"text\":\"F.B\"}"},AttributeModifiers:[{UUIDMost:31492316112044816L,UUIDLeast:-8556528064959196441L,Amount:0.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:60395,Name:"{\"text\":\"F.L\"}"},AttributeModifiers:[{UUIDMost:2502059920319923451L,UUIDLeast:-7340807275252271259L,Amount:0.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:60395,Name:"{\"text\":\"F.C\"}"},AttributeModifiers:[{UUIDMost:7253508311050896534L,UUIDLeast:-8328577651339812818L,Amount:0.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}},{id:"minecraft:player_head",Count:1b,tag:{SkullOwner:{Id:"0c3eedc4-a350-439c-8489-af2a768bdc41",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvNjE2ZjdkYjY3YTcyM2Q1YzMwYmY5ZDQ3ZWQ2YzI4YmY3ZDQzNmQ4ODZlMGYzNTk1MTAzMzY4MTk5ZTNhMTliYiJ9fX0="}]}}}}],PersistenceRequired:0b,Tags:["Elite","boss_charger"]}''',
    },
    {
        'rules': {
            # Spelled wrong
            'id': 'minecraft:ghast',
            'CustomName': 'Dessicated Ghast'
        },
        'mojangson': r'''{id:"minecraft:ghast",CustomName:"[{\"text\":\"Desiccated Ghast\"}]",Health:25.0f,Attributes:[{Base:25.0d,Name:"generic.maxHealth"}],ExplosionPower:2}''',
    },
    {
        'rules': {
            'id': 'minecraft:skeleton',
            'HandItems': ["'§fViridian Hunter'", None],
        },
        'mojangson': r'''{id:"minecraft:skeleton",Attributes:[{Base:30.0d,Name:"generic.maxHealth"},{Base:0.0d,Name:"generic.knockbackResistance"},{Base:0.25d,Name:"generic.movementSpeed"},{Base:0.0d,Name:"generic.armor"},{Base:0.0d,Name:"generic.armorToughness"},{Base:16.0d,Name:"generic.followRange"},{Base:2.0d,Name:"generic.attackDamage"}],Invulnerable:0b,PersistenceRequired:0b,Team:"mobs",Health:30.0f,HandItems:[{id:"minecraft:bow",Count:1b,tag:{display:{Name:"{\"text\":\"§fViridian Hunter\"}"},Enchantments:[{lvl:4s,id:"minecraft:power"}]}},{}]}''',
    },
]

def usage():
    sys.exit("Usage: {} <--world /path/to/world | --schematics /path/to/schematics> <--library-of-souls /path/to/library-of-souls.json> [--logfile <stdout|stderr|path>] [--dry-run]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:s:b:l:di", ["world=", "schematics=", "library-of-souls=", "logfile=", "dry-run"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
schematics_path = None
library_of_souls_path = None
logfile = 'stdout'
dry_run = False

for o, a in opts:
    if o in ("-w", "--world"):
        world_path = a
    elif o in ("-s", "--schematics"):
        schematics_path = a
    elif o in ("-b", "--library-of-souls"):
        library_of_souls_path = a
    elif o in ("-l", "--logfile"):
        logfile = a
    elif o in ("-d", "--dry-run"):
        dry_run = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None and schematics_path is None:
    eprint("--world or --schematics must be specified!")
    usage()
elif library_of_souls_path is None:
    eprint("--library-of-souls must be specified!")
    usage()

los = LibraryOfSouls(library_of_souls_path, readonly=True)
replace_mgr = MobReplacementManager()
los.load_replacements(replace_mgr)

log_handle = None
if logfile == "stdout":
    log_handle = sys.stdout
elif logfile == "stderr":
    log_handle = sys.stderr
elif logfile is not None:
    log_handle = open(logfile, 'w')

replacements_log = {}

mobs_replaced = 0
try:
    # This is handy here because it has direct access to previously defined globals
    def process_entity(entity: nbt.TagCompound, source_pos, entity_path: [nbt.TagCompound], debug_path="") -> None:
        global mobs_replaced

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


        if is_entity_in_spawner(entity_path):
            remove_unwanted_spawner_tags(entity)
            if replace_mgr.replace_mob(entity, replacements_log, debug_path + get_debug_string_from_entity_path(entity_path)):
                mobs_replaced += 1

    if world_path:
        world = World(world_path)
        debug_path = os.path.basename(world_path) + " -> "
        for entity, source_pos, entity_path in world.entity_iterator(readonly=dry_run):
            process_entity(entity, source_pos, entity_path, debug_path=debug_path)

    if schematics_path:
        for root, subdirs, files in os.walk(schematics_path):
            for fname in files:
                if fname.endswith(".schematic"):
                    debug_path = fname + " -> "
                    schem = Schematic(os.path.join(root, fname))
                    for entity, source_pos, entity_path in schem.entity_iterator(readonly=dry_run):
                        process_entity(entity, source_pos, entity_path, debug_path=debug_path)

                    if not dry_run:
                        schem.save()

    print("{} mobs replaced".format(mobs_replaced))

finally:
    if log_handle is not None:
        for to_mob in replacements_log:
            log_handle.write("{}\n".format(to_mob))
            log_handle.write("    TO:\n")
            log_handle.write("        {}\n".format(replacements_log[to_mob]["TO"]))
            log_handle.write("    FROM:\n")

            for from_mob in replacements_log[to_mob]["FROM"]:
                log_handle.write("        {}\n".format(from_mob))

                for from_location in sorted(replacements_log[to_mob]["FROM"][from_mob]):
                    log_handle.write("            {}\n".format(from_location))

            log_handle.write("\n")

    if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
        log_handle.close()
