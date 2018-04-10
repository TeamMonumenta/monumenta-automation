#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).
"""

from lib_monumenta.terrain_reset import terrainReset
import item_replace_list
import entity_update_list
from score_change_list import dungeonScoreRules
from advancement_change_list import advancementRevokeList

from shard_reset import region_1, r1plots, betaplots, white, orange, magenta, lightblue, yellow, r1bonus, roguelike

itemCountLog = "/home/rock/4_SHARED/tmpreset/all_items.txt"

configList = [
    region_1.config,
    r1plots.config,
    betaplots.config,
    white.config,
    orange.config,
    magenta.config,
    lightblue.config,
    yellow.config,
    r1bonus.config,
    roguelike.config,
]

terrainReset(configList)
print "Saving items found after replacement to {}".format(itemCountLog)
# Save this for when the item count stuff is working
#item_replace_list.KingsValley.SaveGlobalLog(itemCountLog)
print "Remember that tutorial, purgatory, bungee, and build are not handled by this script"

