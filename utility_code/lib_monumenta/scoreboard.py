#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tools useful for modifying scoreboard values
"""
# Required libraries have links where not part of a standard Python install.
import os
import shutil
import sys
import time # Just for efficient display purposes when processing large amounts of data

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from pymclevel-Unified
from pymclevel import nbt

################################################################################
# Function definitions

def scoreboardPath(worldFolder):
    if worldFolder[-1] != "/":
        worldFolder = worldFolder + "/"
    return worldFolder + "data/scoreboard.dat"

################################################################################
# Functions that display stuff while they work

class scoreboard(object):
    def __init__(self,worldFolder):
        self.load(worldFolder)

    def load(self,worldFolder):
        self.filePath = scoreboardPath(worldFolder)
        self.nbt = nbt.load(self.filePath)
        self.allScores = self.nbt['data']['PlayerScores']

    def save(self,worldFolder=None):
        if worldFolder is None:
            saveTo = self.filePath
        else:
            saveTo = worldFolder + "data/scoreboard.dat"
        self.nbt.save(saveTo)

    def searchScores(self,Conditions={},Name=None,Objective=None,Score=None,Locked=None):
        if "Name" in Conditions:
            Name = Conditions["Name"]
        if "Objective" in Conditions:
            Objective = Conditions["Objective"]
        if "Score" in Conditions:
            Score = Conditions["Score"]
        if "Locked" in Conditions:
            Locked = Conditions["Locked"]
        matchingScores = []
        for _aScore in self.allScores:
            if (
                Name is not None and
                _aScore['Name'].value != Name
            ):
                continue
            if (
                Objective is not None and
                _aScore['Objective'].value != Objective
            ):
                continue
            if (
                type(Score) is int and
                _aScore['Score'].value != Score
            ):
                continue
            if (
                type(Score) is list and
                _aScore['Score'].value not in Score
            ):
                continue
            if (
                type(Score) is dict and
                "min" in Score and
                _aScore['Score'].value < Score["min"]
            ):
                continue
            if (
                type(Score) is dict and
                "max" in Score and
                _aScore['Score'].value > Score["max"]
            ):
                continue
            if (
                Locked is not None and
                _aScore['Locked'].value != Locked
            ):
                continue
            matchingScores.append(_aScore)
        return matchingScores

    def resetScores(self,Name=None,Objective=None,Score=None,Locked=None):
        """
        Reset all scores matching the specified criteria
        """
        numEntries = len(self.allScores)
        for i in range(numEntries-1,-1,-1):
            _aScore = self.allScores[i]
            if (
                Name is not None and
                _aScore['Name'].value != Name
            ):
                continue
            if (
                Objective is not None and
                _aScore['Objective'].value != Objective
            ):
                continue
            if (
                type(Score) is int and
                _aScore['Score'].value != Score
            ):
                continue
            if (
                type(Score) is list and
                _aScore['Score'].value not in Score
            ):
                continue
            if (
                type(Score) is dict and
                "min" in Score and
                _aScore['Score'].value < Score["min"]
            ):
                continue
            if (
                type(Score) is dict and
                "max" in Score and
                _aScore['Score'].value > Score["max"]
            ):
                continue
            if (
                Locked is not None and
                _aScore['Locked'].value != Locked
            ):
                continue
            self.allScores.pop(i)

    def getScore(self,Name,Objective,Fallback=None):
        """
        Return Name's score for Objective;
        if not found, return Fallback
        """
        matches = self.searchScores(Name=Name,Objective=Objective)
        if len(matches) > 1:
            raise NotImplemented('{} has {} scores for objective {}. This must be resolved manually.'.format(Name,len(matches),Objective))
        elif len(matches) == 1:
            return matches[0]['Score'].value
        elif len(matches) == 0:
            return Fallback

    def setScore(self,Name,Objective,Score):
        matches = self.searchScores(Name=Name,Objective=Objective)
        if len(matches) > 1:
            raise NotImplemented('{} has {} scores for objective {}. This must be resolved manually.'.format(Name,len(matches),Objective))
        elif len(matches) == 1:
            matches[0]['Score'].value = Score
        elif len(matches) == 0:
            newScore = nbt.TAG_Compound()
            newScore['Objective'] = nbt.TAG_String(Objective)
            newScore['Locked'] = nbt.TAG_Byte(0)
            newScore['Score'] = nbt.TAG_Int(Score)
            newScore['Name'] = nbt.TAG_String(Name)
            self.allScores.append(newScore)

    def pruneMissingEntities(self,entitiesToKeep):
        """
        Player names cannot exceed 16 characters; UUID's are
        always 36 characters (4 hyphens and 32 hexadecimal digits).
        This deletes entities that have UUID's not found in entitiesToKeep
        """
        uuidsToKeep = []
        for entity in entitiesToKeep:
            uuidsToKeep.append(str(entity))
        numEntries = len(self.allScores)
        prunedDryRun = 0
        for i in range(numEntries-1,-1,-1):
            aScore = self.allScores[i]
            owner = aScore["Name"].value
            if (
                len(owner) == 36 and
                owner not in uuidsToKeep
            ):
                prunedDryRun += 1
                #self.allScores.pop(i)
        print "    - Dry run; scores not affected."
        print "    - {} entities found.".format(len(uuidsToKeep))
        if len(uuidsToKeep) > 0:
            print "    - Example UUID: {}".format(uuidsToKeep[0])
        print "    - {} scores pruned.".format(prunedDryRun)

    def batchScoreChanges(self,rules):
        for aRule in rules:
            matchedConditions = self.searchScores(Conditions=aRule["condition"])
            for aMatchingScore in matchedConditions:
                Name = aMatchingScore["Name"].value
                if "set" in aRule["actions"]:
                    for toSet in aRule["actions"]["set"]:
                        Objective = toSet["Objective"]
                        Score = toSet["Score"]
                        self.setScore(Name,Objective,Score)

################################################################################
# These are legacy functions that should be merged into the Scoreboard class
# or otherwise removed. To be decided.
# Due to what is probably a naming mistake, leaving these uncommented results
# in Python hanging while trying to import this library. Oops.
'''
def getObjectiveValues(worldFolder,objective):
    """
    For a given objective name, find any value of
    that objective and print who has which values
    """
    filePath = scoreboardPath(worldFolder)
    scoreboard = nbt.load(filePath)
    for aScore in scoreboard["data"]["PlayerScores"]:
        if aScore["Objective"].value == objective:
            print aScore["Score"].value, "-", aScore["Name"].value

def findMatchingObjectiveScores(worldFolder,objective,matchingScores=range(-2147483648,2147483648)):
    """
    For a given objective name,
    list players whose values are
    in the list of selected values
    scores is a list, such as
    [3,5,8]
    range(7,9+1) # for 7 through 9
    the default is any score
    """
    filePath = scoreboardPath(worldFolder)
    scoreboard = nbt.load(filePath)

    found = {}

    for aScore in scoreboard["data"]["PlayerScores"]:
        if aScore["Objective"].value == objective:
            if aScore["Score"].value in matchingScores:
                found[aScore["Name"].value] = aScore["Score"].value

    return found

def updateIGNs(worldFolder,replacementList):
    """
    For any scoreboard value matching oldName, update to newName
    replacementList["oldName"] = "newName"
    """
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

def debugScoreboard(worldFolder):
    """
    Print any errors in scoreboard.dat
    Do not use this yet, it's incomplete and untested.
    """
    # playerObjectives[objective][name][#] = {"Score":#,"Locked":bool}
    # This is to detect duplicate scores for the same player,
    # which would indicate something is wrong with a plugin
    # or modification
    playerObjectives = {}
    # set to speed up search for duplicates
    # playerObjectiveDuplicates[#] = {"Objective":objective:,"Name":name}
    playerObjectiveDuplicates = set()
    # playerObjectiveUndeclared[#] = objective
    playerObjectiveUndeclared = set()

    # format is validObjectives[objective][#] = objective
    # Used to detect duplicates
    validObjectives = {}
    # set to speed up search for duplicates
    # objectiveDuplicates[#] = objective
    objectiveDuplicates = set()

    print "Loading scoreboard.dat..."
    filePath = scoreboardPath(worldFolder)
    scoreboard = nbt.load(filePath)

    print "Checking objective list..."
    for objective in scoreboard["Objectives"]:
        objectiveName = objective["Name"].value
        if objectiveName in validObjectives:
            validObjectives[objectiveName].append(objective)
            objectiveDuplicates.add(objectiveName)
        else:
            validObjectives[objectiveName] = [objective]

    slotNames = {
        "slot_0":"list",
        "slot_1":"sidebar",
        "slot_2":"belowName",
        "slot_3":"sidebar.team.black",
        "slot_4":"sidebar.team.dark_blue",
        "slot_5":"sidebar.team.dark_green",
        "slot_6":"sidebar.team.dark_aqua",
        "slot_7":"sidebar.team.dark_red",
        "slot_8":"sidebar.team.dark_purple",
        "slot_9":"sidebar.team.gold",
        "slot_10":"sidebar.team.gray",
        "slot_11":"sidebar.team.dark_gray",
        "slot_12":"sidebar.team.blue",
        "slot_13":"sidebar.team.green",
        "slot_14":"sidebar.team.aqua",
        "slot_15":"sidebar.team.red",
        "slot_16":"sidebar.team.light_purple",
        "slot_17":"sidebar.team.yellow",
        "slot_18":"sidebar.team.white",
    }

    for displaySlot in scoreboard["DisplaySlots"]:
        if displaySlot.value not in validObjectives.keys():
            print 'Slot {} "{}" contains unknown objective {}'.format(
                displaySlot.name,
                slotNames[displaySlot.name],
                displaySlot.value
            )

    if len(objectiveDuplicates) > 0:
        print "*** Some objectives are entered multiple times:"
    for objective in sorted(objectiveDuplicates):
        duplicates = validObjectives[objective]
        numOccurances = len(occurances)
        print "*** {} appears {} times:".format(objective,numOccurances)
        for i in range(numOccurances):
            duplicate = duplicates[i]
            print "*** [{}/{}] {}".format(
                i,
                numOccurances,
                duplicate.json()
            )

    print "Checking player scores..."
    for entry in ["PlayerScores"]:
        objective = entry["Objective"].value
        name = entry["Name"].value
        score = entry["Score"].value
        # for triggers
        if "Locked" not in entry:
            locked = None
        elif entry["Locked"].value:
            locked = True
        else:
            locked = False
        playerObjectives[objective][name].append({"Score":score,"Locked":locked})
        if len(playerObjectives[objective][name]) > 1:
            playerObjectiveDuplicates.add({"Objective":objective:,"Name":name})
        if objective not in validObjectives.keys():
            playerObjectiveUndeclared.add(objective)

    if len(playerObjectiveUndeclared) > 0:
        print "*** Scores exist for undeclared objectives"
    for undeclaredObjective in playerObjectiveUndeclared:
        print undeclaredObjective + " is undeclared; the following have scores:"
        for name in playerObjectives[objective]:
            count = len(playerObjectives[objective][name])
            print "*** {} has {} score(s) for objective {}".format(name,count,undeclaredObjective)

    for duplicate in playerObjectiveDuplicates:
        objective = duplicate["Objective"]
        name = duplicate["Name"]
        print "*** {} has multiple scores for objective {}".format(name,objective)
        for scoreInstance in playerObjectives[objective][name]:
            score = scoreInstance["Score"]
            locked = scoreInstance["Locked"]
            if locked is None:
                lockState = "no lock"
            elif locked:
                lockState = "locked/disabled"
            else:
                lockState = "unlocked/enabled"
            print "*** {}, {} = {} ({})".format(name,objective,score,lockState)
'''

