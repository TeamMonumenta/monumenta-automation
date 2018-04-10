#!/usr/bin/env python
# -*- coding: utf-8 -*-

config = {
    "server":"r1bonus",
    "localMainFolder":"/home/rock/4_SHARED/tmpreset/PRE_RESET/r1bonus/Project_Epic-r1bonus/",
    "localDstFolder":"/home/rock/4_SHARED/tmpreset/POST_RESET/r1bonus/Project_Epic-r1bonus/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],
    "playerScoreChanges":dungeonScoreRules,
    #"preserveInstance":{
    #    "dungeonScore":"DB1Access",
    #    "targetRegion":{"x":-3, "z":-2},
    #},
    "tagPlayers":["MidTransfer","resetMessage"],
    "tpToSpawn":True,
    "itemReplacements":item_replace_list.KingsValley,
    "itemReplaceLocations":["players"],
    "itemLog":"/home/rock/4_SHARED/tmpreset/items_r1bonus.txt",
}

