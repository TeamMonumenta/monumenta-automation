#!/usr/bin/env pypy3

import os
import sys
import json
import redis

if len(sys.argv) < 4:
    sys.exit(f"Usage: {sys.argv[0]} <redis_host_ip> <namespace(play/build)> <input_directory>")

REDIS_HOST = sys.argv[1]
SERVER_TYPE = sys.argv[2]
IMPORT_DIR = sys.argv[3]

if SERVER_TYPE not in ["play", "build"]:
    sys.exit(f"Unknown namespace: {SERVER_TYPE}. Should be either 'build' or 'play' ")

if not os.path.isdir(IMPORT_DIR):
    sys.exit(f"Input directory '{IMPORT_DIR}' does not exist")

if SERVER_TYPE == 'build':
    print("Using build server settings!")
else:
    print("Using play server settings!")

r = redis.Redis(host=REDIS_HOST)

## ID To Item

# read file
data = {}
with open(os.path.join(IMPORT_DIR, "itemDBIDToItem.json"), "r") as fp:
    for key, value in json.load(fp).items():
        data[key] = value

# remove old data
r.delete(SERVER_TYPE + ":market:ItemDBIDToItem")

# set new data
for key, value in data.items():
    r.hset(SERVER_TYPE + ":market:ItemDBIDToItem", key, value)

print("itemDBIDToItem set in redis")

## Item To ID

# read file
data = {}
with open(os.path.join(IMPORT_DIR, "itemDBItemToID.json"), "r") as fp:
    for key, value in json.load(fp).items():
        data[key] = value

# remove old data
r.delete(SERVER_TYPE + ":market:ItemDBItemToID")

# set new data
for key, value in data.items():
    r.hset(SERVER_TYPE + ":market:ItemDBItemToID", key, value)

print("itemDBItemToID set in redis")
