"""A library to dump and restore Redis data for specific keys.

Note that these backups are version-specific; you cannot restore to a different version than was used to make the backup.
The backups are stored as tgz files with the structure:
.
|-- info.json
|-- keys
|   |-- <key 1>
|   |-- <key 2>
|   `-- <key N>
`-- summary.json

`info.json` contains the results of the `info` command, and is used to verify the version matches.
Each file in the `keys` directory is a binary dump file with the filename matching its key.
`summary.json` is written last, and includes a key count and the uncompressed size of the key data dumps.
    Its presence is used as a terminator to indicate that all Redis data has been successfully written.
"""


from collections import Counter
from datetime import datetime, UTC
import io
import json
from pathlib import Path
import re
import tarfile
import sys
import yaml
import redis

_file = Path(__file__).absolute()
_parent_dir = _file.parent
sys.path.append(str(_parent_dir))
from common import eprint


class RedisBackupManager():
    """The main class for interacting with Redis key backups"""


    SCAN_ITER_COUNT = 5000


    def __init__(self, worm_backup_file, scratch_backup_folder, domain, redis_host="redis", redis_port=6379):
        """Initializes a Redis Backup Manager

        worm_backup_file: The Write Once Read Many backup file. Used in our weekly backups
        scratch_backup_folder: A folder for temporary backups of redis data. These can be created or deleted as needed
        domain: The build/play/etc domain as used by certain redis keys. Used to provide `{domain}` placeholders
        redis_host: The URL used to connect to Redis. kubernetes directs this to the correct internal IP address
        redis_port: The port used to connect to Redis. You don't need to change this unless you've changed the port on the Redis server.
        """
        self._worm_backup_file = Path(worm_backup_file).absolute()
        self._scratch_backup_folder = Path(scratch_backup_folder).absolute()
        self._domain = domain
        self._redis_host = redis_host
        self._redis_port = redis_port

        self._default_keys_str = []
        with open(_parent_dir / "redis_backup_manager_keys.yaml", "r", encoding="utf-8-sig") as fp:
            for friendly_pattern in yaml.load(fp, Loader=yaml.FullLoader):
                self._default_keys_str.append(friendly_pattern.strip())


    def worm_backup_available(self):
        """Returns True if the WORM backup exists."""
        return self.is_valid_backup(self._worm_backup_file)


    def create_worm_backup(self):
        """Create the Write-Once Read-Many backup if it doesn't already exist"""
        self._create_backup(self._worm_backup_file)


    def create_scratch_backup(self, backup_name, keys=None):
        """Creates an unprotected backup"""
        self._create_backup(self._scratch_backup_folder / backup_name, keys=keys)


    def _create_backup(self, backup_file, keys=None):
        """Creates a backup at the specified path if allowed.

        If not None, keys should be an iterable of redis key regex. Otherwise, the default keys will be used.
        """


        # Verify the backup path is allowed

        backup_file = Path(backup_file).absolute()
        if self._worm_backup_file == backup_file:
            if self._worm_backup_file.exists():
                sys.exit('The WORM backup file already exists in whole or in part. Refusing to create a backup.')
        elif not backup_file.name.endswith('.tgz'):
            sys.exit('Scratch backup files must have the file extension ".tgz".')
        elif self._scratch_backup_folder != backup_file.parent:
            sys.exit(f'Scratch backup files must be placed directly in the scratch backup folder in this version ({self._scratch_backup_folder!s}).')
        elif backup_file.exists():
            sys.exit('That scratch backup file already exists and needs to be deleted first.')


        # Determine which Redis key regex to use

        if not keys:
            keys = list(self._default_keys_str)

        keys_re = {}
        for friendly_pattern in keys:
            pattern = (
                friendly_pattern
                    .replace('{domain}', self._domain)
                    .replace('{uuid}', '(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})')
                )

            try:
                keys_re[friendly_pattern] = re.compile(pattern)
            except Exception:
                eprint(f'Could not parse regex pattern {pattern}; skipping')


        # Draw the rest of the owl...I mean, make the rest of the backup

        r = redis.Redis(host=self._redis_host, port=self._redis_port)
        try:
            with tarfile.open(backup_file, 'x:gz') as tf:
                info_dict = r.info()
                RedisBackupManager._add_json_to_tarfile(tf, 'info.json', info_dict)

                total_keys = 0
                key_matches = Counter()
                key_expiries_ms = {}
                for key_bytes in self._iter_keys():
                    key = key_bytes.decode('utf-8')
                    if RedisBackupManager._update_key_match_counter(key_matches, keys_re, key):
                        total_keys += 1
                        expiration_ms = r.pexpiretime(key)
                        if expiration_ms > 0:
                            key_expiries_ms[key] = expiration_ms
                        dumped_value = r.dump(key)
                        RedisBackupManager._add_binary_blob_to_tarfile(tf, f'keys/{key}', dumped_value)

                RedisBackupManager._add_json_to_tarfile(tf, 'key_expiries_ms.json', key_expiries_ms)

                now = datetime.now(UTC)
                RedisBackupManager._add_json_to_tarfile(tf, 'summary.json', {
                    "human_timestamp_utc": now.isoformat(),
                    "unix_timestamp": now.timestamp(),
                    "total": total_keys,
                    "key_matches": key_matches,
                })

                print(f'Backed up {total_keys} keys:')
                for friendly_key, count in key_matches.items():
                    print(f'- {friendly_key!r}: {count}')
                print(f'Additionally, {len(key_expiries_ms)} keys are set to expire')

        except Exception:
            eprint(f'Unable to create the backup {backup_file!s}')
            raise


    @staticmethod
    def _add_json_to_tarfile(tar_file, path, json_data):
        json_str = json.dumps(json_data, ensure_ascii=False, indent=2) + '\n'
        json_bytes = json_str.encode('utf-8')
        RedisBackupManager._add_binary_blob_to_tarfile(tar_file, path, json_bytes)


    @staticmethod
    def _add_binary_blob_to_tarfile(tar_file, path, binary_blob):
        tar_info = tarfile.TarInfo(path)
        tar_info.size = len(binary_blob)
        tar_info.mtime = datetime.now(UTC).timestamp()
        tar_info.mode = 0o644
        tar_file.addfile(tar_info, io.BytesIO(binary_blob))


    def restore_worm_backup(self, keys=None):
        """Restore the Write-Once Read-Many backup if it exists"""
        self._restore_backup(self._worm_backup_file, keys=None)


    def restore_scratch_backup(self, backup_name, keys=None):
        """Restores an unprotected backup"""
        self._restore_backup(self._scratch_backup_folder / backup_name, keys=keys)


    def _restore_backup(self, backup_file, keys=None):
        """Restores a backup at the specified path if allowed.

        If not None, keys should be an iterable of redis key regex. Otherwise, the default keys will be used.
        """


        # Verify the backup path is allowed

        backup_file = Path(backup_file).absolute()
        if self._worm_backup_file == backup_file:
            if not self._worm_backup_file.exists():
                sys.exit('The WORM backup file is NOT present!')
        elif not backup_file.name.endswith('.tgz'):
            sys.exit('Scratch backup files must have the file extension ".tgz".')
        elif self._scratch_backup_folder != backup_file.parent:
            sys.exit(f'Scratch backup files must be placed directly in the scratch backup folder in this version ({self._scratch_backup_folder!s}).')
        elif not backup_file.exists():
            sys.exit('That scratch backup file does not exist!')


        # Check if backup file is valid at all (might not be the correct version, so check that later)
        if not self.is_valid_backup(backup_file):
            sys.exit('That backup file is missing or incomplete!')


        # Determine which Redis key regex to use

        if not keys:
            keys = list(self._default_keys_str)

        keys_re = {}
        for friendly_pattern in keys:
            pattern = (
                friendly_pattern
                    .replace('{domain}', self._domain)
                    .replace('{uuid}', '(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})')
                )

            try:
                keys_re[friendly_pattern] = re.compile(pattern)
            except Exception:
                eprint(f'Could not parse regex pattern {pattern}; skipping')


        # Draw the rest of the owl...I mean, restore the rest of the backup

        r = redis.Redis(host=self._redis_host, port=self._redis_port)
        try:
            with tarfile.open(backup_file, 'r:gz') as tf:
                # Verify version matches, otherwise we'll get an error from Redis later
                redis_info_dict = r.info()
                backup_info_dict = RedisBackupManager._read_json_from_tarfile(tf, 'info.json')
                if not RedisBackupManager._check_version(redis_info_dict, backup_info_dict):
                    sys.exit('This backup was created for a different version of Redis, and cannot be restored in this way.')

                now = datetime.now(UTC)
                now_ms = 1000 * now.timestamp()
                key_expiries_ms = RedisBackupManager._read_json_from_tarfile(tf, 'key_expiries_ms.json')

                # Delete the matching keys that are currently in Redis
                deleted_keys_total = 0
                deleted_key_matches = Counter()
                for key_bytes in self._iter_keys():
                    key = key_bytes.decode('utf-8')
                    if RedisBackupManager._update_key_match_counter(deleted_key_matches, keys_re, key):
                        deleted_keys_total += 1
                        r.delete(key)

                print(f'Deleted {deleted_keys_total} keys:')
                for friendly_key, count in deleted_key_matches.items():
                    print(f'- {friendly_key!r}: {count}')


                # Restore the matching keys from the backup into Redis
                restored_keys_total = 0
                restored_key_matches = Counter()
                for member in tf.getmembers():
                    file_name = member.name
                    if not file_name.startswith('keys/'):
                        continue
                    key = file_name[5:]

                    ttl_ms = key_expiries_ms.get(key, 0)
                    if ttl_ms > 0:
                        if ttl_ms < now_ms:
                            # Key already expired
                            continue

                    if RedisBackupManager._update_key_match_counter(restored_key_matches, keys_re, key):
                        restored_keys_total += 1
                        dumped_value = RedisBackupManager._read_binary_blob_from_tarfile(tf, file_name)
                        r.restore(key, ttl=ttl_ms, value=dumped_value, replace=True, absttl=(ttl_ms != 0))

                print(f'Restored {restored_keys_total} keys:')
                for friendly_key, count in restored_key_matches.items():
                    print(f'- {friendly_key!r}: {count}')


        except Exception:
            eprint(f'Unable to restore the backup {backup_file!s}')
            raise


    @staticmethod
    def _check_version(redis_info, backup_info):
        return all((
            RedisBackupManager._info_field_matches(redis_info, backup_info, ('redis_version',)),
            RedisBackupManager._info_field_matches(redis_info, backup_info, ('redis_build_id',)),
        ))


    def _info_field_matches(redis_info, backup_info, field_path):
        redis_part = redis_info
        backup_part = backup_info

        for path_part in field_path:
            try:
                redis_part = redis_part[path_part]
                backup_part = backup_part[path_part]
            except Exception:
                return False

        return redis_part == backup_part


    @staticmethod
    def _read_json_from_tarfile(tar_file, path):
        binary_blob = RedisBackupManager._read_binary_blob_from_tarfile(tar_file, path)
        json_str = binary_blob.decode('utf-8')
        return json.loads(json_str)


    @staticmethod
    def _read_binary_blob_from_tarfile(tar_file, path):
        member = tar_file.getmember(path)
        with tar_file.extractfile(member) as fp:
            return fp.read()


    def _iter_keys(self):
        r = redis.Redis(host=self._redis_host, port=self._redis_port)
        yield from r.scan_iter(count=RedisBackupManager.SCAN_ITER_COUNT)


    @staticmethod
    def _update_key_match_counter(counter, keys_re, key):
        """Updates a collections.Counter with all matching key regex, and returns True if one of them matched."""
        found_match = False
        for key_str, key_re in keys_re.items():
            if key_re.fullmatch(key):
                found_match = True
                counter[key_str] += 1
        return found_match


    def delete_scratch_backup(self, backup_name):
        """Deletes an unprotected backup"""
        backup_file = Path(backup_name)
        if backup_file.parent == Path('.'):
            backup_file = self._scratch_backup_folder / backup_file.name


        # Verify the backup path is allowed

        if not backup_file.name.endswith('.tgz'):
            sys.exit('Scratch backup files must have the file extension ".tgz".')
        if self._scratch_backup_folder != backup_file.parent:
            sys.exit(f'Scratch backup files must be placed directly in the scratch backup folder in this version ({self._scratch_backup_folder!s}).')
        if not backup_file.exists():
            sys.exit('That scratch backup file does not exist.')


        # Delete!

        backup_file.unlink()
        print(f'Deleted {backup_file!s}')


    def iter_scratch_backups(self, fast=True):
        """Iterates over all valid scratch backups

        Uses a fast check by default (checks for the first file in the backups without checking the last file in the backups)
        """
        try:
            glob_iterator = self._scratch_backup_folder.glob('*.tgz')
        except Exception:
            return

        for backup_file in glob_iterator:
            if self.is_valid_backup(backup_file, fast):
                yield backup_file


    def iter_all_backups(self, fast=True):
        """Iterates over all valid backups

        Uses a fast check by default (checks for the first file in the backups without checking the last file in the backups)
        """
        if self.worm_backup_available():
            yield self._worm_backup_file
        yield from self.iter_scratch_backups(fast)


    def is_valid_backup(self, backup_file, fast=False):
        """Returns True if a given backup is valid"""
        try:
            with tarfile.open(backup_file, 'r:gz') as tf:
                tf.getmember('info.json' if fast else 'summary.json')
            return True
        except Exception:
            return False
