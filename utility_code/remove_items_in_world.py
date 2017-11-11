#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# The effective working directory for this script must always be the MCEdit-Unified directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
import pymclevel

import lib_item_replace
import item_replace_list

################################################################################
# Function definitions

print "Compiling item replacement list..."
compiledItemReplacementList = lib_item_replace.allReplacements(item_replace_list.itemReplacements)

print "Opening Destination World..."
dstWorld = pymclevel.loadWorld("/home/rock/project_epic/test/Project_Epic-test")

print "Replacing items in the world..."
lib_item_replace.replaceItemsInWorld(dstWorld, compiledItemReplacementList)

print "Saving...."
dstWorld.saveInPlace()

print "Done!"


