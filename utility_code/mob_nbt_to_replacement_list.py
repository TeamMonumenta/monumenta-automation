#!/usr/bin/env python3

import sys
import os
import json
import re
from pprint import pprint

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

from lib_py3.common import eprint, parse_name_possibly_json, get_named_hand_items

def usage():
    sys.exit("Usage: {} nbt_in.txt nbt_out.py".format(sys.argv[0]))

if len(sys.argv) != 3:
    usage()

def pop_if_present(spawner_entity, key):
    if isinstance(spawner_entity, nbt.TagCompound) and key in spawner_entity.value:
        print("Popping '{}' from spawner entity".format(key))
        spawner_entity.value.pop(key)

def remove_tags_from_spawner_entity(spawner_entity):
    pop_if_present(spawner_entity, 'Pos')
    pop_if_present(spawner_entity, 'Leashed')
    pop_if_present(spawner_entity, 'Air')
    pop_if_present(spawner_entity, 'OnGround')
    pop_if_present(spawner_entity, 'Dimension')
    pop_if_present(spawner_entity, 'Rotation')
    pop_if_present(spawner_entity, 'WorldUUIDMost')
    pop_if_present(spawner_entity, 'WorldUUIDLeast')
    pop_if_present(spawner_entity, 'HurtTime')
    pop_if_present(spawner_entity, 'HurtByTimestamp')
    pop_if_present(spawner_entity, 'FallFlying')
    pop_if_present(spawner_entity, 'PortalCooldown')
    pop_if_present(spawner_entity, 'FallDistance')
    pop_if_present(spawner_entity, 'DeathTime')
    pop_if_present(spawner_entity, 'HandDropChances')
    pop_if_present(spawner_entity, 'ArmorDropChances')
    pop_if_present(spawner_entity, 'CanPickUpLoot')
    pop_if_present(spawner_entity, 'Bukkit.updateLevel')
    pop_if_present(spawner_entity, 'Spigot.ticksLived')
    pop_if_present(spawner_entity, 'Paper.AAAB')
    pop_if_present(spawner_entity, 'Paper.Origin')
    pop_if_present(spawner_entity, 'Paper.FromMobSpawner')
    pop_if_present(spawner_entity, 'Team')

    # Recurse over passengers
    if (spawner_entity.has_path('Passengers')):
        remove_tags_from_spawner_entity(spawner_entity.at_path('Passengers'))

with open(sys.argv[1], 'r') as in_file:
    with open(sys.argv[2], 'w') as out_file:
        out_file.write("mobs_to_replace = [\n")

        line = in_file.readline()
        while line:
            if line[0] == "/":
                line = line[1:]
            if line.startswith("summon "):
                split = line.split(' ', 5)
                line = '{}id:"{}",{}'.format("{", split[1], split[5][1:])

            mob_nbt = nbt.TagCompound.from_mojangson(line)

            if not mob_nbt.has_path("id"):
                sys.exit("ERROR: mob does not have an id! : {}".format(line))

            remove_tags_from_spawner_entity(mob_nbt)

            mob_id = mob_nbt.at_path("id").value

            if mob_nbt.has_path("CustomName"):
                mob_name = parse_name_possibly_json(mob_nbt.at_path("CustomName").value)

                out_file.write("    {\n")
                out_file.write("        'rules': {\n")
                out_file.write("            'id': '{}',\n".format(mob_id))
                out_file.write("            'CustomName': r'''{}'''\n".format(mob_name))
                out_file.write("        },\n")
                out_file.write("        'mojangson': r'''{}''',\n".format(mob_nbt.to_mojangson()))
                out_file.write("    },\n")
            else:
                hand_items = get_named_hand_items(mob_nbt)

                if hand_items[0] is None and hand_items[1] is None:
                    sys.exit("ERROR: mob does not have a name or named HandItems! : {}".format(line))

                out_file.write("    {\n")
                out_file.write("        'rules': {\n")
                out_file.write("            'id': '{}',\n".format(mob_id))
                out_file.write("            'HandItems': {},\n".format(hand_items))
                out_file.write("        },\n")
                out_file.write("        'mojangson': r'''{}''',\n".format(mob_nbt.to_mojangson()))
                out_file.write("    },\n")

            line = in_file.readline()

        out_file.write("]\n")
