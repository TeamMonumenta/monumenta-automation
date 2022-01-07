#!/usr/bin/env pypy3

import sys
import os
from pprint import pprint
from lib_py3.common import parse_name_possibly_json
from lib_py3.library_of_souls import LibraryOfSouls

from minecraft.chunk_format.schematic import Schematic
from minecraft.chunk_format.structure import Structure
from minecraft.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

from quarry.types import nbt

def process_entity(entity, source_name):
    if entity.nbt.has_path("CustomName"):
        if entity.nbt.has_path("id"):
            entity_id = entity.nbt.at_path("id").value
        elif entity.nbt.has_path("Id"):
            entity_id = entity.nbt.at_path("Id").value
        else:
            return

        # Don't add tile entities!
        if entity.nbt.has_path("LootTable") or entity.nbt.has_path("Items") or entity.nbt.has_path("Command"):
            return
        # Don't add non-mob entities
        for forbidden in forbidden_ids:
            if forbidden in entity_id:
                return

        name = parse_name_possibly_json(entity.nbt.at_path("CustomName").value, remove_color=True)

        # Keep track of how many times each mob is seen
        if name not in mob_counts:
            mob_counts[name] = 0
        mob_counts[name] += 1

        # Check if this mob is already in the library of souls
        soul = los.get_soul(name)
        soul_id = None
        if soul is not None:
            soul_nbt = nbt.TagCompound.from_mojangson(soul["history"][0]["mojangson"])
            soul_id = soul_nbt.at_path("id").value
        if soul is not None and soul_id == entity_id:
            # Already in the library - tag it with the name of the structure for searching
            if "location_names" not in soul:
                soul["location_names"] = []
            if source_name not in soul["location_names"]:
                soul["location_names"].append(source_name)
        else:
            # Not in the library - check if its NBT is unique
            if name not in not_found_different_mobs:
                if name in not_found_unique_mobs:
                    if not_found_unique_mobs[name] != entity.nbt:
                        #print("Diff at mob {}".format(name))
                        #not_found_unique_mobs[name].diff(entity.nbt, order_matters=False, show_values=True)
                        not_found_different_mobs.add(f"{name}  {entity_id}")
                        not_found_unique_mobs.pop(f"{name}  {entity_id}")
                else:
                    not_found_unique_mobs[f"{name}  {entity_id}"] = entity.nbt
                mob_pos[f"{name}  {entity_id}"] = (entity.pos, source_name)

if __name__ == '__main__':
    mob_pos = {}
    not_found_different_mobs = set()
    not_found_unique_mobs = {}
    not_found_unique_low_count_mobs = set()
    mob_counts = {}
    forbidden_ids = ["minecraft:armor_stand", "minecraft:painting", "minecraft:villager", "minecraft:potion", "minecraft:trident", "minecraft:boat",
                     "minecraft:minecart", "minecraft:falling_block", "minecraft:firework_rocket", "minecraft:item_frame", "minecraft:end_crystal",
                     "minecraft:area_effect_cloud", "minecraft:command", "minecraft:command_block", "minecraft:chain_command_block", "minecraft:repeating_command_block"]

    los = LibraryOfSouls("/home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json")
    los.clear_tags()

    for basedir in ["/home/epic/project_epic/server_config/data/generated"]:
        for root, subdirs, files in os.walk(basedir):
            for fname in files:
                if fname.endswith(".nbt"):
                    struct = Structure(os.path.join(root, fname))

                    print("Processing structure: {}".format(struct.name))

                    for entity in struct.recursive_iter_entities():
                        process_entity(entity, struct.name)

    for basedir in ["/home/epic/project_epic/server_config/data/structures/valley", "/home/epic/project_epic/server_config/data/structures/isles"]:
        for root, subdirs, files in os.walk(basedir):
            for fname in files:
                if fname.endswith(".schematic"):
                    schem = Schematic(os.path.join(root, fname))

                    print("Processing schematic: {}".format(schem.name))

                    for entity in schem.recursive_iter_entities():
                        process_entity(entity, schem.name)

    print("Processing shiftingcity schematics...")
    for root, subdirs, files in os.walk("/home/epic/project_epic/server_config/data/structures/roguelite"):
        for fname in files:
            if fname.endswith(".schematic"):
                schem = Schematic(os.path.join(root, fname))
                for entity in schem.recursive_iter_entities():
                    process_entity(entity, "shiftingcity")

    print("Processing corridors schematics...")
    for root, subdirs, files in os.walk("/home/epic/project_epic/server_config/data/structures/dungeon/rogue"):
        for fname in files:
            if fname.endswith(".schematic"):
                schem = Schematic(os.path.join(root, fname))
                for entity in schem.recursive_iter_entities():
                    process_entity(entity, "corridors")

    dungeons = {
        "white":{"x":-3, "z":-2},
        "orange":{"x":-3, "z":-1},
        "magenta":{"x":-3, "z":0},
        "lightblue":{"x":-3, "z":1},
        "yellow":{"x":-3, "z":2},
        "willows":{"x":-3, "z":3},
        "corridors":{"x":-2, "z":-1},
        "verdant":{"x":-2, "z":5},
        "reverie":{"x":-3, "z":4},
        "tutorial":{"x":-2, "z":1},
        "sanctum":{"x":-3, "z":12},
        "labs":{"x":-2, "z":2},
        "lime":{"x":-3, "z":5},
        "pink":{"x":-3, "z":7},
        "gray":{"x":-3, "z":6},
        "cyan":{"x":-3, "z":9},
        "lightgray":{"x":-3, "z":8},
        "purple":{"x":-3, "z":13},
        "teal":{"x":-2, "z":12},
        "forum":{"x":-3, "z":16},
        "rush":{"x":-3, "z":15},
        "mist":{"x":-2, "z":3},
        "remorse":{"x":-3, "z":10},
        "depths":{"x":-2, "z":4},
    }

    dungeonWorld = World('/home/epic/project_epic/dungeon/Project_Epic-dungeon')

    for dungeon in dungeons:
        print("Processing dungeon: {}".format(dungeon))
        rx = dungeons[dungeon]["x"]
        rz = dungeons[dungeon]["z"]
        for chunk in dungeonWorld.get_region(rx, rz, read_only = True).iter_chunks(autosave=False):
            for entity in chunk.recursive_iter_entities():
                process_entity(entity, dungeon)

    print("\n\n\n\n\n\nNot found unique mobs:")
    for name in not_found_unique_mobs:
        print("  {} - {}".format(name, mob_pos[name]))

    print("\n\n\n\n\n\nNot found different mobs:")
    for name in not_found_different_mobs:
        print("  {} - {}".format(name, mob_pos[name]))

    los.save()
