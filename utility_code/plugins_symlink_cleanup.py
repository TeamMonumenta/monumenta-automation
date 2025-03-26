#!/usr/bin/env python3

import re
import time
import argparse
from pathlib import Path
from datetime import datetime

DEFAULT_RETENTION_PERIOD_DAYS = 14
DEFAULT_MINIMUM_KEPT = 3

def get_files_to_remove(targetdir, retention_period, minimum_kept):
    now = time.time()
    return_data = {}

    symlinks = [f for f in Path(targetdir).iterdir() if f.is_symlink()]
    tracked_basenames = {}
    ignore_basenames = set()
    symlink_names = {}
    symlink_targets = {}

    for symlink in symlinks:
        target = symlink.resolve()
        if not target.suffix == ".jar":
            continue

        match = re.match(r"(.+?)\d", target.name)
        if not match:
            continue

        basename = match.group(1)
        if basename in symlink_names:
            print(f"\033[91mWarning: Symlinks '{symlink.name}' and '{symlink_names[basename]}' both have the same basename '{basename}'; neither will be processed\033[0m")
            ignore_basenames.add(basename)

        symlink_targets[basename] = target.stem + target.suffix
        symlink_names[basename] = symlink.stem + symlink.suffix

        if basename not in tracked_basenames:
            tracked_basenames[basename] = []

        for fname in Path(targetdir).iterdir():
            if fname.is_symlink() or not fname.name.startswith(basename) or not fname.suffix == ".jar":
                continue
            tracked_basenames[basename].append((fname, fname.stat().st_mtime))

    for basename in ignore_basenames:
        del tracked_basenames[basename]
        del symlink_names[basename]
        del symlink_targets[basename]

    for basename, files in tracked_basenames.items():
        files.sort(key=lambda x: x[1], reverse=True)  # Sort by modification time, newest first

        to_keep = []
        old_versions = []

        # Find the current link target and remove it from the list of files by modification time
        # Add it to the to-keep list immediately so it certainly will be kept, even if a newer version is present
        for fname, mtime in files:
            if fname.name == symlink_targets[basename]:
                to_keep.append((fname, mtime))
                files.remove((fname, mtime))
                break

        for fname, mtime in files:
            if now - mtime <= retention_period:
                to_keep.append((fname, mtime))
            else:
                old_versions.append((fname, mtime))

        if len(to_keep) < minimum_kept:
            to_keep.extend(old_versions[:minimum_kept - len(to_keep)])

        return_data[basename] = {
            "target": symlink_targets[basename],
            "linkname": symlink_names[basename],
            "keep": to_keep,
            "remove": [(fname, mtime) for fname, mtime in files if fname not in [f for f, _ in to_keep]],
        }

    return return_data

def delete_old_files(targetdir, retention_period, minimum_kept, dry_run=False):
    files_to_process = get_files_to_remove(targetdir, retention_period, minimum_kept)

    for _, file_groups in files_to_process.items():
        print(f"{file_groups['linkname']}  ->  {file_groups['target']}")
        all_files = file_groups["keep"] + file_groups["remove"]
        max_width = max(len(fname.name) for fname, _ in all_files) if all_files else 40

        print(f"  keep:")
        for fname, mtime in file_groups["keep"]:
            print(f"    {fname.name.ljust(max_width)}    {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        if len(file_groups["remove"]) > 0:
            print(f"  remove:")
            for fname, mtime in file_groups["remove"]:
                print(f"\033[91m    {fname.name.ljust(max_width)}    {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
                if not dry_run:
                    fname.unlink()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deletes old versions of symlinked jar files. Run with --dry-run to examine output.")
    parser.add_argument("target_directory", help="Path to server_config/plugins directory containing JAR files and symlinks")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be kept/deleted without deleting anything")
    parser.add_argument("--retention-period", type=int, default=DEFAULT_RETENTION_PERIOD_DAYS, help=f"Retention period in days (default: {DEFAULT_RETENTION_PERIOD_DAYS})")
    parser.add_argument("--minimum-kept", type=int, default=DEFAULT_MINIMUM_KEPT, help=f"Minimum number of files to keep (default: {DEFAULT_MINIMUM_KEPT})")
    args = parser.parse_args()

    retention_period_seconds = args.retention_period * 24 * 60 * 60
    delete_old_files(args.target_directory, retention_period_seconds, args.minimum_kept, args.dry_run)
