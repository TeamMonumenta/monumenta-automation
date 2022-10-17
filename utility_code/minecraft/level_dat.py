import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

class LevelDat():
    """Global level data, loaded from disk."""

    def __init__(self, path):
        """Load a level.dat file from the path provided, and allow saving."""

        self.world_name = os.path.basename(os.path.dirname(os.path.realpath(path)))
        self.path = path
        self.level_dat_file = nbt.NBTFile.load(self.path)
        self.nbt = self.level_dat_file.root_tag.body
        self.data_version = self.nbt.at_path('Data.DataVersion').value
        if self.nbt.has_path('Data.LevelName'):
            self.nbt.at_path('Data.LevelName').value = str(self.world_name)

    def save(self, path=None):
        """Save the level.dat file to its original location."""
        if path is None:
            path = self.path
        self.level_dat_file.save(path)

    def _init_datapack_tags(self):
        if not self.nbt.has_path('Data'):
            self.nbt.value['Data'] = nbt.TagCompound({})
        if not self.nbt.has_path('Data.DataPacks'):
            self.nbt.value['Data.DataPacks'] = nbt.TagCompound({})
        if not self.nbt.has_path('Data.DataPacks'):
            self.nbt.at_path('Data').value['DataPacks'] = nbt.TagCompound({})
        if not self.nbt.has_path('Data.DataPacks.Enabled'):
            self.nbt.at_path('Data.DataPacks').value['Enabled'] = nbt.TagList([])
        if not self.nbt.has_path('Data.DataPacks.Disabled'):
            self.nbt.at_path('Data.DataPacks').value['Disabled'] = nbt.TagList([])

    def enable_datapack(self, datapack):
        """
        Enables a datapack (only relevant to the "main" world)
        """

        # Initialize values
        self._init_datapack_tags()
        enabled_tags = self.nbt.at_path('Data.DataPacks.Enabled').value
        disabled_tags = self.nbt.at_path('Data.DataPacks.Disabled').value

        # Enable specified datapack
        datapack_tag = nbt.TagString(datapack)
        if datapack_tag in disabled_tags:
            disabled_tags.remove(datapack_tag)
            self.sort_disabled()
        if datapack_tag not in enabled_tags:
            enabled_tags.append(datapack_tag)

    def disable_datapack(self, datapack):
        """
        Disables a datapack (only relevant to the "main" world)
        """

        # Initialize values
        self._init_datapack_tags()
        enabled_tags = self.nbt.at_path('Data.DataPacks.Enabled').value
        disabled_tags = self.nbt.at_path('Data.DataPacks.Disabled').value

        # Disable specified datapack
        datapack_tag = nbt.TagString(datapack)
        if datapack_tag in enabled_tags:
            enabled_tags.remove(datapack_tag)
        if datapack_tag not in disabled_tags:
            disabled_tags.append(datapack_tag)
            self.sort_disabled()

    @property
    def difficulty(self):
        """
        Gets the world's current difficulty
        """
        return self.nbt.at_path('Data.Difficulty').value

    @difficulty.setter
    def difficulty(self, new_difficulty):
        """
        Sets the world's current difficulty

        NOTE: Caller must save this level.dat after updating it!
        """

        self.nbt.at_path('Data.Difficulty').value = new_difficulty

    @property
    def enabled_datapacks(self):
        """
        Gets the world's current enabled datapacks (only relevant to the "main" world)
        """

        for datapack_tag in self.nbt.iter_multipath('Data.DataPacks.Enabled[]'):
            yield datapack_tag.value

    @property
    def disabled_datapacks(self):
        """
        Gets the world's current disabled datapacks (only relevant to the "main" world)
        """

        for datapack_tag in self.nbt.iter_multipath('Data.DataPacks.Disabled[]'):
            yield datapack_tag.value

    @enabled_datapacks.setter
    def enabled_datapacks(self, datapacks):
        """
        Sets the world's current enabled datapacks (only relevant to the "main" world)

        NOTE: Caller must save this level.dat after updating it!
        """

        # Initialize values
        self._init_datapack_tags()
        enabled_tags = self.nbt.at_path('Data.DataPacks.Enabled').value
        disabled_tags = self.nbt.at_path('Data.DataPacks.Disabled').value

        # Disable all datapacks
        disabled_tags += enabled_tags
        self.sort_disabled()
        enabled_tags.clear()

        # Enable specified datapacks
        for datapack in datapacks:
            self.enable_datapack(datapack)

    @disabled_datapacks.setter
    def disabled_datapacks(self, datapacks):
        """
        Sets the world's current disabled datapacks (only relevant to the "main" world)

        NOTE: Caller must save this level.dat after updating it!
        """

        # Initialize values
        self._init_datapack_tags()
        enabled_tags = self.nbt.at_path('Data.DataPacks.Enabled').value
        disabled_tags = self.nbt.at_path('Data.DataPacks.Disabled').value

        # Enable all datapacks
        enabled_tags += disabled_tags
        disabled_tags.clear()

        # Disable specified datapacks
        for datapack in datapacks:
            self.disable_datapack(datapack)
        self.sort_disabled()

    def sort_disabled(self):
        """
        Sorts the disabled datapacks by alphanumeric name
        """

        disabled = self.nbt.at_path('Data.DataPacks.Disabled').value
        disabled.sort(key=lambda tag: tag.value)

    def __repr__(self):
        return f'LevelDat({self.path!r})'
