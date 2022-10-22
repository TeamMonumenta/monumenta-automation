#!/usr/bin/env pypy3

import os
import getopt
import math
import multiprocessing
import sys
import traceback
import yaml

from lib_py3.mob_replacement_manager import MobReplacementManager, remove_unwanted_spawner_tags
from lib_py3.common import eprint, get_entity_name_from_nbt, get_named_hand_items, get_named_armor_items, get_named_hand_item_ids, get_named_armor_item_ids, parse_name_possibly_json
from lib_py3.library_of_souls import LibraryOfSouls
from lib_py3.timing import Timings

from minecraft.chunk_format.schematic import Schematic
from minecraft.chunk_format.structure import Structure
from minecraft.chunk_format.entity import Entity
from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.world import World

def is_entity_in_spawner(entity) -> bool:
    # Start at the node above this one and iterate upwards
    node = entity.parent
    while node is not None:
        if node.nbt is not None and node.nbt.has_path("SpawnPotentials"):
            return True
        node = node.parent

    return False

def match_id(target_id: str, chain=lambda mob: True):
    return lambda mob: chain(mob) and ((mob.has_path("id") and mob.at_path("id").value == target_id) or (mob.has_path("Id") and mob.at_path("Id").value == target_id))

def match_armor(armor: [str], chain=lambda mob: True):
    return lambda mob: chain(mob) and get_named_armor_items(mob) == armor

def match_armor_ids(armor_ids: [str], chain=lambda mob: True):
    return lambda mob: chain(mob) and get_named_armor_item_ids(mob) == armor_ids

def match_noarmor(chain=lambda mob: True):
    return lambda mob: chain(mob) and (not mob.has_path('ArmorItems'))

def match_hand(hand: [str], chain=lambda mob: True):
    return lambda mob: chain(mob) and get_named_hand_items(mob) == hand

def match_hand_ids(hand_ids: [str], chain=lambda mob: True):
    return lambda mob: chain(mob) and get_named_hand_item_ids(mob) == hand_ids

def match_nohand(chain=lambda mob: True):
    return lambda mob: chain(mob) and (not mob.has_path('HandItems'))

def match_name(name: str, chain=lambda mob: True):
    return lambda mob: chain(mob) and mob.has_path('CustomName') and get_entity_name_from_nbt(mob) == name

def match_noname(chain=lambda mob: True):
    return lambda mob: chain(mob) and (not mob.has_path('CustomName'))

# Matches health to within += 5.0
def match_hp(hp: float, chain=lambda mob: True):
    return lambda mob: chain(mob) and mob.has_path('Health') and math.isclose(mob.at_path('Health').value, hp, abs_tol=0.5)

def match_passenger(host_chain, passenger_chain):
    return lambda mob: (host_chain(mob)
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
    ('Celsian Creeper', match_noname(match_id('minecraft:creeper', match_hp(28)))),

    # Piglin conversion
    ('Molten Citizen', match_id('minecraft:zombified_piglin', match_name('Molten Citizen'))),

    # Rename mobs
    ('Jaguar Berserker', match_id('minecraft:zombie', match_name('Jaguar Berzerker'))),
    ('Aurian Priest', match_id('minecraft:evoker', match_name('Priest of The Moon'))),
    ('Soaked Ghoul', match_id('minecraft:drowned', match_name('Ghoul'))),
    ('Ice Archer', match_id('minecraft:skeleton', match_name('Ice Archer'))),
    ('Animated Archer', match_id('minecraft:skeleton', match_name('Animated Gear'))),
    ('Coven Aberration', match_id('minecraft:ghast', match_name('6Coven Aberration'))),

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

    # RIP Lich + yellow stuff
    ("Wraith of the Jungle", match_name('Lich of the Forest', match_id('minecraft:evoker'))),
    ("Brute of the Jungle", match_name('Brute of the Forest', match_id('minecraft:zombie_villager'))),

    # Typo
    ("Permafrost Construct", match_name('Permafrost Constuct', match_id('minecraft:iron_golem'))),

    #Yellow and Willows renames
    ("Wrath Particulate", match_name('Malevolent Dragon', match_id('minecraft:vex'))),
    ("Corrupted Cultist", match_name('Nightmare Cultist', match_id('minecraft:zombie'))),
    ("Corrupted Warlord", match_name('Nightmare Warlord', match_id('minecraft:skeleton'))),
    ("Hateful Titan", match_name('Dragongheist', match_id('minecraft:wither_skeleton'))),
    ("River's Will", match_name('Son of the River', match_id('minecraft:zombie_villager'))),
    ("Tuathan", match_name('Corrupted Leprechaun', match_id('minecraft:zombie'))),

    # Depths
    ("Ravenous Ooze", match_name('Abyssal Guardian', match_id('minecraft:guardian'))),

    # Squid to kid
    ("Star Spitter", match_name('Star Spitter', match_id('minecraft:squid'))),

    # Cathedral
    ("Warped Follower", match_name('Starseeker', match_id('minecraft:zombie'))),

    # Fixed R3 mob errors
    ("Living Lightning", match_name('Living Lighting', match_id('minecraft:bee'))),
    ("Waterflight", match_name('Waterflight', match_id('minecraft:bee'))),
    ("Whaleflight", match_name('Sky Whale', match_id('minecraft:bee'))),
    ("Masked Enchanter", match_name('6Masked Enchanter', match_id('minecraft:wither_skeleton'))),
    ("Flying Cannon", match_name('6Flying Cannon', match_id('minecraft:ghast'))),
]

def usage():
    sys.exit("Usage: {} <--worlds /path/to/folder_containing_worlds | --world /path/to/world | --schematics /path/to/schematics | --structures /path/to/structures> <--library-of-souls /path/to/library-of-souls.json> [--pos1 x,y,z --pos2 x,y,z] [--logfile <stdout|stderr|path>] [--num-threads num] [--dry-run] [--force]".format(sys.argv[0]))

def is_pig_to_remove(entity_nbt, subpath):
    if entity_nbt.has_path(subpath):
        sub_nbt = entity_nbt.at_path(subpath)
        return sub_nbt.has_path('id') and sub_nbt.at_path('id').value == "minecraft:pig" and (not sub_nbt.has_path('CustomName') or len(parse_name_possibly_json(sub_nbt.at_path('CustomName').value)) == 0)
    return False

# This is handy here because it has direct access to previously defined globals
def process_entity(entity, replacements_log) -> None:
    if not isinstance(entity, Entity) and not isinstance(entity, BlockEntity):
        return False, []

    # Skip entities outside the specified area
    if (entity.pos is not None and
        (
         entity.pos[0] < min_x or
         entity.pos[1] < min_y or
         entity.pos[2] < min_z or
         entity.pos[0] > max_x or
         entity.pos[1] > max_y or
         entity.pos[2] > max_z
        )):
        return False, []

    nbt = entity.nbt
    if nbt.has_path("Delay"):
        changed_something = False
        if nbt.at_path("Delay").value != 0:
            nbt.at_path("Delay").value = 0
            changed_something = True

        msgs = []

        # Remove pigs
        if nbt.has_path('SpawnPotentials'):
            new_potentials = []
            for nested_entity in nbt.iter_multipath('SpawnPotentials[]'):
                if is_pig_to_remove(nested_entity, 'Entity') or is_pig_to_remove(nested_entity, 'data.entity'):
                    changed_something = True
                    msgs.append(f"Removing pig from SpawnPotentials at {entity.get_path_str()}\n")
                else:
                    new_potentials.append(nested_entity)
            nbt.at_path('SpawnPotentials').value = new_potentials
        if is_pig_to_remove(nbt, 'SpawnData') or is_pig_to_remove(nbt, 'SpawnData.entity'):
            changed_something = True
            msgs.append(f"Removing pig Spawndata at {entity.get_path_str()}\n")
            nbt.value.pop("SpawnData")

        return changed_something, msgs

    if is_entity_in_spawner(entity):
        remove_unwanted_spawner_tags(nbt)
        return replace_mgr.replace_mob(nbt, replacements_log, entity.get_path_str()), []

    return False, []

def process_init(mgr, dry, f, minx, miny, minz, maxx, maxy, maxz):
    global replace_mgr, dry_run, force, min_x, min_y, min_z, max_x, max_y, max_z
    replace_mgr = mgr
    dry_run = dry
    force = f
    min_x = minx
    min_y = miny
    min_z = minz
    max_x = maxx
    max_y = maxy
    max_z = maxz


def process_region(region):
    replacements_log = {}
    return_msgs = []
    num_replacements = 0
    for chunk in region.iter_chunks(autosave=(not dry_run)):
        for entity in chunk.recursive_iter_all_types():
            changed_something, msgs = process_entity(entity, replacements_log)
            if changed_something:
                num_replacements += 1
                return_msgs += msgs

    return (num_replacements, replacements_log, return_msgs)

def process_schematic_or_structure(obj):
    replacements_log = {}
    return_msgs = []
    num_replacements = 0

    for entity in obj.recursive_iter_all_types():
        changed_something, msgs = process_entity(entity, replacements_log)
        if changed_something:
            num_replacements += 1
            return_msgs += msgs

    if not dry_run and num_replacements > 0:
        obj.save()

    return (num_replacements, replacements_log, return_msgs)

def err_func(ex, args):
    eprint(f"Caught exception: {ex}")
    eprint(f"While iterating: {args}")
    eprint(traceback.format_exc())
    return (0, {}, [])

def merge_log_tuples(log_dicts_to_merge, out_log_dict={}, out_msgs=[]):
    """Merges mob replacements log tuples. out_log_dict can be specified to merge multiple different result generators into the same output

    Returns a tuple(num_replacements, {dict})"""

    num_replacements = 0
    for replacements, log_dict, msgs in log_dicts_to_merge:
        num_replacements += replacements
        out_msgs += msgs
        for log_key in log_dict:
            if log_key not in out_log_dict:
                # Cheat and just reference the entire structure in the output
                out_log_dict[log_key] = log_dict[log_key]
            else:
                for orig_tag_mojangson in log_dict[log_key]["FROM"]:
                    if orig_tag_mojangson not in out_log_dict[log_key]["FROM"]:
                        out_log_dict[log_key]["FROM"][orig_tag_mojangson] = []

                    for debug_path in log_dict[log_key]["FROM"][orig_tag_mojangson]:
                        out_log_dict[log_key]["FROM"][orig_tag_mojangson].append(debug_path)
    return num_replacements, out_log_dict, out_msgs

if __name__ == '__main__':
    # Note that this currently needs to be 'fork' and not 'spawn' because pypy can't pickle the lambdas used by mob substitutions
    # Can move the line that loads the substitutions into the process init handler, but then it's slower than without any multiprocessing
    # Will leave this as fork for now, this script seems pretty reliable
    multiprocessing.set_start_method("fork")

    try:
        opts, args = getopt.getopt(sys.argv[1:], "z:w:s:g:b:l:j:dif", ["worlds=", "world=", "schematics=", "structures=", "library-of-souls=", "logfile=", "num-threads=", "dry-run", "pos1=", "pos2=", "force"])
    except getopt.GetoptError as err:
        eprint(str(err))
        usage()

    worlds_path = None
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
        if o in ("-z", "--worlds"):
            worlds_path = a
        elif o in ("-w", "--world"):
            world_path = a
        elif o in ("-s", "--schematics"):
            schematics_path = a
        elif o in ("-s", "--structures"):
            structures_path = a
        elif o in ("-b", "--library-of-souls"):
            library_of_souls_path = a
        elif o in ("--pos1",):
            try:
                split = a.split(",")
                pos1 = (int(split[0]), int(split[1]), int(split[2]))
            except Exception:
                eprint("Invalid --pos1 argument")
                usage()
        elif o in ("--pos2",):
            try:
                split = a.split(",")
                pos2 = (int(split[0]), int(split[1]), int(split[2]))
            except Exception:
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

    if worlds_path is None and world_path is None and schematics_path is None and structures_path is None:
        eprint("--worlds, --world, --schematics, or --structures must be specified!")
        usage()
    elif library_of_souls_path is None:
        eprint("--library-of-souls must be specified!")
        usage()

    min_x = min(pos1[0], pos2[0])
    min_y = min(pos1[1], pos2[1])
    min_z = min(pos1[2], pos2[2])
    max_x = max(pos1[0], pos2[0])
    max_y = max(pos1[1], pos2[1])
    max_z = max(pos1[2], pos2[2])

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

    num_replacements = 0
    replacements_log = {}
    replacements_msgs = []

    if world_path or worlds_path:
        worlds = []
        if world_path:
            worlds.append(world_path)
        if worlds_path:
            for worldname in World.enumerate_worlds(worlds_path):
                worlds.append(os.path.join(worlds_path, worldname))

        for world_path in worlds:
            world = World(world_path)
            timings.nextStep("Loaded world")

            generator = world.iter_regions_parallel(process_region, err_func, num_processes=num_threads, initializer=process_init, initargs=(replace_mgr, dry_run, force, min_x, min_y, min_z, max_x, max_y, max_z))
            replacements, replacements_log, replacements_msgs = merge_log_tuples(generator, replacements_log, replacements_msgs)
            num_replacements += replacements

            timings.nextStep(f"World replacements done, {replacements} replacements")

    if schematics_path:
        # Note: autosave=False is because we only save schematics that had some item replacements in them
        generator = Schematic.iter_schematics_parallel(schematics_path, process_schematic_or_structure, err_func, num_processes=num_threads, autosave=False, initializer=process_init, initargs=(replace_mgr, dry_run, force, min_x, min_y, min_z, max_x, max_y, max_z))
        replacements, replacements_log, replacements_msgs = merge_log_tuples(generator, replacements_log, replacements_msgs)
        num_replacements += replacements

        timings.nextStep(f"Schematics replacements done, {replacements} replacements")

    if structures_path:
        # Note: autosave=False is because we only save structures that had some item replacements in them
        generator = Structure.iter_structures_parallel(structures_path, process_schematic_or_structure, err_func, num_processes=num_threads, autosave=False, initializer=process_init, initargs=(replace_mgr, dry_run, force, min_x, min_y, min_z, max_x, max_y, max_z))
        replacements, replacements_log, replacements_msgs = merge_log_tuples(generator, replacements_log, replacements_msgs)
        num_replacements += replacements

        timings.nextStep(f"Structures replacements done, {replacements} replacements")

    if log_handle is not None:
        for msg in replacements_msgs:
            log_handle.write(msg)
            log_handle.write("\n")
        yaml.dump(replacements_log, log_handle, width=2147483647, allow_unicode=True)
        timings.nextStep("Logs written")

    if log_handle is not None and log_handle is not sys.stdout and log_handle is not sys.stderr:
        log_handle.close()

    print("{} mobs replaced".format(num_replacements))
