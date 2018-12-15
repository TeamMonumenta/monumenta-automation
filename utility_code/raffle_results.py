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
meme_seed = '''Flex Tape! The super strong waterproof tape that can instantly patch, bond, seal, and repair! Flex Tape is no ordinary tape. It's triple thick adhesive virtually welds itself to surfaces, instantly stopping the toughest leaks. Leaky pipes can cause MAJOR damage, but flex tape grips on tight and bonds instantly. PLUS, Flex Tape's powerful adhesive is so strong, it even works underwater! Now you can repair leaks in pools and spas without draining them. Flex Tape is perfect for marine, campers, and RVs. Flex Tape is super strong and once it's on, it holds on tight. And for emergency auto repair, Flex Tape keeps it's grip even in the toughest conditions. Big storms can cause big damage, but Flex Tape comes super wide so you can easily fix large holes. To show you the power of Flex Tape, I SAWED THIS BOAT IN HALF and repaired it with only Flex Tape. Not only does Flex Tape's powerful adhesive hold the boat together, but it creates a super strong, water-tight seal so the inside is completely dry. YEE DOGGIE! Just cut, peel, stick, and seal. Imagine everything you can do with the power of Flex Tape!'''
vote_raffle(meme_seed, scoreboard, raffle_results, int(sys.argv[2]))

rafflefp = open( raffle_results, "r" )
print( rafflefp.read() )
rafflefp.close()
