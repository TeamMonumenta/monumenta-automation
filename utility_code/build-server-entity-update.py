#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This updates entities within the build server
"""

import os
import sys

# The effective working directory for this script must always be the MCEdit-Unified directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
import pymclevel

import entity_update_list

worldDir = "/home/rock/project_epic/test/Project_Epic-test/"
world = pymclevel.loadWorld(worldDir)
entity_update_list.KingsValleyBuild.InWorld(world)
world.saveInPlace()

