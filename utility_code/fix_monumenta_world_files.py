#!/usr/bin/env pypy3
"""Fixes coordinate error for Monumenta chunk folders"""

import argparse
import re
import sys
from pathlib import Path
from lib_py3.common import move_file
from minecraft.world import World


RE_REGION_PATH = re.compile('r.(-?\\d+).(-?\\d+)')
RE_CHUNK_PATH = re.compile('c.(-?\\d+).(-?\\d+)')
RE_WALLET_PATH = re.compile('wallet_block.(-?\\d+).(-?\\d+).(-?\\d+).json')


def prune_empty_folders(parent):
    """Removes empty folders, and folders containing only empty folders"""
    if not parent.is_dir():
        return

    for child in parent.iterdir():
        prune_empty_folders(child)

    # Delete only if empty (length of list is not greater than 0)
    if not list(parent.iterdir()):
        parent.rmdir()


def process_world(world_path):
    """Fixes the names of Monumenta chunk folders for a given world"""
    monumenta_dir = world_path / 'monumenta'
    if not monumenta_dir.is_dir():
        return 0

    moved_count = 0
    for region_path in list(monumenta_dir.iterdir()):
        if not (region_path.is_dir() and RE_REGION_PATH.fullmatch(region_path.name)):
            continue

        for chunk_path in list(region_path.iterdir()):
            if not (chunk_path.is_dir() and RE_CHUNK_PATH.fullmatch(chunk_path.name)):
                continue

            for block_file in list(chunk_path.iterdir()):
                wallet_match = RE_WALLET_PATH.fullmatch(block_file.name)
                if not wallet_match:
                    print(f'Unexpected file {block_file}; need to parse its coordinates before it can be moved')
                    continue

                x = int(wallet_match[1])
                # Not required
                #y = int(wallet_match[2])
                z = int(wallet_match[3])

                cx = x // 16
                cz = z // 16

                rx = cx // 32
                rz = cz // 32

                correct_path = monumenta_dir / f'r.{rx}.{rz}' / f'c.{cx}.{cz}' / block_file.name

                if block_file != correct_path:
                    print(f'Moving {block_file} -> {correct_path}')
                    moved_count += 1
                    correct_parent = correct_path.parent
                    correct_parent.mkdir(mode=0o755, parents=True, exist_ok=True)
                    move_file(block_file, correct_path)

    prune_empty_folders(monumenta_dir)

    return moved_count


def main():
    """Fixes coordinate error for Monumenta chunk folders"""
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('world', type=Path, nargs='+', help='A folder containing one or more worlds')
    args = arg_parser.parse_args()

    all_world_paths = []
    for world_root_path in args.world:
        for world_path in World.enumerate_worlds(world_root_path):
            all_world_paths.append(world_path)

    if len(all_world_paths) <= 0:
        sys.exit("No valid worlds found")

    moved_count = 0
    for world_path in all_world_paths:
        moved_count += process_world(world_path)
    print(f'Moved {moved_count} files.')

if __name__ == '__main__':
    main()
