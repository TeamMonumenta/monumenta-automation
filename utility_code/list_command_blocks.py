#!/usr/bin/env python
# -*- coding: utf-8 -*-

import list_command_blocks_lib

################################################################################
# Config section

worldFolder = "/home/rock/tmp/Project Epic"
logFolder = "/home/rock/tmp/Project Epic Command Blocks"

coordinatesToScan = (
    # ("region name",        (lowerCoordinate),  (upperCoordinate),  ( id, dmg), "block name (comment)"),
    ("main template region", (-30000, 0, -30000), (30000, 255,30000), (   7, 0 ), "bedrock"),
)

################################################################################
# Main Code

# This shows where the selected regions are, as your old script does.
# WARNING: This version saves in place!
#list_command_blocks_lib.fillRegions(worldFolder,coordinatesToScan)

# This scans for tile entities are command blocks
list_command_blocks_lib.run(worldFolder,coordinatesToScan,logFolder)


