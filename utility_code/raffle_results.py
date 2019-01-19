#!/usr/bin/env python3

import sys
import tempfile
import numpy

from lib_py3.raffle import vote_raffle
from lib_py3.scoreboard import Scoreboard

if (len(sys.argv) != 3):
    sys.exit("Usage: {} </path/to/world> <num_winners>".format(sys.argv[0]))

scoreboard = Scoreboard(sys.argv[1])
raffle_results = tempfile.mktemp()
meme_seed = ''':TOOHYPE:'''
vote_raffle(meme_seed, scoreboard, raffle_results, int(sys.argv[2]))

rafflefp = open( raffle_results, "r" )
print( rafflefp.read() )
rafflefp.close()
