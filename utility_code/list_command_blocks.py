#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from lib_monumenta import list_command_blocks

################################################################################
# Config section

worldFolder = "/home/rock/tmp/Project Epic"
logFolder = "/home/rock/tmp/Project Epic Command Blocks"

################################################################################
# Main Code

# This scans for tile entities are command blocks
list_command_blocks.run(worldFolder,logFolder)


