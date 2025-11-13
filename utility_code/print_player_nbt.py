#!/usr/bin/env python3

import sys
import os

from minecraft.player_dat_format.player import PlayerFile

if __name__ == '__main__':
    args = sys.argv

    if len(args) != 2:
        print("Usage: print_player_nbt </path/to/player.dat>")
    else:
        player = PlayerFile(args[1]).player

        player.nbt.tree(highlight=False)
