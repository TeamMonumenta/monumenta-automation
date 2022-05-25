import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

class NbtPathDebug():
    """
        A subclass of entities to help understand where they are and
        their relationship to other entities they are stored inside of.

        Subclasses that extend this should call __init__() with appropriate data
    """

    def nbt_path_init(self, nbt, parent, root, data_version):
        self.nbt = nbt
        self.parent = parent
        self.root = root
        self.data_version = data_version

    def is_in_spawner(self):
        parent = self.parent
        while parent is not None:
            if hasattr(parent, 'nbt') and parent.nbt:
                if parent.nbt.has_path('MaxSpawnDelay'):
                    return True

            if not hasattr(parent, 'parent'):
                return False

            # Remember to go up a level, or infinite recursion issues occur
            parent = parent.parent

        return False

    def is_in_spawn_egg(self):
        parent = self.parent
        while parent is not None:
            if isinstance(parent, Item) and parent.id.endswith('_spawn_egg'):
                return True

            if not hasattr(parent, 'parent'):
                return False

            # Remember to go up a level, or infinite recursion issues occur
            parent = parent.parent

        return False

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

    def get_path_repr_str(self):
        """Return the text to be entered in a script or interpretter."""
        if self.parent is None:
            return repr(self)
        return f'{repr(self.parent)} \\\n    {repr(self)}'

    def get_path_str(self):
        if self.parent is None:
            return self.get_debug_str()
        return f'{self.parent.get_path_str()} -> {self.get_debug_str()}'

    def get_path_pretty_str(self):
        """Return the text to be entered in a script or interpretter."""
        if self.parent is None:
            return repr(self)
        return f'{repr(self.parent)} \\\n    {repr(self)}'

from minecraft.player_dat_format.item import Item
