"""A library to check the lockout status of shards"""


import asyncio
from datetime import datetime
from datetime import timezone
import json
from pathlib import Path
import subprocess


_file = Path(__file__).absolute()
_top_level = _file.parents[2]


class LockoutAPI():
    """The API to interact with Lockout entries"""


    def __init__(self, domain):
        """Sets up the connection to the Lockout database"""
        self.domain = domain


    @staticmethod
    def _lockout_bin():
        return _top_level / 'rust' / 'bin' / 'lockout'


    async def check_all(self):
        """Returns a map of active lockout entries by shard"""

        lockout_bin = self._lockout_bin()
        cmd = [str(lockout_bin), self.domain, 'checkall']

        process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_raw, _ = await process.communicate()

        stdout_text = stdout_raw.decode('utf-8')
        full_json = json.loads(stdout_text)
        results_json = full_json["results"]

        results = {}
        for shard_name, lockout_json in results_json.items():
            lockout = Lockout(lockout_json)
            results[shard_name] = lockout
        return results


    async def check(self, shard):
        """Returns the active lockout for a specific shard, or None

        Specifying the shard '*' checks the domain as a whole, rather than individual shard lockouts
        """

        lockout_bin = self._lockout_bin()
        cmd = [str(lockout_bin), self.domain, 'check', shard]

        process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_raw, _ = await process.communicate()

        stdout_text = stdout_raw.decode('utf-8')
        full_json = json.loads(stdout_text)
        results_json = full_json["results"]

        if results_json is None:
            result = None
        else:
            result = Lockout(results_json)
        return result


    async def claim(self, shard, owner, duration, reason):
        """Attempts to claim a lockout

        Specifying the shard '*' claims the domain as a whole
        Duration is a time from the present in minutes

        On success, returns your new claim
        On conflict, returns the conflicting claim
        """

        lockout_bin = self._lockout_bin()
        cmd = [str(lockout_bin), self.domain, 'claim', shard, owner, duration, reason]

        process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_raw, _ = await process.communicate()

        stdout_text = stdout_raw.decode('utf-8')
        full_json = json.loads(stdout_text)
        results_json = full_json["results"]

        return Lockout(results_json)


    async def clear(self, shard, owner):
        """Clears matching lockouts, returning a map of remaining lockouts

        The shard and owner fields support '*' to match all shards/owners
        """

        lockout_bin = self._lockout_bin()
        cmd = [str(lockout_bin), self.domain, 'clear', shard, owner]

        process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_raw, _ = await process.communicate()

        stdout_text = stdout_raw.decode('utf-8')
        full_json = json.loads(stdout_text)
        results_json = full_json["results"]

        results = {}
        for shard_name, lockout_json in results_json.items():
            lockout = Lockout(lockout_json)
            results[shard_name] = lockout
        return results


class Lockout():
    """The lockout status of a given shard"""


    def __init__(self, json_obj):
        """Initializes a Lockout from a json object after deserialzation"""
        self.domain = json_obj["domain"]
        self.shard = json_obj["shard"]
        self.owner = json_obj["owner"]
        self.expiration = datetime.fromtimestamp(json_obj["expiration"], timezone.utc)
        self.reason = json_obj["reason"]


    def to_json(self):
        """Returns this Lockout as a json structure, ready for serialization"""
        return {
            "domain": self.domain,
            "shard": self.shard,
            "owner": self.owner,
            "expiration": int(self.expiration.timestamp()),
            "reason": self.reason,
        }


    def discord_str(self):
        """Returns this entry as a Discord-formatted string, including timestamp"""
        owner_str = f'`{self.owner}`'
        return f'{owner_str} has a lockout claim on `{self.shard}` expiring <t:{int(self.expiration.timestamp())}:R> for `{self.reason}`'


    def as_exception(self):
        """Returns an exception with an appropriate message for general use"""
        return LockoutException(str(self))


    def as_discord_exception(self):
        """Returns an exception with an appropriate message for Discord"""
        return LockoutException(self.discord_str())


    def __str__(self):
        """Returns a friendly string for this entry"""
        return f'{self.owner} has a lockout on {self.domain} {self.shard} until {self.expiration} for {self.reason}'


    def __repr__(self):
        """Returns the code to create this object as a string"""
        return f'Lockout({self.to_json()!r})'


class LockoutException(Exception):
    """An exception specific to lockouts"""
