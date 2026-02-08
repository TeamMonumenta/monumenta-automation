#!/usr/bin/env python3

import sys
import os
from pprint import pprint

from minecraft.player_dat_format.player import PlayerFile

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

if __name__ == '__main__':
    args = sys.argv

    if len(args) != 2:
        print("Usage: print_player_nbt </path/to/player.dat>")
    else:
        playerfile = PlayerFile(args[1])
        player = playerfile.player


        # player.nbt.at_path("Tags").remove("DisableGraves")
        # player.nbt.at_path("Tags").remove("arena_player")

        arraystuff = player.nbt.at_path("Tags").value
        arraystuff = [arrayentry for arrayentry in arraystuff if arrayentry.value not in ["DisableGraves", "arena_player"]]
        player.nbt.at_path("Tags").value = arraystuff
        player.nbt.at_path("Tags").tree()
        playerfile.save()


