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
meme_seed = '''Ralof: Hey, you. You're finally awake. You were trying to cross the border, right? Walked right into that Imperial ambush, same as us, and that thief over there.  Lokir: Damn you Stormcloaks. Skyrim was fine until you came along. Empire was nice and lazy. If they hadn't been looking for you, I could've stolen that horse and been half way to Hammerfell. You there. You and me -- we should be here. It's these Stormcloaks the Empire wants.  Ralof: We're all brothers and sisters in binds now, thief.  Imperial Soldier: Shut up back there!  [Lokir looks at the gagged man.] Lokir: And what's wrong with him?  Ralof: Watch your tongue! You're speaking to Ulfric Stormcloak, the true High King.  Lokir: Ulfric? The Jarl of Windhelm? You're the leader of the rebellion. But if they captured you... Oh gods, where are they taking us?  Ralof: I don't know where we're going, but Sovngarde awaits.  Lokir: No, this can't be happening. This isn't happening.  Ralof: Hey, what village are you from, horse thief?  Lokir: Why do you care?  Ralof: A Nord's last thoughts should be of home.  Lokir: Rorikstead. I'm...I'm from Rorikstead.  [They approach the village of Helgen. A soldier calls out to the lead wagon.] Imperial Soldier: General Tullius, sir! The headsman is waiting!  General Tullius: Good. Let's get this over with.  Lokir: Shor, Mara, Dibella, Kynareth, Akatosh. Divines, please help me.  Ralof: Look at him, General Tullius the Military Governor. And it looks like the Thalmor are with him. Damn elves. I bet they had something to do with this.  This is Helgen. I used to be sweet on a girl from here. Wonder if Vilod is still making that mead with juniper berries mixed in. Funny...when I was a boy, Imperial walls and towers used to make me feel so safe.'''
vote_raffle(meme_seed, scoreboard, raffle_results, int(sys.argv[2]))

rafflefp = open( raffle_results, "r" )
print( rafflefp.read() )
rafflefp.close()
