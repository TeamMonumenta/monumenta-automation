#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../"))

import item_replace_list
import entity_update_list
from score_change_list import dungeonScoreRules, dungeonScoreTestRules
from advancement_change_list import advancementRevokeList

config = {
    "server":"yellow",
    "localMainFolder":"/home/rock/4_SHARED/tmpreset/PRE_RESET/yellow/Project_Epic-yellow/",
    "localDstFolder":"/home/rock/4_SHARED/tmpreset/POST_RESET/yellow/Project_Epic-yellow/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],
    "playerScoreChanges":dungeonScoreTestRules,
    "playerScoreChangesTest":dungeonScoreRules,
    "preserveInstance":{
        "dungeonScore":"D5Access",
        "targetRegion":{"x":-3, "z":-2},
    },
    "tagPlayers":["MidTransfer","resetMessage"],
    "tpToSpawn":True,
    "itemReplacements":item_replace_list.KingsValley,
    "itemReplaceLocations":["players"],
    "itemLog":"/home/rock/4_SHARED/tmpreset/items_yellow.txt",
}

