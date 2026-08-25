#!/usr/bin/env pypy3
"""Scans through all available player stats, merging them into an output folder"""


import argparse
from datetime import datetime, timedelta
import json
from json.decoder import JSONDecodeError
from pathlib import Path
import shutil
import sys


ONE_SECOND = timedelta(seconds=1)
UPDATE_TIME_DELTA = timedelta(seconds=0.1)
BLANK_LINE = '\r' + ' ' * 240 + '\r'
IGNORED_PATHS = {
    'Project_Epic-build',
    'Project_Epic-purgatory',
    'Project_Epic-tutorial',
}


def blank_current_line():
    print(BLANK_LINE, end='', flush=False)


class StatFileManager():
    def __init__(self, root_folder, output_folder):
        if not root_folder.is_dir():
            sys.exit("Root folder must be a folder")
        self._root_folder = root_folder
        self.output_folder = output_folder
        self._first_iter = True


    def scan(self):
        start_time = datetime.now()
        next_update = start_time

        user_set = set()
        total_count = 0
        success_count = 0
        path_stats = {}

        for stat_path, stat_data in self.iter_files():
            now = datetime.now()
            if now >= next_update:
                next_update = now + UPDATE_TIME_DELTA
                time_so_far = (now - start_time) // ONE_SECOND
                minutes, seconds = divmod(time_so_far, 60)
                hours, minutes = divmod(minutes, 60)

                blank_current_line()
                print(f'[{hours:02d}:{minutes:02d}:{seconds:02d}] Scanning {stat_path}', end='', flush=True)

            total_count += 1
            user_set.add(stat_path.name)

            data_version = stat_data.get("DataVersion", None)
            if data_version is None:
                # Ignore ancient files with no upgrade path
                continue
            if data_version not in path_stats:
                path_stats[data_version] = {}
                path_stats[data_version]["0_TYPES"] = {}
            version_data_stats = path_stats[data_version]

            stats_block = stat_data.get("stats", None)
            if stats_block is None:
                if self._first_iter:
                    blank_current_line()
                    print(f'No "stats" in version {data_version} at {stat_path}')
                continue
            for stat_type, stat_type_map in stats_block.items():
                if stat_type not in version_data_stats:
                    version_data_stats[stat_type] = {}
                    version_data_stats["0_TYPES"][stat_type] = 1
                stat_type_stats = version_data_stats[stat_type]

                for stat_name, stat_value in stat_type_map.items():
                    if stat_name not in stat_type_stats:
                        stat_type_stats[stat_name] = type(stat_value).__name__

            success_count += 1

        blank_current_line()
        print(f'Scanned {len(user_set)} users in {success_count} out of {total_count} files')

        if self.output_folder.exists():
            shutil.rmtree(self.output_folder, ignore_errors=True)
        self.output_folder.mkdir(mode=0o775, parents=True)
        for data_version, version_data_stats in path_stats.items():
            data_version_path = self.output_folder / f'{data_version}.json'
            with open(data_version_path, 'w', encoding='utf-8') as fp:
                json.dump(version_data_stats, fp, ensure_ascii=False, indent=4, sort_keys=True)
        print('Done!')


    def merge(self):
        start_time = datetime.now()
        next_update = start_time

        if self.output_folder.exists():
            shutil.rmtree(self.output_folder, ignore_errors=True)
        self.output_folder.mkdir(mode=0o775, parents=True)

        total_count = 0

        for stat_path, stat_data in self.iter_files():
            now = datetime.now()
            if now >= next_update:
                next_update = now + UPDATE_TIME_DELTA
                time_so_far = (now - start_time) // ONE_SECOND
                minutes, seconds = divmod(time_so_far, 60)
                hours, minutes = divmod(minutes, 60)

                blank_current_line()
                print(f'[{hours:02d}:{minutes:02d}:{seconds:02d}] Scanning {stat_path}', end='', flush=True)

            total_count += 1

            stat_filename = stat_path.name
            merged_path = self.output_folder / stat_filename
            if not merged_path.is_file():
                # Copy the old stats file as-is if we don't have merged stats yet
                shutil.copy2(stat_path, merged_path)
                continue

            # Load the previously merged stats
            merged_data = {}
            with open(merged_path, 'r', encoding='utf-8-sig') as fp:
                merged_data = json.load(fp)

            # Merge the stats
            for namespace, namespace_data_current in stat_data["stats"].items():
                if namespace not in merged_data["stats"]:
                    merged_data["stats"][namespace] = namespace_data_current
                    continue
                namespace_data_merged = merged_data["stats"][namespace]

                for key, key_value_current in namespace_data_current.items():
                    if key not in namespace_data_merged:
                        namespace_data_merged[key] = key_value_current
                        continue
                    key_value_merged = namespace_data_merged[key]

                    if namespace == "minecraft:custom" and key.startswith("minecraft:time_since_"):
                        # Take the lower of the "Time Since" values
                        key_value_merged = min(key_value_merged, key_value_current)
                    else:
                        # Add everything else together
                        key_value_merged += key_value_current

                    namespace_data_merged[key] = key_value_merged

            # Write the merged stats back
            with open(merged_path, 'w', encoding='utf-8') as fp:
                json.dump(merged_data, fp, ensure_ascii=False) #, indent=2, sort_keys=True) # Remove the indent when done debugging

        blank_current_line()
        output_count = len(list(self.output_folder.glob('*.json')))
        print(f'[{hours:02d}:{minutes:02d}:{seconds:02d}] Done! Merged {output_count} user stats from {total_count} files.', flush=True)


    def iter_files(self):
        for stat_folder in self.iter_stat_folders():
            for stat_path in stat_folder.glob('*.json'):
                try:
                    with open(stat_path, 'r', encoding='utf-8-sig') as fp:
                        stat_data = json.load(fp)
                        yield (stat_path, stat_data)
                except (UnicodeDecodeError, JSONDecodeError):
                    if self._first_iter:
                        blank_current_line()
                        print(f'Could not read {stat_path}')
                    continue
            self._first_iter = False


    def iter_stat_folders(self):
        for stat_folder in sorted(self._root_folder.glob('**/Project_Epic-*/stats')):
            if not stat_folder.is_dir() or any(x in str(stat_folder) for x in IGNORED_PATHS):
                continue
            yield stat_folder


def main():
    """Parse args, then stat files"""
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('root_folder', type=Path)
    arg_parser.add_argument('output_folder', type=Path)
    args = arg_parser.parse_args()

    manager = StatFileManager(args.root_folder, args.output_folder)
    manager.merge()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting', flush=True)
