#!/usr/bin/env python3

import datetime
import json
import os
import sys
import uuid
from urllib.request import urlopen

from minecraft.chunk_format.entity import Entity
from minecraft.player_dat_format.item import Item
from minecraft.util.changelog_map import ChangelogMap
from minecraft.util.comparison_util import AlwaysLess
from minecraft.util.debug_util import NbtPathDebug
from minecraft.util.iter_util import TypeMultipathMap

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

class Player(Entity):
    """A player, loaded from a tag."""
    __CLASS_UNINITIALIZED = True
    __MULTIPATHS = TypeMultipathMap()

    def __init__(self, nbt, path_debug=None, root=None):
        """Load a player from an NBT tag.

        Must be saved from wherever the tag was loaded from to apply.
        path_debug is the new NbtPathDebug object for this object, missing its references to this.
        root is the base Entity, BlockEntity, or Item of this Entity, which may be itself.
        """
        if type(self).__CLASS_UNINITIALIZED:
            self._init_multipaths(type(self).__MULTIPATHS)
            type(self).__CLASS_UNINITIALIZED = False
        self._multipaths = type(self).__MULTIPATHS

        self.nbt = nbt
        self.path_debug = path_debug
        if self.path_debug is not None:
            self.path_debug.obj = self
        self.root = root if root is not None else self
        self.root_entity = self

    def _init_multipaths(self, multipaths):
        super()._init_multipaths(multipaths)
        multipaths[Entity] |= frozenset({
            'RootVehicle.Entity',
        })
        multipaths[Item] |= frozenset({
            #'SelectedItem', # Not actually saved to disk
            'EnderItems[]',
        })

    @property
    def dimension(self):
        """Returns the player's dimension as an integer

        1 = The End
        0 = The Overworld
        -1 = The Nether

        >>> print(self.dimension)
        1
        """
        return self.nbt.at_path('Dimension').value

    @dimension.setter
    def dimension(self, dimension):
        """Set the player's dimension

        1 = The End
        0 = The Overworld
        -1 = The Nether

        >>> self.dimension = 1
        """
        self.nbt.at_path('Dimension').value = dimension

    @property
    def spawn(self):
        """Returns the player's spawn coordinates, or None if not set.

        If None is returned, use the world spawn.

        >>> print(self.spawn)
        None
        >>> self.spawn = [1, 2, 5]
        >>> print(self.spawn)
        [1, 2, 5]
        """
        result = None

        if (
            self.nbt.has_path('SpawnX') and
            self.nbt.has_path('SpawnY') and
            self.nbt.has_path('SpawnZ')
        ):
            x = self.nbt.at_path('SpawnX').value
            y = self.nbt.at_path('SpawnY').value
            z = self.nbt.at_path('SpawnZ').value

            result = [x, y, z]

        return result

    @spawn.setter
    def spawn(self, pos):
        """Set or delete the player's spawn position.

        Set the player's spawn coordinates to pos=[x, y, z],
        or remove the player's spawn coordinates with pos=None
        to cause them to respawn at the world spawn.

        >>> self.spawn = None
        >>> self.spawn = [1, 2, 5]
        """
        paths = ['SpawnX', 'SpawnY', 'SpawnZ']
        if pos is None:
            for path in paths:
                self.nbt.value.pop(path)
            self.nbt.value.pop('SpawnForced')
            return

        if len(pos) != 3:
            raise IndexError('pos must have 3 entries, xyz')
        for i in range(3):
            if self.nbt.has_path(paths[i]):
                self.nbt.at_path(paths[i]).value = pos[i]
            else:
                self.nbt.value[paths[i]] = nbt.TagInt(pos[i])
        if self.nbt.has_path('SpawnForced'):
            self.nbt.at_path('SpawnForced').value = 1
        else:
            self.nbt.value['SpawnForced'] = nbt.TagByte(1)

    def full_heal(self):
        """Fully heal the player.

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

    @staticmethod
    def get_uuid_by_name(name, when=datetime.datetime.now()):
        """Get the UUID of a player by their name.

        Optionally specify when they had that IGN in the event of name changes.
        """
        unix_timestamp = int(when.timestamp())
        with urlopen(f'https://api.mojang.com/users/profiles/minecraft/{name}?at={unix_timestamp}') as response:
            player_profile_json = json.loads(response.read().decode())
            # Also contains:
            # "name": name (the same one you requested)
            # "demo": True (missing if False; indicates unpaid account)
        return uuid.UUID(player_profile_json["id"])

    @staticmethod
    def get_names_by_uuid(uuid):
        """Get all past and current player names for a UUID."""
        formatted_uuid = uuid_util.to_tag_string(uuid, hyphens=False)
        with urlopen(f'https://api.mojang.com/user/profiles/{formatted_uuid}/names') as response:
            player_names_json = json.loads(response.read().decode())

        player_names = ChangelogMap({AlwaysLess(): player_names_json[0]["name"]})
        for name_timestamp_pair in player_names_json[1:]:
            unix_timestamp = name_timestamp_pair["changedToAt"] / 1000.0 # Convert from ms to seconds
            time_obj = datetime.datetime.fromtimestamp(unix_timestamp)
            player_names[time_obj] = name_timestamp_pair["name"]

        return player_names

    def load_names(self):
        """Load all past and current player names for this player's UUID."""
        self._player_names = self.get_names_by_uuid(self.uuid)

    def name(self, when=datetime.datetime.now()):
        if self._player_names is None:
            self.load_names()

        return self._player_names[when]

    def __str__(self):
        return self.name()

    def __repr__(self):
        return f'Player(nbt.TagCompound.from_mojangson({self.nbt.to_mojangson()!r}))'


class PlayerFile():
    """A player file, stored on disk."""
    def __init__(self, path):
        """Load a player file from the path provided, and allow saving."""
        self.path = path
        with open(self.path, 'rb') as fp:
            self.player_dat_file = nbt.NBTFile.load(self.path)
            self.nbt = self.player_dat_file.root_tag.body
        self.data_version = self.nbt.at_path('DataVersion').value
        self.path_debug = NbtPathDebug(f'file://{os.path.realpath(self.path)}', self.nbt, self, self.data_version)
        self.player = Player(self.nbt, self.path_debug)

    def save(self):
        """Save the player file to its original location."""
        self.player_dat_file.save(self.path)

    def __repr__(self):
        return f'PlayerFile({os.path.basename(self.path)!r})'


from minecraft.util import uuid_util
