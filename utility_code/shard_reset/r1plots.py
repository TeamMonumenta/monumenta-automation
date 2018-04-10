#!/usr/bin/env python
# -*- coding: utf-8 -*-

config = {
    "server":"r1plots",

    "localMainFolder":"/home/rock/4_SHARED/tmpreset/PRE_RESET/r1plots/Project_Epic-r1plots/",
    "localDstFolder":"/home/rock/4_SHARED/tmpreset/POST_RESET/r1plots/Project_Epic-r1plots/",

    "copyBaseFrom":"main",

    "tagPlayers":["MidTransfer","resetMessage"],
    "playerScoreChanges":dungeonScoreRules,
    "blockReplacements":item_replace_list.blockReplacements,
    "blockReplaceLocations":["world",],
    "itemReplacements":item_replace_list.KingsValley,
    "itemReplaceLocations":["players", "world",],
    "entityUpdates":entity_update_list.KingsValley,
    "entityUpdateLocations":["world",],
    "itemLog":"/home/rock/4_SHARED/tmpreset/items_r1plots.txt",
}

