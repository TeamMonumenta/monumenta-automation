#!/usr/bin/env python
# -*- coding: utf-8 -*-

config = {
    "server":"orange",
    "localMainFolder":"/home/rock/4_SHARED/tmpreset/PRE_RESET/orange/Project_Epic-orange/",
    "localDstFolder":"/home/rock/4_SHARED/tmpreset/POST_RESET/orange/Project_Epic-orange/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],
    "playerScoreChanges":dungeonScoreRules,
    #"preserveInstance":{
    #    "dungeonScore":"D2Access",
    #    "targetRegion":{"x":-3, "z":-2},
    #},
    "tagPlayers":["MidTransfer","resetMessage"],
    "tpToSpawn":True,
    "itemReplacements":item_replace_list.KingsValley,
    "itemReplaceLocations":["players"],
    "itemLog":"/home/rock/4_SHARED/tmpreset/items_orange.txt",
}

