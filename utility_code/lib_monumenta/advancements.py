#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from json_file import jsonFile

def renameAdvancements(worldDir,replaceList):
    """
    If you want to rename an advancement without
    it getting removed from players, use this.
    
    replaceList looks like this:
    [
        ["old","new"],
        ["dungeons:yellow/find","monumenta:dungeons/yellow/find"],
        ["dungeons:yellow/complete","monumenta:dungeons/yellow/complete"],
    ]
    """
    for fileName in os.listdir(worldDir+"advancements"):
        advFile = jsonFile(worldDir+"advancements/" + fileName)
        for replacement in replaceList:
            old = replacement[0]
            if old in advFile.dict.keys():
                new = replacement[1]
                advFile.dict[new] = advFile.dict.pop(old)
        advFile.save()

