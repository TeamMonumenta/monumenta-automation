#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

def main():
    symlinked_paths = [
        ('velocity/plugins/monumenta-velocity/config.yaml', 'server_config/data/plugins/proxy/monumenta-velocity/config.yaml'),
        ('velocity/plugins/monumenta-network-relay/config.yaml', 'server_config/data/plugins/proxy/monumenta-network-relay/config.yaml'),
        ('velocity/plugins/luckperms', 'server_config/plugins/LuckPerms/build'),
        ('sdk1/plugins/LuckPerms', 'server_config/plugins/LuckPerms/build'),
        ('sdk2/plugins/LuckPerms', 'server_config/plugins/LuckPerms/build')
    ]

    # weird naming?
    for src, dst in symlinked_paths:
        src_path = Path(src)
        dst_path = Path(dst)

        os.unlink(src_path)
        if dst_path.is_dir():
            shutil.copytree(dst_path, src_path)
        else:
            shutil.copy2(dst_path, src_path)

        print(f"Updated symlink: {dst_path} -> {src_path}")

if __name__ == "__main__":
    main()

