#!/usr/bin/env python3

import copy
import json
import os
import re
import shutil
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.text_format import unformat_text
from quarry.types import nbt

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_entity_name_from_nbt(entity_nbt: nbt.TagCompound, remove_color=True) -> str:
    """
    Parses a color-removed name out of an entity's NBT. Returns a string or None if no name exists
    """
    if not entity_nbt.has_path('CustomName'):
        return None
    return parse_name_possibly_json(entity_nbt.at_path('CustomName').value, remove_color)

def get_item_name_from_nbt(item_nbt: nbt.TagCompound, remove_color=True):
    """
    Parses a color-removed name out of an item's NBT. Returns a string or None if no name exists
    """
    if not item_nbt.has_path("display.Name"):
        return None

    return parse_name_possibly_json(item_nbt.at_path("display.Name").value, remove_color)

def json_text_to_plain_text(json_text):
    result = ""

    if isinstance(json_text, str):
        result = json_text

    elif isinstance(json_text, dict):
        if "text" in json_text:
            result = json_text["text"]

    elif isinstance(json_text, list):
        for item in json_text:
            result += json_text_to_plain_text(item)

    return result

def parse_name_possibly_json(name, remove_color=False):
    name = re.sub(r"\\u0027", "'", name)
    try:
        name_json = json.loads(name)
        name = json_text_to_plain_text(name_json)
    except:
        pass

    if remove_color:
        name = unformat_text(name)

    return name

def get_named_hand_items(entity):
    if not entity.has_path("HandItems"):
        return [None, None]

    hand_items = []
    hand_items_nbt = entity.at_path("HandItems")

    if len(hand_items_nbt.value) != 2:
        if len(hand_items_nbt.value) == 1:
            hand_items.append(None)
            for hand_item in hand_items_nbt.value:
                if hand_item.has_path("tag.display.Name"):
                    item_name = parse_name_possibly_json(hand_item.at_path("tag.display.Name").value, remove_color=True)
                    hand_items.append("{}".format(item_name))
                else:
                    hand_items.append(None)

        else:
            eprint("Entity has weird hand items length!")
            entity.tree()
            return [None, None]

    for hand_item in hand_items_nbt.value:
        if hand_item.has_path("tag.display.Name"):
            item_name = parse_name_possibly_json(hand_item.at_path("tag.display.Name").value, remove_color=True)
            hand_items.append("{}".format(item_name))
        else:
            hand_items.append(None)

    return hand_items


class AlwaysEqual(object):
    def __init__(self):
        pass
    def __hash__(self):
        return True
    def __eq__(self,other):
        return True
always_equal = AlwaysEqual()

class NeverEqual(object):
    def __init__(self):
        pass
    def __hash__(self):
        return False
    def __eq__(self,other):
        return False
never_equal = NeverEqual()

def move_file(old, new):
    if not os.path.exists(old):
        print("*** '{}' does not exist, preserving original.".format(old))
        return False
    if os.path.exists(new):
        os.remove(new)
    if os.path.islink(old):
        linkto = os.readlink(old)
        os.symlink(linkto, new)
        os.remove(old)
    else:
        shutil.move(old, new)
    return True

def copy_file(old, new):
    if not os.path.exists(old):
        print("*** '{}' does not exist, preserving original.".format(old))
        return False
    if not os.path.isdir(os.path.dirname(new)):
        os.makedirs(os.path.dirname(new), mode=0o775)
    if os.path.exists(new):
        os.remove(new)
    if os.path.islink(old):
        linkto = os.readlink(old)
        os.symlink(linkto, new)
    else:
        shutil.copy2(old, new)
    return True

def copy_folder(old, new):
    # This does not check if it's a path or a file, but there's another function for that case.
    if not os.path.exists(old):
        print("*** '{}' does not exist, preserving original.".format(old))
        return
    if not os.path.isdir(os.path.dirname(new)):
        os.makedirs(os.path.dirname(new), mode=0o775)
    shutil.rmtree(new, ignore_errors=True)
    shutil.copytree(old, new, symlinks=True)

def copy_path(old, new, path):
    if os.path.isdir(os.path.join(old, path)):
        copy_folder(os.path.join(old, path), os.path.join(new, path))
    else:
        copy_file(os.path.join(old, path), os.path.join(new, path))

def copy_paths(old, new, paths):
    for path in paths:
        try:
            copy_path(old, new, path);
        except:
            print("*** " + path + " could not be copied, may not exist.")

def bounded_range(min_in, max_in, range_start, range_length, divide=1):
    """
    Clip the input so the start and end don't exceed some other range.
    range_start is multiplied by range_length before use
    The output is relative to the start of the range.
    divide allows the range to be scaled to ( range // divide )
    """
    range_length //= divide
    range_start *= range_length

    min_out = min_in//divide - range_start
    max_out = max_in//divide - range_start + 1

    min_out = max( 0, min( min_out, range_length ) )
    max_out = max( 0, min( max_out, range_length ) )

    return range( min_out, max_out )

class DictWithDefault(dict):
    def __init__(self, init={}, default=0):
        if isinstance(init, type(self)):
            self._default = init._default
            super().__init__(init)
        else:
            self._default = default
            super().__init__(init)

    def __getitem__(self, key):
        result = super().__getitem__(key)
        self[key] = result
        return result

    def __missing__(self, key):
        return copy.deepcopy(self._default)

