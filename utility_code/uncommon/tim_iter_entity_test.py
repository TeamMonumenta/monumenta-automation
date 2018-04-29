#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))

# TODO debug test
import pymclevel

# Import pymclevel from MCLevel-Unified
from pymclevel import nbt

from lib_monumenta.iter_entity import IterEntities

logData = {
    "root entities found":0,
    "root block entities found":0,
    "entities found":0,
    "block entities found":0,
    "unknown entities found":0,
    "players found":0,
    "errors occured":0
}

def testFunction(options=None,entityDetails=None):
    if type(entityDetails) is None:
        options["errors occured"] += 1
        return
    if entityDetails["root entity"] is True:
        if entityDetails["player file"] is not None:
            options["players found"] += 1
        elif entityDetails["entity type"] == "block entity":
            options["root block entities found"] += 1
        else:
            options["root entities found"] += 1
    else:
        if entityDetails["entity type"] == "unknown":
            options["unknown entities found"] += 1
        elif entityDetails["entity type"] == "block entity":
            options["block entities found"] += 1
        else:
            options["entities found"] += 1

test = IterEntities(["search spawners","search item entities"],testFunction,logData)

world = pymclevel.loadWorld("/home/tim/.minecraft/saves/Item Reset Test")
test.InWorld(world)

print ""
for key in sorted(logData.keys()):
    print key + ": " + str(logData[key])


