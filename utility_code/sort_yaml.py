#!/usr/bin/env python3
"""Sort a yaml file in-place, removing comments as a side effect.

Leaves a .bak file next to the original file
"""
import argparse
import shutil
import yaml

from pathlib import Path


def sort_yaml_file(path):
    if not path.is_file():
        raise FileNotFoundError(path)

    path_bak = path.parent / (path.name + '.bak')
    shutil.copy2(path, path_bak)

    with open(path, 'r') as fp:
        original_contents = yaml.load(fp, Loader=yaml.FullLoader)

    sorted_contents = get_sorted_node(original_contents)
    with open(path, 'w') as fp:
        yaml.dump(sorted_contents, fp, indent=2, allow_unicode=True, sort_keys=False)


def get_sorted_node(node):
    if isinstance(node, str):
        return node

    if isinstance(node, dict):
        sorted_node = {}

        for key, value in sorted(node.items(), key=_node_sort_key):
            sorted_node[key] = get_sorted_node(value)

        return sorted_node

    if isinstance(node, list):
        return [get_sorted_node(value) for value in node]

    return node


def _node_sort_key(key_value_pair):
    key, value = key_value_pair
    return (isinstance(value, (dict, list)) and not isinstance(value, str), key.lower(), key)


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('path', nargs='+', type=Path)
    args = arg_parser.parse_args()

    for path in args.path:
        sort_yaml_file(path)


if __name__ == '__main__':
    main()
