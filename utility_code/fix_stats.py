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


def format_elapsed(start_time):
    """Returns the time since start_time as HH:MM:SS"""
    time_so_far = (datetime.now() - start_time) // ONE_SECOND
    minutes, seconds = divmod(time_so_far, 60)
    hours, minutes = divmod(minutes, 60)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}'


def blank_current_line():
    """Erases the text on the current line so that it can be overwritten"""
    print(BLANK_LINE, end='', flush=False)


def fix_negative(num):
    """Returns negative stats as 0. These are small negative damage awards, not 32-bit wraparound - MC clamps stats at INT_MAX"""
    if num < 0:
        return 0
    return num


def is_time_since(namespace, key):
    """Time Since stats aren't cumulative"""
    return namespace == "minecraft:custom" and key.startswith("minecraft:time_since_")


def merge_stats(merged_data, stat_data, same_world):
    """Merges one stats file's contents into merged_data.

    Copies of the same world take the highest value of each stat, since they share history. Different worlds add
    them together. Time Since stats always take the lowest value.
    """
    for namespace, namespace_data_current in stat_data["stats"].items():
        namespace_data_merged = merged_data["stats"].get(namespace, None)
        if namespace_data_merged is None:
            namespace_data_merged = {}
            merged_data["stats"][namespace] = namespace_data_merged

        for key, key_value_current in namespace_data_current.items():
            key_value_current = fix_negative(key_value_current)
            if key not in namespace_data_merged:
                namespace_data_merged[key] = key_value_current
            elif is_time_since(namespace, key):
                namespace_data_merged[key] = min(namespace_data_merged[key], key_value_current)
            elif same_world:
                namespace_data_merged[key] = max(namespace_data_merged[key], key_value_current)
            else:
                namespace_data_merged[key] += key_value_current


class StatFileManager():
    def __init__(self, root_folder, output_folder):
        if not root_folder.is_dir():
            sys.exit("Root folder must be a folder")
        self._root_folder = root_folder
        self.output_folder = output_folder
        self._first_iter = True


    def scan(self):
        """Scan for player stat files of miscellaneous versions and report the data types for each field in those versions"""
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
        """Merge player stat files from all shards into one file per player.

        Shards running copies of the same world (e.g. valley, valley-2) have the same world folder name, and their
        stats folders have been copied between each other too many times to work out which stats are shared. So each
        world's copies are combined first, taking the highest value of each stat, and then the worlds are added.
        """
        start_time = datetime.now()
        next_update = start_time

        self.check_data_versions()

        if self.output_folder.exists():
            shutil.rmtree(self.output_folder, ignore_errors=True)
        self.output_folder.mkdir(mode=0o775, parents=True)

        total_count = 0

        for world_name, stat_folders in self.iter_worlds():
            if len(stat_folders) > 1:
                blank_current_line()
                shards = ', '.join(stat_folder.parent.parent.name for stat_folder in stat_folders)
                print(f'Combining {len(stat_folders)} copies of {world_name}: {shards}', flush=True)

            # Player stats filename -> that player's stats combined across this world's copies
            world_data = {}
            for stat_path, stat_data in self.iter_files(stat_folders):
                now = datetime.now()
                if now >= next_update:
                    next_update = now + UPDATE_TIME_DELTA
                    blank_current_line()
                    print(f'[{format_elapsed(start_time)}] Scanning {stat_path}', end='', flush=True)

                total_count += 1

                if "stats" not in stat_data:
                    continue

                merged_data = world_data.setdefault(stat_path.name, {"stats": {}, "DataVersion": stat_data["DataVersion"]})
                merge_stats(merged_data, stat_data, same_world=True)

            # Add this world's stats to each player's merged stats
            for stat_filename, world_stats in world_data.items():
                merged_path = self.output_folder / stat_filename
                if merged_path.is_file():
                    with open(merged_path, 'r', encoding='utf-8') as fp:
                        merged_data = json.load(fp)
                    merge_stats(merged_data, world_stats, same_world=False)
                else:
                    merged_data = world_stats

                with open(merged_path, 'w', encoding='utf-8') as fp:
                    json.dump(merged_data, fp, ensure_ascii=False)

        blank_current_line()
        output_count = len(list(self.output_folder.glob('*.json')))
        print(f'[{format_elapsed(start_time)}] Done! Merged {output_count} user stats from {total_count} files.', flush=True)


    def check_data_versions(self):
        """Exits if any stats file isn't on the newest DataVersion.

        Merging doesn't upgrade stats - run /monumenta upgradeplayerstats on every shard first, so vanilla upgrades
        every stats file to the current version.
        """
        print('Checking stats file versions...', flush=True)
        data_versions = {}
        for stat_path, stat_data in self.iter_files():
            data_versions.setdefault(stat_data.get("DataVersion", None), []).append(stat_path)

        newest = max((version for version in data_versions if version is not None), default=None)
        old_versions = {version: paths for version, paths in data_versions.items() if version != newest}
        if old_versions:
            for version, paths in sorted(old_versions.items(), key=lambda item: -1 if item[0] is None else item[0]):
                version_name = "no DataVersion" if version is None else f"DataVersion {version}"
                print(f'{len(paths)} files with {version_name}, for example {paths[0]}', flush=True)
            sys.exit(f'Found stats files that are not on the newest DataVersion {newest}. '
                     'Run /monumenta upgradeplayerstats on every shard first.')
        print(f'All stats files are on DataVersion {newest}', flush=True)


    def iter_worlds(self):
        """Yields (world folder name, stats folders) - shards running copies of the same world share a world folder name"""
        worlds = {}
        for stat_folder in self.iter_stat_folders():
            worlds.setdefault(stat_folder.parent.name, []).append(stat_folder)
        yield from worlds.items()


    def iter_files(self, stat_folders=None):
        """Yields the path and parsed contents of every json file in the given stats folders, or all expected ones"""
        for stat_folder in stat_folders if stat_folders is not None else self.iter_stat_folders():
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
        """Yields expected stats folders"""
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
