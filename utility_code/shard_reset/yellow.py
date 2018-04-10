#!/usr/bin/env python
# -*- coding: utf-8 -*-

config = {
    "server":"yellow",
    "localMainFolder":"/home/rock/4_SHARED/tmpreset/PRE_RESET/yellow/Project_Epic-yellow/",
    "localDstFolder":"/home/rock/4_SHARED/tmpreset/POST_RESET/yellow/Project_Epic-yellow/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],
    "playerScoreChanges":dungeonScoreRules,
    #"preserveInstance":{
    #    "dungeonScore":"D5Access",
    #    "targetRegion":{"x":-3, "z":-2},
    #},
    "tagPlayers":["MidTransfer","resetMessage"],
    "tpToSpawn":True,
    "itemReplacements":item_replace_list.KingsValley,
    "itemReplaceLocations":["players"],
    "itemLog":"/home/rock/4_SHARED/tmpreset/items_yellow.txt",
}

