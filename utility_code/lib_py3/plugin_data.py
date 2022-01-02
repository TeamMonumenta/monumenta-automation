#!/usr/bin/env python3

import json
import os
import sys
import concurrent.futures

from minecraft.player_dat_format.item import Item
from minecraft.util.debug_util import NbtPathDebug
from minecraft.util.iter_util import RecursiveMinecraftIterator, TypeMultipathMap

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt


def _parallel_plugin_data_wrapper(arg):
    full_path, autosave, func, err_func, additional_args = arg
    try:
        plugin_data = PluginData(json_path=full_path)
        result = func(*((plugin_data,) + additional_args))
        if autosave:
            plugin_data.save()
    except Exception as ex:
        result = err_func(ex)
    return result


def iter_plugin_data_parallel(path, func, err_func, num_processes=4, autosave=False, additional_args=(), initializer=None, initargs=()):
    """Iterates player plugin data in parallel using multiple processes.

    func will be called with each PluginData object that this folder contains.

    Any value returned by that function will be collected into a list and
    returned to the caller. For example, if there are three players, func
    will be called three times. If each one returns a dict, the return value
    from this function will be: [{}, {}, {}]

    Processes are pooled such that only at most num_processes will run simultaneously

    Set num_processes to 1 for debugging to invoke the function without creating a new process
    """
    if not os.path.isdir(path):
        raise ValueError("Expected path to be a folder")
    plugin_data_list = []
    for plugin_data_path in os.listdir(path):
        if plugin_data_path.endswith(".json"):
            full_path = os.path.join(path, plugin_data_path)
            plugin_data_list.append((full_path, autosave, func, err_func, additional_args))

    if num_processes == 1:
        # Don't bother with processes if only going to use one
        # This makes debugging much easier
        for plugin_data_arg in plugin_data_list:
            yield _parallel_plugin_data_wrapper(plugin_data_arg)
    else:
        if len(plugin_data_list) > 0:
            with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes, initializer=initializer, initargs=initargs) as pool:
                yield from pool.map(_parallel_plugin_data_wrapper, plugin_data_list)

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

    def __repr__(self):
        return f'PluginData({os.path.basename(self._path)!r})'

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
        pass

    def iter_entities(self):
        pass

    def iter_items(self):
        pass

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
                if item_snbt is None:
                    self._equipment[key] = None
                else:
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
                if item is None:
                    self._data["equipment"][key] = None
                else:
                    self._data["equipment"][key] = item.nbt.to_mojangson()

        if isinstance(self._items, list):
            for i, grave_item in enumerate(self._items):
                self._data["items"][i] = grave_item.serialize()

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
        pass

    def iter_entities(self):
        pass

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
        return f'Grave({self._data["world"]} {" ".join([str(round(x, 1)) for x in self.pos])})'


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
        """Returns the grave's coordinates as (x, y, z).

        >>> print(self.pos)
        (2.71817181, 63.5, 3.1415)
        """
        return (self._data["location"]["x"], self._data["location"]["y"], self._data["location"]["z"])
