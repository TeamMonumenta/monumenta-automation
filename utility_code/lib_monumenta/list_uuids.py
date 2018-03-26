#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import codecs

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
from pymclevel import nbt

from lib_monumenta.iter_entity import IterEntities
from lib_monumenta.mcUUID import mcUUID

def listUUIDs(world):
    allUUIDs = []
    entityIter = IterEntities(
        [
            "entities"
        ],
        _OnEntities,
        allUUIDs
    )
    entityIter.InWorld(world)
    return allUUIDs

def _OnEntities(allUUIDs,entityDetails):
    if entityDetails["entity type"] != "entity":
        return
    entity = entityDetails["entity"]
    if "uuidMost" not in entity:
        return
    uuidMost  = entity["uuidMost"]
    uuidLeast = entity["uuidLeast"]
    entityUUID = mcUUID(uuidMost,uuidLeast)
    allUUIDs.append(entityUUID)

