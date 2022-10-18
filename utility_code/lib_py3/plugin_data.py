#!/usr/bin/env python3

import json
import os
import sys

from minecraft.player_dat_format.item import Item
from minecraft.util.debug_util import NbtPathDebug
from minecraft.util.iter_util import process_in_parallel

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

def _create_plugindata_lambda(full_path):
    return PluginData(json_path=full_path)

def _finalize_plugindata_lambda(plugin_data, autosave):
    if autosave:
        plugin_data.save()

def iter_plugin_data_parallel(path, func, err_func, num_processes=4, autosave=False, additional_args=(), initializer=None, initargs=()):
    """Iterates player plugin data in parallel using multiple processes.

    func will be called with each PluginData object that this folder contains
    plus any arguments supplied in additional_args

    This function is a generator - values returned by func(...) will be yielded
    back to the caller as those results become available.

    For example, if there are three players, func will be called three times.
    If each one returns a dict, the values yielded from this function will be:
    [{}, {}, {}]

    err_func will be called with (exception, args) if an exception is triggered
    and should return an empty result of the same type as func()

    Processes are pooled such that only at most num_processes will run
    simultaneously. If num_processes is set to 0 will automatically use as many
    CPUs as are available. If num_processes is 1, will iterate directly and not
    launch any new processes, which is easier to debug.

    initializer can be set to a function that initializes any variables once
    for each process worker, which for large static arguments is much faster
    than putting them in additional_args which would copy them for each
    iteration. initializer will be called with the arguments supplied in
    init_args.
    """
    if not os.path.isdir(path):
        raise ValueError("Expected path to be a folder")

    parallel_args = []
    for plugin_data_path in os.listdir(path):
        if plugin_data_path.endswith(".json"):
            full_path = os.path.join(path, plugin_data_path)
            parallel_args.append((_create_plugindata_lambda, (full_path,), _finalize_plugindata_lambda, (autosave,), func, err_func, additional_args))

    yield from process_in_parallel(parallel_args, num_processes=num_processes, initializer=initializer, initargs=initargs)

class PluginData(NbtPathDebug):
    """Plugin data loaded alongside player data."""

    def __init__(self, json_data=None, json_path=None):
        """Load a plugin data from json.

        Must be saved from wherever the json was loaded from for changes to apply.
        """
        self._path = json_path
        self._data = json_data

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

    def graves(self):
        """Get the graves stored on a player, if they exist."""
        return MonumentaGraves(self._data.get("MonumentaGravesV2", {}), self)

    def charms(self):
        """Get the charms stored on a player, if they exist."""
        return MonumentaCharms(self._data.get("R3Charms", {}), self)

    def __repr__(self):
        return f'PluginData({os.path.basename(self._path)!r})'

    @property
    def pos(self):
        return None

class MonumentaCharms(NbtPathDebug):
    """A collection of items in charm slots."""

    def __init__(self, json_data, parent):
        self._data = json_data

        self.nbt_path_init(None, parent, parent.root if parent is not None and parent.root is not None else self, None)

        self._items = None
        charms_array = self._data.get("charms", None)
        if charms_array is not None:
            self._items = []
            for item_json in charms_array:
                self._items.append(JsonWrappedCharmItem(item_json, self))

    def get_debug_str(self):
        return str(self)

    def serialize(self):
        if isinstance(self._items, list):
            self._data["charms"] = [charm_item.serialize() for charm_item in self._items]

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
        """Iterates charm items"""
        if isinstance(self._items, list):
            yield from self._items

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

    @property
    def pos(self):
        """Gets charm position, which is same as the parent player"""
        if self.parent is not None:
            return self.parent.pos
        return None

    def __repr__(self):
        return f'Charms'

class JsonWrappedCharmItem(Item, NbtPathDebug):
    """A JSON charm object containing an 'item' field describing an item

    Can be instantiated, edited, and re-serialized, which will change the nbt data but keep the other JSON object fields intact.

    Otherwise has all the methods a regular Item has (iterating, etc.)
    """

    def __init__(self, json_data, parent=None):
        self._data = json_data
        item_nbt = nbt.TagCompound.from_mojangson(self._data["item"])
        super().__init__(item_nbt, parent, None)

    def serialize(self):
        self._data["item"] = self.nbt.to_mojangson()
        return self._data

    @property
    def pos(self):
        if self.parent is not None:
            return self.parent.pos
        return None

class MonumentaGraves(NbtPathDebug):
    """A collection of items preserved from death or carelessness."""

    def __init__(self, json_data, parent):
        self._data = json_data

        self.nbt_path_init(None, parent, parent.root if parent is not None and parent.root is not None else self, None)

    def get_debug_str(self):
        return str(self)

    def iter_graves(self):
        graves = self._data.get("graves", [])
        num_graves = len(graves)
        for i in range(num_graves):
            grave = MonumentaGrave(graves[i], self)
            yield grave
            graves[i] = grave.serialize()

    def iter_thrown_items(self):
        thrown_items = self._data.get("thrown_items", [])
        num_thrown_items = len(thrown_items)
        for i in range(num_thrown_items):
            thrown_item = JsonWrappedItem(thrown_items[i], self)
            yield thrown_item
            thrown_items[i] = thrown_item.serialize()

    def iter_all_types(self):
        yield from self.iter_graves()
        yield from self.iter_thrown_items()

    def iter_block_entities(self):
        return

    def iter_entities(self):
        return

    def iter_items(self):
        return

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
        return f'Graves'

class MonumentaGrave(NbtPathDebug):
    """A collection of items preserved from a single death."""

    def __init__(self, json_data, parent):
        self._data = json_data

        self.nbt_path_init(None, parent, parent.root if parent is not None and parent.root is not None else self, None)

        # Cosmetic
        self._equipment = None
        equipment = self._data.get("equipment", None)
        if equipment is not None:
            self._equipment = {}
            for key, item_snbt in equipment.items():
                item_nbt = nbt.TagCompound.from_mojangson(item_snbt)
                self._equipment[key] = Item(item_nbt)

        # Given to players
        self._items = None
        items = self._data.get("items", None)
        if items is not None:
            self._items = []
            for item_json in items:
                self._items.append(JsonWrappedItem(item_json, self))

    def get_debug_str(self):
        return str(self)

    def serialize(self):
        if isinstance(self._equipment, dict):
            for key, item in self._equipment.items():
                self._data["equipment"][key] = item.nbt.to_mojangson()

        if isinstance(self._items, list):
            self._data["items"] = [grave_item.serialize() for grave_item in self._items]

        return self._data

    def iter_all_types(self):
        if isinstance(self._equipment, dict):
            for item in self._equipment.values():
                if item is not None:
                    yield item
                    yield from item.iter_all_types()

        if isinstance(self._items, list):
            yield from self._items

    def iter_block_entities(self):
        return

    def iter_entities(self):
        return

    def iter_items(self):
        if isinstance(self._equipment, dict):
            for item in self._equipment.values():
                if item is not None:
                    yield item

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

    @property
    def pos(self):
        """Returns the grave's coordinates as (x, y, z).

        >>> print(self.pos)
        (2.71817181, 63.5, 3.1415)
        """
        return (self._data["location"]["x"], self._data["location"]["y"], self._data["location"]["z"])

    def __repr__(self):
        return f'Grave({self._data["shard"]} {" ".join([str(round(x, 1)) for x in self.pos])})'


class JsonWrappedItem(Item, NbtPathDebug):
    """A JSON object containing an 'nbt' field describing an item

    Can be instantiated, edited, and re-serialized, which will change the nbt data but keep the other JSON object fields intact.

    Otherwise has all the methods a regular Item has (iterating, etc.)
    """

    def __init__(self, json_data, parent=None):
        self._data = json_data
        item_nbt = nbt.TagCompound.from_mojangson(self._data["nbt"])
        super().__init__(item_nbt, parent, None)

    def serialize(self):
        self._data["nbt"] = self.nbt.to_mojangson()
        return self._data

    @property
    def pos(self):
        """Returns the items's coordinates as (x, y, z) or None"""
        if "location" in self._data:
            return (self._data["location"]["x"], self._data["location"]["y"], self._data["location"]["z"])
        if self.parent is not None:
            return self.parent.pos
        return None
