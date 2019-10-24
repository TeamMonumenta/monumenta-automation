#!/usr/bin/env python3

import sys
import os

from pprint import pformat

from lib_py3.common import eprint
from lib_py3.world import World
from lib_py3.terrain_reset import terrain_reset_instance
from lib_py3.iterators.base_chunk_entity_iterator import BaseChunkEntityIterator

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

if (len(sys.argv) != 2):
    sys.exit("Usage: {} </path/to/world>".format(sys.argv[0]))

world_path = sys.argv[1]

entries = (
    {"name":"Guild_1",                "pos1":( -583,   0,  137), "pos2":(-622, 255,  105)},
    {"name":"Guild_2",                "pos1":( -573,   0,  112), "pos2":(-534, 255,  154)},
    {"name":"Guild_3",                "pos1":( -581,   0,  147), "pos2":(-613, 255,  186)},
    {"name":"Guild_4",                "pos1":( -649,   0,  272), "pos2":(-617, 255,  311)},
    {"name":"Guild_5",                "pos1":( -683,   0,  272), "pos2":(-651, 255,  311)},
    {"name":"Guild_6",                "pos1":( -685,   0,  272), "pos2":(-717, 255,  311)},
    {"name":"Guild_7",                "pos1":( -819,   0,  235), "pos2":(-780, 255,  267)},
    {"name":"Guild_8",                "pos1":( -829,   0,  257), "pos2":(-868, 255,  289)},
    {"name":"Guild_9",                "pos1":( -819,   0,  269), "pos2":(-780, 255,  301)},
    {"name":"Guild_10",               "pos1":( -937,   0,  269), "pos2":(-969, 255,  308)},
    {"name":"Guild_11",               "pos1":( -969,   0,  259), "pos2":(-937, 255,  220)},
    {"name":"Guild_12",               "pos1":( -955,   0,  104), "pos2":(-994, 255,  136)},
    {"name":"Guild_14",               "pos1":( -955,   0,   70), "pos2":(-994, 255,  102)},
    {"name":"Guild_15",               "pos1":( -581,   0,  -61), "pos2":(-613, 255, -100)},
    {"name":"Guild_18",               "pos1":( -945,   0,   93), "pos2":(-906, 255,  125)},
    {"name":"Guild_20",               "pos1":( -748,   0, -230), "pos2":(-787, 255, -198)},
    {"name":"Guild_21",               "pos1":( -787,   0, -232), "pos2":(-748, 255, -264)},
    {"name":"Guild_22",               "pos1":( -603,   0, -191), "pos2":(-564, 255, -159)},
    {"name":"Guild_23",               "pos1":( -612,   0, -180), "pos2":(-651, 255, -212)},
    {"name":"Guild_24",               "pos1":( -564,   0, -192), "pos2":(-603, 255, -224)},
    {"name":"Guild_26",               "pos1":( -596,   0,  -49), "pos2":(-564, 255,  -10)},
    {"name":"Guild_27",               "pos1":( -548,   0,  -61), "pos2":(-580, 255, -100)},
    {"name":"Guild_Archive_N1",       "pos1":(-1626,   0, 1408), "pos2":(-1594,255, 1446)},
    {"name":"Guild_Archive_N2",       "pos1":(-1589,   0, 1408), "pos2":(-1557,255, 1446)},
    {"name":"Guild_Archive_N3",       "pos1":(-1552,   0, 1408), "pos2":(-1520,255, 1446)},
    {"name":"Guild_Archive_N4",       "pos1":(-1515,   0, 1408), "pos2":(-1483,255, 1446)},
    {"name":"Guild_Archive_N5",       "pos1":(-1478,   0, 1408), "pos2":(-1446,255, 1446)},
    {"name":"Guild_Archive_E1",       "pos1":(-1446,   0, 1446), "pos2":(-1409,255, 1478)},
    {"name":"Guild_Archive_E2",       "pos1":(-1446,   0, 1483), "pos2":(-1409,255, 1515)},
    {"name":"Guild_Archive_E3",       "pos1":(-1446,   0, 1520), "pos2":(-1409,255, 1552)},
    {"name":"Guild_Archive_E4",       "pos1":(-1446,   0, 1557), "pos2":(-1409,255, 1589)},
    {"name":"Guild_Archive_E5",       "pos1":(-1446,   0, 1594), "pos2":(-1409,255, 1626)},
    {"name":"Guild_Archive_S1",       "pos1":(-1626,   0, 1626), "pos2":(-1594,255, 1663)},
    {"name":"Guild_Archive_S2",       "pos1":(-1589,   0, 1626), "pos2":(-1557,255, 1663)},
    {"name":"Guild_Archive_S3",       "pos1":(-1552,   0, 1626), "pos2":(-1520,255, 1663)},
    {"name":"Guild_Archive_S4",       "pos1":(-1515,   0, 1626), "pos2":(-1483,255, 1663)},
    {"name":"Guild_Archive_S5",       "pos1":(-1478,   0, 1626), "pos2":(-1446,255, 1663)},
    {"name":"Guild_Archive_W1",       "pos1":(-1664,   0, 1446), "pos2":(-1626,255, 1478)},
    {"name":"Guild_Archive_W2",       "pos1":(-1664,   0, 1483), "pos2":(-1626,255, 1515)},
    {"name":"Guild_Archive_W3",       "pos1":(-1664,   0, 1520), "pos2":(-1626,255, 1552)},
    {"name":"Guild_Archive_W4",       "pos1":(-1664,   0, 1557), "pos2":(-1626,255, 1589)},
    {"name":"Guild_Archive_W5",       "pos1":(-1664,   0, 1594), "pos2":(-1626,255, 1626)},
)

item_locations_to_wipe = (
    "ArmorItem",
    "Item",
    "RecordItem",
    "SaddleItem",
    "Trident",
    "ArmorItems",
    "EnderItems",
    "HandItems",
    "Inventory",
    "Items",
)

eprint("Entries to process: {}".format(pformat(entries)))

eprint("Opening world '{}'...".format(world_path))
world = World(world_path)

for entry in entries:
    print("Processing {}".format(entry["name"]))
    for entity in BaseChunkEntityIterator(world, entry["pos1"], entry["pos2"], readonly=False):
        if not entity.has_path("id"):
            eprint("WARNING: Entity has no 'id': {}".format(entity.to_mojangson()))

        if "armor_stand" in entity.at_path("id").value:
            # Set invulnerable, lock item slots
            entity.value["Invulnerable"] = nbt.TagByte(1)
            entity.value["DisabledSlots"] = nbt.TagInt(2097151)
            print("Setting armor stand to be invulnerable / slots disabled: '{}'".format(entity.to_mojangson()))

        elif "item_frame" in entity.at_path("id").value:
            # Set invulnerable
            entity.value["Invulnerable"] = nbt.TagByte(1)
            print("Setting item frame to be invulnerable: '{}'".format(entity.to_mojangson()))

        else:
            for location in item_locations_to_wipe:
                if entity.has_path(location):
                    print("Popping '{}' from '{}'".format(location, entity.at_path("id").value))
                    entity.value.pop(location)

        # Lock... everything, including entities. Who cares!
        if entity.has_path("Lock"):
            entity.value.pop("Lock")
        entity.value["Lock"] = nbt.TagString("AdminEquipmentTool")

eprint("Done")

