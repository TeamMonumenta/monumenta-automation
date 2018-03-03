#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Remove glowing effect from entities in world
"""
import os
import shutil
import sys


# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from pymclevel-Unified
import pymclevel
from pymclevel import nbt

from lib_monumenta.iter_entity import IterEntities

################################################################################
# Config section

worldFolder = "/home/rock/tmp/Project Epic"

################################################################################
# Function to run on each entity found

def _onEntity(args,entityDetails):
    # Check if tileEntity is being scanned
    mobs = args["mobs"]

    entity = entityDetails["entity"]
    entityType = entityDetails["entity type"]

    if entityType == "entity":
        if "ActiveEffects" in entity:
            ActiveEffects = entity["ActiveEffects"]
            for i in range(len(ActiveEffects)-1,-1,-1):
                Effect = ActiveEffects[i]
                if Effect["Id"] == 24:
                    ActiveEffects.pop(i)

################################################################################
# Main Code

print "Beginning scan..."
world = pymclevel.loadWorld(worldFolder)

# iterate over entities here
searchArgs = ["block entities","entities","search spawners"]
cmdIter = IterEntities( searchArgs, _onEntity, args )
cmdIter.InWorld(world)

world.saveInPlace()

print "Done."

