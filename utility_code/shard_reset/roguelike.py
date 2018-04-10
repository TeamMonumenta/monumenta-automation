#!/usr/bin/env python
# -*- coding: utf-8 -*-

config = {
    "server":"roguelike",
    "localMainFolder":"/home/rock/4_SHARED/tmpreset/PRE_RESET/roguelike/Project_Epic-roguelike/",
    "localDstFolder":"/home/rock/4_SHARED/tmpreset/POST_RESET/roguelike/Project_Epic-roguelike/",
    "copyMainFolders":["advancements/", "playerdata/", "stats/"],
    "copyMainFiles":["data/scoreboard.dat","data/villages.dat","data/villages_end.dat","data/advancements","data/functions","data/loot_tables"],
    "playerScoreChanges":dungeonScoreRules,
    "tagPlayers":["MidTransfer","resetMessage"],
    "tpToSpawn":True,
    "itemReplacements":item_replace_list.KingsValley,
    "itemReplaceLocations":["players"],
    "itemLog":"/home/rock/4_SHARED/tmpreset/items_roguelike.txt",
}

