#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This takes a main world (play area), handles item
replacement, and saves to dstWorld (destination).
"""

from lib_world_item_replacements import resetItemsInWorld

config = {
    # Dst is the destination world, which gets overwritten by the build world.
    # Then, data from the main world replaces the relevant parts of the dst world.
    # Please note that no special care need be taken with whitespace in filenames.
    "localMainFolder":"/home/rock/tmp/PRE_RESET/r1plots/Project_Epic-r1plots/",
    "localDstFolder":"/home/rock/tmp/POST_RESET/r1plots/Project_Epic-r1plots/",

    # No 0.5 offset here, add it yourself if you like.
    # (x,y,z,ry,rx)
    # Shouldn't be needed, as players are safe in plot worlds.
    #"safetyTpLocation":(-1450, 241, -1498, 270.0, 0.0),

    "coordinatesToFill":(
        {"name":"Magic Block", "pos1":(-1441, 2,-1441), "pos2":(-1441, 2,-1441),
            "replace":True, "material":(0, 0), "materialName":"air"},
    ),
}

resetItemsInWorld(config)

