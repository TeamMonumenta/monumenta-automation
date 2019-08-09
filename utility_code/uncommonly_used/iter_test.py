#!/usr/bin/env python3

import sys
import os
import pprint

from lib_py3.world import World
from lib_py3.common import eprint
from lib_py3.item_replacement_manager import ItemReplacementManager
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path

def iterprint(entity, pos, entity_path):
    try:
        print(get_debug_string_from_entity_path(entity_path, ansii_colors=True))

    except Exception as e:
        eprint("Exception!")
        entity.tree()
        raise(e)

#world = World("/home/epic/project_epic/mobs/Project_Epic-mobs")
world = World("Project_Epic-mobs")
lootmgr = LootTableManager()
lootmgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")
#lootmgr.load_world(world)
mgr = ItemReplacementManager(lootmgr.get_unique_item_map())

for item, source_pos, entity_path in world.items(readonly=False):
    #iterprint(item, source_pos, entity_path)
    mgr.replace_item(item)


#for entity, source_pos, entity_path in world.entity_iterator(pos1=(-922, 57, -1588), pos2=(-922, 57, -1588)):
#    iterprint(entity, source_pos, entity_path)
#for entity, source_pos, entity_path in world.entity_iterator(pos1=(-938, 57, -1588), pos2=(-922, 57, -1588)):
#    iterprint(entity, source_pos, entity_path)
#for entity, source_pos, entity_path in world.entity_iterator(pos1=(-1160,40,-1202), pos2=(-1149,34,-1209)):
#    iterprint(entity, source_pos, entity_path)
#for entity, source_pos, entity_path in world.entity_iterator(pos1=(-968,57,-1648), pos2=(-968,57,-1648)):
#    iterprint(entity, source_pos, entity_path)
#for entity, source_pos, entity_path in world.entity_iterator():
#    iterprint(entity, source_pos, entity_path)
#for item, pos in world.items():
    #iterprint(item, False, pos)

#minxregion = -3000//512 - 1
#minzregion = -4000//512 - 1
#maxxregion = 2000//512 + 1
#maxzregion = 2000//512 + 1
#for region in world.region_files:
#    if region[0] < minxregion or region[0] > maxxregion or region[1] < minzregion or region[1] > maxzregion:
#        print("rm", os.path.join(world.path, "region", "r.{}.{}.mca".format(region[0], region[1])))

