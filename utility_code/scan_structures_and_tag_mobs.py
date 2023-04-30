#!/usr/bin/env pypy3

import math
import os
import sys

from lib_py3.common import parse_name_possibly_json
from lib_py3.library_of_souls import LibraryOfSouls
from minecraft.chunk_format.schematic import Schematic
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
    forbidden_ids = ["minecraft:painting", "minecraft:potion", "minecraft:trident", "minecraft:boat",
                     "minecraft:minecart", "minecraft:falling_block", "minecraft:firework_rocket", "minecraft:item_frame", "minecraft:end_crystal",
                     "minecraft:area_effect_cloud", "minecraft:command", "minecraft:command_block", "minecraft:chain_command_block", "minecraft:repeating_command_block"]

    los = LibraryOfSouls("/home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json")
    los.clear_tags()

# TODO: Don't scan these until they can be reorganized
#    for basedir in ["/home/epic/project_epic/server_config/data/generated"]:
#        for root, subdirs, files in os.walk(basedir):
#            for fname in files:
#                if fname.endswith(".nbt"):
#                    struct = Structure(os.path.join(root, fname))
#
#                    print("Processing structure: {}".format(struct.name))
#
#                    for entity in struct.recursive_iter_entities():
#                        process_entity(entity, struct.name)

    for basedir in ["/home/epic/project_epic/server_config/data/structures/valley", "/home/epic/project_epic/server_config/data/structures/isles", "/home/epic/project_epic/server_config/data/structures/ring"]:
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
        "white":{"world": "white"},
        "whiteexalted":{"world": "whiteexalted"},
        "orange":{"world": "orange"},
        "orangeexalted":{"world": "orangeexalted"},
        "magenta":{"world": "magenta"},
        "magentaexalted":{"world": "magentaexalted"},
        "lightblue":{"world": "lightblue"},
        "lightblueexalted":{"world": "lightblueexalted"},
        "yellow":{"world": "yellow"},
        "willows":{"world": "willows"},
        "reverie":{"world": "reverie"},
        "labs":{"world": "labs"},
        "lime":{"world": "lime"},
        "pink":{"world": "pink"},
        "gray":{"world": "gray"},
        "cyan":{"world": "cyan"},
        "lightgray":{"world": "lightgray"},
        "purple":{"world": "purple"},
        "blue":{"world": "blue"},
        "brown":{"world": "brown"},
        "teal":{"world": "teal"},
        "forum":{"world": "forum"},

        "tutorial":{"world": "tutorial"},
        "verdantstrike":{"path": "valley/verdant", "min": (-1024, 0, 2815), "max": (-768, 255, 3071)},
        "verdantstory":{"path": "valley/verdant", "min": (-767, 0, 2560), "max": (-513, 255, 2815)},
        "sanctum":{"path": "valley/sanctum"},
        "rush":{"world": "rush"},
        "mist":{"path": "isles/mist"},
        "remorse":{"path": "isles/remorse"},
        "depths":{"world": "depths"},
        "gallery":{"world": "gallery"},
        "portal":{"world": "portal"},
        "ruin":{"world": "bluestrike"},
        "skt":{"world": "SKT"},
    }


    for dungeon in dungeons:
        dungeon_config = dungeons[dungeon]

        if "world" in dungeon_config:
            dungeonWorld = World(f'/home/epic/project_epic/dungeon/{dungeon_config["world"]}')
        elif "path" in dungeon_config:
            dungeonWorld = World(f'/home/epic/project_epic/{dungeon_config["path"]}')
        else:
            dungeonWorld = World('/home/epic/project_epic/dungeon/Project_Epic-dungeon')

        print("Processing dungeon: {}".format(dungeon))
        if "rx" in dungeon_config and "rz" in dungeon_config:
            rx = dungeon_config["rx"]
            rz = dungeon_config["rz"]
            for chunk in dungeonWorld.get_region(rx, rz, read_only=True).iter_chunks(autosave=False):
                for entity in chunk.recursive_iter_entities():
                    process_entity(entity, dungeon)
        else:
            # Some worlds may have bounding boxes for the dungeon, some may not and will use the whole world
            pos1 = [-math.inf, -math.inf, -math.inf]
            pos2 = [math.inf, math.inf, math.inf]
            if "min" in dungeon_config:
                pos1 = dungeon_config["min"]
            if "max" in dungeon_config:
                pos2 = dungeon_config["max"]

            for region in dungeonWorld.iter_regions(min_x=pos1[0], min_y=pos1[1], min_z=pos1[2], max_x=pos2[0], max_y=pos2[1], max_z=pos2[2], read_only=True):
                for chunk in region.iter_chunks(min_x=pos1[0], min_y=pos1[1], min_z=pos1[2], max_x=pos2[0], max_y=pos2[1], max_z=pos2[2], autosave=False):
                    for entity in chunk.recursive_iter_entities(min_x=pos1[0], min_y=pos1[1], min_z=pos1[2], max_x=pos2[0], max_y=pos2[1], max_z=pos2[2]):
                        process_entity(entity, dungeon)

    print("\n\n\n\n\n\nNot found unique mobs:")
    for name in not_found_unique_mobs:
        print("  {} - {}".format(name, mob_pos[name]))

    print("\n\n\n\n\n\nNot found different mobs:")
    for name in not_found_different_mobs:
        print("  {} - {}".format(name, mob_pos[name]))

    los.save()
