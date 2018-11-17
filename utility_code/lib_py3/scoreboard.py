#!/usr/bin/env python3
"""
Tools useful for modifying Scoreboard values
"""
# Required libraries have links where not part of a standard Python install.
import os
import sys
import weakref

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

from lib_py3.common import always_equal

class ScoreCondition(object):
    """
    Internal class to test if a single score object matches the conditions specified.
    Any criteria can be None or left out to ignore.

    - Name is a player IGN, entity UUID string, or list of the two.

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

    - Conditions is a dictionary containing the other criteria, and the values
      it provides will override the other fields

    This must come first in a comparison operation, or the other object's
    comparison operation will be in control instead.
    """
    def __init__(self,Conditions={},Name=None,Objective=None,Score=None,Locked=None):
        self.Name = Name
        if 'Name' in Conditions:
            self.Name = Conditions['Name']
        if type(self.Name) is str:
            self.Name = [self.Name]

        self.Objective = Objective
        if 'Objective' in Conditions:
            self.Objective = Conditions['Objective']
        if type(self.Objective) is str:
            self.Objective = [self.Objective]

        self.Score = Score
        if 'Score' in Conditions:
            self.Score = Conditions['Score']

        self.Locked = Locked
        if 'Locked' in Conditions:
            self.Locked = Conditions['Locked']

    def __eq__(self,aScore):
        if (
            self.Name is not None and
            aScore.at_path('Name').value not in self.Name
        ):
            return False
        if (
            self.Objective is not None and
            aScore.at_path('Objective').value not in self.Objective
        ):
            return False
        if (
            type(self.Score) is int and
            aScore.at_path('Score').value != self.Score
        ):
            return False
        if (
            type(self.Score) is list and
            aScore.at_path('Score').value not in self.Score
        ):
            return False
        if (
            type(self.Score) is dict and
            "min" in self.Score and
            aScore.at_path('Score').value < self.Score["min"]
        ):
            return False
        if (
            type(self.Score) is dict and
            "max" in self.Score and
            aScore.at_path('Score').value > self.Score["max"]
        ):
            return False
        if (
            type(self.Score) is dict and
            "in" in self.Score and
            aScore.at_path('Score').value not in self.Score["in"]
        ):
            return False
        if (
            type(self.Score) is dict and
            "not_in" in self.Score and
            aScore.at_path('Score').value in self.Score["not_in"]
        ):
            return False
        if (
            self.Locked is not None and
            aScore.at_path('Locked').value != self.Locked
        ):
            return False
        return True

class Scoreboard(object):
    """
    An object that represents a scoreboard.dat file, and allows
    its data to be read, searched, edited, and deleted.
    """
    def __init__(self,worldFolder):
        """
        Create a new Scoreboard object from a scoreboard.dat file.
        Provided path must contain a data folder.
        """
        self.load(worldFolder)

    class _ScoreboardCache(object):
        """
        A cache of scores to speed up future searches.
        """
        def __init__(self,scores,parent=None,conditions=always_equal):
            self.parent = parent
            self.conditions = conditions
            self.children = weakref.WeakSet()
            self.scores = scores

        def __hash__(self):
            return hash( (type(self),self.parent,self.conditions,self.children,self.scores) )

        def __len__(self):
            return len(self.scores)

        def __getitem__(self,index):
            return self.scores[index]

        def append(self,theScore,checkIfParent=True):
            """
            Do not mess with checkIfParent;
            - it is there to handle relevant all caches.

            Do not use this outside of the Scoreboard class!
            - The Scoreboard format allows duplicate score entries,
              but the results are unknown. The Scoreboard class ensures
              that no Name/Objective pair has two entries.
            """
            if self.parent is not None and checkIfParent is True:
                self.parent.append(theScore,checkIfParent=True)
                return

            if self.conditions != theScore:
                return

            self.scores.append(theScore)
            for child in self.children:
                try:
                    child.append(theScore,checkIfParent=False)
                except:
                    # Child cache may no longer be referenced; keep going.
                    pass

        def refresh(self,checkIfParent=True):
            """
            Do not mess with checkIfParent;
            - it is there to handle relevant all caches.

            Used when removing lots of scores at once, such as
            for dead entities.
            """
            if self.parent is not None and checkIfParent is True:
                self.parent.append(theScore,checkIfParent=True)
                return

            for child in self.children:
                try:
                    child.scores = []
                    for aScore in self.scores:
                        if child.conditions == aScore:
                            child.scores.append(aScore)
                    child.refresh(checkIfParent=False)
                except:
                    # Child cache may no longer be referenced; keep going.
                    pass

        def could_contain(self,theScore):
            """
            Used to avoid setting a score after checking the wrong cache.
            """
            if self.conditions != theScore:
                return False
            if self.parent is None:
                return True
            return self.parent.could_contain(theScore)

    def load(self,worldFolder):
        """
        Load a scoreboard.dat file. Provided path must contain a data folder.
        """
        self.file_path = os.path.join(worldFolder,"data/scoreboard.dat")
        self.nbt_file = nbt.NBTFile.load(self.file_path)
        self.nbt = self.nbt_file.root_tag.body
        self.all_objectives = self.nbt.at_path('data.Objectives').value
        self.all_scores = self._ScoreboardCache(self.nbt.at_path('data.PlayerScores').value)

    def save(self,worldFolder=None):
        """
        Save this Scoreboard data to the specified world folder, which must
        contain a data folder.
        If no path is provided, this saves the loaded Scoreboard file in place.
        """
        self.nbt.at_path('data.PlayerScores').value = self.all_scores.scores
        if worldFolder is None:
            saveTo = self.file_path
        else:
            saveTo = os.path.join(worldFolder,"data/scoreboard.dat")
        self.nbt_file.save(saveTo)

    def search_scores(self,Conditions={},Name=None,Objective=None,Score=None,Locked=None,Cache=None):
        """
        Return a list of scores that match specified criteria.

        Any criteria can be None or left out to ignore.

        - Name is a player IGN, entity UUID string, or list of the two.
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
        """
        theConditions = ScoreCondition(Conditions,Name,Objective,Score,Locked)
        if Cache is None:
            Cache = self.all_scores
        matchingScores = []
        for _aScore in Cache.scores:
            if theConditions != _aScore:
                continue
            matchingScores.append(_aScore)
        return matchingScores

    def get_cache(self,Conditions={},Name=None,Objective=None,Score=None,Locked=None,Cache=None):
        """
        Returns a cache of scores that match specified criteria.

        So long as scores are modified using the Scoreboard class methods,
        any changes to scores will update all relevant caches that are
        referenced somewhere.

        Any criteria can be None or left out to ignore.

        - Name is a player IGN, entity UUID string, or list of the two.
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

        - Cache may be a higher level cache.
        """
        if Cache is None:
            Cache = self.all_scores

        theConditions = ScoreCondition(Conditions,Name,Objective,Score,Locked)
        matchingScores = self.search_scores(Conditions,Name,Objective,Score,Locked,Cache)

        return self._ScoreboardCache(matchingScores,parent=Cache,conditions=theConditions)

    def reset_scores(self,Conditions={},Name=None,Objective=None,Score=None,Locked=None):
        """
        Reset all scores matching the specified criteria, and return True.
        If an error occurs, no changes are made, and False is returned instead.
        """
        theConditions = ScoreCondition(Conditions,Name,Objective,Score,Locked)

        preserved = []
        pruned = []

        for _aScore in self.all_scores.scores:
            if theConditions == _aScore:
                pruned.append(_aScore)
            else:
                preserved.append(_aScore)
        print( "    - {} scores reset.".format(len(pruned)) )
        print( "    - {} scores preserved.".format(len(preserved)) )
        failed = 0
        for _aScore in pruned:
            if theConditions != _aScore:
                failed += 1
        for _aScore in preserved:
            if theConditions == _aScore:
                failed += 1
        print( "    - {} reset scores failed inspection.".format(failed) )
        if failed == 0:
            self.all_scores.scores = pruned
            self.all_scores.refresh()
            return True
        else:
            print("    - ! Scores not reset.")
            return False

    def restore_scores(self,other,Conditions=None,Name=None,Objective=None,Score=None,Locked=None):
        """
        Restore scores matching Conditions in self to the scores matching Conditions in other.
        Removes scores not found in other.
        """
        self.reset_scores(Conditions,Name,Objective,Score,Locked)
        for score in other.search_scores(Conditions,Name,Objective,Score,Locked):
            self.all_scores.append(score)

    def get_score(self,Name,Objective,Fallback=None,Cache=None):
        """
        Return Name's score for Objective;
        if not found, return Fallback (default is None)

        A Cache can be provided to speed up the search for this score.
        """
        matches = self.search_scores(Name=Name,Objective=Objective,Cache=Cache)
        if len(matches) > 1:
            raise NotImplemented('{} has {} scores for objective {}. This must be resolved manually.'.format(Name,len(matches),Objective))
        elif len(matches) == 1:
            return matches[0].at_path('Score').value
        elif len(matches) == 0:
            return Fallback

    def set_score(self,Name,Objective,Score,Cache=None):
        """
        Set Name's Objective score to Score

        A Cache can be provided to speed up the search for this score.
        """
        newScore = nbt.TagCompound({
            'Objective':nbt.TagString(Objective),
            'Locked':nbt.TagByte(0),
            'Score':nbt.TagInt(Score),
            'Name':nbt.TagString(Name),
        })

        if (
            Cache is not None and
            Cache.could_contain(newScore)
        ):
            Cache = self.all_scores

        matches = self.search_scores(Name=Name,Objective=Objective,Cache=Cache)
        if len(matches) > 1:
            raise NotImplemented('{} has {} scores for objective {}. This must be resolved manually.'.format(Name,len(matches),Objective))
        elif len(matches) == 1:
            matches[0].at_path('Score').value = Score
        elif len(matches) == 0:
            self.all_scores.append(newScore)

    def add_score(self,Name,Objective,Score,Cache=None):
        """
        Add Score to Name's Objective score

        A Cache can be provided to speed up the search for this score.
        """
        newScore = nbt.TagCompound({
            'Objective':nbt.TagString(Objective),
            'Locked':nbt.TagByte(0),
            'Score':nbt.TagInt(Score),
            'Name':nbt.TagString(Name),
        })

        if (
            Cache is not None and
            Cache.could_contain(newScore)
        ):
            Cache = self.all_scores

        matches = self.search_scores(Name=Name,Objective=Objective,Cache=Cache)
        if len(matches) > 1:
            raise NotImplemented('{} has {} scores for objective {}. This must be resolved manually.'.format(Name,len(matches),Objective))
        elif len(matches) == 1:
            matches[0].at_path('Score').value += Score
        elif len(matches) == 0:
            self.all_scores.append(newScore)

    def prune_missing_entities(self,entitiesToKeep):
        """
        This deletes entity scores that have UUID's not found
        in entitiesToKeep, while leaving player scores alone.
        """
        # Player names cannot exceed 16 characters; UUID's are
        # always 36 characters (4 hyphens and 32 hexadecimal digits).
        uuidsToKeep = []
        for entity in entitiesToKeep:
            uuidsToKeep.append(str(entity))
        preserved = nbt.TAG_List()
        pruned = nbt.TAG_List()
        numEntries = len(self.all_scores.scores)
        print( "    - {} entities found.".format(len(uuidsToKeep)) )
        for aScore in self.all_scores.scores:
            owner = aScore.at_path("Name").value
            if (
                len(owner) == 36 and
                owner not in uuidsToKeep
            ):
                pruned.append(aScore)
            else:
                preserved.append(aScore)
        print( "    - {} scores pruned.".format(len(pruned)) )
        print( "    - {} scores preserved.".format(len(preserved)) )
        failed = 0
        for aScore in preserved:
            owner = aScore.at_path("Name").value
            if (
                len(owner) == 36 and
                owner not in uuidsToKeep
            ):
                failed += 1
        failed = 0
        for aScore in pruned:
            owner = aScore.at_path("Name").value
            if not (
                len(owner) == 36 and
                owner not in uuidsToKeep
            ):
                failed += 1
        print( "    - {} pruned scores failed inspection.".format(failed) )
        if failed == 0:
            self.all_scores.scores = pruned
            self.all_scores.refresh()
            return True
        else:
            print( "    - ! Score pruning canceled; scores unchanged." )
            return False

    def batch_score_changes(self,rules):
        """
        Edit scores in bulk; uses an internal cache to speed up edits.

        Example:
        Scoreboard.batchScoreChanges(
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
        AllRuleObjectives = []
        for aRule in rules:
            RuleObjectives = set()
            RuleObjectives.add(aRule["condition"]["Objective"])
            if "set" in aRule["actions"]:
                for toSet in aRule["actions"]["set"]:
                    RuleObjectives.add(toSet["Objective"])
            if "add" in aRule["actions"]:
                for toAdd in aRule["actions"]["add"]:
                    RuleObjectives.add(toAdd["Objective"])
            AllRuleObjectives.append(RuleObjectives)
            Objectives.update(RuleObjectives)
        BatchCache = self.get_cache(Objective=list(Objectives))

        # Now modify the Scoreboard as needed
        for i in range(len(rules)):
            aRule = rules[i]
            RuleObjectives = AllRuleObjectives[i]
            RuleCache = self.get_cache(Objective=list(RuleObjectives),Cache=BatchCache)

            matchedConditions = self.search_scores(Conditions=aRule["condition"],Cache=RuleCache)
            for aMatchingScore in matchedConditions:
                Name = aMatchingScore.at_path("Name").value
                if "set" in aRule["actions"]:
                    for toSet in aRule["actions"]["set"]:
                        Objective = toSet["Objective"]
                        Score = toSet["Score"]
                        self.set_score(Name,Objective,Score,Cache=RuleCache)
                if "add" in aRule["actions"]:
                    for toAdd in aRule["actions"]["add"]:
                        Objective = toAdd["Objective"]
                        Score = toAdd["Score"]
                        self.add_score(Name,Objective,Score,Cache=RuleCache)

    ############################################################################
    # Here on is WIP

    def _objectiveMatches(self,anObjective,CriteriaName=None,DisplayName=None,Name=None,RenderType=None):
        """
        Internal function to test if a single objective object matches the conditions specified.
        Any criteria can be None or left out to ignore.
        """
        if (
            CriteriaName is not None and
            anObjective.at_path('CriteriaName').value not in CriteriaName
        ):
            return False
        if (
            DisplayName is not None and
            anObjective.at_path('DisplayName').value not in DisplayName
        ):
            return False
        if (
            Name is not None and
            anObjective.at_path('Name').value not in Name
        ):
            return False
        if (
            RenderType is not None and
            anObjective.at_path('RenderType').value not in RenderType
        ):
            return False
        return True

    def searchObjectives(self,Conditions={},CriteriaName=None,DisplayName=None,Name=None,RenderType=None):
        """
        Search through all objectives to find a match

        NYI
        """
        CriteriaName = Conditions.get('CriteriaName',CriteriaName)
        DisplayName = Conditions.get('DisplayName',DisplayName)
        Name = Conditions.get('CriteriaName',Name)
        RenderType = Conditions.get('RenderType',RenderType)

        results = []

        for anObjective in self.all_objectives:
            if self._objectiveMatches(anObjective,CriteriaName,DisplayName,Name,RenderType):
                results.append(anObjective)

        return results

