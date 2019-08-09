#!/usr/bin/python3
import os
from lib_py3.scoreboard import Scoreboard
from r1plot_lookup import lut

score_rules = []

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

    score_rules.append(newRule)

tile_x = 0
for addr_entry in lut.address_to_coord.items():
    street_id,street_num = addr_entry[0]
    t0_x,t0_y,t0_z = addr_entry[1]

    for tile_z in range(-1,1+1):
        address = lut.pack_r1address(tile_x,tile_z,street_id,street_num)
        x,y,z = lut.coordinates_from_r1address( address )

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

        score_rules.append(newRule)

for shard in os.listdir('/home/epic/project_epic'):
    if (
        shard == 'server_config' or
        not os.path.isdir( os.path.join( '/home/epic/project_epic', shard ) ) or
        not os.path.isfile( os.path.join( '/home/epic/project_epic', shard, 'Project_Epic-' + shard, 'level.dat' ) ) or
        not os.path.isfile( os.path.join( '/home/epic/project_epic', shard, 'Project_Epic-' + shard, 'data', 'scoreboard.dat' ) )
    ):
        continue

    print(shard)
    scoreboard = Scoreboard( os.path.join( '/home/epic/project_epic', shard, 'Project_Epic-' + shard ) )
    scoreboard.batch_score_changes( score_rules )
    scoreboard.save()

