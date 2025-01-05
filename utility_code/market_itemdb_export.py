#!/usr/bin/env pypy3

"""Exports items from the market/mail database into json files"""

import argparse
import sys
import json
import redis
from pathlib import Path

from lib_py3.mail_data import MailboxSlot, MailRedis
from lib_py3.market_data import MarketListing, MarketRedis

arg_parser = argparse.ArgumentParser(description=__doc__)
arg_parser.add_argument('redis_host_ip', type=str)
arg_parser.add_argument('namespace', type=str, help='either "build" or "play"')
arg_parser.add_argument('output_directory', type=Path)
arg_parser.add_argument('--debug', action='store_true')
args = arg_parser.parse_args()

REDIS_HOST = args.redis_host_ip
SERVER_TYPE = args.namespace
EXPORT_DIR = args.output_directory
DEBUG = args.debug

if SERVER_TYPE not in ["play", "build"]:
    sys.exit(f"Unknown namespace: {SERVER_TYPE}. Should be either 'build' or 'play' ")

if not EXPORT_DIR.is_dir():
    sys.exit(f"Output directory '{EXPORT_DIR}' does not exist")

if SERVER_TYPE == 'build':
    print("Using build server settings!")
else:
    print("Using play server settings!")

r = redis.Redis(host=REDIS_HOST)

if DEBUG:
    print("Reading ID to Item data")

formatted = {}
for key, value in r.hgetall(SERVER_TYPE + ":market:ItemDBIDToItem").items():
    formatted[key.decode('UTF-8')] = value.decode('UTF-8')

if DEBUG:
    print("Writing ID to Item data")

with open(EXPORT_DIR / "itemDBIDToItem.json", "w") as fp:
    json.dump(formatted, fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

if DEBUG:
    print("Reading Item to ID data")

formatted = {}
for key, value in r.hgetall(SERVER_TYPE + ":market:ItemDBItemToID").items():
    formatted[key.decode('UTF-8')] = value.decode('UTF-8')

if DEBUG:
    print("Writing Item to ID data")

with open(EXPORT_DIR / "itemDBItemToID.json", "w") as fp:
    json.dump(formatted, fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

if DEBUG:
    print("Reading Market Listings")

listing_item_ids = set()
for market_listing in MarketRedis(SERVER_TYPE, REDIS_HOST).market_listings().values():
    listing_item_ids |= MarketListing(market_listing).market_id_set()

if DEBUG:
    print("Reading Mailboxes")

mail_item_ids = set()
mail_redis = MailRedis(SERVER_TYPE, REDIS_HOST)
for mailbox_key in mail_redis.mailbox_keys():
    if DEBUG:
        print(f'\r{mailbox_key}' + ' '*100, end='')
    for mailbox_slot_data in mail_redis.get_mailbox_slot_data(mailbox_key).values():
        mail_item_ids |= MailboxSlot(mailbox_slot_data).market_id_set()

if DEBUG:
    print("\rWriting used IDs" + " "*100)

formatted = {
    "listings": [str(x) for x in sorted(listing_item_ids)],
    "mail": [str(x) for x in sorted(mail_item_ids)],
}
with open(EXPORT_DIR / "itemDBUsedIds.json", "w") as fp:
    json.dump(formatted, fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

print("Wrote itemDBIDToItem.json, itemDBItemToID.json, and itemDBUsedIds.json")
