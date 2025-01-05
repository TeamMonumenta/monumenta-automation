#!/usr/bin/env pypy3

"""Imports items to the market/mail database from json files"""

import argparse
import sys
import json
import redis
from pathlib import Path

arg_parser = argparse.ArgumentParser(description=__doc__)
arg_parser.add_argument('redis_host_ip', type=str)
arg_parser.add_argument('namespace', type=str, help='either "build" or "play"')
arg_parser.add_argument('input_directory', type=Path)
args = arg_parser.parse_args()

REDIS_HOST = args.redis_host_ip
SERVER_TYPE = args.namespace
IMPORT_DIR = args.input_directory

if SERVER_TYPE not in ["play", "build"]:
    sys.exit(f"Unknown namespace: {SERVER_TYPE}. Should be either 'build' or 'play' ")

if not IMPORT_DIR.is_dir():
    sys.exit(f"Input directory '{IMPORT_DIR}' does not exist")

if SERVER_TYPE == 'build':
    print("Using build server settings!")
else:
    print("Using play server settings!")

r = redis.Redis(host=REDIS_HOST)

## ID To Item

# read file
data = {}
with open(IMPORT_DIR / "itemDBIDToItem.json", "r") as fp:
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
with open(IMPORT_DIR / "itemDBItemToID.json", "r") as fp:
    for key, value in json.load(fp).items():
        data[key] = value

# remove old data
r.delete(SERVER_TYPE + ":market:ItemDBItemToID")

# set new data
for key, value in data.items():
    r.hset(SERVER_TYPE + ":market:ItemDBItemToID", key, value)

print("itemDBItemToID set in redis")
