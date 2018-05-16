#!/usr/bin/env python2.7
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
    return list(set(allUUIDs))

def _OnEntities(allUUIDs,entityDetails):
    if entityDetails["entity type"] != "entity":
        return
    entity = entityDetails["entity"]
    if "UUIDMost" not in entity:
        return
    UUIDMost  = entity["UUIDMost"].value
    UUIDLeast = entity["UUIDLeast"].value
    entityUUID = mcUUID( (UUIDMost,UUIDLeast) )
    allUUIDs.append(entityUUID)

