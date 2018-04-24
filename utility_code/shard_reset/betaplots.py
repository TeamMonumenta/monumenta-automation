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
    "server":"betaplots",

    "localMainFolder":"/home/rock/4_SHARED/tmpreset/PRE_RESET/betaplots/Project_Epic-betaplots/",
    "localDstFolder":"/home/rock/4_SHARED/tmpreset/POST_RESET/betaplots/Project_Epic-betaplots/",

    "copyBaseFrom":"main",

    "tagPlayers":["MidTransfer","resetMessage"],
    "playerScoreChanges":dungeonScoreRules,
    "blockReplacements":item_replace_list.blockReplacements,
    "blockReplaceLocations":["world",],
    "itemReplacements":item_replace_list.KingsValley,
    "itemReplaceLocations":["players", "world",],
    "entityUpdates":entity_update_list.KingsValley,
    "entityUpdateLocations":["world",],
    "itemLog":"/home/rock/4_SHARED/tmpreset/items_betaplots.txt",
}

