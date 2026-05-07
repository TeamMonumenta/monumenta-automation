#!/usr/bin/env pypy3

"""
redis_schema.py — Reverse-engineer the Monumenta Redis keyspace schema.

Scans all keys, collapses high-cardinality segments (UUIDs, numeric IDs,
bungee instance IDs, leaderboard names, etc.) into placeholders, and prints
a tree of unique key patterns with counts and value type info.

Usage:
    python redis_schema.py redis://127.0.0.1/
    python redis_schema.py redis://127.0.0.1:6379/0 --no-values
"""

import argparse
import re
import sys
from collections import defaultdict

import redis

# ---------------------------------------------------------------------------
# Segment classifiers — order matters, first match wins
# ---------------------------------------------------------------------------

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
# Bare UUID without dashes (32 hex chars)
UUID_NODASH_RE = re.compile(r"^[0-9a-f]{32}$", re.I)
# Generic long hex (16+ chars, not caught above)
HEX_RE = re.compile(r"^[0-9a-f]{16,}$", re.I)
# Pure integer
INT_RE = re.compile(r"^-?\d+$")
# Bungee instance IDs: "bungee-<uuid>" or "bungee-<int>"
BUNGEE_RE = re.compile(
    r"^bungee-(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|\d+)$",
    re.I,
)


def classify_segment(segment: str) -> str:
    """Return a placeholder if the segment looks like a variable, else the
    literal segment."""
    if UUID_RE.match(segment):
        return "<uuid>"
    if UUID_NODASH_RE.match(segment):
        return "<uuid>"
    if BUNGEE_RE.match(segment):
        return "<bungee-instance>"
    if HEX_RE.match(segment):
        return "<hex>"
    if INT_RE.match(segment):
        return "<int>"
    return segment


# ---------------------------------------------------------------------------
# Key-level pattern rules (applied to the full key before segment splitting)
# ---------------------------------------------------------------------------

# Matches e.g. "play:leaderboard:SomeName" or "playerbuild:leaderboard:Foo-Bar"
LEADERBOARD_RE = re.compile(r"^([^:]+:leaderboard):(.+)$")


def apply_key_rules(key: str) -> str:
    """Apply whole-key collapsing rules before segment-level classification."""
    m = LEADERBOARD_RE.match(key)
    if m:
        return f"{m.group(1)}:<leaderboard_name>"
    return key


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------


def scan_keys(r: redis.Redis, batch_size: int = 5000):
    """Yield all keys from Redis using SCAN (safe for production)."""
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor=cursor, count=batch_size)
        for key in keys:
            yield key.decode("utf-8", errors="replace")
        if cursor == 0:
            break


# ---------------------------------------------------------------------------
# Schema building
# ---------------------------------------------------------------------------


def build_schema(r: redis.Redis, delimiter: str, sample_count: int, batch_size: int):
    """Scan all keys and return:
        patterns:  {pattern_string: count}
        samples:   {pattern_string: [key, ...]}  (up to sample_count per pattern)
    """
    patterns = defaultdict(int)
    samples = defaultdict(list)

    scanned = 0
    for key in scan_keys(r, batch_size):
        # Apply whole-key rules first (e.g. leaderboard collapsing)
        key = apply_key_rules(key)
        # Then classify each segment individually
        parts = key.split(delimiter)
        collapsed = delimiter.join(classify_segment(p) for p in parts)
        patterns[collapsed] += 1
        if len(samples[collapsed]) < sample_count:
            samples[collapsed].append(key)
        scanned += 1
        if scanned % 50_000 == 0:
            print(f"  ... scanned {scanned:,} keys so far", file=sys.stderr)

    print(f"  Scanned {scanned:,} keys total.", file=sys.stderr)
    return patterns, samples


def get_value_info(r: redis.Redis, key: str) -> dict:
    """Return just the Redis type of the value at *key*."""
    vtype = r.type(key).decode()
    return {"type": vtype}


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

INDENT = "  "


def print_tree(patterns: dict, samples: dict, r: redis.Redis, show_samples: bool):
    """Print the schema as a sorted, indented tree with counts."""

    # Build a tree structure: nested dicts with __count__ and __pattern__ at leaves
    tree = {}
    for pattern, count in sorted(patterns.items(), key=lambda x: x[0]):
        parts = pattern.split(":")
        node = tree
        for part in parts:
            node = node.setdefault(part, {})
        node["__count__"] = count
        node["__pattern__"] = pattern

    def walk(node, depth=0):
        children = {k: v for k, v in node.items() if not k.startswith("__")}

        for child_key in sorted(children.keys()):
            child = children[child_key]
            child_count = child.get("__count__")
            child_pattern = child.get("__pattern__")
            grandchildren = {k: v for k, v in child.items() if not k.startswith("__")}

            if child_count is not None and not grandchildren:
                # Leaf node
                if show_samples and child_pattern in samples:
                    sample_key = samples[child_pattern][0]
                    vinfo = get_value_info(r, sample_key)
                    print(f"{INDENT * depth}{child_key}  ({child_count:,} keys)  [{vinfo['type']}]")
                else:
                    print(f"{INDENT * depth}{child_key}  ({child_count:,} keys)")
            else:
                total = sum_counts(child)
                print(f"{INDENT * depth}{child_key}  ({total:,} keys beneath)")
                walk(child, depth + 1)

    print("\n╔══════════════════════════════════════════════╗")
    print("║          REDIS KEY SCHEMA SUMMARY            ║")
    print("╚══════════════════════════════════════════════╝\n")
    walk(tree)

    # Flat list: sort by count descending, then pattern alphabetically
    print("\n── Flat pattern list ──\n")
    for pattern, count in sorted(patterns.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {count:>8,}  {pattern}")


def sum_counts(node: dict) -> int:
    total = node.get("__count__", 0)
    for k, v in node.items():
        if not k.startswith("__") and isinstance(v, dict):
            total += sum_counts(v)
    return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Reverse-engineer the Monumenta Redis keyspace schema."
    )
    parser.add_argument(
        "uri",
        help="Redis URI, e.g. redis://127.0.0.1/ or redis://host:6379/0",
    )
    parser.add_argument(
        "--delimiter",
        default=":",
        help="Key segment delimiter (default: ':')",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=1,
        help="Number of sample keys to keep per pattern (default: 1)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5000,
        help="SCAN batch size (default: 5000)",
    )
    parser.add_argument(
        "--no-values",
        action="store_true",
        help="Skip fetching value type/structure info (faster)",
    )
    args = parser.parse_args()

    print(f"Connecting to {args.uri} ...", file=sys.stderr)
    r = redis.Redis.from_url(args.uri, decode_responses=False)
    r.ping()
    print("Connected. Scanning keys...", file=sys.stderr)

    db_size = r.dbsize()
    print(f"  DBSIZE reports {db_size:,} keys.", file=sys.stderr)

    patterns, samples = build_schema(r, args.delimiter, args.sample, args.batch_size)
    print(f"  Found {len(patterns):,} unique patterns.\n", file=sys.stderr)

    print_tree(patterns, samples, r, show_samples=not args.no_values)


if __name__ == "__main__":
    main()

