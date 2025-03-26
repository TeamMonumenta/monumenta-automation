#!/usr/bin/env python3

import re
import time
import argparse
from pathlib import Path
from datetime import datetime

RETENTION_PERIOD = 14 * 24 * 60 * 60  # Two weeks in seconds
MINIMUM_KEPT = 3

def get_files_to_remove(targetdir):
    now = time.time()
    return_data = {}

    symlinks = [f for f in Path(targetdir).iterdir() if f.is_symlink()]
    tracked_basenames = {}
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
        symlink_targets[basename] = target.stem + target.suffix
        symlink_names[basename] = symlink.stem + symlink.suffix

        if basename not in tracked_basenames:
            tracked_basenames[basename] = []

        for fname in Path(targetdir).iterdir():
            if fname.is_symlink() or not fname.name.startswith(basename) or not fname.suffix == ".jar":
                continue
            tracked_basenames[basename].append((fname, fname.stat().st_mtime))

    for basename, files in tracked_basenames.items():
        files.sort(key=lambda x: x[1], reverse=True)  # Sort by modification time, newest first

        to_keep = []
        old_versions = []

        for fname, mtime in files:
            if now - mtime <= RETENTION_PERIOD:
                to_keep.append((fname, mtime))
            else:
                old_versions.append((fname, mtime))

        if len(to_keep) < MINIMUM_KEPT:
            to_keep.extend(old_versions[:MINIMUM_KEPT - len(to_keep)])

        return_data[basename] = {
            "target": symlink_targets[basename],
            "linkname": symlink_names[basename],
            "keep": to_keep,
            "remove": [(fname, mtime) for fname, mtime in files if fname not in [f for f, _ in to_keep]],
        }

    return return_data

def delete_old_files(targetdir, dry_run=False):
    files_to_process = get_files_to_remove(targetdir)

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
                print(f"    {fname.name.ljust(max_width)}    {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")
                if not dry_run:
                    fname.unlink()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deletes old versions of symlinked jar files. Run with --dry-run to examine output.")
    parser.add_argument("target_directory", help="Path to server_config/plugins directory containing JAR files and symlinks")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be kept/deleted without deleting anything")
    args = parser.parse_args()

    delete_old_files(args.target_directory, args.dry_run)
