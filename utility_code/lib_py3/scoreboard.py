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
    def __init__(self, Conditions={}, Name=None, Objective=None, Score=None, Locked=None):
        self.Name = Name
        if 'Name' in Conditions:
            self.Name = Conditions['Name']
        if type(self.Name) is str:
            self.Name = (self.Name,)
        elif self.Name is not None:
            self.Name = tuple(self.Name)

        self.Objective = Objective
        if 'Objective' in Conditions:
            self.Objective = Conditions['Objective']
        if type(self.Objective) is str:
            self.Objective = (self.Objective,)
        elif self.Objective is not None:
            self.Objective = tuple(self.Objective)

        self.Score = Score
        if 'Score' in Conditions:
            self.Score = Conditions['Score']
        if type(self.Score) is list:
            self.Score = tuple(self.Score)
        elif type(self.Score) is dict:
            # There's no immutable dict, so just don't change it once loaded, k?
            pass

        self.Locked = Locked
        if 'Locked' in Conditions:
            self.Locked = Conditions['Locked']

    def __hash__(self):
        if type(self.Score) is dict:
            # Workaround for lack of immutable (thus hashable) dict
            score_hash = tuple(sorted(self.Score.items()))
        else:
            score_hash = hash(self.Score)
        return hash((self.Name, self.Objective, score_hash, self.Locked))

    def __eq__(self, score):
        if (
            self.Name is not None and
            score.at_path('Name').value not in self.Name
        ):
            return False
        if (
            self.Objective is not None and
            score.at_path('Objective').value not in self.Objective
        ):
            return False
        if (
            type(self.Score) is int and
            score.at_path('Score').value != self.Score
        ):
            return False
        if (
            type(self.Score) is tuple and
            score.at_path('Score').value not in self.Score
        ):
            return False
        if (
            type(self.Score) is dict and
            "min" in self.Score and
            score.at_path('Score').value < self.Score["min"]
        ):
            return False
        if (
            type(self.Score) is dict and
            "max" in self.Score and
            score.at_path('Score').value > self.Score["max"]
        ):
            return False
        if (
            type(self.Score) is dict and
            "in" in self.Score and
            score.at_path('Score').value not in self.Score["in"]
        ):
            return False
        if (
            type(self.Score) is dict and
            "not_in" in self.Score and
            score.at_path('Score').value in self.Score["not_in"]
        ):
            return False
        if (
            self.Locked is not None and
            score.at_path('Locked').value != self.Locked
        ):
            return False
        return True

class Scoreboard(object):
    """
    An object that represents a scoreboard.dat file, and allows
    its data to be read, searched, edited, and deleted.
    """
    def __init__(self, scoreboard_file):
        """
        Create a new Scoreboard object from a scoreboard.dat file.
        """
        self.load(scoreboard_file)

    class _ScoreboardCache(object):
        """
        A cache of scores to speed up future searches.
        """
        def __init__(self, scores, parent=None, conditions=always_equal):
            self.parent = parent
            self.conditions = conditions
            self.children = weakref.WeakSet()
            self.scores = scores

            if self.parent:
                self.parent.children.add(self)

        def __hash__(self):
            return hash((type(self), self.parent, self.conditions))

        def __len__(self):
            return len(self.scores)

        def __getitem__(self, index):
            return self.scores[index]

        def append(self, the_score, check_if_parent=True):
            """
            Do not mess with check_if_parent;
            - it is there to handle relevant all caches.

            Do not use this outside of the Scoreboard class!
            - The Scoreboard format allows duplicate score entries,
              but the results are unknown. The Scoreboard class ensures
              that no Name/Objective pair has two entries.
            """
            if self.parent is not None and check_if_parent is True:
                self.parent.append(the_score, check_if_parent=True)
                return

            if self.conditions != the_score:
                return

            self.scores.append(the_score)
            for child in self.children:
                try:
                    child.append(the_score, check_if_parent=False)
                except:
                    # Child cache may no longer be referenced; keep going.
                    pass

        def refresh(self, check_if_parent=True):
            """
            Do not mess with check_if_parent;
            - it is there to handle relevant all caches.

            Used when removing lots of scores at once, such as
            for dead entities.
            """
            if self.parent is not None and check_if_parent is True:
                self.parent.append(the_score, check_if_parent=True)
                return

            for child in self.children:
                try:
                    child.scores = []
                    for score in self.scores:
                        if child.conditions == score:
                            child.scores.append(score)
                    child.refresh(check_if_parent=False)
                except:
                    # Child cache may no longer be referenced; keep going.
                    pass

        def could_contain(self, the_score):
            """
            Used to avoid setting a score after checking the wrong cache.
            """
            if self.conditions != the_score:
                return False
            if self.parent is None:
                return True
            return self.parent.could_contain(the_score)

    def load(self, scoreboard_file):
        """
        Load a scoreboard.dat file. Provided path must contain a data folder.
        """
        self.file_path = scoreboard_file
        self.nbt_file = nbt.NBTFile.load(self.file_path)
        self.nbt = self.nbt_file.root_tag.body
        self.all_objectives = self.nbt.at_path('data.Objectives').value
        self.all_scores = self._ScoreboardCache(self.nbt.at_path('data.PlayerScores').value)

    def save(self, scoreboard_file=None):
        """
        Save this Scoreboard data to the specified world folder, which must
        contain a data folder.
        If no path is provided, this saves the loaded Scoreboard file in place.
        """
        self.nbt.at_path('data.PlayerScores').value = self.all_scores.scores
        if scoreboard_file is None:
            save_to = self.file_path
        else:
            save_to = scoreboard_file
        self.nbt_file.save(save_to)

    def search_scores(self, Conditions={}, Name=None, Objective=None, Score=None, Locked=None, Cache=None):
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
        the_conditions = ScoreCondition(Conditions, Name, Objective, Score, Locked)
        if Cache is None:
            Cache = self.all_scores
        matching_scores = []
        for _score in Cache.scores:
            if the_conditions != _score:
                continue
            matching_scores.append(_score)
        return matching_scores

    def get_cache(self, Conditions={}, Name=None, Objective=None, Score=None, Locked=None, Cache=None):
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

        the_conditions = ScoreCondition(Conditions, Name, Objective, Score, Locked)
        matching_scores = self.search_scores(Conditions, Name, Objective, Score, Locked, Cache)

        return self._ScoreboardCache(matching_scores, parent=Cache, conditions=the_conditions)

    def reset_scores(self, Conditions={}, Name=None, Objective=None, Score=None, Locked=None):
        """
        Reset all scores matching the specified criteria, and return True.
        If an error occurs, no changes are made, and False is returned instead.
        """
        the_conditions = ScoreCondition(Conditions, Name, Objective, Score, Locked)

        preserved = []

        for _score in self.all_scores.scores:
            if the_conditions != _score:
                preserved.append(_score)
        self.all_scores.scores = preserved
        self.all_scores.refresh()

    def restore_scores(self, other, Conditions={}, Name=None, Objective=None, Score=None, Locked=None):
        """
        Restore scores matching Conditions in self to the scores matching Conditions in other.
        Removes scores not found in other.
        """
        self.reset_scores(Conditions, Name, Objective, Score, Locked)
        for score in other.search_scores(Conditions, Name, Objective, Score, Locked):
            self.all_scores.append(score)

    def get_score(self, Name, Objective, Fallback=None, Cache=None):
        """
        Return Name's score for Objective;
        if not found, return Fallback (default is None)

        A Cache can be provided to speed up the search for this score.
        """
        matches = self.search_scores(Name=Name, Objective=Objective, Cache=Cache)
        if len(matches) > 1:
            raise ValueError('{} has {} scores for objective {}. This must be resolved manually.'.format(Name, len(matches), Objective))
        elif len(matches) == 1:
            return matches[0].at_path('Score').value
        elif len(matches) == 0:
            return Fallback

    def set_score(self, Name, Objective, Score, Cache=None):
        """
        Set Name's Objective score to Score

        A Cache can be provided to speed up the search for this score.
        """
        new_score = nbt.TagCompound({
            'Objective':nbt.TagString(Objective),
            'Locked':nbt.TagByte(0),
            'Score':nbt.TagInt(Score),
            'Name':nbt.TagString(Name),
        })

        if (
            Cache is not None and
            Cache.could_contain(new_score)
        ):
            Cache = self.all_scores

        matches = self.search_scores(Name=Name, Objective=Objective, Cache=Cache)
        if len(matches) > 1:
            raise ValueError('{} has {} scores for objective {}. This must be resolved manually.'.format(Name, len(matches), Objective))
        elif len(matches) == 1:
            matches[0].at_path('Score').value = Score
        elif len(matches) == 0:
            self.all_scores.append(new_score)

    def add_score(self, Name, Objective, Score, Cache=None):
        """
        Add Score to Name's Objective score

        A Cache can be provided to speed up the search for this score.
        """
        new_score = nbt.TagCompound({
            'Objective':nbt.TagString(Objective),
            'Locked':nbt.TagByte(0),
            'Score':nbt.TagInt(Score),
            'Name':nbt.TagString(Name),
        })

        if (
            Cache is not None and
            Cache.could_contain(new_score)
        ):
            Cache = self.all_scores

        matches = self.search_scores(Name=Name, Objective=Objective, Cache=Cache)
        if len(matches) > 1:
            raise NotImplemented('{} has {} scores for objective {}. This must be resolved manually.'.format(Name, len(matches), Objective))
        elif len(matches) == 1:
            matches[0].at_path('Score').value += Score
        elif len(matches) == 0:
            self.all_scores.append(new_score)

    def prune_missing_entities(self, uuids_to_keep):
        """
        This deletes entity scores that have UUID's not found
        in entities_to_keep, while leaving player scores alone.
        """
        # Player names cannot exceed 16 characters; UUID's are
        # always 36 characters (4 hyphens and 32 hexadecimal digits).
        preserved = []
        for score in self.all_scores.scores:
            owner = score.at_path("Name").value
            if len(owner) != 36 or owner in uuids_to_keep:
                preserved.append(score)
        self.all_scores.scores = preserved
        self.all_scores.refresh()

    def batch_score_changes(self, rules):
        """
        Edit scores in bulk; uses an internal cache to speed up edits.

        Example:
        Scoreboard.batch_score_changes(
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
        all_rule_objectives = []
        for rule in rules:
            rule_objectives = set()
            rule_objectives.add(rule["condition"]["Objective"])
            if "set" in rule["actions"]:
                for to_change in rule["actions"]["set"]:
                    rule_objectives.add(to_change["Objective"])
            if "add" in rule["actions"]:
                for to_change in rule["actions"]["add"]:
                    rule_objectives.add(to_change["Objective"])
            all_rule_objectives.append(rule_objectives)
            Objectives.update(rule_objectives)
        batch_cache = self.get_cache(Objective=list(Objectives))

        # Now modify the Scoreboard as needed
        for i in range(len(rules)):
            rule = rules[i]
            rule_objectives = all_rule_objectives[i]
            rule_cache = self.get_cache(Objective=list(rule_objectives), Cache=batch_cache)

            matched_conditions = self.search_scores(Conditions=rule["condition"], Cache=rule_cache)
            for matching_score in matched_conditions:
                Name = matching_score.at_path("Name").value

                if "set" in rule["actions"]:
                    for to_change in rule["actions"]["set"]:
                        Objective = to_change["Objective"]
                        Score = to_change["Score"]
                        self.set_score(Name, Objective, Score, Cache=rule_cache)

                if "add" in rule["actions"]:
                    for to_change in rule["actions"]["add"]:
                        Objective = to_change["Objective"]
                        Score = to_change["Score"]
                        self.add_score(Name, Objective, Score, Cache=rule_cache)

    ############################################################################
    # Here on is WIP

    def _objective_matches(self, an_objective, CriteriaName=None, DisplayName=None, Name=None, RenderType=None):
        """
        Internal function to test if a single objective object matches the conditions specified.
        Any criteria can be None or left out to ignore.
        """
        if (
            CriteriaName is not None and
            an_objective.at_path('CriteriaName').value not in CriteriaName
        ):
            return False
        if (
            DisplayName is not None and
            an_objective.at_path('DisplayName').value not in DisplayName
        ):
            return False
        if (
            Name is not None and
            an_objective.at_path('Name').value not in Name
        ):
            return False
        if (
            RenderType is not None and
            an_objective.at_path('RenderType').value not in RenderType
        ):
            return False
        return True

    def searchObjectives(self, Conditions={}, CriteriaName=None, DisplayName=None, Name=None, RenderType=None):
        """
        Search through all objectives to find a match

        NYI
        """
        CriteriaName = Conditions.get('CriteriaName', CriteriaName)
        DisplayName = Conditions.get('DisplayName', DisplayName)
        Name = Conditions.get('CriteriaName', Name)
        RenderType = Conditions.get('RenderType', RenderType)

        results = []

        for an_objective in self.all_objectives:
            if self._objective_matches(an_objective, CriteriaName, DisplayName, Name, RenderType):
                results.append(an_objective)

        return results

