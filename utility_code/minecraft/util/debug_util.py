#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

class NbtPathDebug():
    """A helper to follow where in an NBT file we're recursively iterating."""
    def __init__(self, file_uri, root_tag, obj, data_version):
        self.file_uri = file_uri
        self.root_tag = root_tag
        self.data_version = data_version

        self.parent = None # NbtPathDebug
        self.nbt_path_from_parent = '{}'
        self.tag_here = self.root_tag
        self.obj = obj # Object for the current path

    def get_child_debug(self, path_from_here, tag, obj):
        """Create a debug entry from this entry.

        path_from_here is an NBT path from this entry.
        tag is the NBT tag at that path.
        obj is the wrapper object that makes sense of that tag.
        """
        child_debug = NbtPathDebug(self.file_uri, self.root_tag, obj, self.data_version)

        child_debug.parent = self
        child_debug.nbt_path_from_parent = path_from_here
        child_debug.tag_here = tag

        return child_debug

    @property
    def full_nbt_path(self):
        """Get the full NBT path from the original file."""
        if self.parent is None:
            return self.nbt_path_from_parent

        return nbt.nbt_path_join(self.parent.full_nbt_path, self.nbt_path_from_parent)

    def print(self):
        """Print the debug path from file root to here."""
        if self.parent is None:
            print(f'NBT debug path for {type(self.obj)} {self.file_uri}')
            return

        self.parent.print()
        print(f'- go into {type(self.obj)} at {self.nbt_path_from_parent}')

