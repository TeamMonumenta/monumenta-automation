#!/usr/bin/env python3

import json
import os
import sys

from minecraft.player_dat_format.item import Item
from minecraft.util.debug_util import NbtPathDebug

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

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

    def iter_all_types(self):
        """Iterates charm items"""
        yield from self.iter_items()


    def iter_block_entities(self):
        """Iterates charm block entities (none)"""
        return


    def iter_entities(self):
        """Iterates charm entities (none)"""
        return


    def iter_items(self):
        """Iterates items, either in key or value position in the map"""

        # A new map - values are added to it as iterating happens
        newdata = {}
        # Iterate items in the input map, without modifying it
        for k, v in self._data.items():
            # Pull out the actual item nbt, depending on which type of map this is
            if self._item_to_id:
                nbtstr = k
            else:
                nbtstr = v

            # Deserialize to an Item and yield to the caller
            item = Item(nbt.TagCompound.from_mojangson(nbtstr), self, None)
            yield item

            # Re-serialize the resulting item
            new_nbtstr = item.nbt.to_mojangson()

            # Insert the new item into the new map
            if self._item_to_id:
                newdata[new_nbtstr] = v
            else:
                newdata[k] = new_nbtstr

        # New map replaces the original map
        self._data = newdata

    def recursive_iter_all_types(self):
        yield self
        for obj in self.iter_all_types():
            yield from obj.recursive_iter_all_types()


    def recursive_iter_block_entities(self):
        for obj in self.iter_all_types():
            yield from obj.recursive_iter_block_entities()


    def recursive_iter_entities(self):
        for obj in self.iter_all_types():
            yield from obj.recursive_iter_entities()


    def recursive_iter_items(self):
        for obj in self.iter_all_types():
            yield from obj.recursive_iter_items()

    def __repr__(self):
        return f'MarketData({os.path.basename(self._path)!r})'

    @property
    def pos(self):
        return None
