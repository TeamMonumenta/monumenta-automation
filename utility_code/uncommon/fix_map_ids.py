#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
from mclevel import nbt

worldDir = "/home/rock/project_epic/region_1/Project_Epic/"

maxID = -1
for f in os.listdir(worldDir+"data"):
    if (f[:4] == "map_") and (f[-4:] == ".dat"):
        maxID += 1

if maxID >= 0:
    idCountsTag = nbt.TAG_Compound()
    idCountsTag["map"] = nbt.TAG_Short(maxID)
    idCountsTag.save(worldDir+"data/idcounts.dat",compressed=False)


