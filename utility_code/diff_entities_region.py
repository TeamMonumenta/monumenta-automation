#!/usr/bin/env python3
"""Diff two Minecraft entities region (.mca) files, ignoring UUID differences.

Entities are matched by (type, position) rather than UUID, since this tool is
designed to validate world copies where UUIDs are intentionally regenerated.
All UUID fields are stripped from both sides before diffing NBT content.
"""

import io
import os
import sys
import re
from contextlib import redirect_stdout

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from minecraft.region import EntitiesRegion

# UUID field names to strip at any level of the NBT tree
_UUID_KEYS = frozenset({"UUID", "UUIDMost", "UUIDLeast", "WorldUUIDMost", "WorldUUIDLeast"})


def parse_rx_rz(path):
    m = re.search(r'r\.(-?\d+)\.(-?\d+)\.mca', os.path.basename(path))
    if not m:
        raise ValueError(f"Cannot parse rx,rz from filename: {path}")
    return int(m.group(1)), int(m.group(2))


def entity_pos_key(nbt):
    """Return a (type, x, y, z) tuple usable as a match key across copies.

    Positions are rounded to 2 decimal places to tolerate float serialization
    differences. Tile-based entities (paintings, item frames) use TileX/Y/Z.
    """
    eid = nbt.at_path('id').value if nbt.has_path('id') else 'unknown'

    if nbt.has_path('TileX') and nbt.has_path('TileZ'):
        x = nbt.at_path('TileX').value
        y = nbt.at_path('TileY').value if nbt.has_path('TileY') else 0
        z = nbt.at_path('TileZ').value
        return (eid, x, y, z)

    if nbt.has_path('Pos[0]'):
        x = round(nbt.at_path('Pos[0]').value, 2)
        y = round(nbt.at_path('Pos[1]').value, 2)
        z = round(nbt.at_path('Pos[2]').value, 2)
        return (eid, x, y, z)

    # Fallback: use full mojangson (will still show up as unmatched if content changed)
    return (eid, nbt.to_mojangson())


def strip_uuids(nbt):
    """Return a deep copy of a TagCompound with all UUID fields removed recursively."""
    from quarry.types.nbt import TagCompound, TagList

    def _strip(tag):
        if isinstance(tag, TagCompound):
            result = {}
            for k, v in tag.value.items():
                if k in _UUID_KEYS:
                    continue
                result[k] = _strip(v)
            return TagCompound(result)
        elif isinstance(tag, TagList):
            return TagList([_strip(v) for v in tag.value])
        else:
            return tag

    return _strip(nbt)


def load_entities(path):
    """Return dict of {pos_key: (entity_nbt, uuid_str)} for all top-level entities."""
    rx, rz = parse_rx_rz(path)
    region = EntitiesRegion(path, rx, rz, read_only=True)
    entities = {}
    collisions = []
    for chunk in region.iter_chunks(autosave=False):
        for entity in chunk.iter_entities():
            key = entity_pos_key(entity.nbt)
            uid = entity.uuid
            uid_str = str(uid) if uid is not None else 'no-uuid'
            if key in entities:
                collisions.append(key)
            entities[key] = (entity.nbt, uid_str)
    if collisions:
        print(f"  WARNING: {len(collisions)} duplicate position keys in {path} — those entities may not match correctly", file=sys.stderr)
    return entities


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <region1.mca> <region2.mca>")
        sys.exit(1)

    path1, path2 = sys.argv[1], sys.argv[2]

    print(f"Loading {path1}...")
    entities1 = load_entities(path1)
    print(f"Loading {path2}...")
    entities2 = load_entities(path2)

    keys1 = set(entities1)
    keys2 = set(entities2)

    only_in_1 = keys1 - keys2
    only_in_2 = keys2 - keys1
    in_both = keys1 & keys2

    print(f"\n=== Summary ===")
    print(f"Entities in {path1}: {len(entities1)}")
    print(f"Entities in {path2}: {len(entities2)}")
    print(f"Matched by position+type: {len(in_both)}")
    print(f"Only in file 1: {len(only_in_1)}")
    print(f"Only in file 2: {len(only_in_2)}")

    if only_in_1:
        print(f"\n=== Only in {path1} ===")
        for k in sorted(only_in_1, key=str):
            nbt, uid = entities1[k]
            print(f"  {uid}  {k}")

    if only_in_2:
        print(f"\n=== Only in {path2} ===")
        for k in sorted(only_in_2, key=str):
            nbt, uid = entities2[k]
            print(f"  {uid}  {k}")

    changed = 0
    for k in sorted(in_both, key=str):
        nbt1, uid1 = entities1[k]
        nbt2, uid2 = entities2[k]
        stripped1 = strip_uuids(nbt1)
        stripped2 = strip_uuids(nbt2)
        buf = io.StringIO()
        with redirect_stdout(buf):
            is_different = stripped1.diff(stripped2, order_matters=False, show_values=True)
        if is_different:
            changed += 1
            eid = nbt1.at_path('id').value if nbt1.has_path('id') else '?'
            print(f"\n=== Changed: {eid} at {k[1:]}  (old uuid {uid1}) ===")
            print(buf.getvalue(), end='')

    if changed == 0:
        print(f"\nAll {len(in_both)} matched entities are identical (excluding UUIDs).")
    else:
        print(f"\n{changed} of {len(in_both)} matched entities differ (excluding UUIDs).")


if __name__ == '__main__':
    main()
