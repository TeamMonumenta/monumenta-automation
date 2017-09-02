#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tools useful for modifying scoreboard values
"""
# Required libraries have links where not part of a standard Python install.
import os
import shutil
import time # Just for efficient display purposes when processing large amounts of data

import numpy
from numpy import zeros, bincount
import itertools

# These are expected in your site-packages folder, see:
# https://stackoverflow.com/questions/31384639/what-is-pythons-site-packages-directory
from pymclevel import nbt

################################################################################
# Config section

# The world folder to edit the scoreboard values for
#worldFolder = "/home/rock/tmp/Project Epic"
worldFolder = "/home/rock/tmp/project_epic/region_1/Project_Epic/"

# Dictionary of name changes to move scoreboard
# values from one IGN to another (case sensitive)
# Verify name changes with:
# https://api.mojang.com/users/profiles/minecraft/<Current_IGN>
# https://api.mojang.com/user/profiles/<UUID>/names
# Another bad example:
# https://api.mojang.com/users/profiles/minecraft/NickNackGus
# https://api.mojang.com/user/profiles/25c8b7fadd4a4bbb8cf9d534cf66d6f9/names
IGNReplacements = {
    "dinnerbone":"NickNackGus", # Normally, an index is in [], but a string is a list!
    # There, proof dinnerbone played in my singleplayer world...sorta.
}

################################################################################
# Function definitions

def scoreboardPath(worldFolder):
    if worldFolder[-1] != "/":
        worldFolder = worldFolder + "/"
    return worldFolder + "data/scoreboard.dat"

################################################################################
# Functions that display stuff while they work

def getUniqueValues(worldFolder,objective):
    filePath = scoreboardPath(worldFolder)
    scoreboard = nbt.load(filePath)
    scores = set()
    for aScore in scoreboard["data"]["PlayerScores"]:
        if aScore["Objective"].value == objective:
            print aScore["Score"].value, "-", aScore["Name"].value
            print #scores.add(aScore["Score"].value)
    #print sorted(scores)

def updateIGNs(worldFolder,replacementList):
    # Good news! Scoreboard tags are stored in each player.dat
    # Just need to move the scores to the new player.
    print "Updating IGNs, one moment..."
    filePath = scoreboardPath(worldFolder)
    scoreboard = nbt.load(filePath)

    lastDisplayedTime = int(time.time())
    numChanged = 0

    for aScore in scoreboard["data"]["PlayerScores"]:
        aScoreOwner = aScore["Name"].value
        if aScoreOwner in replacementList:
            aScore["Name"].value = replacementList[aScoreOwner]
            numChanged+=1
        if lastDisplayedTime != int(time.time()):
            print "{0} score owners changed.".format(numChanged)
            lastDisplayedTime = int(time.time())
    print "{0} score owners changed.".format(numChanged)
    print "Updated all objective owners."

    print "Checking teams..."
    # Not displaying updates as we go here;
    # This list is much shorter to handle.
    for aTeam in scoreboard["data"]["Teams"]:
        for aPlayer in aTeam["Players"]:
            ign = aPlayer.value
            if ign in replacementList:
                aPlayer.value = replacementList[ign]
    print "Players moved to correct teams."
    scoreboard.save(filePath)
    print "Saved."

################################################################################
# Main Code

# Get unique values for a given objective, ie for plots or apartments.
getUniqueValues(worldFolder,objective="Plot")

# updateIGNs within the scoreboard
#updateIGNs(worldFolder,IGNReplacements)


