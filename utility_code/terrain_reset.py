#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).
"""

from lib_monumenta.terrain_reset import terrainReset

from shard_reset import region_1, r1plots, betaplots, white, orange, magenta, lightblue, yellow, nightmare, r1bonus, roguelike

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
    nightmare.config,
    r1bonus.config,
    roguelike.config,
]

terrainReset(configList)
print "Saving items found after replacement to {}".format(itemCountLog)
print "Remember that tutorial, purgatory, bungee, and build are not handled by this script"

