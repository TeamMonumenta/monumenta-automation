#!/usr/bin/env python
# -*- coding: utf-8 -*-

config = {
    "server":"lightblue",
    "localMainFolder":"/home/rock/4_SHARED/tmpreset/PRE_RESET/lightblue/Project_Epic-lightblue/",
    "localDstFolder":"/home/rock/4_SHARED/tmpreset/POST_RESET/lightblue/Project_Epic-lightblue/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],
    "playerScoreChanges":dungeonScoreRules,
    #"preserveInstance":{
    #    "dungeonScore":"D4Access",
    #    "targetRegion":{"x":-3, "z":-2},
    #},
    "tagPlayers":["MidTransfer","resetMessage"],
    "tpToSpawn":True,
    "itemReplacements":item_replace_list.KingsValley,
    "itemReplaceLocations":["players"],
    "itemLog":"/home/rock/4_SHARED/tmpreset/items_lightblue.txt",
}

