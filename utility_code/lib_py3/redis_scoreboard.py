"""
Tools useful for modifying Scoreboard values
"""
# Required libraries have links where not part of a standard Python install.
import os
import sys
import redis
import json
from pprint import pformat
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

        # Fetch all player scores in batches from the redis server
        # Batches are needed to deal with high latency
        cursor = 0
        while True:
            cursor, keys = r.scan(cursor=cursor, match="{}:playerdata:*:scores".format(self._domain), count=5000)

            if len(keys) > 0:
                pipe = r.pipeline()
                for key in keys:
                    pipe.lindex(key, 0)
                results = pipe.execute()
                for i in range(len(keys)):
                    split = keys[i].decode("utf-8").split(":")
                    uuid = split[2]
                    self._players[uuid] = json.loads(results[i])

            # Only done when cursor is 0. The keys are allowed to sometimes be empty even when still iterating
            if cursor == 0:
                break

        self._uuid2name = {k.decode("utf-8"): v.decode("utf-8") for k, v in r.hgetall("uuid2name").items()}
        self._name2uuid = {k.decode("utf-8"): v.decode("utf-8") for k, v in r.hgetall("name2uuid").items()}

    def get_name(self, uuid):
        return self._uuid2name[uuid]

    def get_uuid(self, name):
        return self._name2uuid[name]

    def save(self, playeruuid):
        # TODO
        pass

    def search_scores(self, Conditions={}, Name=None, Objective=None, Score=None, Locked=None):
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

    def get_score(self, Name, Objective, Fallback=None):
        """
        Return Name's score for Objective;
        if not found, return Fallback (default is None)
        """
        try:
            return self._players[self.get_uuid(Name)].get(Objective, Fallback)
        except KeyError:
            return Fallback

    def set_score(self, Name, Objective, Score):
        """
        Set Name's Objective score to Score
        """

        if Score is None and Objective in self._players[self.get_uuid(Name)]:
            self._players[self.get_uuid(Name)].pop(Objective)
        else:
            self._players[self.get_uuid(Name)][Objective] = Score


    def add_score(self, Name, Objective, Score):
        """
        Add Score to Name's Objective score
        """
        current = self._players[self.get_uuid(Name)].get(Objective, 0)
        self.set_score(Name, Objective, current + Score)

    def batch_score_changes(self, rules):
        """
        Edit scores in bulk.

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
        for i in range(len(rules)):
            rule = rules[i]

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

class RedisRBoard(object):
    """
    An API for reading and writing from the Monumenta redis RBoard
    """

    def __init__(self, domain: str, redis_host="redis", redis_port=6379):
        self._domain = domain
        self._redis_host = redis_host
        self._redis_port = redis_port
        self._r = redis.Redis(host=self._redis_host, port=self._redis_port)

    def get(self, name: str, objective: str) -> int:
        val = self._r.hget(f"{self._domain}:rboard:{name}", objective)
        if val is None:
            return None
        return int(val)

    def set(self, name: str, objective: str, value: int) -> str:
        return self._r.hset(f"{self._domain}:rboard:{name}", objective, value)

    def setmulti(self, name: str, mapping: dict, validate=True) -> None:
        key = f"{self._domain}:rboard:{name}"
        self._r.hmset(key, mapping=mapping)

        if validate:
            hash_keys = []
            expected_values = []
            for hash_key in mapping:
                hash_keys.append(hash_key)
                expected_values.append(mapping[hash_key])
            values = []
            for e in self._r.hmget(key, hash_keys):
                try:
                    values.append(int(e.decode()))
                except Exception:
                    values.append(e)

            if expected_values != values:
                eprint(f"WARNING: Failed to set redis data at {key}: values read after set did not match set values")
                eprint(f"Expected to get these values:")
                eprint(pformat(expected_values))
                eprint(f"Got these values:")
                eprint(pformat(values))
