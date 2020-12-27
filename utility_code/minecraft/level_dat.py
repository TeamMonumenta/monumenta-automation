#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

class LevelDat():
    """Global level data, loaded from disk."""

    def __init__(self, path):
        """Load a level.dat file from the path provided, and allow saving."""

        self.path = path
        with open(self.path, 'rb') as fp:
            self.level_dat_file = nbt.NBTFile.load(self.path)
            self.nbt = self.level_dat_file.root_tag.body
        self.data_version = self.nbt.at_path('Data.DataVersion').value

    def save(self):
        """Save the level.dat file to its original location."""
        self.level_dat_file.save(self.path)

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
        # Initialize values
        self._init_datapack_tags()
        enabled_tags = self.nbt.at_path('Data.DataPacks.Enabled').value
        disabled_tags = self.nbt.at_path('Data.DataPacks.Disabled').value

        # Enable specified datapack
        datapack_tag = nbt.TagString(datapack)
        if datapack_tag in disabled_tags:
            disabled_tags.remove(datapack_tag)
        if datapack_tag not in enabled_tags:
            enabled_tags.append(datapack_tag)

    def disable_datapack(self, datapack):
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

    @property
    def enabled_datapacks(self):
        for datapack_tag in self.nbt.iter_multipath('Data.DataPacks.Enabled[]'):
            yield datapack_tag.value

    @property
    def disabled_datapacks(self):
        for datapack_tag in self.nbt.iter_multipath('Data.DataPacks.Disabled[]'):
            yield datapack_tag.value

    @enabled_datapacks.setter
    def enabled_datapacks(self, datapacks):
        # Initialize values
        self._init_datapack_tags()
        enabled_tags = self.nbt.at_path('Data.DataPacks.Enabled').value
        disabled_tags = self.nbt.at_path('Data.DataPacks.Disabled').value

        # Disable all datapacks
        disabled_tags += enabled_tags
        enabled_tags.clear()

        # Enable specified datapacks
        for datapack in datapacks:
            self.enable_datapack(datapack)

    @disabled_datapacks.setter
    def disabled_datapacks(self, datapacks):
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

    def __repr__(self):
        return f'LevelDat({self.path!r})'
