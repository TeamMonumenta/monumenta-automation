#!/usr/bin/env python3
#
# NOTE! This file is not used by the terrain reset code anymore!

import os
import sys
import tempfile
import numpy

from lib_py3.raffle import vote_raffle

raffle_results = tempfile.mktemp()
meme_seed = '''Cursed Raffle Seed:TM:'''
vote_raffle(meme_seed, '/home/epic/play/project_epic/bungee/uuid2name.yml', '/home/epic/play/project_epic/bungee/plugins/Monumenta-Bungee/votes', raffle_results, 2, dry_run=True)

rafflefp = open( raffle_results, "r" )
print( rafflefp.read() )
rafflefp.close()
