#!/usr/bin/env python3

import os

from lib_py3.world import World
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path

for filename in os.listdir("/home/epic/stage/project_epic"):
    world = None
    try:
        world = World("/home/epic/stage/project_epic/{0}/Project_Epic-{0}".format(filename))
    except:
        print("Failed to load world {}".format(filename))
        continue

    print("Processing {}...".format(filename))

    for item, source_pos, entity_path in world.items(readonly=True):
        if item.has_path("tag.display.Name") and item.has_path("tag.display.Lore") and item.has_path("tag.Enchantments"):
            shattered = False
            for it in item.at_path("tag.display.Lore").value:
                if "SHATTERED" in it.value:
                    shattered = True

            cov = False
            for enchant in item.at_path("tag.Enchantments").value:
                if enchant.has_path("id") and "vanish" in enchant.at_path("id").value:
                    cov = True

            if shattered and cov:
                print(get_debug_string_from_entity_path(entity_path, ansii_colors=True))
