#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

class Player(object):
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
