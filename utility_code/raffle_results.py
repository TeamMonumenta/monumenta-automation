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
meme_seed = '''Shake it up is all that we know Using the bodies up as we go I'm waking up to fantasy The shades all around Aren't the colors we used to see Broken ice still melts in the sun And times that are broken Can often be one again We're soul alone And soul really matters to me Take a look around You're out of touch I'm out of time (time) But I'm out of my head When you're not around You're out of touch I'm out of time (time) But I'm out of my head When you're not around Oh, oh-oh, oh Oh, oh-oh, oh Reaching out for something to hold Looking for a love Where the climate is cold Manic moves and drowsy dreams Or living in the middle Between the two extremes Smoking guns hot to the touch Would cool down If we didn't use them so much We're soul alone And soul really matters to me Too much You're out of touch I'm out of time (time) But I'm out of my head When you're not around You're out of touch I'm out of time (time) But I'm out of my head When you're not around Oh, oh-oh, oh Oh, oh-oh, oh...(Out of touch) Out of touch You're out of touch I'm out of time (time) But I'm out of my head When you're not around You're out of touch I'm out of time (time) But I'm out of my head When you're not around...'''
vote_raffle(meme_seed, scoreboard, raffle_results, int(sys.argv[2]))

rafflefp = open( raffle_results, "r" )
print( rafflefp.read() )
rafflefp.close()
