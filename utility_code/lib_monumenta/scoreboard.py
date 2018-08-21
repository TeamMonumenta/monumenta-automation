#!/usr/bin/env python2.7
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

class scoreboard(object):
    """
    An object that represents a scoreboard.dat file, and allows
    its data to be read, searched, edited, and deleted.
    """
    def __init__(self,worldFolder):
        """
        Create a new scoreboard object from a scoreboard.dat file.
        Provided path must contain a data folder.
        """
        self.load(worldFolder)

    def load(self,worldFolder):
        """
        Load a scoreboard.dat file. Provided path must contain a data folder.
        """
        self.filePath = worldFolder
        if self.filePath[-1] != "/":
            self.filePath = self.filePath + "/"
        self.filePath += "data/scoreboard.dat"
        self.nbt = nbt.load(self.filePath)
        self.allObjectives = self.nbt['data']['Objectives']
        self.allScores = self.nbt['data']['PlayerScores']

    def save(self,worldFolder=None):
        """
        Save this scoreboard data to the specified world folder, which must
        contain a data folder.
        If no path is provided, this saves the loaded scoreboard file in place.
        """
        if worldFolder is None:
            saveTo = self.filePath
        else:
            saveTo = worldFolder + "data/scoreboard.dat"
        self.nbt.save(saveTo)

    def _scoreMatches(self,aScore,Name=None,Objectives=None,Score=None,Locked=None):
        """
        Internal function to test if a single score object matches the conditions specified.
        Any criteria can be None or left out to ignore.

        - Name is a player IGN or entity UUID string.
        - Objectives is an objective name as a string, or a list of objective names.
        - Score is the integer value of a score; it can also be a dictionary with
          one or more of the following keys:
            - "min" (int): match if Score >= min
            - "max" (int): match if Score <= min
            - "in" (list): match if Score in list
            - "not_in" (list): match if Score not in list
          For these lists, the range function can generate a range of values when
          written as Python. This does not work when parsed from outside sources,
          as it could allow execution of arbitrary code.
        - Locked is 0 if enabled, 1 if disabled. This only applies to the objective
          type trigger, but is specified as 0 for other types.
        """
        if (
            Name is not None and
            aScore['Name'].value != Name
        ):
            return False
        if (
            Objectives is not None and
            aScore['Objective'].value not in Objectives
        ):
            return False
        if (
            type(Score) is int and
            aScore['Score'].value != Score
        ):
            return False
        if (
            type(Score) is list and
            aScore['Score'].value not in Score
        ):
            return False
        if (
            type(Score) is dict and
            "min" in Score and
            aScore['Score'].value < Score["min"]
        ):
            return False
        if (
            type(Score) is dict and
            "max" in Score and
            aScore['Score'].value > Score["max"]
        ):
            return False
        if (
            type(Score) is dict and
            "in" in Score and
            aScore['Score'].value not in Score["in"]
        ):
            return False
        if (
            type(Score) is dict and
            "not_in" in Score and
            aScore['Score'].value in Score["not_in"]
        ):
            return False
        if (
            Locked is not None and
            aScore['Locked'].value != Locked
        ):
            return False
        return True

    def searchScores(self,Conditions={},Name=None,Objective=None,Score=None,Locked=None,Cache=None):
        """
        Return a list of scores that match specified criteria.

        Any criteria can be None or left out to ignore.

        - Name is a player IGN or entity UUID string.
        - Objective is an objective name as a string, or a list of objective names.
        - Score is the integer value of a score; it can also be a dictionary with
          one or more of the following keys:
            - "min" (int): match if Score >= min
            - "max" (int): match if Score <= min
            - "in" (list): match if Score in list
            - "not_in" (list): match if Score not in list
          For these lists, the range function can generate a range of values when
          written as Python. This does not work when parsed from outside sources,
          as it could allow execution of arbitrary code.
        - Locked is 0 if enabled, 1 if disabled. This only applies to the objective
          type trigger, but is specified as 0 for other types.

        - Conditions is a dictionary that overrides any of the above conditions if
          a key of the same name is provided.

        The results of a search can be used as a Cache to speed up future searches.
        Caches update the master score list directly by reference, but if any score
        is deleted from the master score list, all caches are invalid. Similarly,
        adding scores that should be in a cache using a different cache or the
        master list invalidates that cache.
        """
        if "Name" in Conditions:
            Name = Conditions["Name"]
        if "Objective" in Conditions:
            Objective = Conditions["Objective"]
        if "Score" in Conditions:
            Score = Conditions["Score"]
        if "Locked" in Conditions:
            Locked = Conditions["Locked"]
        if type(Objective) == list or type(Objective) == tuple:
            Objectives = Objective
        else:
            Objectives = [Objective]
        if Cache is None:
            Cache = self.allScores
        matchingScores = []
        for _aScore in Cache:
            if not self._scoreMatches(_aScore,Name=Name,Objectives=Objectives,Score=Score,Locked=Locked):
                continue
            matchingScores.append(_aScore)
        return matchingScores

    def resetScores(self,Conditions=None,Name=None,Objective=None,Score=None,Locked=None):
        """
        Reset all scores matching the specified criteria, and return True.
        If an error occurs, no changes are made, and False is returned instead.
        """
        if "Name" in Conditions:
            Name = Conditions["Name"]
        if "Objective" in Conditions:
            Objective = Conditions["Objective"]
        if "Score" in Conditions:
            Score = Conditions["Score"]
        if "Locked" in Conditions:
            Locked = Conditions["Locked"]
        Objectives = None
        if type(Objective) == list or type(Objective) == tuple:
            Objectives = Objective
        elif type(Objective) == None:
            Objectives = [Objective]

        preserved = nbt.TAG_List()
        pruned = nbt.TAG_List()

        for _aScore in self.allScores:
            if self._scoreMatches(_aScore,Name=Name,Objective=Objective,Score=Score,Locked=Locked):
                pruned.append(_aScore)
            else:
                preserved.append(_aScore)
        print "    - {} scores pruned.".format(len(pruned))
        print "    - {} scores preserved.".format(len(preserved))
        failed = 0
        for _aScore in pruned:
            if not self._scoreMatches(_aScore,Name=Name,Objective=Objective,Score=Score,Locked=Locked):
                failed += 1
        for _aScore in preserved:
            if self._scoreMatches(_aScore,Name=Name,Objective=Objective,Score=Score,Locked=Locked):
                failed += 1
        print "    - {} pruned scores failed inspection.".format(failed)
        if failed == 0:
            self.allScores = pruned
            return True
        else:
            print "    - ! Scores not reset."
            return False

    def getScore(self,Name,Objective,Fallback=None,Cache=None):
        """
        Return Name's score for Objective;
        if not found, return Fallback (default is None)

        A Cache can be provided to speed up the search for this score.
        """
        matches = self.searchScores(Name=Name,Objective=Objective,Cache=Cache)
        if len(matches) > 1:
            raise NotImplemented('{} has {} scores for objective {}. This must be resolved manually.'.format(Name,len(matches),Objective))
        elif len(matches) == 1:
            return matches[0]['Score'].value
        elif len(matches) == 0:
            return Fallback

    def setScore(self,Name,Objective,Score,Cache=None):
        """
        Set Name's Objective score to Score

        A Cache can be provided to speed up the search for this score.
        """
        matches = self.searchScores(Name=Name,Objective=Objective,Cache=Cache)
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
            try:
                Cache.append(newScore)
            except:
                pass

    def addScore(self,Name,Objective,Score,Cache=None):
        """
        Add Score to Name's Objective score

        A Cache can be provided to speed up the search for this score.
        """
        matches = self.searchScores(Name=Name,Objective=Objective,Cache=Cache)
        if len(matches) > 1:
            raise NotImplemented('{} has {} scores for objective {}. This must be resolved manually.'.format(Name,len(matches),Objective))
        elif len(matches) == 1:
            matches[0]['Score'].value += Score
        elif len(matches) == 0:
            newScore = nbt.TAG_Compound()
            newScore['Objective'] = nbt.TAG_String(Objective)
            newScore['Locked'] = nbt.TAG_Byte(0)
            newScore['Score'] = nbt.TAG_Int(Score)
            newScore['Name'] = nbt.TAG_String(Name)
            self.allScores.append(newScore)
            try:
                Cache.append(newScore)
            except:
                pass

    def pruneMissingEntities(self,entitiesToKeep):
        """
        This deletes entities that have UUID's not found in entitiesToKeep,
        while leaving player scores alone.
        """
        # Player names cannot exceed 16 characters; UUID's are
        # always 36 characters (4 hyphens and 32 hexadecimal digits).
        uuidsToKeep = []
        for entity in entitiesToKeep:
            uuidsToKeep.append(str(entity))
        preserved = nbt.TAG_List()
        pruned = nbt.TAG_List()
        numEntries = len(self.allScores)
        print "    - {} entities found.".format(len(uuidsToKeep))
        for aScore in self.allScores:
            owner = aScore["Name"].value
            if (
                len(owner) == 36 and
                owner not in uuidsToKeep
            ):
                pruned.append(aScore)
            else:
                preserved.append(aScore)
        print "    - {} scores pruned.".format(len(pruned))
        print "    - {} scores preserved.".format(len(preserved))
        failed = 0
        for aScore in preserved:
            owner = aScore["Name"].value
            if (
                len(owner) == 36 and
                owner not in uuidsToKeep
            ):
                failed += 1
        failed = 0
        for aScore in pruned:
            owner = aScore["Name"].value
            if not (
                len(owner) == 36 and
                owner not in uuidsToKeep
            ):
                failed += 1
        print "    - {} pruned scores failed inspection.".format(failed)
        if failed == 0:
            self.allScores = pruned
        else:
            print "    - ! Score pruning canceled; scores unchanged."

    def batchScoreChanges(self,rules):
        """
        Edit scores in bulk; uses an internal cache to speed up edits.

        Example:
        scoreboard.batchScoreChanges(
            [
                {
                    "condition": {
                        "Objective": "D1Access",
                        "Score": {
                            "min": 1
                        }
                    },
                    "actions": {
                        "add": [
                            {
                                "Objective": "D1Access",
                                "Score": 1000
                            }
                        ]
                    }
                },
                {
                    "condition": {
                        "Objective": "D1Access",
                        "Score": {
                            "min": 2000
                        }
                    },
                    "actions": {
                        "set": [
                            {
                                "Objective": "D1Access",
                                "Score": 0
                            },
                            {
                                "Objective": "D1Finished",
                                "Score": 0
                            }
                        ]
                    }
                },
            ]
        )
        """
        # Generate a cache
        Objectives = set()
        #AllRuleObjectives = []
        for aRule in rules:
            RuleObjectives = set()
            RuleObjectives.add(aRule["condition"]["Objective"])
            if "set" in aRule["actions"]:
                for toSet in aRule["actions"]["set"]:
                    RuleObjectives.add(toSet["Objective"])
            if "add" in aRule["actions"]:
                for toAdd in aRule["actions"]["add"]:
                    RuleObjectives.add(toAdd["Objective"])
            #AllRuleObjectives.append(RuleObjectives)
            Objectives.update(RuleObjectives)
        Cache = self.searchScores(Objective=list(Objectives))

        # Now modify the scoreboard as needed
        for i in range(len(rules)):
            aRule = rules[i]
            #RuleObjectives = AllRuleObjectives[i]
            # This would help a fair bit, but invalidate the larger cache :/
            #RuleCache = self.searchScores(Objective=list(Objectives),Cache=Cache)

            matchedConditions = self.searchScores(Conditions=aRule["condition"],Cache=Cache)
            for aMatchingScore in matchedConditions:
                Name = aMatchingScore["Name"].value
                if "set" in aRule["actions"]:
                    for toSet in aRule["actions"]["set"]:
                        Objective = toSet["Objective"]
                        Score = toSet["Score"]
                        self.setScore(Name,Objective,Score,Cache=Cache)
                if "add" in aRule["actions"]:
                    for toAdd in aRule["actions"]["add"]:
                        Objective = toAdd["Objective"]
                        Score = toAdd["Score"]
                        self.addScore(Name,Objective,Score,Cache=Cache)

    def _objectiveMatches(self,anObjective,CriteriaName=None,DisplayName=None,Name=None,RenderType=None):
        """
        Internal function to test if a single objective object matches the conditions specified.
        Any criteria can be None or left out to ignore.
        """
        if (
            CriteriaName is not None and
            aScore['CriteriaName'].value not in CriteriaName
        ):
            return False
        if (
            DisplayName is not None and
            aScore['DisplayName'].value not in DisplayName
        ):
            return False
        if (
            Name is not None and
            aScore['Name'].value not in Name
        ):
            return False
        if (
            RenderType is not None and
            aScore['RenderType'].value not in RenderType
        ):
            return False
        return True

    def searchObjectives(self,Conditions={},CriteriaName=None,DisplayName=None,Name=None,RenderType=None):
        """
        NYI
        """
        raise NotImplemented

################################################################################
# These are legacy functions that should be merged into the Scoreboard class
# or otherwise removed. To be decided.
# Due to what is probably a naming mistake, leaving these uncommented results
# in Python hanging while trying to import this library. Oops.
'''
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

