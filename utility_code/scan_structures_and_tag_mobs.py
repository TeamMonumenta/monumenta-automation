#!/usr/bin/env python3

import sys
import os
from pprint import pprint
from lib_py3.common import parse_name_possibly_json
from lib_py3.schematic import Schematic
from lib_py3.library_of_souls import LibraryOfSouls
from lib_py3.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

# This ugly function references tons of global variables...
def process_entity(entity, source_pos, entity_path, source_name):
    if entity.has_path("CustomName"):
        if not entity.has_path("id"):
            return
        # Don't add tile entities!
        if entity.has_path("LootTable") or entity.has_path("Items") or entity.has_path("Command"):
            return
        # Don't add non-mob entities
        for forbidden in forbidden_ids:
            if forbidden in entity.at_path("id").value:
                return

        name = parse_name_possibly_json(entity.at_path("CustomName").value, remove_color=True)

        # Keep track of how many times each mob is seen
        if name not in mob_counts:
            mob_counts[name] = 0
        mob_counts[name] += 1

        # Check if this mob is already in the library of souls
        soul = los.get_soul(name)
        if soul is not None:
            # Already in the library - tag it with the name of the structure for searching
            if "location_names" not in soul:
                soul["location_names"] = []
            if source_name not in soul["location_names"]:
                soul["location_names"].append(source_name)
        else:
            # Not in the library - check if its NBT is unique
            if name not in not_found_different_mobs:
                if name in not_found_unique_mobs:
                    if not_found_unique_mobs[name] != entity:
                        #print("Diff at mob {}".format(name))
                        #not_found_unique_mobs[name].diff(entity, order_matters=False, show_values=True)
                        not_found_different_mobs.add(name)
                        not_found_unique_mobs.pop(name)
                else:
                    not_found_unique_mobs[name] = entity
                mob_pos[name] = (source_pos, source_name)


mob_pos = {}
not_found_different_mobs = set()
not_found_unique_mobs = {}
not_found_unique_low_count_mobs = set()
mob_counts = {}
forbidden_ids = ["minecraft:armor_stand", "minecraft:painting", "minecraft:villager", "minecraft:potion", "minecraft:trident", "minecraft:boat",
                 "minecraft:minecart", "minecraft:falling_block", "minecraft:firework_rocket", "minecraft:item_frame", "minecraft:end_crystal",
                 "minecraft:area_effect_cloud", "minecraft:command"]

los = LibraryOfSouls("/home/epic/project_epic/mobs/plugins/LibraryOfSouls/souls_database.json")
los.clear_tags()

for basedir in ["/home/epic/project_epic/server_config/data/structures/region_1", "/home/epic/project_epic/server_config/data/structures/region_2"]:
    for root, subdirs, files in os.walk(basedir):
        for fname in files:
            if fname.endswith(".schematic"):
                schem = Schematic(os.path.join(root, fname))

                print("Processing schematic: {}".format(schem.name))

                for entity, source_pos, entity_path in schem.entity_iterator(readonly=True):
                    process_entity(entity, source_pos, entity_path, schem.name)

print("Processing shiftingcity schematics...")
for root, subdirs, files in os.walk("/home/epic/project_epic/server_config/data/structures/roguelite"):
    for fname in files:
        if fname.endswith(".schematic"):
            schem = Schematic(os.path.join(root, fname))
            for entity, source_pos, entity_path in schem.entity_iterator(readonly=True):
                process_entity(entity, source_pos, entity_path, "shiftingcity")

print("Processing roguelike schematics...")
for root, subdirs, files in os.walk("/home/epic/project_epic/server_config/data/structures/dungeon/rogue"):
    for fname in files:
        if fname.endswith(".schematic"):
            schem = Schematic(os.path.join(root, fname))
            for entity, source_pos, entity_path in schem.entity_iterator(readonly=True):
                process_entity(entity, source_pos, entity_path, "roguelike")

dungeons = {
    "white":{"x":-3, "z":-2},
    "orange":{"x":-3, "z":-1},
    "magenta":{"x":-3, "z":0},
    "lightblue":{"x":-3, "z":1},
    "yellow":{"x":-3, "z":2},
    "willows":{"x":-3, "z":3},
    "roguelike":{"x":-2, "z":-1},
    "reverie":{"x":-3, "z":4},
    "tutorial":{"x":-2, "z":0},
    "sanctum":{"x":-3, "z":12},
    "labs":{"x":-2, "z":2},
    "lime":{"x":-3, "z":5},
    "pink":{"x":-3, "z":7},
    "gray":{"x":-3, "z":6},
    "cyan":{"x":-3, "z":9},
    "lightgray":{"x":-3, "z":8},
    "purple":{"x":-3, "z":13},
}

dungeonWorld = World('/home/epic/project_epic/dungeon/Project_Epic-dungeon')

for dungeon in dungeons:
    print("Processing dungeon: {}".format(dungeon))
    rx = dungeons[dungeon]["x"]
    rz = dungeons[dungeon]["z"]
    pos1 = (512*rx      ,   0, 512*rz      )
    pos2 = (512*rx + 511, 255, 512*rz + 511)
    for entity, source_pos, entity_path in dungeonWorld.entity_iterator(pos1=pos1, pos2=pos2, readonly=True):
        process_entity(entity, source_pos, entity_path, dungeon)


print("\n\n\n\n\n\nNot found unique mobs:")
for name in not_found_unique_mobs:
    print("  {} - {}".format(name, mob_pos[name]))

print("\n\n\n\n\n\nNot found different mobs:")
for name in not_found_different_mobs:
    print("  {} - {}".format(name, mob_pos[name]))

los.save()
