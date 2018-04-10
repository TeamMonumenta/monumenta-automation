#!/usr/bin/env python
# -*- coding: utf-8 -*-

config = {
    "server":"magenta",
    "localMainFolder":"/home/rock/4_SHARED/tmpreset/PRE_RESET/magenta/Project_Epic-magenta/",
    "localDstFolder":"/home/rock/4_SHARED/tmpreset/POST_RESET/magenta/Project_Epic-magenta/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/", "data/"],
    "playerScoreChanges":dungeonScoreRules,
    #"preserveInstance":{
    #    "dungeonScore":"D3Access",
    #    "targetRegion":{"x":-3, "z":-2},
    #},
    "tagPlayers":["MidTransfer","resetMessage"],
    "tpToSpawn":True,
    "itemReplacements":item_replace_list.KingsValley,
    "itemReplaceLocations":["players"],
    "itemLog":"/home/rock/4_SHARED/tmpreset/items_magenta.txt",
}

