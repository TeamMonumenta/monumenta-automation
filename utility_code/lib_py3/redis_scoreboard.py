#!/usr/bin/env python3
"""
Tools useful for modifying Scoreboard values
"""
# Required libraries have links where not part of a standard Python install.
import os
import sys
import redis
import json
from lib_py3.common import eprint

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

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

    - Conditions is a dictionary containing the other criteria, and the values
      it provides will override the other fields

    This must come first in a comparison operation, or the other object's
    comparison operation will be in control instead.
    """
    def __init__(self, Conditions={}, Name=None, Objective=None, Score=None):
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

    def __hash__(self):
        if type(self.Score) is dict:
            # Workaround for lack of immutable (thus hashable) dict
            score_hash = tuple(sorted(self.Score.items()))
        else:
            score_hash = hash(self.Score)
        return hash((self.Name, self.Objective, score_hash))

    def score_matches(self, checkscore):
        if type(self.Score) is int:
            return checkscore == self.Score
        if type(self.Score) is tuple:
            return checkscore in self.Score
        if type(self.Score) is dict:
            if (
                "min" in self.Score and
                checkscore < self.Score["min"]
            ):
                return False
            if (
                "max" in self.Score and
                checkscore > self.Score["max"]
            ):
                return False
            if (
                "in" in self.Score and
                checkscore not in self.Score["in"]
            ):
                return False
            if (
                "not_in" in self.Score and
                checkscore in self.Score["not_in"]
            ):
                return False
        return True


class RedisScoreboard(object):
    """
    A collection of player scores loaded from Redis
    Manipulating this data will only have an effect for offline players
    """

    def __init__(self, domain, redis_host="redis", redis_port=6379):
        self._players = {}
        self._uuid2name = {}
        self._name2uuid = {}
        self._domain = domain
        self._redis_host = redis_host
        self._redis_port = redis_port
        self.load()

    def load(self):
        r = redis.Redis(host=self._redis_host, port=self._redis_port)

        for key in r.scan_iter("{}:playerdata:*:scores".format(self._domain)):
            split = key.decode("utf-8").split(":")
            uuid = split[2]
            self._players[uuid] = json.loads(r.lindex(key, 0))

        self._uuid2name = {k.decode("utf-8"): v.decode("utf-8") for k, v in r.hgetall("uuid2name").items()}
        self._name2uuid = {k.decode("utf-8"): v.decode("utf-8") for k, v in r.hgetall("name2uuid").items()}

    def get_name(self, uuid):
        return self._uuid2name[uuid]

    def get_uuid(self, name):
        return self._name2uuid[name]

    def save(self, playeruuid):
        # TODO
        pass

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
        - Locked is unused

        - Conditions is a dictionary that overrides any of the above conditions if
          a key of the same name is provided.

        Return data:

        nbt.TagCompound({
            'Objective':nbt.TagString(Objective),
            'Locked':nbt.TagByte(0),
            'Score':nbt.TagInt(Score),
            'Name':nbt.TagString(Name),
        })
        """
        the_conditions = ScoreCondition(Conditions, Name, Objective, Score)

        matching_scores = []

        if the_conditions.Name is not None:
            for name in the_conditions.Name:
                try:
                    scores = self._players.get(self.get_uuid(name), {})
                    if the_conditions.Objective is not None:
                        for objective in the_conditions.Objective:
                            value = scores.get(objective, 0)
                            if the_conditions.score_matches(value):
                                matching_scores.append(nbt.TagCompound({
                                    'Objective':nbt.TagString(objective),
                                    'Locked':nbt.TagByte(0),
                                    'Score':nbt.TagInt(value),
                                    'Name':nbt.TagString(name),
                                }))
                    else:
                        for objective in scores:
                            value = scores[objective]
                            if the_conditions.score_matches(value):
                                matching_scores.append(nbt.TagCompound({
                                    'Objective':nbt.TagString(objective),
                                    'Locked':nbt.TagByte(0),
                                    'Score':nbt.TagInt(value),
                                    'Name':nbt.TagString(name),
                                }))
                except KeyError:
                    eprint("Failed to get uuid for player '{}' - does this player exist?".format(name))

        else:
            for uuid in self._players:
                name = self.get_name(uuid)
                scores = self._players[uuid]
                if the_conditions.Objective is not None:
                    for objective in the_conditions.Objective:
                        value = scores.get(objective, 0)
                        if the_conditions.score_matches(value):
                            matching_scores.append(nbt.TagCompound({
                                'Objective':nbt.TagString(objective),
                                'Locked':nbt.TagByte(0),
                                'Score':nbt.TagInt(value),
                                'Name':nbt.TagString(name),
                            }))
                else:
                    for objective in scores:
                        value = scores[objective]
                        if the_conditions.score_matches(value):
                            matching_scores.append(nbt.TagCompound({
                                'Objective':nbt.TagString(objective),
                                'Locked':nbt.TagByte(0),
                                'Score':nbt.TagInt(value),
                                'Name':nbt.TagString(name),
                            }))

        return matching_scores

    def get_cache(self, Conditions={}, Name=None, Objective=None, Score=None, Locked=None, Cache=None):
        return None

    def reset_scores(self, Conditions={}, Name=None, Objective=None, Score=None, Locked=None):
        """
        Reset all scores matching the specified criteria, and return True.
        If an error occurs, no changes are made, and False is returned instead.
        """

        for score in self.search_scores(Conditions, Name, Objective, Score):
            Name = score.at_path("Name").value
            Objective = score.at_path("Objective").value
            self.set_score(Name, Objective, None)

    def restore_scores(self, other, Conditions={}, Name=None, Objective=None, Score=None, Locked=None):
        """
        Restore scores matching Conditions in self to the scores matching Conditions in other.
        Removes scores not found in other.
        """

        self.reset_scores(Conditions, Name, Objective, Score)
        for score in other.search_scores(Conditions, Name, Objective, Score):
            Name = score.at_path("Name").value
            Objective = score.at_path("Objective").value
            Score = score.at_path("Score").value
            self.set_score(Name, Objective, Score)

    def get_score(self, Name, Objective, Fallback=None, Cache=None):
        """
        Return Name's score for Objective;
        if not found, return Fallback (default is None)
        """
        return self._players[self.get_uuid(Name)].get(Objective, Fallback)

    def set_score(self, Name, Objective, Score, Cache=None):
        """
        Set Name's Objective score to Score
        """

        if Score is None and Objective in self._players[self.get_uuid(Name)]:
            self._players[self.get_uuid(Name)].pop(Objective)
        else:
            self._players[self.get_uuid(Name)][Objective] = Score


    def add_score(self, Name, Objective, Score, Cache=None):
        """
        Add Score to Name's Objective score

        A Cache can be provided to speed up the search for this score.
        """
        current = self._players[self.get_uuid(Name)].get(Objective, 0)
        self.set_score(Name, Objective, current + Score)

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





