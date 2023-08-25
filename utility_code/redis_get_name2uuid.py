#!/usr/bin/env pypy3

import json
import redis

r = redis.Redis(host="127.0.0.1")

formatted = {}
for key, value in r.hgetall("name2uuid").items():
    formatted[key.decode('UTF-8')] = value.decode('UTF-8')

with open("name2uuid.json", "w") as fp:
    json.dump(formatted, fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

formatted = {}
for key, value in r.hgetall("uuid2name").items():
    formatted[key.decode('UTF-8')] = value.decode('UTF-8')

with open("uuid2name.json", "w") as fp:
    json.dump(formatted, fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

print("Wrote uuid2name.json and name2uuid.json")
