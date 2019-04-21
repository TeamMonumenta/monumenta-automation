#!/usr/bin/env python3

from numpy import random
import hashlib

seed = '''TL;DR LET ME IN REEEEEEEEEE'''
num_winners = 10
vote_names = [
  'Badbird27',
  'Biw_',
  'Brydudethegreat',
  'Bubignao',
  'DeKleineKabouter',
  'Deneb_Stargazer',
  'dragon_sliaor',
  'Eb_',
  'Firestorm256',
  'Fwap_a_Durp',
  'g3p0',
  'Golden_Paladin',
  'greatwell',
  'helphelp11',
  'Keick',
  'Mandolino17',
  'Masoncooler1',
  'MatixD26',
  'ming0328ming',
  'nightmessenger ',
  'NobodyPi',
  'NoobGamingITA',
  'NoverFast',
  'Omsitua',
  'Parallax2316',
  'PetBunny',
  'Pwn4d226',
  'RealBraven',
  'ScryingStan',
  'SecretSeller',
  'ShadowVisions',
  'Siravia',
  'SpicyTortilla',
  'st0mpa',
  'SunnyVisions',
  'TheGamerMig',
  'ThePelocho88',
  'Tostitokid259',
  'W_Schnee',
  'xEpicB',
  'YourBoiMicro',
  'Zehinsky',
]

# Convert string seed into a number, set the random number generator to start with that
random.seed(int(hashlib.sha1(seed.encode('utf-8')).hexdigest()[:8], 16))

# Pick winners
winners = list(random.choice(vote_names, replace=False, size=num_winners))
print("This week's winners:")
for winner in sorted(winners):
    print(winner)
