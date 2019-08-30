#!/usr/bin/python3
from lib_py3.world import World

shards = {}

for shard in [
    'region_1',
    'dungeon',
]:
    shards[shard] = World('/home/epic/project_epic/'+shard+'/Project_Epic-'+shard+'/')

areas = [
    {
        "name":"white",
        "shard":"dungeon",
        "size":(160, 256, 352),
        "region":{"x":-3, "z":-2},
    },{
        "name":"orange",
        "shard":"dungeon",
        "size":(320, 120, 352),
        "region":{"x":-3, "z":-1},
    },{
        "name":"magenta",
        "shard":"dungeon",
        "size":(256, 256, 256),
        "region":{"x":-3, "z":0},
    },{
        "name":"lightblue",
        "shard":"dungeon",
        "size":(288, 256, 272),
        "region":{"x":-3, "z":1},
    },{
        "name":"yellow",
        "shard":"dungeon",
        "size":(256, 256, 256),
        "region":{"x":-3, "z":2},
    },{
        "name":"willows",
        "shard":"dungeon",
        "size":(288, 93, 368),
        "region":{"x":-3, "z":3},
    },{
        "name":"roguelike",
        "shard":"dungeon",
        "size":(464, 101, 464),
        "region":{"x":-2, "z":-1},
    },{
        "name":"reverie",
        "shard":"dungeon",
        "size":(382, 255, 476),
        "region":{"x":-3, "z":4},
    },{
        "name":"tutorial",
        "shard":"dungeon",
        "size":(80, 72, 96),
        "region":{"x":-2, "z":0},
    },{
        "name":"region_1",
        "shard":"region_1",
        "size":(6000, 255, 4000), # coordinates are a very rough estimate to cover all of Region 1
        "minimum_coordinate":{"x":-3072, "z":-2560},
    },
]

for area in areas:
    name = area['name']
    world = shards[ area['shard'] ]

    if 'region' in area:
        x = 512 * area['region']['x']
        y = 0
        z = 512 * area['region']['z']
    else:
        x = area['minimum_coordinate']['x']
        z = area['minimum_coordinate']['z']
        if 'y' in area['minimum_coordinate']:
            y = area['minimum_coordinate']['y']
        else:
            y = 0
    dx,dy,dz = area['size']

    total = world.dump_command_blocks( (x,y,z), (x+dx,y+dy,z+dz), '/home/epic/project_epic/server_config/data/commands_to_update/'+name+'.txt' )

    print( 'Scanned ' + name + ', found {} total command blocks (working or otherwise).'.format(total) )

