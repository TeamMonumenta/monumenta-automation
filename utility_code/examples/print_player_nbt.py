#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from lib_py3.player import Player

args = sys.argv

if len(args) != 2:
    print("Usage: print_player_nbt </path/to/player.dat>")
else:
    player = Player(args[1])

    player.player_tag.tree()
