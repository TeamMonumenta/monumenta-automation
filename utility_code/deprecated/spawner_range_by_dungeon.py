#!/usr/bin/env python3

from pprint import pprint
from collections import OrderedDict

from lib_py3.common import eprint, get_entity_name_from_nbt
from lib_py3.world import World

dungeons = (
        {
            "name":"white",
            "region":{"x":-3, "z":-2},
        },{
            "name":"orange",
            "region":{"x":-3, "z":-1},
        },{
            "name":"magenta",
            "region":{"x":-3, "z":0},
        },{
            "name":"lightblue",
            "region":{"x":-3, "z":1},
        },{
            "name":"yellow",
            "region":{"x":-3, "z":2},
        },{
            "name":"lime",
            "region":{"x":-3, "z":5},
        },{
            "name":"pink",
            "region":{"x":-3, "z":7},
        },{
            "name":"gray",
            "region":{"x":-3, "z":6},
        },{
            "name":"cyan",
            "region":{"x":-3, "z":9},
        },{
            "name":"lightgray",
            "region":{"x":-3, "z":8},
        },{
            "name":"purple",
            "region":{"x":-3, "z":13},
        },{
            "name":"teal",
            "region":{"x":-2, "z":12},
        },{
            "name":"forum",
            "region":{"x":-3, "z":16},
        },{
            "name":"willows",
            "region":{"x":-3, "z":3},
        },{
            "name":"reverie",
            "region":{"x":-3, "z":4},
        },{
            "name":"tutorial",
            "region":{"x":-2, "z":0},
        },{
            "name":"sanctum",
            "region":{"x":-3, "z":12},
        },{
            "name":"labs",
            "region":{"x":-2, "z":2},
        },
)

world = World('/home/epic/project_epic/dungeon/Project_Epic-dungeon')

for dungeon in dungeons:
    dungeonName = dungeon["name"]
    pos1 = (dungeon["region"]["x"] * 512, 0, dungeon["region"]["z"] * 512)
    pos2 = ((dungeon["region"]["x"] + 1) * 512, 255, (dungeon["region"]["z"] + 1) * 512)

    counts = OrderedDict();
    dungeonTotal = 0
    for entity, source_pos, entity_path in world.entity_iterator(pos1=pos1, pos2=pos2, readonly=True):
        if source_pos is not None and entity.has_path('MinSpawnDelay') and entity.has_path('MaxSpawnDelay') and entity.has_path("SpawnPotentials"):
            key = "{}-{}".format(entity.at_path('MinSpawnDelay').value, entity.at_path('MaxSpawnDelay').value)

            if key in counts:
                data = counts[key]
            else:
                data = OrderedDict()
                counts[key] = data

            if entity.has_path("SpawnPotentials[0]") and entity.at_path("SpawnPotentials[0]").has_path("Entity"):
                spawnedEntity = entity.at_path("SpawnPotentials[0]").at_path("Entity")
                name = get_entity_name_from_nbt(spawnedEntity)
                if name is None:
                    name = spawnedEntity.at_path("id").value

            if name in data:
                data[name] += 1
            else:
                data[name] = 1
            dungeonTotal += 1

    print("{}: {} spawners".format(dungeonName, dungeonTotal))
    continue
    counts = OrderedDict(sorted(counts.items(), key=lambda kv: (int(kv[0].split("-")[0]) + int(kv[0].split("-")[1])), reverse=False))
    for key in counts:
        value = counts[key]
        value = OrderedDict(sorted(value.items(), key=lambda kv: kv[1]), reverse=False)
        total = 0;
        for item in value:
            total += value[item]

        print("  {}: {}".format(key, total))

        for item in value:
            print("    {}: {}".format(item, value[item]))
