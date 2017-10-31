#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Player scoreboard tag library
"""

import os

from mclevel import nbt

def listUniqueTags(worldDir):
    """
    Prints every tag applied to a player,
    but not which players have which tags,
    nor the number of occurances of each tag
    """
    tags = set()

    for playerFile in os.listdir(worldDir+"playerdata"):
        playerFile = worldDir + "playerdata/" + playerFile
        try:
            player = nbt.load(playerFile)
        except:
            print "*** Could not open " + playerFile
            continue
        if "Tags" not in player:
            continue
        tags.update([tag.value for tag in player["Tags"]])

    print sorted(tags)
    #for tag in sorted(tags):
    #    print tag

def deleteTheseTags(worldDir,tagsToDelete):
    """
    For every player, if they have a
    tag in tagsToDelete, delete that tag.
    """
    playerPaths = os.listdir(worldDir+"playerdata")
    playerCount = len(playerPaths)
    playerNumber = 0

    for playerFile in playerPaths:
        playerNumber += 1
        #print "[{}/{}] {}".format(playerNumber,playerCount,playerFile)
        playerFile = worldDir + "playerdata/" + playerFile
        try:
            player = nbt.load(playerFile)
        except:
            print "*** Could not open " + playerFile
            continue
        if "Tags" not in player:
            continue
        playerTags = player["Tags"]
        for i in range(len(playerTags)-1,-1,-1):
            if playerTags[i].value in tagsToDelete:
                playerTags.pop(i)
        player.save(playerFile)

def deleteOtherTags(worldDir,tagsToKeep):
    """
    For every player, if they have a
    tag in tagsToDelete, delete that tag.
    """
    playerPaths = os.listdir(worldDir+"playerdata")
    playerCount = len(playerPaths)
    playerNumber = 0

    for playerFile in playerPaths:
        playerNumber += 1
        #print "[{}/{}] {}".format(playerNumber,playerCount,playerFile)
        playerFile = worldDir + "playerdata/" + playerFile
        try:
            player = nbt.load(playerFile)
        except:
            print "*** Could not open " + playerFile
            continue
        if "Tags" not in player:
            continue
        playerTags = player["Tags"]
        for i in range(len(playerTags)-1,-1,-1):
            if playerTags[i].value not in tagsToKeep:
                playerTags.pop(i)
        player.save(playerFile)


