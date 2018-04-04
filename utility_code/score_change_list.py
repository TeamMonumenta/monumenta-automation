#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yes, this could currently be a list of scores to reset globally.
# I've formatted it this way to prepare for making it possible to
# enter dungeons from the previous terrain reset.

# This searches for scores matching Condition, makes a list of Names
# appearing in the results, and runs actions for every name in the list.

dungeonScoreRules = [
    {
        "condition":{"Objective":"D1Access","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"D1Access","Score":0},
            {"Objective":"D1Finished","Score":0},
        ]},
    },
    {
        "condition":{"Objective":"D2Access","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"D2Access","Score":0},
            {"Objective":"D2Finished","Score":0},
        ]},
    },
    {
        "condition":{"Objective":"D3Access","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"D3Access","Score":0},
            {"Objective":"D3Finished","Score":0},
        ]},
    },
    {
        "condition":{"Objective":"D4Access","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"D4Access","Score":0},
            {"Objective":"D4Finished","Score":0},
        ]},
    },
    {
        "condition":{"Objective":"D5Access","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"D5Access","Score":0},
            {"Objective":"D5Finished","Score":0},
        ]},
    },
    {
        "condition":{"Objective":"DB1Access","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"DB1Access","Score":0},
        ]},
    },
    {
        "condition":{"Objective":"DRAccess","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"DRAccess","Score":0},
        ]},
    },
]

