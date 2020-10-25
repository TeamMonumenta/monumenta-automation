#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

class Player(object):
    """
    An object for editing a player (1.13+).

    The path you provide is expected to be a player.dat file.
    """
    def __init__(self, path=None):
        """
        Load a world folder, fetching the list of region files and players that it contains.

        >>> player = Player(os.path.join(world.path, 'playerdata/25c8b7fa-dd4a-4bbb-8cf9-d534cf66d6f9.dat'))
        """
        self.path = path
        if self.path is not None:
            self.player_dat_file = nbt.NBTFile.load(self.path)
            self.player_tag = self.player_dat_file.root_tag.body
        else:
            self.player_dat_file = None
            self.player_tag = None

    @classmethod
    def from_tag(cls, player_tag):
        """
        Load a player from NBT; used for the player tag
        from level.dat. Must be saved from wherever the
        tag was loaded from to apply.

        >>> singleplayer_player = Player.from_tag(world.single_player())
        """
        result = cls()
        result.player_tag = player_tag
        return result

    def save(self):
        """
        Save the player; does nothing if loaded from a tag,
        such as the player tag from level.dat, as it is
        read as a reference, and thus saved with level.dat.

        >>> self.save()
        """
        if self.path:
            self.player_dat_file.save(self.path)

    @property
    def dimension(self):
        """
        Returns the player's dimension as an integer

        1 = The End
        0 = The Overworld
        -1 = The Nether

        >>> print(self.dimension)
        1
        """
        return self.player_tag.at_path('Dimension').value

    @dimension.setter
    def dimension(self, dimension):
        """
        Set the player's dimension

        1 = The End
        0 = The Overworld
        -1 = The Nether

        >>> self.dimension = 1
        """
        self.player_tag.at_path('Dimension').value = dimension

    @property
    def pos(self):
        """
        Returns the player's coordinates as [x, y, z, yaw, pitch]

        >>> print(self.pos)
        [2.71817181, 63.5, 3.1415]
        """
        x = self.player_tag.at_path('Pos[0]').value
        y = self.player_tag.at_path('Pos[1]').value
        z = self.player_tag.at_path('Pos[2]').value

        yaw = self.player_tag.at_path('Rotation[0]').value
        pitch = self.player_tag.at_path('Rotation[1]').value

        result = [x, y, z, yaw, pitch]

        return result

    @pos.setter
    def pos(self, pos):
        """
        Set the player's coordinates to pos=[x, y, z] or pos=[x, y, z, yaw, pitch]

        >>> self.pos = [2.71817181, 63.5, 3.1415]
        """
        if len(pos) != 3 and len(pos) != 5:
            raise IndexError('pos must have 3 or 5 entries; x, y, z or x, y, z, yaw, pitch')
        for i in range(3):
            self.player_tag.at_path(f'Pos[{i}]').value = pos[i]
        if len(pos) == 5:
            for i in range(2):
                self.player_tag.at_path('Rotation[{i}]').value = pos[i+3]

    @property
    def rotation(self):
        """
        Returns the player's rotation as [yaw, pitch]

        >>> print(self.rotation)
        [180.0, 45.0]
        """
        yaw = self.player_tag.at_path('Rotation[0]').value
        pitch = self.player_tag.at_path('Rotation[1]').value

        result = [yaw, pitch]

        return result

    @rotation.setter
    def rotation(self, rotation):
        """
        Set the player's rotation to rotation=[yaw, pitch]

        >>> self.rotation = [180.0, 45.0]
        """
        if len(rotation) != 2:
            raise IndexError('rotation must have 2 entries; yaw, pitch')
        for i in range(2):
            self.player_tag.at_path(f'Rotation[{i}]').value = rotation[i]

    @property
    def motion(self):
        """
        Returns the player's motion as [x, y, z]

        >>> print(self.motion)
        [0.7, -1.5, 0.3]
        """
        x = self.player_tag.at_path('Motion[0]').value
        y = self.player_tag.at_path('Motion[1]').value
        z = self.player_tag.at_path('Motion[2]').value

        result = [x, y, z]

        return result

    @motion.setter
    def motion(self, motion):
        """
        Set the player's coordinates to motion=[x, y, z]

        >>> self.motion = [0.7, -1.5, 0.3]
        """
        if len(motion) != 3:
            raise IndexError('motion must have 3 entries; x, y, z')
        for i in range(3):
            self.player_tag.at_path('Motion[{i}]').value = motion[i]

    @property
    def spawn(self):
        """
        Returns the player's spawn coordinates, or
        None if not set. In that case, use the world spawn.

        >>> print(self.spawn)
        None
        >>> self.spawn = [1, 2, 5]
        >>> print(self.spawn)
        [1, 2, 5]
        """
        result = None

        if (
            self.player_tag.has_path('SpawnX') and
            self.player_tag.has_path('SpawnY') and
            self.player_tag.has_path('SpawnZ')
        ):
            x = self.player_tag.at_path('SpawnX').value
            y = self.player_tag.at_path('SpawnY').value
            z = self.player_tag.at_path('SpawnZ').value

            result = [x, y, z]

        return result

    @spawn.setter
    def spawn(self, pos):
        """
        Set the player's spawn coordinates to pos=[x, y, z],
        or remove the player's spawn coordinates with pos=None
        to cause them to respawn at the world spawn.

        >>> self.spawn = None
        >>> self.spawn = [1, 2, 5]
        """
        paths = ['SpawnX', 'SpawnY', 'SpawnZ']
        if pos is None:
            for path in paths:
                self.player_tag.value.pop(path)
            self.player_tag.value.pop('SpawnForced')
            return

        if len(pos) != 3:
            raise IndexError('pos must have 3 entries, xyz')
        for i in range(3):
            if self.player_tag.has_path(paths[i]):
                self.player_tag.at_path(paths[i]).value = pos[i]
            else:
                self.player_tag.value[paths[i]] = nbt.TagInt(pos[i])
        if self.player_tag.has_path('SpawnForced'):
            self.player_tag.at_path('SpawnForced').value = 1
        else:
            self.player_tag.value['SpawnForced'] = nbt.TagByte(1)

    @property
    def tags(self):
        """
        Returns the player's tags as a list of strings

        >>> print(self.tags)
        ["TagA", "TagB"]
        """
        result = []
        if self.player_tag.has_path('Tags'):
            for tag in self.player_tag.iter_multipath('Tags[]'):
                result.append(tag.value)

        return result

    @tags.setter
    def tags(self, tags):
        """
        Replace the player's tags with a list of strings

        >>> self.tags = ["TagA", "TagB"]
        """
        if not self.player_tag.has_path('Tags'):
            self.player_tag.value['Tags'] = nbt.TagList([])

        result = []
        for tag in tags:
            result.append(nbt.TagString(tag))
        self.player_tag.at_path('Tags').value = result

    def modify_tags(self, tags):
        """
        Add and remove tags more like the in-game "/tags" command.
        Will not duplicate tags or throw errors for valid tags.

        >>> self.modify_tags("!DeletedTag")
        >>> self.modify_tags("NewTag")
        >>> self.modify_tags(["!DeletedTag", "NewTag", "AlsoNew"])
        """
        if type(tags) == str:
            tags = [tags]

        result = self.tags

        for tag in tags:
            if tag.startswith('!'):
                tag = tag[1:]
                if tag in result:
                    result.remove(tag)
            else:
                if tag not in result:
                    result.append(tag)

        self.tags = result

    def full_heal(self):
        """
        Fully heal the player:
        - put them at full health
        - put them out if they're on fire
        - cancel any built-up fall damage
        - cancel any momentum they've built up
        - fill their lungs with air
        - sate their hunger
        - revive them from the dead

        >>> self.full_heal()
        """
        self.player_tag.at_path('Health').value = 20.0
        self.player_tag.at_path('Fire').value = -20
        self.player_tag.at_path('Air').value = 300
        self.player_tag.at_path('foodLevel').value = 20
        self.player_tag.at_path('foodSaturationLevel').value = 5.0
        self.player_tag.at_path('foodExhaustionLevel').value = 0.0
        self.player_tag.at_path('foodTickTimer').value = 0
        self.player_tag.at_path('DeathTime').value = 0

