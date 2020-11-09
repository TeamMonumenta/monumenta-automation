#!/usr/bin/env python3

import copy
import json
import os
import shutil
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.text_format import unformat_text
from quarry.types import nbt
from quarry.types.chunk import PackedArray

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

def get_entity_uuid(entity: nbt.TagCompound) -> uuid.UUID:
    """Returns UUID or None for any entity with a UUID, including 1.16"""
    result = None

    if entity.has_path("UUIDMost") and entity.has_path("UUIDLeast"):
        upper = entity.at_path("UUIDMost").value
        if upper < 0:
            upper += 1<<64

        lower = entity.at_path("UUIDLeast").value
        if lower < 0:
            lower += 1<<64

        uuid_int = upper << 64 | lower
        result = uuid.UUID(int=uuid_int)

    elif entity.has_path("UUID") and isinstance(entity.at_path("UUID"), nbt.TagIntArray) and len(entity.at_path("UUID").value) == 4:
        uuid_int = 0
        for part in entity.at_path("UUID").value:
            uuid_int <<= 32
            if part < 0:
                part += 1<<32
            uuid_int += part
        result = uuid.UUID(int=uuid_int)

    return result

def uuid_to_mc_uuid_tag_int_array(uuid: uuid):
    int_uuid = int(uuid)
    uuid_components = [ (int_uuid>>96) & ((1<<32)-1), (int_uuid>>64) & ((1<<32)-1), (int_uuid>>32) & ((1<<32)-1), int_uuid & ((1<<32)-1) ]
    uuid_components_centered = []
    for uuid_component in uuid_components:
        if uuid_component >= (1<<31):
            uuid_component -= (1<<32)
        if (uuid_component < -2147483648 or uuid_component > 2147483647):
            raise ValueError("uuid_component out of range: " + str(uuid_component))
        uuid_components_centered.append(uuid_component)

    return nbt.TagIntArray(PackedArray.from_int_list(uuid_components_centered, 32))

def json_text_to_plain_text(json_text):
    result = ""

    if isinstance(json_text, str):
        result = json_text

    elif isinstance(json_text, dict):
        result = ""
        if "text" in json_text:
            result = json_text["text"]
        elif "translate" in json_text:
            result = json_text["translate"]
        elif "score" in json_text:
            result = ""
            if "value" in json_text["score"]:
                result = str(json_text["score"]["score"])
        elif "selector" in json_text:
            result = ""
        elif "keybind" in json_text:
            result = json_text["keybind"]

        if "extra" in json_text:
            for extra in json_text["extra"]:
                result += json_text_to_plain_text(extra)

    elif isinstance(json_text, list):
        for item in json_text:
            result += json_text_to_plain_text(item)

    return result

def parse_name_possibly_json(name, remove_color=False):
    name = name.replace(r"\\u0027", "'")
    name = name.replace(r"\\u00a7", "§")
    try:
        possibly_json_workaround = '{"value":' + name + '}'
        name_json_workaround = json.loads(possibly_json_workaround)
        name = json_text_to_plain_text(name_json_workaround["value"])
    except:
        pass

    if remove_color:
        name = unformat_text(name)

    return name

def jsonify_text(text):
    return json.dumps({"text":text}, ensure_ascii=False, separators=(',', ':'))

def get_named_items(entity: nbt.TagCompound, path: str, expected_len: int) -> [str]:
    items = []

    if not entity.has_path(path):
        for x in range(expected_len):
            items.append(None)
    else:
        items_nbt = entity.at_path(path)

        if len(items_nbt.value) != expected_len:
            eprint("Entity has weird {} length! Got {}, expected {}: {}".format(path, len(items_nbt.value), expected_len, entity.to_mojangson()))
            for x in range(expected_len):
                items.append(None)
        else:
            for item in items_nbt.value:
                if item.has_path("tag.display.Name"):
                    item_name = parse_name_possibly_json(item.at_path("tag.display.Name").value, remove_color=True)
                    items.append("{}".format(item_name))
                else:
                    items.append(None)

    return items

def get_named_hand_items(entity):
    return get_named_items(entity, "HandItems", 2)

def get_named_armor_items(entity):
    return get_named_items(entity, "ArmorItems", 4)

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
        print("*** {!r} does not exist, preserving original.".format(old))
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
        print("*** {!r} does not exist, preserving original.".format(old))
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
        print("*** {!r} does not exist, preserving original.".format(old))
        return
    if not os.path.isdir(os.path.dirname(new)):
        os.makedirs(os.path.dirname(new), mode=0o775)
    shutil.rmtree(new, ignore_errors=True)
    shutil.copytree(old, new, symlinks=True)

def copy_maps(old, new):
    copy_file(os.path.join(old, "data", "idcounts.dat"),
              os.path.join(new, "data", "idcounts.dat"))
    map_id = 0
    while True:
        old_map = os.path.join(old, "data", "map_{}.dat".format(map_id))
        new_map = os.path.join(new, "data", "map_{}.dat".format(map_id))
        if not os.path.exists(old_map) or not copy_file(old_map, new_map):
            break
        map_id += 1

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

