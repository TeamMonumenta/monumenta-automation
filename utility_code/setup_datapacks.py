#!/usr/bin/env python3

import os

from lib_py3.world import World

# When to enable the dungeon data pack
dungeons = ['white','orange','magenta','light_blue','yellow','r1bonus','roguelike','nightmare',]

for shard in os.listdir('/home/rock/project_epic'):
    if (
        shard == 'server_config' or
        not os.path.isdir( os.path.join( '/home/rock/project_epic', shard ) ) or
        not os.path.isfile( os.path.join( '/home/rock/project_epic', shard, 'Project_Epic-' + shard, 'level.dat' ) )
    ):
        continue

    datapacks = ['vanilla','file/bukkit','file/base']
    if shard in dungeons:
        datapacks.append('file/dungeon')
    if shard != 'dungeon':
        datapacks.append( 'file/' + shard )

    world = World( os.path.join( '/home/rock/project_epic', shard, 'Project_Epic-' + shard ) )
    world.enabled_data_packs = datapacks
    world.save_data_packs()
    world.save()

