#!/usr/bin/env python3
"""Diff two NBT files or Mojangson strings."""

import argparse
import os
import sys

from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt


def diff_files(path1, path2):
    file1 = nbt.NBTFile.load(path1).root_tag.body
    file2 = nbt.NBTFile.load(path2).root_tag.body

    file1.diff(file2, order_matters=False, show_values=True)


def nbt_prompt(name):
    input_type = input(f'{name} is [F]ile or [M]onjangson: ')
    if len(input_type) == 0:
        print('Exiting.')
        sys.exit()
    c = input_type[0].lower()
    if c == 'f':
        path = input(f'{name} path: ')
        try:
            path = os.path.expanduser(path)
            return nbt.NBTFile.load(path).root_tag.body
        except Exception:
            raise
            print(f'{name} must be an NBT file')
            sys.exit()

    elif c == 'm':
        mojangson = input(f'{name} mojangson: ')
        try:
            return nbt.TagCompound.from_mojangson(mojangson)
        except Exception:
            print(f"{name} must be a compound tag's mojangson")
            sys.exit()

    else:
        print('Exiting.')
        sys.exit()


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('-i', '--interactive', action='store_true')
    arg_parser.add_argument('file1', type=Path, nargs='?')
    arg_parser.add_argument('file2', type=Path, nargs='?')
    args = arg_parser.parse_args()

    if args.file1:
        if not args.file2:
            arg_parser.error('must provide two files to diff')
            sys.exit()

        try:
            nbt1 = nbt.NBTFile.load(args.file1).root_tag.body
        except Exception:
            raise
            arg_parser.error('file1 must be an NBT file')
            sys.exit()

        try:
            nbt2 = nbt.NBTFile.load(args.file2).root_tag.body
        except Exception:
            arg_parser.error('file2 must be an NBT file')
            sys.exit()

        nbt1.diff(nbt2, order_matters=False, show_values=True)

    if args.interactive:
        while True:
            nbt1 = nbt_prompt('NBT1')
            nbt2 = nbt_prompt('NBT2')
            nbt1.diff(nbt2, order_matters=False, show_values=True)

    if not args.file1 and not args.interactive:
        arg_parser.print_usage()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")
        sys.exit()
