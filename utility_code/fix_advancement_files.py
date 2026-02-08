#!/usr/bin/env python3
"""Apply fixes to advancement files, ie for new versions of Minecraft"""


import argparse
import json
from pathlib import Path
import re
import sys


LOCATION_FIELD_REMOVED_TYPES_RE = re.compile("(minecraft:)?(location|slept_in_bed|hero_of_the_village|voluntary_exile)")


def fix_criteria(criteria_name, criteria_data):
    fix_count = 0

    # Remove `location` field from relevant criteria types
    if LOCATION_FIELD_REMOVED_TYPES_RE.fullmatch(criteria_data.get('trigger', '')):
        conditions = criteria_data.get('conditions', {})

        player_condition = conditions.setdefault('player', [])

        if isinstance(player_condition, dict):
            player_condition = [
                {
                    "condition": "minecraft:entity_properties",
                    "entity": "this",
                    "predicate": player_condition
                }
            ]
            conditions['player'] = player_condition
            fix_count += 1

        location = conditions.pop('location‌', None)
        if location is not None:
            player_condition.append({
                "condition": "minecraft:entity_properties",
                "entity": "this",
                "predicate": {
                    "location": location
                }
            })
            fix_count += 1

        # Legacy format where location fields are directly in the root node
        if len(conditions) > 1: # player field always present by here
            legacy_location = conditions
            del legacy_location['player']
            conditions = {
                "player": player_condition
            }
            criteria_data['conditions'] = conditions

            player_condition.append({
                "condition": "minecraft:entity_properties",
                "entity": "this",
                "predicate": {
                    "location": legacy_location
                }
            })
            fix_count += 1

    return fix_count


def fix_advancement(advancement_path, dry_run=False):
    data = None
    with open(advancement_path, 'r', encoding='utf-8-sig') as fp:
        data = json.load(fp)

    if data is None:
        return

    fix_count = 0

    for criteria_name, criteria_data in data.get('criteria', {}).items():
        fix_count += fix_criteria(criteria_name, criteria_data)

    if fix_count:
        print(f'- {advancement_path}: {fix_count}')
        if dry_run:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            with open(advancement_path, 'w', encoding='utf-8') as fp:
                json.dump(
                    data,
                    fp,
                    ensure_ascii=False,
                    indent=2
                )
                fp.write('\n')


def fix_datapack(datapack_path, dry_run=False):
    if not datapack_path.is_dir():
        print(f'Non-folder datapacks not supported; try extracting them first: {datapack_path}', file=sys.stderr)
        return

    print(f'Scanning {datapack_path}...')

    for advancement_path in datapack_path.glob('data/*/advancements/**/*.json'):
        fix_advancement(advancement_path, dry_run=dry_run)


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('--datapacks_folder', type=Path, nargs='+')
    arg_parser.add_argument('--advancement_path', type=Path, nargs='+')
    arg_parser.add_argument('--dry-run', action='store_true')
    args = arg_parser.parse_args()

    dry_run = args.dry_run

    if args.datapacks_folder:
        for datapacks_folder in args.datapacks_folder:
            for datapack_path in datapacks_folder.glob('*'):
                fix_datapack(datapack_path, dry_run=dry_run)

    if args.advancement_path:
        for advancement_path in args.advancement_path:
            fix_advancement(advancement_path, dry_run=dry_run)


if __name__ == '__main__':
    main()
