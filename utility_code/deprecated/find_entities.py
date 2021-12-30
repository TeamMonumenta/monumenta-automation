#!/usr/bin/env python3

from pprint import pprint
from minecraft.world import World
from collections import OrderedDict
import yaml

def sum_children(items):
    pprint(items)
    count = 0
    for item in items:
        count += items[item]
    return count

if __name__ == '__main__':
    #w = World('/home/epic/project_epic/region_2/Project_Epic-region_2')
    #
    #entities_by_chunk = {}
    #world_totals = {}
    #
    #for region in w.iter_regions(read_only=True):
    #    for chunk in region.iter_chunks(autosave=False):
    #        chunk_key = f"{chunk.cx * 16},{chunk.cz * 16}"
    #        this_chunk_entities = entities_by_chunk.get(chunk_key, {})
    #        for entity in chunk.iter_entities():
    #            this_chunk_entities[entity.id] = this_chunk_entities.get(entity.id, 0) + 1
    #            world_totals[entity.id] = world_totals.get(entity.id, 0) + 1
    #        if len(this_chunk_entities) > 0:
    #            entities_by_chunk[chunk_key] = OrderedDict(sorted(this_chunk_entities.items(), key=lambda item: item[1], reverse=True))
    #
    #world_totals = OrderedDict(sorted(world_totals.items(), key=lambda item: item[1], reverse=True))
    #pprint(world_totals)
    #
    #entities_by_chunk = OrderedDict(sorted(entities_by_chunk.items(), key=lambda item: sum_children(item[1]), reverse=True))
    #
    #with open("r2_entities.yml", 'w') as fp:
    #    yaml.dump(entities_by_chunk, fp, width=2147483647)

    entities_by_chunk = {}
    with open("r2_entities.yml", 'r') as fp:
        entities_by_chunk = yaml.load(fp, Loader=yaml.FullLoader)

    pprint(entities_by_chunk)
