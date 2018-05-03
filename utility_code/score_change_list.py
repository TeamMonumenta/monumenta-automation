#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This searches for scores matching Condition, makes a list of Names
# appearing in the results, and runs actions for every name in the list.

dungeonScoreRules = [
    {"condition":{"Objective":"D1Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D1Access","Score":1000}]}},
    {"condition":{"Objective":"D1Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D1Access","Score":0},
            {"Objective":"D1Finished","Score":0}]}},
    {"condition":{"Objective":"D2Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D2Access","Score":1000}]}},
    {"condition":{"Objective":"D2Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D2Access","Score":0},
            {"Objective":"D2Finished","Score":0}]}},
    {"condition":{"Objective":"D3Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D3Access","Score":1000}]}},
    {"condition":{"Objective":"D3Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D3Access","Score":0},
            {"Objective":"D3Finished","Score":0}]}},
    {"condition":{"Objective":"D4Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D4Access","Score":1000}]}},
    {"condition":{"Objective":"D4Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D4Access","Score":0},
            {"Objective":"D4Finished","Score":0}]}},
    {"condition":{"Objective":"D5Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"D5Access","Score":1000}]}},
    {"condition":{"Objective":"D5Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"D5Access","Score":0},
            {"Objective":"D5Finished","Score":0}]}},
    {"condition":{"Objective":"DCAccess","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"DCAccess","Score":1000}]}},
    {"condition":{"Objective":"DCAccess","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"DCAccess","Score":0}]}},
    {"condition":{"Objective":"DB1Access","Score":{"min":1}},
        "actions":{"add":[
            {"Objective":"DB1Access","Score":1000}]}},
    {"condition":{"Objective":"DB1Access","Score":{"min":2000}},
        "actions":{"set":[
            {"Objective":"DB1Access","Score":0}]}},
    {"condition":{"Objective":"DRAccess","Score":{"min":1}},
        "actions":{"set":[
            {"Objective":"DRAccess","Score":0}]}},
    {"condition":{"Objective":"Quest21","Score":{"min":102}},
        "actions":{"set":[
            {"Objective":"Quest21","Score":101}]}},
]

