#!/usr/bin/env python3

import sys
import os
import getopt
import yaml
import multiprocessing
import traceback

from lib_py3.mob_replacement_manager import MobReplacementManager, remove_unwanted_spawner_tags
from lib_py3.common import eprint, get_entity_name_from_nbt, get_named_hand_items, get_named_armor_items
from lib_py3.library_of_souls import LibraryOfSouls
from lib_py3.timing import Timings

from minecraft.chunk_format.schematic import Schematic
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
    return lambda mob : chain(mob) and mob.at_path("id").value == target_id

def match_armor(armor: [str], chain=lambda mob: True):
    return lambda mob : chain(mob) and get_named_armor_items(mob) == armor

def match_noarmor(chain=lambda mob: True):
    return lambda mob : chain(mob) and (not mob.has_path('ArmorItems'))

def match_hand(hand: [str], chain=lambda mob: True):
    return lambda mob : chain(mob) and get_named_hand_items(mob) == hand

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
    ("Lighthouse Defender", match_hand(["Enraged Captain's Axe", "Hawk's Talon"], match_id('minecraft:skeleton'))),
    ("Frost Moon Archer", match_name('Frost Moon Brute', match_id('minecraft:skeleton'))),
    ("Frost Moon Archer", match_name('Frost Moon Knight', match_id('minecraft:skeleton'))),
    ("Desiccated Ghast", match_name('Dessicated Ghast', match_id('minecraft:ghast'))),
    ("Mercenary Bowman", match_name('Mercenery Bowman', match_id('minecraft:skeleton'))),
    ("Flame Imp", match_name('Fire Imp', match_id('minecraft:zombie'))),
    ("Earth Spectre", match_name('Earth Shade', match_id('minecraft:skeleton'))),
    ("Phaser Guardian", match_name('Phaser Assassin', match_id('minecraft:guardian'))),
    ("Jungle Flyer", match_hand(["Druidic Stick", None], match_noname(match_id('minecraft:vex')))),
    # TODO: Re-enable when stacked mobs are fixed
    #("Cherry Boomsom", match_name('Cheery Boomsome', match_id('minecraft:creeper'))),
    ("Blast Miner", match_name('Pyro Miner', match_id('minecraft:zombie'))),
    ("Viridian Juggernaut", match_name('Viridian Juggernaught', match_id('minecraft:wither_skeleton'))),
    ("Frozen Grunt", match_name('Frost Knight', match_id('minecraft:zombie_villager'))),
    ("Frozen Sniper", match_name('Frost Knight Archer', match_id('minecraft:stray'))),
    ("Monstrous Arachnid", match_name('Monsterous Arachnid', match_id('minecraft:spider'))),

    # Generic, un-named R2 mobs
    ("Celsian Sniper", match_hp(30, match_hand(["Composite Bow", None], match_noarmor(match_noname(match_id('minecraft:skeleton')))))),
    ("Celsian Ghast", match_hand(["Generic blaze1", None], match_noname(match_id('minecraft:ghast')))),
    ("Molten Citizen", match_hp(30, match_nohand(match_noname(match_id('minecraft:zombie_pigman'))))),
    ("Theraphosidae", match_armor(["Generic spider5", None, None, None],match_nohand(match_noname(match_id('minecraft:spider'))))),
    ("Hungry Dolphin", match_armor([None, None, None, "Generic Fang"],match_nohand(match_noname(match_id('minecraft:dolphin'))))),
    ("Drowned Pirate", match_armor([None,"generic drowned",None,None],match_nohand(match_noname(match_id('minecraft:drowned'))))),
    ("Drowned Pirate", match_passenger(match_id('minecraft:guardian'), match_name('Drowned Pirate', match_id('minecraft:drowned')))),

    ("Gear Gremlin", match_passenger(match_id('minecraft:endermite'), match_name('Gear Gremlin', match_id('minecraft:drowned')))),
    ("Rusted Gear", match_passenger(match_id('minecraft:guardian'), match_name('Rusted Gear', match_id('minecraft:drowned')))),
    ("Silver Theurge", match_passenger(match_id('minecraft:silverfish'), match_name('Silver Theurge', match_id('minecraft:drowned')))),
    ("Inundated Draugr", match_passenger(match_id('minecraft:silverfish'), match_name('Inundated Draugr', match_id('minecraft:drowned')))),
    ("Drowned Lancer", match_passenger(match_id('minecraft:silverfish'), match_name('Drowned Lancer', match_id('minecraft:drowned')))),
    ("Water Wisp", match_passenger(match_id('minecraft:silverfish'), match_name('Water Wisp', match_id('minecraft:drowned')))),
    ("Sodden Corpse", match_passenger(match_id('minecraft:silverfish'), match_name('Sodden Corpse', match_id('minecraft:drowned')))),
    ("Camouflaged Swarmer", match_passenger(match_id('minecraft:silverfish'), match_name('Camouflaged Swarmer', match_id('minecraft:drowned')))),
    ("Gillman Fighter", match_passenger(match_id('minecraft:silverfish'), match_name('Gillman Fighter', match_id('minecraft:drowned')))),
    ("Elder Gillman", match_passenger(match_id('minecraft:silverfish'), match_name('Elder Gillman', match_id('minecraft:drowned')))),
    ('Viridian Defender', match_passenger(match_id('minecraft:silverfish'), match_name('Viridian Defender', match_id('minecraft:drowned')))),
    ('Viridian Wizard', match_passenger(match_id('minecraft:silverfish'), match_name('Viridian Wizard', match_id('minecraft:drowned')))),
    ('Viridian Royal Guard', match_passenger(match_id('minecraft:guardian'), match_name('Viridian Royal Guard', match_id('minecraft:drowned')))),
    ('Viridian Royal Harpooner', match_passenger(match_id('minecraft:guardian'), match_name('Viridian Royal Harpooner', match_id('minecraft:drowned')))),
    ('Mutated Royal Guard', match_passenger(match_id('minecraft:guardian'), match_name('Mutated Royal Guard', match_id('minecraft:drowned')))),

    ("Pirate Buccaneer", match_name('Pirate Buckaneer', match_id('minecraft:husk'))),
    ("Pirate Oarsman", match_name('Pirate Oarman', match_id('minecraft:vindicator'))),

    # Cyan
    ("Cursed Demolitionist", match_name('Cursed Demolitionist', match_id('minecraft:zombie_villager'))),

    # Pink same-named mobs
    ("Fall Citizen", match_hand(["Earthbound Runeblade", None], match_name("Tempered Citizen", match_id('minecraft:zombie_villager')))),
    ("Summer Citizen", match_hand(["Lingering Flame", None], match_name("Tempered Citizen", match_id('minecraft:zombie_villager')))),
    ("Spring Citizen", match_hand(["Rosethorn Blade", "Talaya's Blossom"], match_name("Tempered Citizen", match_id('minecraft:zombie_villager')))),
    ("Winter Citizen", match_hand(["Iceborn Runeblade", None], match_name("Tempered Citizen", match_id('minecraft:zombie_villager')))),
    ("Fall Watcher", match_hand(["Soulvenom Bow", None], match_name("Tempered Watcher", match_id('minecraft:skeleton')))),
    ("Summer Watcher", match_hand(["Ishkarian Longbow", None], match_name("Tempered Watcher", match_id('minecraft:skeleton')))),
    ("Spring Watcher", match_hand(["Steelsiege", None], match_name("Tempered Watcher", match_id('minecraft:skeleton')))),
    ("Winter Watcher", match_hand(["Icicle Greatbow", None], match_name("Tempered Watcher", match_id('minecraft:skeleton')))),
]

def usage():
    sys.exit("Usage: {} <--world /path/to/world | --schematics /path/to/schematics> <--library-of-souls /path/to/library-of-souls.json> [--pos1 x,y,z --pos2 x,y,z] [--logfile <stdout|stderr|path>] [--dry-run]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:s:b:l:j:di", ["world=", "schematics=", "library-of-souls=", "logfile=", "num-threads=", "dry-run", "pos1=", "pos2="])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
schematics_path = None
library_of_souls_path = None
pos1 = None
pos2 = None
logfile = None
num_threads = 4
dry_run = False

for o, a in opts:
    if o in ("-w", "--world"):
        world_path = a
    elif o in ("-s", "--schematics"):
        schematics_path = a
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
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None and schematics_path is None:
    eprint("--world or --schematics must be specified!")
    usage()
elif library_of_souls_path is None:
    eprint("--library-of-souls must be specified!")
    usage()
elif ((pos1 is not None) and (pos2 is None)) or ((pos1 is None) and (pos2 is not None)):
    eprint("--pos1 and --pos2 must be specified (or neither specified)!")
    usage()
elif (pos1 is not None) and (schematics_path is not None):
    eprint("--pos1 and --pos2 do not currently work for schematics")
    usage()


timings = Timings(enabled=dry_run)
los = LibraryOfSouls(library_of_souls_path, readonly=True)
timings.nextStep("Loaded Library of Souls")
replace_mgr = MobReplacementManager()
los.load_replacements(replace_mgr)
replace_mgr.add_substitutions(sub)
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
                if nested_entity.has_path('nbt.id') and nested_entity.at_path('nbt.id').value == "minecraft:pig":
                    if log_handle is not None:
                        log_handle.write(f"Removing pig from SpawnPotentials at {entity.get_path_str()}\n")
                else:
                    new_potentials.append(nested_entity)
            nbt.at_path('SpawnPotentials').value = new_potentials
        if nbt.has_path("SpawnData.id") and nbt.at_path("SpawnData.id").value == "minecraft:pig":
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

if world_path:
    world = World(world_path)
    timings.nextStep("Loaded world")

    parallel_results = world.iter_regions_parallel(process_region, num_processes=num_threads)
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

