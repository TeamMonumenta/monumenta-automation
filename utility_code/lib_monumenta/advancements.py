#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from json_file import jsonFile
from dateutil.parser import parse as parsetime

class advancements(object):
    def __init__(self,worldDir):
        """
        A class to edit player advancements.

        Usage:
        newObject = advancements(worldDir)

        Each method saves changes in place.
        """
        if worldDir[-1] != '/':
            self.worldDir = worldDir + '/'
        else:
            self.worldDir = worldDir
        self.advDir = self.worldDir+"advancements/"
        self.fileList = os.listdir(self.advDir)

    def renameAdvancements(self,replaceList):
        """
        Renames advancements. replaceList format is:
        [
          ["old:A","new:A"],
          ["old:B","new:B"],
        ]
        """
        for fileName in self.fileList:
            try:
                path = self.advDir + fileName
                advFile = jsonFile(path)
                for replacement in replaceList:
                    old = replacement[0]
                    if old in advFile.dict.keys():
                        new = replacement[1]
                        advFile.dict[new] = advFile.dict.pop(old)
                advFile.save()
            except:
                print "\r!!! Error occured with file "+fileName+"!\n"
                pass

    def revoke(self,revokeList):
        """
        Revoke advancements or their criteria. Allows selecting by date.
        revokeList format is:
        [
          # Remove all occurences of an advancement
          {"advancement":"minecraft:the_end"},
          # Remove all occurences of an advancement's criteria
          {"advancement":"monumenta:jp_all","criteria":"NyrWindmill"},
          # Remove all occurences of an advancement within a date range (must indicate timezone)
          {"advancement":"slayer:bslayer5","from":"2018-03-31 02:00:00 -0400","to":"'2018-04-07 02:00:00 -0400'"},
          # Remove all advancements within a date range (must indicate timezone)
          {"from":"2018-03-31 02:00:00 -0400","to":"'2018-04-07 02:00:00 -0400'"},
          # "from" does not require "to", and vice versa.
        ]
        """
        cache = []
        for toRevoke in revokeList:
            cachedItem = {}
            if "advancement" in toRevoke:
                cachedItem["advancement"] = toRevoke["advancement"]
            if "criteria" in toRevoke:
                cachedItem["criteria"] = toRevoke["criteria"]
            if "from" in toRevoke:
                cachedItem["from"] = parsetime(toRevoke["from"])
            if "to" in toRevoke:
                cachedItem["to"] = parsetime(toRevoke["to"])
            cache.append(cachedItem)

        for fileName in self.fileList:
            try:
                path = self.advDir + fileName
                advFile = jsonFile(path)
                advs = advFile.dict
                for change in cache:
                    if (
                        "advancement" in change and
                        change["advancement"] in advs
                    ):
                        advKeys = (change["advancement"],)
                        if advKeys[0] not in advs:
                            continue
                    else:
                        advKeys = advs.keys()
                    for advKey in advKeys:
                        advCrit = advs[advKey]['criteria']
                        if "criteria" in change:
                            critList = (change["criteria"],)
                            if critList[0] not in advCrit:
                                continue
                        else:
                            critList = advCrit.keys()
                        for critKey in critList:
                            timestamp = parsetime(advCrit[critKey])
                            if (
                                "from" in change and
                                change["from"] > timestamp
                            ):
                                continue
                            if (
                                "to" in change and
                                change["to"] < timestamp
                            ):
                                continue
                            advCrit.pop(critKey)
                        if len(advCrit.keys()) == 0:
                            advs.pop(advKey)
                advFile.save()
            except:
                print "!!! Error occured with file "+fileName+"!\n"
                pass

