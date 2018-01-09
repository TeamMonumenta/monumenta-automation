#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib_monumenta import list_spawner_mobs

################################################################################
# Config section

worldFolder = "/home/rock/tmp/Project Epic"
logFolder = "/home/rock/tmp/Project Epic Mob Spawners"

################################################################################
# Main Code

# This scans for tile entities are mob spawners
list_spawner_mobs.run(worldFolder,logFolder)


