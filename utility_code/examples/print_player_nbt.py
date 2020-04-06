#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from lib_py3.player import Player


player = Player("/home/epic/play/project_epic/lightgray/Project_Epic-lightgray/playerdata/f374dfda-9760-4d74-aae8-7be7f61294b5.dat")

player.player_tag.tree()
