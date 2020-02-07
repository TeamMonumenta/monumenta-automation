#!/usr/bin/env python3

from lib_py3.world import World
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path

world = World("/home/epic/project_epic/region_2/Project_Epic-region_2")

for entity, source_pos, entity_path in world.entity_iterator(readonly=True):
    if entity.has_path("CustomName"):
        if "Moon Brute" in entity.at_path("CustomName").value:
            print(get_debug_string_from_entity_path(entity_path, ansii_colors=True))
