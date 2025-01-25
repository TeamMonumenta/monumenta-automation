#!/usr/bin/env python3

import json
import os
import sys
import redis

from minecraft.player_dat_format.item import Item
from minecraft.util.debug_util import NbtPathDebug

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt


class MarketRedis():
    """Class for loading and saving market data in Redis"""


    def __init__(self, domain, redis_host="redis", redis_port=6379):
        """Initialize values to later connect to Redis"""
        self._domain = domain
        self._redis_host = redis_host
        self._redis_port = redis_port


    def market_listings(self):
        """List all known market listings"""
        r = redis.Redis(host=self._redis_host, port=self._redis_port)

        result = {}
        for listing_id_bytes, listing_data_bytes in r.hgetall(f"{self._domain}:market:listings").items():
            listing_id = listing_id_bytes.decode("utf-8")
            listing_json = json.loads(listing_data_bytes.decode("utf-8"))
            result[listing_id] = listing_json
        return result


class MarketListing():
    """A listing within the market"""


    def __init__(self, json_data):
        """Loads a MarketListing from json"""
        self.json_data = json_data


    def market_id_set(self):
        """Returns a set of all market IDs used by this MailboxSlot and its child items"""
        result = set()

        to_sell_id = self.json_data.get("mItemToSellID", None)
        if isinstance(to_sell_id, int):
            result.add(to_sell_id)

        to_buy_id = self.json_data.get("mCurrencyToBuyID", None)
        if isinstance(to_buy_id, int):
            result.add(to_buy_id)

        return result


class MarketData(NbtPathDebug):
    """Single class to support both ItemToID and IdToItem maps"""


    def __init__(self, json_data=None, json_path=None, item_to_id=True):
        """Load from json.

        Must be saved from wherever the json was loaded from for changes to apply.

        item_to_id = True: This is an item -> id map file.
        item_to_id = False: This is an id -> item map file.

        Since it's the same format for both, just with reversed keys and values, we reuse most of the code for both
        """
        self._path = json_path
        self._data = json_data
        self._item_to_id = item_to_id

        if self._path is not None and self._data is None:
            with open(self._path, 'r') as fp:
                self._data = json.load(fp)
                fp.close()

        if self._data is None:
            raise ValueError("No json data or path was provided")

        self.nbt_path_init(None, None, self, None)


    def get_debug_str(self):
        """Returns debug information about the given MarketData"""
        return str(self)


    def save(self, json_path=None):
        """Save json data.

        Always returns the json data.
        If loaded from a path, or a path is provided, saves to that path.
        """
        if json_path is None:
            json_path = self._path

        if json_path:
            with open(json_path, 'w') as fp:
                json.dump(
                    self._data,
                    fp,
                    ensure_ascii=False,
                    indent=2,
                    separators=(',', ': '),
                    sort_keys=False
                )
                fp.write("\n")

        return self._data


    def __len__(self):
        return len(self._data)


    def iter_all_types(self):
        """Iterates charm items"""
        yield from self.iter_items()


    def iter_block_entities(self):
        """Iterates charm block entities (none)"""
        return


    def iter_entities(self):
        """Iterates charm entities (none)"""
        return


    def iter_items(self, keep_ids=None, yield_ids=None):
        """Iterates items, either in key or value position in the map"""

        # A new map - values are added to it as iterating happens
        newdata = {}
        # Iterate items in the input map, without modifying it
        for k, v in self._data.items():
            # Pull out the actual item nbt, depending on which type of map this is
            if self._item_to_id:
                item_id = v
                nbt_str = k
            else:
                item_id = k
                nbt_str = v

            # If keep_ids is a container, skip values not inside without preserving them
            if keep_ids is not None and str(item_id) not in keep_ids:
                continue

            # If yield_ids is a container, skip values not inside, but preserve them
            if yield_ids is not None and str(item_id) not in yield_ids:
                new_nbt_str = nbt_str
            else:
                # Deserialize to an Item and yield to the caller
                try:
                    item = Item(nbt.TagCompound.from_mojangson(nbt_str), self, None)
                except:
                    print('[Market Data] Error trying to parse item NBT:', file=sys.stderr)
                    print(f'k={k!r}', file=sys.stderr)
                    print(f'v={v!r}', file=sys.stderr)
                    raise
                yield item

                # Re-serialize the resulting item
                new_nbt_str = item.nbt.to_mojangson()

            # Insert the new item into the new map
            if self._item_to_id:
                newdata[new_nbt_str] = v
            else:
                newdata[k] = new_nbt_str

        # New map replaces the original map
        self._data = newdata


    def recursive_iter_all_types(self):
        """Recursively lists all Minecraft data types in this MarketData"""
        yield self
        for obj in self.iter_all_types():
            yield from obj.recursive_iter_all_types()


    def recursive_iter_block_entities(self):
        """Recursively lists all block entities in this MarketData"""
        for obj in self.iter_all_types():
            yield from obj.recursive_iter_block_entities()


    def recursive_iter_entities(self):
        """Recursively lists all entities in this MarketData"""
        for obj in self.iter_all_types():
            yield from obj.recursive_iter_entities()


    def recursive_iter_items(self):
        """Recursively lists all items in this MarketData"""
        for obj in self.iter_all_types():
            yield from obj.recursive_iter_items()


    def __repr__(self):
        return f'MarketData({os.path.basename(self._path)!r})'


    @property
    def pos(self):
        """MarketData does not have a location in a world; return None"""
        return None
