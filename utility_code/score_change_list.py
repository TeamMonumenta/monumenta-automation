#!/usr/bin/env python3

# This searches for scores matching Condition, makes a list of Names
# appearing in the results, and runs actions for every name in the list.

dungeon_score_rules = [
    {"condition":{"Objective":"D0Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D0Access","Score":1000}]}},
    {"condition":{"Objective":"D0Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D0Access","Score":0},
            {"Objective":"D0Finished","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D0Access"},
        "actions":{"set":[
            {"Objective":"D0Access","Score":0}]}},

    {"condition":{"Objective":"D1Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D1Access","Score":1000}]}},
    {"condition":{"Objective":"D1Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D1Access","Score":0},
            {"Objective":"D1Finished","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D1Access"},
        "actions":{"set":[
            {"Objective":"D1Access","Score":0}]}},

    {"condition":{"Objective":"D2Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D2Access","Score":1000}]}},
    {"condition":{"Objective":"D2Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D2Access","Score":0},
            {"Objective":"D2Finished","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D2Access"},
        "actions":{"set":[
            {"Objective":"D2Access","Score":0}]}},

    {"condition":{"Objective":"D3Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D3Access","Score":1000}]}},
    {"condition":{"Objective":"D3Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D3Access","Score":0},
            {"Objective":"D3Finished","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D3Access"},
        "actions":{"set":[
            {"Objective":"D3Access","Score":0}]}},

    {"condition":{"Objective":"D4Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D4Access","Score":1000}]}},
    {"condition":{"Objective":"D4Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D4Access","Score":0},
            {"Objective":"D4Finished","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D4Access"},
        "actions":{"set":[
            {"Objective":"D4Access","Score":0}]}},

    {"condition":{"Objective":"D5Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D5Access","Score":1000}]}},
    {"condition":{"Objective":"D5Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D5Access","Score":0},
            {"Objective":"D5Finished","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D5Access"},
        "actions":{"set":[
            {"Objective":"D5Access","Score":0}]}},

    {"condition":{"Objective":"D6Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D6Access","Score":1000}]}},
    {"condition":{"Objective":"D6Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D6Access","Score":0},
            {"Objective":"D6Finished","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D6Access"},
        "actions":{"set":[
            {"Objective":"D6Access","Score":0}]}},

    {"condition":{"Objective":"D7Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D7Access","Score":1000}]}},
    {"condition":{"Objective":"D7Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D7Access","Score":0},
            {"Objective":"D7Finished","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D7Access"},
        "actions":{"set":[
            {"Objective":"D7Access","Score":0}]}},

    {"condition":{"Objective":"D8Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D8Access","Score":1000}]}},
    {"condition":{"Objective":"D8Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D8Access","Score":0},
            {"Objective":"D8Finished","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D8Access"},
        "actions":{"set":[
            {"Objective":"D8Access","Score":0}]}},

    {"condition":{"Objective":"D9Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D9Access","Score":1000}]}},
    {"condition":{"Objective":"D9Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D9Access","Score":0},
            {"Objective":"D9Finished","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D9Access"},
        "actions":{"set":[
            {"Objective":"D9Access","Score":0}]}},

    {"condition":{"Objective":"D10Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D10Access","Score":1000}]}},
    {"condition":{"Objective":"D10Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D10Access","Score":0},
            {"Objective":"D10Finished","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"D10Access"},
        "actions":{"set":[
            {"Objective":"D10Access","Score":0}]}},

    {"condition":{"Objective":"DCAccess","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"DCAccess","Score":1000}]}},
    {"condition":{"Objective":"DCAccess","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"DCAccess","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"DCAccess"},
        "actions":{"set":[
            {"Objective":"DCAccess","Score":0}]}},

    {"condition":{"Objective":"DB1Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"DB1Access","Score":1000}]}},
    {"condition":{"Objective":"DB1Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"DB1Access","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"DB1Access"},
        "actions":{"set":[
            {"Objective":"DB1Access","Score":0}]}},

    {"condition":{"Objective":"DRAccess","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"DRAccess","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"DRAccess"},
        "actions":{"set":[
            {"Objective":"DRAccess","Score":0}]}},

    {"condition":{"Objective":"DS1Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"DS1Access","Score":1000}]}},
    {"condition":{"Objective":"DS1Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"DS1Access","Score":0}]}},
    {"condition":{"Objective":"DS1Finished","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"DS1Finished","Score":0}]}},
    {"condition":{"Name":"$last","Objective":"DS1Access"},
        "actions":{"set":[
            {"Objective":"DS1Access","Score":0}]}},
    {"condition":{"Objective":"VotesWeekly","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"VotesWeekly","Score":0}]}},

    {"condition":{"Objective":"MarketBanned","Score":{"min":1,"max":7}},
        "actions":{"set":[
            {"Objective":"MarketBanned","Score":0}]}},
    {"condition":{"Objective":"MarketBanned","Score":{"min":8}},
        "actions":{"add":[
            {"Objective":"MarketBanned","Score":-7}]}},
]

