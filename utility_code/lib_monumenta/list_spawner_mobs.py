#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
This lists the command block tile entities.
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
# Functions that display stuff while they work

def _onEntity(args,entityDetails):
    # Check if tileEntity is being scanned
    mobs = args["mobs"]

    entity = entityDetails["entity"]
    entityType = entityDetails["entity type"]

    if entityType == "entity":
        originalJson = entity.json()

        # entity nbt has a different name if it's in
        # spawn potentials or spawn data; remove
        # that difference so they merge.
        cloneEntity = nbt.json_to_tag(originalJson)
        if "id" not in cloneEntity:
            cloneEntity = cloneEntity[cloneEntity.keys()[0]]
        cloneEntity.name = ""
        noTagNameJson = cloneEntity.json(["CustomName","id","Tags","Passengers"])

        # Get the mob's name, if it exists
        mobName = None
        if "CustomName" in cloneEntity:
            mobName=cloneEntity["CustomName"].value

        # Create set for entity's name if needed
        if mobName not in mobs:
            mobs[mobName] = set()

        mobs[mobName].add(noTagNameJson)

def run(worldFolder,logFile):
    print "Beginning scan..."
    world = pymclevel.loadWorld(worldFolder)

    mobs = {}

    args = {
        "world":world,
        "mobs":mobs,
    }

    # iterate over entities here
    cmdIter = IterEntities( ["block entities","search spawners"], _onEntity, args )
    cmdIter.InWorld(world)

    strBuffer = u""
    for mobName in sorted(mobs.keys()):
        mobNameStr = mobName
        if mobName is None:
            mobNameStr = u"Unnamed mobs"
        print mobNameStr
        strBuffer += u"="*80 + u"\n" + mobNameStr + u"\n\n"
        for mob in sorted(mobs[mobName]):
            strBuffer += mob + u"\n\n"

    f = open(logFile,"w")
    f.write(strBuffer.encode('utf8'))
    f.close()

    print "Done."

