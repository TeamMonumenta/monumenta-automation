#!/usr/bin/env python3

"""A tool to backup and restore specific Redis keys"""


import argparse
from pathlib import Path
import sys
from lib_py3.redis_backup_manager import RedisBackupManager


def get_manager(args):
    """Gets the RedisBackupManager from the common arguments"""
    worm_file = args.worm_backup_file
    scratch_dir = args.scratch_backup_folder

    if worm_file.exists():
        if not worm_file.is_file():
            sys.exit(f'Worm backup file {worm_file!s} exists, but is not a file')

    try:
        scratch_dir.mkdir(mode=0o755, parents=True, exist_ok=True)
    except Exception:
        sys.exit(f'Scratch backup folder {scratch_dir!s} cannot be created')

    return RedisBackupManager(
        worm_file,
        scratch_dir,
        args.domain,
        redis_host=args.redis_host,
        redis_port=args.redis_port
    )


def test_worm(args):
    """Subcommand to test if the worm backup is valid"""
    rbm = get_manager(args)
    if rbm.worm_backup_available():
        print('WORM backup is available!')
    else:
        print('WORM backup is NOT available!')


def list_backups(args):
    """Subcommand to list available backups"""
    rbm = get_manager(args)
    iterator = rbm.iter_scratch_backups if args.skip_worm else rbm.iter_all_backups

    print('Backups:')
    count = 0
    for backup in iterator():
        print(f'- {backup}')
        count += 1

    print(f'Found {count} backups')


def create_worm_backup(args):
    """Subcommand to create the worm backup if possible"""
    rbm = get_manager(args)
    rbm.create_worm_backup()


def create_scratch_backup(args):
    """Subcommand to create a scratch backup if possible"""
    rbm = get_manager(args)
    rbm.create_scratch_backup(args.backup_name, keys=args.key)


def restore_worm_backup(args):
    """Subcommand to restore the worm backup if possible"""
    rbm = get_manager(args)
    rbm.restore_worm_backup(keys=args.key)


def restore_scratch_backup(args):
    """Subcommand to restore a scratch backup if possible"""
    rbm = get_manager(args)
    rbm.restore_scratch_backup(args.backup_name, keys=args.key)


def delete_scratch_backup(args):
    """Subcommand to create a scratch backup if possible"""
    rbm = get_manager(args)
    rbm.delete_scratch_backup(args.backup_name)


def main():
    """Main program and argument parsing

    subcommands are handled by individual methods
    """
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('--worm_backup_file', type=Path, help='The path to the write-once read-many backup file as used by weekly updates')
    arg_parser.add_argument('--scratch_backup_folder', type=Path, help='The folder of backups that can be created or deleted at any time')
    arg_parser.add_argument('--redis_host', type=str, default='redis')
    arg_parser.add_argument('--redis_port', type=int, default=6379)
    arg_parser.add_argument('--domain', type=str, default='play', help='The domain as used in certain Redis keys')
    subparsers = arg_parser.add_subparsers(required=True, help='Subcommand descriptions:')

    parser_test_worm = subparsers.add_parser('test_worm_backup', help='Verifies that the Write-Once Read-Many backup is valid')
    parser_test_worm.set_defaults(func=test_worm)

    parser_list_backups = subparsers.add_parser('list_backups', help='Lists available backups')
    parser_list_backups.add_argument('--skip_worm', action='store_true')
    parser_list_backups.set_defaults(func=list_backups)

    parser_create_worm = subparsers.add_parser('create_worm_backup', help='Creates a Write-Once Read-Many backup if possible')
    parser_create_worm.set_defaults(func=create_worm_backup)

    parser_create_scratch = subparsers.add_parser('create_scratch_backup', help='Creates a scratch backup if possible')
    parser_create_scratch.add_argument('backup_name', type=str, help='The name of the backup to create. Must end in .tgz')
    parser_create_scratch.add_argument('key', type=str, nargs='*', help='Redis keys to include; overrides the default key list')
    parser_create_scratch.set_defaults(func=create_scratch_backup)

    parser_restore_worm = subparsers.add_parser('restore_worm_backup', help='Restores a Write-Once Read-Many backup if possible')
    parser_restore_worm.add_argument('key', type=str, nargs='*', help='Redis keys to include; overrides the default key list')
    parser_restore_worm.set_defaults(func=restore_worm_backup)

    parser_restore_scratch = subparsers.add_parser('restore_scratch_backup', help='Restores a scratch backup if possible')
    parser_restore_scratch.add_argument('backup_name', type=str, help='The name of the backup to restore. Must end in .tgz')
    parser_restore_scratch.add_argument('key', type=str, nargs='*', help='Redis keys to include; overrides the default key list')
    parser_restore_scratch.set_defaults(func=restore_scratch_backup)

    parser_delete_scratch = subparsers.add_parser('delete_scratch_backup', help='Deletes a scratch backup if possible')
    parser_delete_scratch.add_argument('backup_name', type=str, help='The name of the backup to delete. Must end in .tgz')
    parser_delete_scratch.set_defaults(func=delete_scratch_backup)

    args = arg_parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
