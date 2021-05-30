#!/usr/bin/env python3

import math
import sys
import os
import getopt
import yaml
import multiprocessing
import traceback

from lib_py3.mob_replacement_manager import MobReplacementManager, remove_unwanted_spawner_tags
from lib_py3.common import eprint, get_entity_name_from_nbt, get_named_hand_items, get_named_armor_items, get_named_hand_item_ids, get_named_armor_item_ids
from lib_py3.library_of_souls import LibraryOfSouls
from lib_py3.timing import Timings

from minecraft.chunk_format.schematic import Schematic
from minecraft.chunk_format.structure import Structure
from minecraft.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

def is_entity_in_spawner(entity) -> bool:
    # Start at the node above this one and iterate upwards
    node = entity.parent
    while node is not None:
        if node.nbt.has_path("SpawnPotentials"):
            return True
        node = node.parent

    return False

def match_id(target_id: str, chain=lambda mob: True):
    return lambda mob : chain(mob) and ((mob.has_path("id") and mob.at_path("id").value == target_id) or (mob.has_path("Id") and mob.at_path("Id").value == target_id))

def match_armor(armor: [str], chain=lambda mob: True):
    return lambda mob : chain(mob) and get_named_armor_items(mob) == armor

def match_armor_ids(armor_ids: [str], chain=lambda mob: True):
    return lambda mob : chain(mob) and get_named_armor_item_ids(mob) == armor_ids

def match_noarmor(chain=lambda mob: True):
    return lambda mob : chain(mob) and (not mob.has_path('ArmorItems'))

def match_hand(hand: [str], chain=lambda mob: True):
    return lambda mob : chain(mob) and get_named_hand_items(mob) == hand

def match_hand_ids(hand_ids: [str], chain=lambda mob: True):
    return lambda mob : chain(mob) and get_named_hand_item_ids(mob) == hand_ids

def match_nohand(chain=lambda mob: True):
    return lambda mob : chain(mob) and (not mob.has_path('HandItems'))

def match_name(name: str, chain=lambda mob: True):
    return lambda mob : chain(mob) and mob.has_path('CustomName') and get_entity_name_from_nbt(mob) == name

def match_noname(chain=lambda mob: True):
    return lambda mob : chain(mob) and (not mob.has_path('CustomName'))

# Matches health to within += 1.0
def match_hp(hp: float, chain=lambda mob: True):
    return lambda mob : chain(mob) and mob.has_path('Health') and math.isclose(mob.at_path('Health').value, hp, abs_tol=1.0)

def match_passenger(host_chain, passenger_chain):
    return lambda mob : (host_chain(mob)
            and mob.has_path('Passengers')
            and mob.count_multipath('Passengers[]') >= 1
            and passenger_chain(mob.at_path('Passengers[0]')))

# Note that these will be evaluated last to first - so put more broad checks first for performance
sub = [
    # Unnamed R2 mobs
    ('Departed Seafarer', match_passenger(match_id('minecraft:guardian'), match_noname(match_id('minecraft:drowned', match_armor_ids(["minecraft:chainmail_boots", "minecraft:string", "minecraft:chainmail_chestplate", None]))))),
    ('Departed Seafarer', match_noname(match_id('minecraft:drowned', match_armor_ids(["minecraft:chainmail_boots", "minecraft:string", "minecraft:chainmail_chestplate", None])))),
    ('Twilight Gryphon', match_passenger(match_id('minecraft:vex'), match_passenger(match_id('minecraft:phantom'), match_id('minecraft:zombie_villager', match_name('Twilight Rider'))))),
    ('Sky Screecher', match_passenger(match_id('minecraft:vex'), match_noname(match_id('minecraft:phantom', match_armor(["Generic phantom 1", None, None, None]))))),

    # Piglin conversion
    ('Molten Citizen', match_id('minecraft:zombified_piglin', match_name('Molten Citizen'))),

    # Rename mobs
    ('Jaguar Berserker', match_id('minecraft:zombie', match_name('Jaguar Berzerker'))),
    ('Aurian Priest', match_id('minecraft:evoker', match_name('Priest of The Moon'))),
    ('Soaked Ghoul', match_id('minecraft:drowned', match_name('Ghoul'))),

    # Mobs on insta-die trash
    ("Rusted Gear", match_passenger(match_id('minecraft:guardian'), match_name('Rusted Gear', match_id('minecraft:drowned')))),
    ("Frost Wisp", match_passenger(match_id('minecraft:silverfish'), match_name('Frost Wisp', match_id('minecraft:stray')))),
    ("Ice Archer", match_passenger(match_id('minecraft:silverfish'), match_name('Ice Archer', match_id('minecraft:stray')))),
    ("Guardian Brawler", match_passenger(match_id('minecraft:silverfish'), match_name('Guardian Brawler', match_id('minecraft:drowned')))),
    ("Spirit of the Drowned", match_passenger(match_id('minecraft:silverfish'), match_name('Spirit of the Drowned', match_id('minecraft:drowned')))),
    ("Flame Imp", match_passenger(match_id('minecraft:silverfish'), match_name('Flame Imp', match_id('minecraft:zombie')))),
    ("Flaming Archer", match_passenger(match_id('minecraft:silverfish'), match_name('Flaming Archer', match_id('minecraft:skeleton')))),
    ("Scorchguard", match_passenger(match_id('minecraft:silverfish'), match_name('Scorchguard', match_id('minecraft:wither_skeleton')))),
    ("Petrified Archer", match_passenger(match_id('minecraft:silverfish'), match_name('Petrified Archer', match_id('minecraft:skeleton')))),
    ("Mutated Dolphin", match_passenger(match_id('minecraft:guardian'), match_name('Mutated Dolphin', match_id('minecraft:dolphin')))),
    ("Delphinus Guardian", match_passenger(match_id('minecraft:guardian'), match_name('Delphinus Guardian', match_id('minecraft:dolphin')))),
    ("Frost Moon Retiarius", match_passenger(match_id('minecraft:silverfish'), match_name('Frost Moon Retiarius', match_id('minecraft:drowned')))),
    ("Ghoul", match_passenger(match_id('minecraft:silverfish'), match_name('Ghoul', match_id('minecraft:drowned')))),
    ("Raging Minotaur", match_passenger(match_id('minecraft:silverfish'), match_name('Raging Minotaur', match_id('minecraft:drowned')))),
    ("Bloodraven", match_passenger(match_id('minecraft:vex'), match_name('Bloodraven', match_id('minecraft:phantom')))),
    ("Hungry Dolphin", match_passenger(match_id('minecraft:guardian'), match_name('Hungry Dolphin', match_id('minecraft:dolphin')))),
    ("Rosebud Golem", match_passenger(match_id('minecraft:endermite'), match_name('Rosebud Golem', match_id('minecraft:iron_golem')))),
    ("Twilight Construct", match_passenger(match_id('minecraft:silverfish'), match_name('Twilight Construct', match_id('minecraft:iron_golem')))),
    ("Frost Golem", match_passenger(match_id('minecraft:silverfish'), match_name('Frost Golem', match_id('minecraft:iron_golem')))),
    ("Rabid Wolf", match_passenger(match_id('minecraft:silverfish'), match_name('Rabid Wolf', match_id('minecraft:wolf')))),

    # TODO: Re-enable when stacked mobs are fixed
    #("Cherry Boomsom", match_name('Cheery Boomsome', match_id('minecraft:creeper'))),
    ("Monstrous Arachnid", match_name('Monsterous Arachnid', match_id('minecraft:spider'))),
    ("Archaic Guardian", match_name('Ancient Guardian', match_id('minecraft:wither_skeleton'))),

    # Orange
    ("Savage Jaguar", match_name('Fern Warrior', match_id('minecraft:zombie'))),
    ("Serpensia Corpse", match_name('Serpentsia Corpse', match_id('minecraft:wither_skeleton'))),
    ("Savage Hawk", match_name('Fern Archer', match_id('minecraft:skeleton'))),

    # Misc
    ("Animated Algae", match_name('Animated Algae', match_id('minecraft:creeper'))),
]

def usage():
    sys.exit("Usage: {} <--world /path/to/world | --schematics /path/to/schematics | --structures /path/to/structures> <--library-of-souls /path/to/library-of-souls.json> [--pos1 x,y,z --pos2 x,y,z] [--logfile <stdout|stderr|path>] [--num-threads num] [--dry-run] [--force]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:s:g:b:l:j:dif", ["world=", "schematics=", "structures=", "library-of-souls=", "logfile=", "num-threads=", "dry-run", "pos1=", "pos2=", "force"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
schematics_path = None
structures_path = None
library_of_souls_path = None
pos1 = [-math.inf, -math.inf, -math.inf]
pos2 = [math.inf, math.inf, math.inf]
logfile = None
num_threads = 4
dry_run = False
force = False

for o, a in opts:
    if o in ("-w", "--world"):
        world_path = a
    elif o in ("-s", "--schematics"):
        schematics_path = a
    elif o in ("-s", "--structures"):
        structures_path = a
    elif o in ("-b", "--library-of-souls"):
        library_of_souls_path = a
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
    elif o in ("-l", "--logfile"):
        logfile = a
    elif o in ("-j", "--num-threads"):
        num_threads = int(a)
    elif o in ("-d", "--dry-run"):
        dry_run = True
    elif o in ("-f", "--force"):
        force = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None and schematics_path is None and structures_path is None:
    eprint("--world, --schematics, or --structures must be specified!")
    usage()
elif library_of_souls_path is None:
    eprint("--library-of-souls must be specified!")
    usage()

timings = Timings(enabled=dry_run)
los = LibraryOfSouls(library_of_souls_path, readonly=True)
timings.nextStep("Loaded Library of Souls")
replace_mgr = MobReplacementManager()
los.load_replacements(replace_mgr)
replace_mgr.add_substitutions(sub, force_add_ignoring_conflicts=force)
timings.nextStep("Loaded mob replacement manager")

log_handle = None
if logfile == "stdout":
    log_handle = sys.stdout
elif logfile == "stderr":
    log_handle = sys.stderr
elif logfile is not None:
    log_handle = open(logfile, 'w')

# This is handy here because it has direct access to previously defined globals
def process_entity(entity, replacements_log) -> None:
    nbt = entity.nbt
    if nbt.has_path("Delay"):
        nbt.at_path("Delay").value = 0

        # Remove pigs
        if nbt.has_path('SpawnPotentials'):
            new_potentials = []
            for nested_entity in nbt.iter_multipath('SpawnPotentials[]'):
                if (nested_entity.has_path('nbt.id') and nested_entity.at_path('nbt.id').value == "minecraft:pig") or (nested_entity.has_path('nbt.Id') and nested_entity.at_path('nbt.Id').value == "minecraft:pig"):
                    if log_handle is not None:
                        log_handle.write(f"Removing pig from SpawnPotentials at {entity.get_path_str()}\n")
                else:
                    new_potentials.append(nested_entity)
            nbt.at_path('SpawnPotentials').value = new_potentials
        if (nbt.has_path("SpawnData.id") and nbt.at_path("SpawnData.id").value == "minecraft:pig") or (nbt.has_path("SpawnData.Id") and nbt.at_path("SpawnData.Id").value == "minecraft:pig"):
            if log_handle is not None:
                log_handle.write(f"Removing pig Spawndata at {entity.get_path_str()}\n")
            nbt.value.pop("SpawnData")

    if is_entity_in_spawner(entity):
        remove_unwanted_spawner_tags(nbt)
        return replace_mgr.replace_mob(nbt, replacements_log, entity.get_path_str())

def process_region(region):
    replacements_log = {}
    num_replacements = 0
    for chunk in region.iter_chunks(autosave=(not dry_run)):
        for entity in chunk.recursive_iter_entities():
            if process_entity(entity, replacements_log):
                num_replacements += 1

    return (num_replacements, replacements_log)

def process_schematic(schem_path):
    replacements_log = {}
    num_replacements = 0

    try:
        schem = Schematic(schem_path)
        for entity in schem.recursive_iter_entities():
            if process_entity(entity, replacements_log):
                num_replacements += 1

        if not dry_run and num_replacements > 0:
            schem.save()
    except Exception as ex:
        eprint(f"Failed to process schematic '{schem_path}': {ex}\n{str(traceback.format_exc())}")
        replacements_log = {}
        num_replacements = 0

    return (num_replacements, replacements_log)

def process_structure(struct_path):
    replacements_log = {}
    num_replacements = 0

    try:
        struct = Structure(struct_path)
        for entity in struct.recursive_iter_entities():
            if process_entity(entity, replacements_log):
                num_replacements += 1

        if not dry_run and num_replacements > 0:
            struct.save()
    except Exception as ex:
        eprint(f"Failed to process structure '{struct_path}': {ex}\n{str(traceback.format_exc())}")
        replacements_log = {}
        num_replacements = 0

    return (num_replacements, replacements_log)

if world_path:
    world = World(world_path)
    timings.nextStep("Loaded world")

    parallel_results = world.iter_regions_parallel(process_region, num_processes=num_threads, min_x=pos1[0], min_y=pos1[1], min_z=pos1[2], max_x=pos2[0], max_y=pos2[1], max_z=pos2[2])
    timings.nextStep("World replacements done")

if schematics_path:
    schem_paths = []
    for root, subdirs, files in os.walk(schematics_path):
        for fname in files:
            if fname.endswith(".schematic"):
                schem_paths.append(os.path.join(root, fname))

    if num_threads == 1:
        # Don't bother with processes if only going to use one
        # This makes debugging much easier
        parallel_results = []
        for schem_path in schem_paths:
            parallel_results.append(process_schematic(schem_path))
    else:
        with multiprocessing.Pool(num_threads) as pool:
            parallel_results = pool.map(process_schematic, schem_paths)
    timings.nextStep("Schematics replacements done")

if structures_path:
    struct_paths = []
    for root, subdirs, files in os.walk(structures_path):
        for fname in files:
            if fname.endswith(".nbt"):
                struct_paths.append(os.path.join(root, fname))

    if num_threads == 1:
        # Don't bother with processes if only going to use one
        # This makes debugging much easier
        parallel_results = []
        for struct_path in struct_paths:
            parallel_results.append(process_structure(struct_path))
    else:
        with multiprocessing.Pool(num_threads) as pool:
            parallel_results = pool.map(process_structure, struct_paths)
    timings.nextStep("Structures replacements done")

replacements_log = {}
num_replacements = 0

replacements_to_merge = []
for region_result in parallel_results:
    num_replacements += region_result[0]
    replacements_to_merge.append(region_result[1])

replacements_log = replace_mgr.merge_logs(replacements_to_merge)
timings.nextStep("Logs merged")

if log_handle is not None:
    yaml.dump(replacements_log, log_handle, width=2147483647, allow_unicode=True)
    timings.nextStep("Logs written")

if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
    log_handle.close()

print("{} mobs replaced".format(num_replacements))

