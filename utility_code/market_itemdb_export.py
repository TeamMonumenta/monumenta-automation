#!/usr/bin/env pypy3

import os
import sys
import json
import redis

if len(sys.argv) < 4:
    sys.exit(f"Usage: {sys.argv[0]} <redis_host_ip> <namespace(play/build)> <output_directory>")

REDIS_HOST = sys.argv[1]
SERVER_TYPE = sys.argv[2]
EXPORT_DIR = sys.argv[3]

if SERVER_TYPE not in ["play", "build"]:
    sys.exit(f"Unknown namespace: {SERVER_TYPE}. Should be either 'build' or 'play' ")

if not os.path.isdir(EXPORT_DIR):
    sys.exit(f"Output directory '{EXPORT_DIR}' does not exist")

if SERVER_TYPE == 'build':
    print("Using build server settings!")
else:
    print("Using play server settings!")

r = redis.Redis(host=REDIS_HOST)

formatted = {}
for key, value in r.hgetall(SERVER_TYPE + ":market:ItemDBIDToItem").items():
    formatted[key.decode('UTF-8')] = value.decode('UTF-8')

with open(os.path.join(EXPORT_DIR, "itemDBIDToItem.json"), "w") as fp:
    json.dump(formatted, fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

formatted = {}
for key, value in r.hgetall(SERVER_TYPE + ":market:ItemDBItemToID").items():
    formatted[key.decode('UTF-8')] = value.decode('UTF-8')

with open(os.path.join(EXPORT_DIR, "itemDBItemToID.json"), "w") as fp:
    json.dump(formatted, fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

print("Wrote itemDBIDToItem.json and itemDBItemToID.json")
