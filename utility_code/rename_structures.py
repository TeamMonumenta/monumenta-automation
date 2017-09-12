#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rename_structures_lib

################################################################################
# Config section

worldFolder = "/home/rock/tmp/Project Epic/"

# rename structures staring with old to start with new
renameList = [
    [ # A replacement
        # [old,new]
        "Rogue-", "rogue/"
    ],
    [ # Just in case someone used the wrong case
        "rogue-", "rogue/"
    ],
]

coordinatesToScan = (
    # ("region name",        (lowerCoordinate),  (upperCoordinate),  ( id, dmg), "block name (comment)"),
    ("main template region", (-30000, 0, -30000), (30000, 255,30000), (   7, 0 ), "bedrock"),
)

################################################################################
# Main Code

# This shows where the selected regions are, as your old script does.
# WARNING: This version saves in place!
#rename_structures_lib.fillRegions(worldFolder,coordinatesToScan)

# This scans for tile entities are command blocks
rename_structures_lib.rename(worldFolder,coordinatesToScan,renameList)


