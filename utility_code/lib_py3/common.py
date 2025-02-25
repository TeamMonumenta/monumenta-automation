import codecs
import copy
import json
import os
import re
import shutil
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.text_format import unformat_text
from quarry.types import nbt
from quarry.types.chunk import PackedArray


def eprint(*args, **kwargs):
    """
    Convenience function identical to print() but to stderr
    """
    print(*args, file=sys.stderr, **kwargs)


def get_entity_name_from_nbt(entity_nbt: nbt.TagCompound, remove_color=True) -> str:
    """
    Parses a color-removed name out of an entity's NBT. Returns a string or None if no name exists
    """
    if not entity_nbt.has_path('CustomName'):
        return None
    return parse_name_possibly_json(entity_nbt.at_path('CustomName').value, remove_color)


def get_item_name_from_nbt(item_tag: nbt.TagCompound, remove_color=True, include_masterwork_level=False) -> str:
    """
    Parses a color-removed name out of an item's NBT. Returns a string or None if no name exists
    if include_masterwork_level is True, _m{masterwork_level} will be appended to the item's name if both name and masterwork level exist
    """
    if not item_tag.has_path("display.Name"):
        if item_tag.has_path("title"):
            title = item_tag.at_path("title").value
            if remove_color:
                title = unformat_text(title)
            return title
        return None

    item_name = parse_name_possibly_json(item_tag.at_path("display.Name").value, remove_color)
    if include_masterwork_level:
        masterwork_level = get_masterwork_level_from_nbt(item_tag)
        if masterwork_level is not None:
            item_name = f"{item_name}_m{masterwork_level}"

    return item_name


# Returns
def get_masterwork_level_from_nbt(item_tag: nbt.TagCompound, err_print_on_inval=True) -> str:
    """
    Gets the masterwork level from the item's NBT. Returns the string level if present, otherwise None
    If the value is invalid it is still returned, and an error is printed to stderr if err_print_on_inval is True
    """
    if item_tag.has_path('Monumenta.Masterwork'):
        masterwork_level = item_tag.at_path('Monumenta.Masterwork').value

        # Special cases that map to None
        if masterwork_level in ['error', 'none']:
            return None

        # Check for other invalid cases and print an error if configured to do so
        if err_print_on_inval and masterwork_level not in ['0', '1', '2', '3', '4', '5', '6', '7a', '7b', '7c']:
            eprint(f"WARNING: Item has invalid masterwork value '{masterwork_level}'")
            eprint(item_tag.to_mojangson(sort=False, highlight=True))

        return masterwork_level

    return None


def uuid_int_array_to_uuid(int_array: nbt.TagIntArray) -> uuid.UUID:
    """Converts an NBT UUID integer array into a UUID"""
    if not (isinstance(int_array, nbt.TagIntArray) and len(int_array.value) == 4):
        return None

    uuid_int = 0
    for part in int_array.value:
        uuid_int <<= 32
        if part < 0:
            part += 1<<32
        uuid_int += part
    return uuid.UUID(int=uuid_int)


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
        result = uuid_int_array_to_uuid(entity.at_path("UUID"))

    return result


def uuid_to_mc_uuid_tag_int_array(uuid: uuid):
    int_uuid = int(uuid)
    uuid_components = [(int_uuid>>96) & ((1<<32)-1), (int_uuid>>64) & ((1<<32)-1), (int_uuid>>32) & ((1<<32)-1), int_uuid & ((1<<32)-1)]
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
                result = str(json_text["score"]["value"])
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
    name = name.replace(r"\\u00A7", "§")
    name = name.replace(r"\u00a7", "§")
    name = name.replace(r"\u00A7", "§")
    try:
        possibly_json_workaround = '{"value":' + name + '}'
        name_json_workaround = json.loads(possibly_json_workaround)
        name = json_text_to_plain_text(name_json_workaround["value"])
    except Exception:
        pass

    if remove_color:
        name = unformat_text(name)

    return name


def jsonify_text(text):
    return json.dumps({"text":text}, ensure_ascii=False, separators=(',', ':'))


def get_item_ids(entity: nbt.TagCompound, path: str, expected_len: int) -> [str]:
    items = []

    if not entity.has_path(path):
        for _ in range(expected_len):
            items.append(None)
    else:
        items_nbt = entity.at_path(path)

        if len(items_nbt.value) != expected_len:
            eprint("Entity has weird {} length! Got {}, expected {}: {}".format(path, len(items_nbt.value), expected_len, entity.to_mojangson()))
            for _ in range(expected_len):
                items.append(None)
        else:
            for item in items_nbt.value:
                if item.has_path("id"):
                    items.append(item.at_path("id").value.lower())
                else:
                    items.append(None)

    return items


def get_named_items(entity: nbt.TagCompound, path: str, expected_len: int) -> [str]:
    items = []

    if not entity.has_path(path):
        for _ in range(expected_len):
            items.append(None)
    else:
        items_nbt = entity.at_path(path)

        if len(items_nbt.value) != expected_len:
            eprint("Entity has weird {} length! Got {}, expected {}: {}".format(path, len(items_nbt.value), expected_len, entity.to_mojangson()))
            for _ in range(expected_len):
                items.append(None)
        else:
            for item in items_nbt.value:
                if item.has_path("tag"):
                    item_name = get_item_name_from_nbt(item.at_path("tag"), remove_color=True)
                    items.append(item_name)
                else:
                    items.append(None)

    return items


def get_named_hand_item_ids(entity):
    return get_item_ids(entity, "HandItems", 2)


def get_named_armor_item_ids(entity):
    return get_item_ids(entity, "ArmorItems", 4)


def get_named_hand_items(entity):
    return get_named_items(entity, "HandItems", 2)


def get_named_armor_items(entity):
    return get_named_items(entity, "ArmorItems", 4)


class AlwaysEqual():
    def __init__(self):
        pass
    def __hash__(self):
        return hash(True)
    def __eq__(self, other):
        return True
always_equal = AlwaysEqual()


class NeverEqual():
    def __init__(self):
        pass
    def __hash__(self):
        return hash(False)
    def __eq__(self, other):
        return False
never_equal = NeverEqual()


UUID_REGEX = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


class EqualIfUuidStr(str):
    def __init__(self):
        pass
    def __hash__(self):
        return hash('xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')
    def __eq__(self, other):
        if not isinstance(other, str):
            return False
        return UUID_REGEX.fullmatch(other) is not None
equal_if_uuid_str = EqualIfUuidStr()


def move_file(old, new):
    if not os.path.exists(old):
        eprint("*** {!r} does not exist, preserving original.".format(old))
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
        raise Exception(f"Source file {old} does not exist!")
    if not os.path.isdir(os.path.dirname(new)):
        os.makedirs(os.path.dirname(new), mode=0o775)
    if os.path.exists(new):
        os.remove(new)
    if os.path.islink(old):
        linkto = os.readlink(old)
        os.symlink(linkto, new)
    else:
        shutil.copy2(old, new)


def move_folder(old, new):
    # This does not check if it's a path or a file, but there's another function for that case.
    if not os.path.exists(old):
        eprint("*** {!r} does not exist, preserving original.".format(old))
        return
    if not os.path.isdir(os.path.dirname(new)):
        os.makedirs(os.path.dirname(new), mode=0o775)
    shutil.rmtree(new, ignore_errors=True)
    if os.path.islink(old):
        linkto = os.readlink(old)
        os.symlink(linkto, new)
        os.remove(old)
    else:
        shutil.move(old, new)


def copy_folder(old, new):
    # This does not check if it's a path or a file, but there's another function for that case.
    if not os.path.exists(old):
        eprint("*** {!r} does not exist, preserving original.".format(old))
        return
    if not os.path.isdir(os.path.dirname(new)):
        os.makedirs(os.path.dirname(new), mode=0o775)
    shutil.rmtree(new, ignore_errors=True)
    shutil.copytree(old, new, symlinks=True)


def copy_maps(old, new):
    copy_file(os.path.join(old, "data", "idcounts.dat"),
              os.path.join(new, "data", "idcounts.dat"))
    for fname in os.listdir(os.path.join(old, "data")):
        if fname.startswith("map_") and fname.endswith(".dat"):
            old_map = os.path.join(old, "data", fname)
            new_map = os.path.join(new, "data", fname)
            if os.path.exists(old_map):
                copy_file(old_map, new_map)


def move_path(old, new, path):
    if os.path.isdir(os.path.join(old, path)):
        move_folder(os.path.join(old, path), os.path.join(new, path))
    else:
        move_file(os.path.join(old, path), os.path.join(new, path))


def copy_path(old, new, path):
    if os.path.isdir(os.path.join(old, path)):
        copy_folder(os.path.join(old, path), os.path.join(new, path))
    else:
        copy_file(os.path.join(old, path), os.path.join(new, path))


def move_paths(old, new, paths):
    for path in paths:
        try:
            move_path(old, new, path)
        except Exception:
            eprint("*** " + path + " could not be moved, may not exist.")


def copy_paths(old, new, paths):
    for path in paths:
        try:
            copy_path(old, new, path)
        except Exception:
            eprint("*** " + path + " could not be copied, may not exist.")


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

    min_out = max(0, min(min_out, range_length))
    max_out = max(0, min(max_out, range_length))

    return range(min_out, max_out)


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


# https://catonmat.net/my-favorite-regex
# Matches all printable ascii characters, from ' ' to '~'
NON_PLAIN_REGEX = re.compile('[^ -~]')


def update_plain_tag(item_nbt: nbt.TagCompound) -> None:
    """Given a Minecraft item's tag, (re)generate tag.plain.

    tag.plain stores the unformatted version of formatted text on items.
    """
    for formatted_path, plain_subpath_parts, is_multipath in (
            ('display.Name', ['display', 'Name'], False),
            ('display.Lore[]', ['display', 'Lore'], True),
            #('pages[]', ['pages'], True),
    ):
        if item_nbt.count_multipath(formatted_path) > 0:
            if item_nbt.has_path("id") and "command_block" in item_nbt.at_path("id").value:
                # Don't store plain names for command blocks
                continue

            plain_subpath_parts = ['plain'] + plain_subpath_parts
            plain_subtag = item_nbt
            for plain_subpath in plain_subpath_parts[:-1]:
                if not plain_subtag.has_path(plain_subpath):
                    plain_subtag.value[plain_subpath] = nbt.TagCompound({})
                plain_subtag = plain_subtag.at_path(plain_subpath)
            plain_subpath = plain_subpath_parts[-1]

            if is_multipath:
                plain_subtag.value[plain_subpath] = nbt.TagList([])
                for formatted in item_nbt.iter_multipath(formatted_path):
                    formatted_str = formatted.value
                    plain_str = parse_name_possibly_json(formatted_str, remove_color=True)
                    plain_str = NON_PLAIN_REGEX.sub('', plain_str).strip()
                    plain_subtag.at_path(plain_subpath).value.append(nbt.TagString(plain_str))

            else: # Single path, not multipath
                formatted = item_nbt.at_path(formatted_path)
                formatted_str = formatted.value
                plain_str = parse_name_possibly_json(formatted_str, remove_color=True)
                plain_str = NON_PLAIN_REGEX.sub('', plain_str).strip()
                plain_subtag.value[plain_subpath] = nbt.TagString(plain_str)


def mark_dirty(item):
    if not item.nbt.has_path('tag.Monumenta'):
        return
    item.nbt.at_path('tag.Monumenta').value['Dirty'] = nbt.TagByte(1)


ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)


def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


def get_main_world(shard_path):
    """Gets the primary world of a shard

    shard_path must be a pathlib.Path object or compatible
    """
    level_name_prefix = 'level-name='
    server_properties_path = shard_path / 'server.properties'

    main_world = None
    with open(server_properties_path, 'r') as fp:
        for line in fp:
            if line.startswith(level_name_prefix):
                main_world = shard_path / line[len(level_name_prefix):].rstrip()
                break
    if main_world is None:
        raise Exception(f'Could not find main world for shard {shard_path}')

    return main_world

def int_to_ordinal(i):
    """Converts a number to an ordinal string with suffix"""
    num = str(i)
    if len(num) == 0:
        return num
    last_char = num[-1]
    if last_char == '1':
        return num + 'st'
    if last_char == '2':
        return num + 'nd'
    if last_char == '3':
        return num + 'rd'
    return num + 'th'

