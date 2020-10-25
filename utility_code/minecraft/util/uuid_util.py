#!/usr/bin/env python3

import os
import sys
from uuid import UUID, uuid4

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

def generate():
    return uuid4()

def from_tag_int_array(tag: nbt.TagIntArray):
    """Returns a UUID stored as an int array (from 1.16+), or None."""
    if not isinstance(tag, nbt.TagIntArray) or not len(tag.value) == 4:
        return None

    uuid_int = 0
    for part in tag.value:
        uuid_int <<= 32
        part_val = part & ((1<<32)-1)
        uuid_int |= part_val

    return UUID(int=uuid_int)

def from_tag_most_least(most: nbt.TagLong, least: nbt.TagLong):
    """Returns a UUID stored as a most/least pair."""
    if not isinstance(most, nbt.TagLong) or not isinstance(least, nbt.TagLong):
        return None

    upper = most.value & ((1<<64)-1)
    lower = least.value & ((1<<64)-1)

    uuid_int = upper << 64 | lower
    return UUID(int=uuid_int)

def from_tag_string(tag: nbt.TagString):
    """Returns a UUID stored as a string tag (hyphenated or not), or None."""
    if not isinstance(tag, nbt.TagString):
        return None

    try:
        return UUID(tag.value)
    except ValueError:
        return None

def to_tag_int_array(uuid: UUID):
    """Converts a UUID to nbt.TagIntArray."""
    if not isinstance(uuid, UUID):
        raise TypeError("Expected uuid of type UUID.")

    result = []
    for shift in range(0, 128, 32):
        part = (int(uuid) << shift) & ((1<<32)-1)
        part = (part & ((1<<31)-1)) - (part & (1<<31))
        result.insert(0, part)

    return nbt.TagIntArray(result)

def to_tag_most_least(uuid: UUID):
    """Converts a UUID to {"most": nbt.TagLong, "least": nbt.TagLong}."""
    if not isinstance(uuid, UUID):
        raise TypeError("Expected uuid of type UUID.")

    upper = (int(uuid) >> 64) & ((1<<64)-1)
    upper = (upper & ((1<<63)-1)) - (upper & (1<<63))
    tag_most = nbt.TagLong(upper)

    lower = int(uuid) & ((1<<64)-1)
    lower = (lower & ((1<<63)-1)) - (lower & (1<<63))
    tag_least = nbt.TagLong(lower)

    return {"most": tag_most, "least": tag_least}

def to_tag_string(uuid: UUID, hyphens=True):
    """Converts a UUID to nbt.TagString.

    If hyphens=True, the hyphenated UUID format will be used.
    Otherwise, only the hexadecimal digits will be used.
    """
    if not isinstance(uuid, UUID):
        raise TypeError("Expected uuid of type UUID.")

    if hyphens:
        return str(uuid)
    else:
        return str(uuid).replace('-', '')

