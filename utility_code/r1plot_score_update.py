#!/usr/bin/python3
import os
from lib_py3.scoreboard import Scoreboard
from r1plot_lookup import lut

dungeonScoreRules = []

for plot in lut.plot_to_address.keys():
    address = lut.plot_to_address[plot]
    newRule = {
        "condition":{
            "Objective":"R1Plot",
            "Score":plot
        },
        "actions":{
            "set":[
                {
                    "Objective":"R1Address",
                    "Score":address
                }
            ]
        }
    }

    dungeonScoreRules.append(newRule)

tile_x = 0
for addr_entry in lut.address_to_coord:
    street_id = addr_entry[0]
    street_num = addr_entry[1]

    t0_x = addr_entry[2]
    t0_y = addr_entry[3]
    t0_z = addr_entry[4]

    for tile_z in range(-1,1+1):
        address = ( ( ( tile_x & 0xff ) * 256 + ( tile_z & 0xff ) ) * 32 + street_id ) * 128 + street_num
        x = t0_x + 768 * tile_x
        y = t0_y
        z = t0_x + 768 * tile_z

        newRule = {
            "condition":{
                "Objective":"R1Address",
                "Score":address
            },
            "actions":{"set":[
                {"Objective":"plotx","Score":x},
                {"Objective":"ploty","Score":y},
                {"Objective":"plotz","Score":z},
            ]}
        }

        dungeonScoreRules.append(newRule)

for shard in os.listdir('/home/rock/project_epic'):
    if (
        shard == 'server_config' or
        not os.path.isdir( os.path.join( '/home/rock/project_epic', shard ) ) or
        not os.path.isfile( os.path.join( '/home/rock/project_epic', shard, 'Project_Epic-' + shard, 'level.dat' ) ) or
        not os.path.isfile( os.path.join( '/home/rock/project_epic', shard, 'Project_Epic-' + shard, 'data', 'scoreboard.dat' ) )
    ):
        continue

    print(shard)
    scoreboard = Scoreboard( os.path.join( '/home/rock/project_epic', shard, 'Project_Epic-' + shard ) )

