#!/usr/bin/env pypy3

import sys
from minecraft.world import World

if __name__ == '__main__':
    args = sys.argv

    if len(args) != 3:
        print("Usage: copy_world <existing world path> <new world path>")
        sys.exit(1)

    from_path = args[1]
    dest_path = args[2]

    source_world = World(from_path)
    source_world.copy_to(dest_path, clear_world_uuid=True)
