#!/usr/bin/env python3

import sys

from lib_py3.terrain_reset import terrain_reset_instance

if (len(sys.argv) != 9):
    sys.exit("Usage: {} </path/to/from> </path/to/dest> <x1> <y1> <z1> <x2> <y2> <z2>".format(sys.argv[0]))

config = {
    "server":"temp",
    "localMainFolder":sys.argv[1],
    "localDstFolder":sys.argv[2],
    "coordinatesToCopy":(
        {
            "name":"region",
            "pos1":(int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])),
            "pos2":(int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8])),
        },
    )
}

print("Config:" + str(config))

input('Enter to accept/run, control+c to cancel:')

terrain_reset_instance(config)

print("Done")
