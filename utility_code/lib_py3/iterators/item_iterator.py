#
# Recursive iterator for items everywhere in the world
#

from lib_py3.iterators.iterator_interface import item_iterator

class ItemIterator(object):
    def __init__(self, world, pos1=None, pos2=None, readonly=True, no_players=False, players_only=False):
        self._world = world
        self._pos1 = pos1
        self._pos2 = pos2
        self._readonly = readonly
        self._no_players = no_players
        self._players_only = players_only

        self._iter = item_iterator(self._world, self._pos1, self._pos2, self._readonly, self._no_players, self._players_only)

    def __iter__(self):
        """
        Initialize the iterator for use.

        Doing this here instead of in __init__ allows the iterator to potentially be re-used
        """
        self._iter = item_iterator(self._world, self._pos1, self._pos2, self._readonly, self._no_players, self._players_only)

        return self

    def __next__(self):
        """
        Iterates over items in the world

        Iteration order is depth-first, returning the higher-level object first then using
        a depth-first iterator into nested sub elements

        Return value is:
            item - the item TagCompound
        """
        return self._iter.__next__()
