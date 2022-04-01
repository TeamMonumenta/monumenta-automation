#!/usr/bin/env pypy3

import os
import json
from collections import OrderedDict
from pprint import pformat, pprint
import yaml
import redis

vote_data = {}

for root, _, files in os.walk("bungee/plugins/Monumenta-Bungee/votes"):
    for aFile in files:
        if aFile.endswith(".json"):
            uuid = aFile[:-5]
            full_file_path = os.path.join(root, aFile)
            with open(full_file_path, "r") as fp:
                data = json.load(fp)

                if "offCooldownTimes" in data:
                    data.pop("offCooldownTimes")

                if len(data) > 0:
                    vote_data[uuid] = data

r = redis.StrictRedis(host='127.0.0.1', port=6379, charset="utf-8", decode_responses=True)
for uuid in vote_data:
    user_vote_data = vote_data[uuid]

    votesTotal = r.hget(f"play:playerdata:{uuid}:remotedata", "votesTotal")

    if "votesTotal" in user_vote_data and votesTotal is None or int(votesTotal) < user_vote_data["votesTotal"]:
        print(f"Only {votesTotal} votes for user {uuid}, should be {user_vote_data['votesTotal']}")
        pipe = r.pipeline()
        for key in user_vote_data:
            path = f"play:playerdata:{uuid}:remotedata"
            print(f"Incrementing {path} {key} by {user_vote_data[key]}")
            pipe.hincrby(path, key, user_vote_data[key])
        pipe.execute()

# with open("bungee/locations.yml", "r") as fp:
#     locs = yaml.load(fp, Loader=yaml.FullLoader)
#     for name in list(locs):
#         if len(name) != 36 or "-" not in name:
#             locs.pop(name)
#
# r.hset(f"play:bungee:locations", mapping=locs)
