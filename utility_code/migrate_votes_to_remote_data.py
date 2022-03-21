#!/usr/bin/env pypy3

import os
import json
from collections import OrderedDict
from pprint import pformat, pprint
import yaml
import redis

vote_data = {}

for root, _, files in os.walk("/home/epic/stage/m12/bungee/plugins/Monumenta-Bungee/votes"):
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

r = redis.Redis(host="127.0.0.1")
pipe = r.pipeline()
for uuid in vote_data:
    pipe.hset(f"play:playerdata:{uuid}:remotedata", mapping=vote_data[uuid])
pipe.execute()

with open("/home/epic/stage/m12/bungee/locations.yml", "r") as fp:
    locs = yaml.load(fp, Loader=yaml.FullLoader)
    for name in list(locs):
        if len(name) != 36 or "-" not in name:
            locs.pop(name)

r.hset(f"play:bungee:locations", mapping=locs)
