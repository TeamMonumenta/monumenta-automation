#!/usr/bin/env python3

# This searches for scores matching Condition, makes a list of Names
# appearing in the results, and runs actions for every name in the list.

world_dungeon_score_rules = [
    {"condition":{"Name":"$last","Objective":"D0Access"},
        "actions":{"set":[
            {"Objective":"D0Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D1Access"},
        "actions":{"set":[
            {"Objective":"D1Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D2Access"},
        "actions":{"set":[
            {"Objective":"D2Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D3Access"},
        "actions":{"set":[
            {"Objective":"D3Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D4Access"},
        "actions":{"set":[
            {"Objective":"D4Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D5Access"},
        "actions":{"set":[
            {"Objective":"D5Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D6Access"},
        "actions":{"set":[
            {"Objective":"D6Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D7Access"},
        "actions":{"set":[
            {"Objective":"D7Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D8Access"},
        "actions":{"set":[
            {"Objective":"D8Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D9Access"},
        "actions":{"set":[
            {"Objective":"D9Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D10Access"},
        "actions":{"set":[
            {"Objective":"D10Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D11Access"},
        "actions":{"set":[
            {"Objective":"D11Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"DCAccess"},
        "actions":{"set":[
            {"Objective":"DCAccess","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"DB1Access"},
        "actions":{"set":[
            {"Objective":"DB1Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"DRAccess"},
        "actions":{"set":[
            {"Objective":"DRAccess","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"DRL2Access"},
        "actions":{"set":[
            {"Objective":"DRL2Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"DS1Access"},
        "actions":{"set":[
            {"Objective":"DS1Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"DRDAccess"},
        "actions":{"set":[
            {"Objective":"DRDAccess","Score":0}]}},

]
