#!/usr/bin/env python
# -*- coding: utf-8 -*-

import disable_command_block_output_lib

################################################################################
# Config section

worldFolder = "/home/rock/tmp/Project Epic"

coordinatesToScan = (
    # ("region name",        (lowerCoordinate),  (upperCoordinate),  ( id, dmg), "block name (comment)"),
    ("main template region", (-30000, 0, -30000), (30000, 255,30000), (   7, 0 ), "bedrock"),
)

################################################################################
# Main Code

# This shows where the selected regions are, as your old script does.
# WARNING: This version saves in place!
#disable_command_block_output_lib.fillRegions(worldFolder,coordinatesToScan)

# This scans for tile entities are command blocks
disable_command_block_output_lib.run(worldFolder,coordinatesToScan)


