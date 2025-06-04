#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

def main():
    symlinked_paths = [
        ('velocity/plugins/monumenta-velocity/config.yaml', 'server_config/data/plugins/proxy/monumenta-velocity/config.yaml'),
        ('velocity/plugins/monumenta-network-relay/config.yaml', 'server_config/data/plugins/proxy/monumenta-network-relay/config.yaml'),
    ]

    for src, dst in symlinked_paths:
        src_path = Path(src)
        dst_path = Path(dst)

        os.unlink(src_path)
        shutil.copy2(dst_path, src_path)

        print(f"Updated symlink: {dst_path} -> {src_path}")

if __name__ == "__main__":
    main()

