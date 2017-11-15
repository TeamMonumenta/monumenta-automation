#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# The effective working directory for this script must always be the MCEdit-Unified directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
import pymclevel

from lib_monumenta import item_replace
from item_replace_list import itemReplacements

################################################################################
# Function definitions

print "Opening Destination World..."
dstWorld = pymclevel.loadWorld("/home/rock/project_epic/test/Project_Epic-test")

print "Replacing items in the world..."
itemReplacements.InWorld(dstWorld)

print "Saving...."
dstWorld.saveInPlace()

print "Done!"

