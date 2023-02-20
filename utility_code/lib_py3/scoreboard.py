"""Tools useful for modifying Scoreboard values"""
# Required libraries have links where not part of a standard Python install.
import os
import sys
import uuid

from lib_py3.common import get_main_world

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt


class ScoreCondition():
    """Internal class to test if a single score object matches the conditions specified.

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
        if isinstance(self.Name, str):
            self.Name = (self.Name,)
        elif self.Name is not None:
            self.Name = tuple(self.Name)

        self.Objective = Objective
        if 'Objective' in Conditions:
            self.Objective = Conditions['Objective']
        if isinstance(self.Objective, str):
            self.Objective = (self.Objective,)
        elif self.Objective is not None:
            self.Objective = tuple(self.Objective)

        self.Score = Score
        if 'Score' in Conditions:
            self.Score = Conditions['Score']
        if isinstance(self.Score, dict):
            # There's no immutable dict, so just don't change it once loaded, k?
            pass
        elif isinstance(self.Score, list):
            self.Score = tuple(self.Score)

        self.Locked = Locked
        if 'Locked' in Conditions:
            self.Locked = Conditions['Locked']

    def __hash__(self):
        if isinstance(self.Score, dict):
            # Workaround for lack of immutable (thus hashable) dict
            score_hash = tuple(sorted(self.Score.items()))
        else:
            score_hash = hash(self.Score)
        return hash((self.Name, self.Objective, score_hash, self.Locked))

    def owner_matches(self, owner):
        return (
            self.Name is None or
            owner in self.Name
        )

    def objective_matches(self, objective):
        return (
            self.Objective is None or
            objective in self.Objective
        )

    def __eq__(self, score):
        if not self.owner_matches(score.at_path('Name').value):
            return False
        if not self.objective_matches(score.at_path('Objective').value):
            return False
        if (
                isinstance(self.Score, int) and
                score.at_path('Score').value != self.Score
        ):
            return False
        if isinstance(self.Score, dict):
            if (
                    "min" in self.Score and
                    score.at_path('Score').value < self.Score["min"]
            ):
                return False
            if (
                    "max" in self.Score and
                    score.at_path('Score').value > self.Score["max"]
            ):
                return False
            if (
                    "in" in self.Score and
                    score.at_path('Score').value not in self.Score["in"]
            ):
                return False
            if (
                    "not_in" in self.Score and
                    score.at_path('Score').value in self.Score["not_in"]
            ):
                return False
        if (
                isinstance(self.Score, tuple) and
                score.at_path('Score').value not in self.Score
        ):
            return False
        if (
                self.Locked is not None and
                score.at_path('Locked').value != self.Locked
        ):
            return False
        return True

class Scoreboard():
    """An object that represents a scoreboard.dat file

    Allows its data to be read, searched, edited, and deleted.
    """
    def __init__(self, scoreboard_file):
        """Create a new Scoreboard object from a scoreboard.dat file."""
        self.load(scoreboard_file)

    class _ScoreboardScores():
        """A cache of scores to speed up future searches."""
        def __init__(self, scores):
            self.scores = scores

        def __len__(self):
            return len(self.scores)

        def __getitem__(self, index):
            return self.scores[index]

        @property
        def scores(self):
            """Get scores as a list"""
            result = []
            for owner_map in self.score_map.values():
                for score in owner_map.values():
                    result.append(score)
            return result

        @scores.setter
        def scores(self, values):
            """Set scores as a list"""
            score_map = {}
            for score in values:
                owner = score.at_path('Name').value
                if owner not in score_map:
                    score_map[owner] = {}
                owner_map = score_map[owner]

                objective = score.at_path('Objective').value
                owner_map[objective] = score
            self.score_map = score_map

        def append(self, the_score):
            """Adds a score to the cache"""
            owner = the_score.at_path('Name').value
            if owner not in self.score_map:
                self.score_map[owner] = {}
            owner_map = self.score_map[owner]

            objective = the_score.at_path('Objective').value
            owner_map[objective] = the_score

    def load(self, scoreboard_file):
        """Load a scoreboard.dat file. Provided path must contain a data folder."""
        self.file_path = scoreboard_file
        self.nbt_file = nbt.NBTFile.load(self.file_path)
        self.nbt = self.nbt_file.root_tag.body
        self.all_objectives = self.nbt.at_path('data.Objectives').value
        self.all_scores = self._ScoreboardScores(self.nbt.at_path('data.PlayerScores').value)

    def save(self, scoreboard_file=None):
        """Save this Scoreboard data to the specified world folder

        The world folder, which must contain a data folder.
        If no path is provided, this saves the loaded Scoreboard file in place.
        """
        self.nbt.at_path('data.PlayerScores').value = self.all_scores.scores
        if scoreboard_file is None:
            save_to = self.file_path
        else:
            save_to = scoreboard_file
        self.nbt_file.save(save_to)

    def search_scores(self, Conditions={}, Name=None, Objective=None, Score=None, Locked=None):
        """Return a list of scores that match specified criteria.

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
        matching_scores = []
        for owner, owner_map in self.all_scores.score_map.items():
            if not the_conditions.owner_matches(owner):
                continue
            for _score in owner_map.values():
                matching_scores.append(_score)
        return matching_scores

    def reset_scores(self, Conditions={}, Name=None, Objective=None, Score=None, Locked=None):
        """Reset all scores matching the specified criteria, and return True.

        If an error occurs, no changes are made, and False is returned instead.
        """
        the_conditions = ScoreCondition(Conditions, Name, Objective, Score, Locked)

        preserved = {}
        for owner, owner_map in self.all_scores.score_map.items():
            if not the_conditions.owner_matches(owner):
                preserved[owner] = owner_map
                continue

            preserved_owner_map = {}
            for objective, _score in owner_map.items():
                if the_conditions != _score:
                    preserved_owner_map[objective] = _score

        self.all_scores.score_map = preserved

    def restore_scores(self, other, Conditions={}, Name=None, Objective=None, Score=None, Locked=None):
        """Restore scores matching Conditions in self to the scores matching Conditions in other.

        Removes scores not found in other.
        """
        self.reset_scores(Conditions, Name, Objective, Score, Locked)
        for score in other.search_scores(Conditions, Name, Objective, Score, Locked):
            self.all_scores.append(score)

    def get_score(self, Name, Objective, Fallback=None):
        """Return Name's score for Objective

        if not found, return Fallback (default is None)
        """
        owner_map = self.all_scores.score_map.get(Name, None)
        if owner_map is None:
            return Fallback
        score = owner_map.get(Objective, None)
        if score is None:
            return Fallback
        return score.at_path('Score').value

    def set_score(self, Name, Objective, Score):
        """Set Name's Objective score to Score"""
        new_score = nbt.TagCompound({
            'Objective':nbt.TagString(Objective),
            'Locked':nbt.TagByte(0),
            'Score':nbt.TagInt(Score),
            'Name':nbt.TagString(Name),
        })

        if Name not in self.all_scores.score_map:
            self.all_scores.score_map[Name] = {}
        owner_map = self.all_scores.score_map[Name]

        owner_map[Objective] = new_score

    def add_score(self, Name, Objective, Score):
        """Add Score to Name's Objective score"""
        if Name not in self.all_scores.score_map:
            self.all_scores.score_map[Name] = {}
        owner_map = self.all_scores.score_map[Name]

        if Objective not in owner_map:
            owner_map[Objective] = nbt.TagCompound({
                'Objective':nbt.TagString(Objective),
                'Locked':nbt.TagByte(0),
                'Score':nbt.TagInt(Score),
                'Name':nbt.TagString(Name),
            })
            return

        _score = owner_map[Objective]
        _score.at_path('Objective').value += Score

    def prune_missing_entities(self, uuids_to_keep):
        """This deletes entity scores that have UUID's not found in entities_to_keep, while leaving player scores alone.

        ```python
        uuids_to_keep = world.entity_uuids()
        world.scoreboard.prune_missing_entities(uuids_to_keep)
        world.scoreboard.save()
        ```
        """
        # Player names cannot exceed 16 characters; UUID's are
        # always 36 characters (4 hyphens and 32 hexadecimal digits).
        for owner in list(self.all_scores.score_map.keys()):
            if len(owner) != 36 or owner in uuids_to_keep:
                # Definitely not a UUID, or in the list to keep
                continue

            try:
                uuid.UUID(owner)
                # Removed entity
                del self.all_scores.score_map[owner]
            except Exception:
                # Not a UUID, keep anyways
                continue

    def batch_score_changes(self, rules):
        """Edit scores in bulk

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
        for rule in rules:
            matched_conditions = self.search_scores(Conditions=rule["condition"])
            for matching_score in matched_conditions:
                Name = matching_score.at_path("Name").value

                if "set" in rule["actions"]:
                    for to_change in rule["actions"]["set"]:
                        Objective = to_change["Objective"]
                        Score = to_change["Score"]
                        self.set_score(Name, Objective, Score)

                if "add" in rule["actions"]:
                    for to_change in rule["actions"]["add"]:
                        Objective = to_change["Objective"]
                        Score = to_change["Score"]
                        self.add_score(Name, Objective, Score)


def get_main_scoreboard(shard_path):
    """Gets the primary world's scoreboard file

    shard_path must be a pathlib.Path object or compatible
    """
    return Scoreboard(get_main_world(shard_path) / 'data' / 'scoreboard.dat')
