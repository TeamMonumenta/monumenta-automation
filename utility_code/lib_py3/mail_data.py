#!/usr/bin/env python3

import json
import redis


class MailRedis():
    """Class for loading and saving mail data in Redis"""


    def __init__(self, domain, redis_host="redis", redis_port=6379):
        """Initialize values to later connect to Redis"""
        self._domain = domain
        self._redis_host = redis_host
        self._redis_port = redis_port


    def mailbox_keys(self):
        """List all known mailbox redis keys (type: hash)"""
        r = redis.Redis(host=self._redis_host, port=self._redis_port)

        for key in r.scan_iter(f"{self._domain}:mailbox:slots:*"):
            yield key


    def get_mailbox_slot_data(self, mailbox_key):
        """Gets the json data for a given mailbox"""
        r = redis.Redis(host=self._redis_host, port=self._redis_port)

        result = {}
        for slot_id_bytes, slot_data_bytes in r.hgetall(mailbox_key).items():
            slot_id = slot_id_bytes.decode("utf-8")
            slot_json = json.loads(slot_data_bytes.decode("utf-8"))
            result[slot_id] = slot_json
        return result


class MailboxSlot():
    """Class that lists a mailbox slot's market item IDs"""
    def __init__(self, slot_json):
        """Load a mailbox slot from json (recursive data structure)"""
        self._item_id = slot_json["mItemId"]
        self._amount = slot_json["mAmount"]
        self._virtual_amount = slot_json.get("mVirtualAmount", None)
        self._vanilla_content_array = MailboxSlot.load_nullable_array(slot_json.get("mVanillaContentArray", None))

        vanilla_content_map = slot_json.get("mVanillaContentMap", None)
        self._vanilla_content_map = None
        if isinstance(vanilla_content_map, dict):
            self._vanilla_content_map = {}
            for slot_id, nullable_slot in vanilla_content_map.items():
                self._vanilla_content_map[slot_id] = MailboxSlot.load_nullable(nullable_slot)

        self._monumenta_content_array = MailboxSlot.load_nullable_array(slot_json.get("mMonumentaContentArray", None))


    @staticmethod
    def load_nullable(nullable_slot_json):
        """If provided None, returns None; else attempts to load a MailboxSlot from json"""
        if nullable_slot_json is None:
            return None
        return MailboxSlot(nullable_slot_json)


    @staticmethod
    def load_nullable_array(nullable_slot_json_array):
        """If provided None, returns None; else attempts to load a list of nullable MailboxSlot from json"""
        if not isinstance(nullable_slot_json_array, list):
            return None

        result = []
        for nullable_slot in nullable_slot_json_array:
            result.append(MailboxSlot.load_nullable(nullable_slot))
        return result


    def market_id_set(self):
        """Returns a set of all market IDs used by this MailboxSlot and its child items"""
        result = {self._item_id,}

        if self._vanilla_content_array is not None:
            for x in self._vanilla_content_array:
                if x is not None:
                    result |= x.market_id_set()

        if self._vanilla_content_map is not None:
            for x in self._vanilla_content_map.values():
                if x is not None:
                    result |= x.market_id_set()

        if self._monumenta_content_array is not None:
            for x in self._monumenta_content_array:
                if x is not None:
                    result |= x.market_id_set()

        return result
