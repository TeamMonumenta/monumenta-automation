#!/usr/bin/env pypy3

import os
import sys
import json
import redis

from lib_py3.mail_data import MailboxSlot, MailRedis
from lib_py3.market_data import MarketListing, MarketRedis

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

listing_item_ids = set()
for market_listing in MarketRedis(SERVER_TYPE, REDIS_HOST).market_listings().values():
    listing_item_ids |= MarketListing(market_listing).market_id_set()

mail_item_ids = set()
mail_redis = MailRedis(SERVER_TYPE, REDIS_HOST)
for mailbox_key in list(mail_redis.mailbox_keys()):
    for mailbox_slot_data in mail_redis.get_mailbox_slot_data(mailbox_key).values():
        mail_item_ids |= MailboxSlot(mailbox_slot_data).market_id_set()

formatted = {
    "0_item_ids_from_listings": len(listing_item_ids),
    "0_item_ids_from_mail": len(mail_item_ids),
    "used_ids": list(listing_item_ids | mail_item_ids),
}
with open(os.path.join(EXPORT_DIR, "itemDBUsedIds.json"), "w") as fp:
    json.dump(formatted, fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

print("Wrote itemDBIDToItem.json, itemDBItemToID.json, and itemDBUsedIds.json")
