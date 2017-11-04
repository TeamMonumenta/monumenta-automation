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

    # List of blocks to not copy over for the regions above
    "blockReplaceList":(
        ("minecraft:iron_block", "air"),
        ("minecraft:iron_ore", "air"),
        ("minecraft:hopper", "air"),
        #("minecraft:gold_block", "air"), # probably fine
        #("minecraft:gold_ore", "air"),
        ("minecraft:diamond_block", "air"),
        ("minecraft:diamond_ore", "air"),
        #("minecraft:emerald_block", "air"), # probably fine
        #("minecraft:emerald_ore", "air"),

        ("minecraft:beacon", "air"),

        # Not sure about this section
        #("enchanting_Table", "air"),
        #("quartz_ore", "air"),
        #("hopper", "air"),

        # anvils
        ((145,0), "air"),
        ((145,1), "air"),
        ((145,2), "air"),
        ((145,3), "air"),
        ((145,4), "air"),
        ((145,5), "air"),
        ((145,6), "air"),
        ((145,7), "air"),
        ((145,8), "air"),
        ((145,9), "air"),
        ((145,10), "air"),
        ((145,11), "air"),
    )
}

resetItemsInWorld(config)

