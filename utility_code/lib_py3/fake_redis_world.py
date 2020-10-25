import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

from lib_py3.iterators.item_iterator import ItemIterator
from lib_py3.player import Player

class FakeRedisWorld(object):
    def __init__(self, path):
        self.path = path
        self.find_players()

    def find_players(self):
        self._player_paths = []

        player_data_path = os.path.join(self.path, 'playerdata')
        if os.path.isdir(player_data_path):
            for filename in os.listdir( player_data_path ):
                try:
                    player = None
                    if filename[-4:] == '.dat':
                        player = uuid.UUID(filename[:-4])
                    if player:
                        self._player_paths.append(os.path.join(player_data_path, filename))
                except:
                    pass

    @property
    def player_paths(self):
        return self._player_paths

    def players(self):
        for player_path in self._player_paths:
            yield Player(player_path)

    def items(self, readonly=True):
        return ItemIterator(self, pos1=None, pos2=None, readonly=readonly, no_players=False, players_only=True)

