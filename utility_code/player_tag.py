#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Player scoreboard tag utility
"""

from player_tag_lib import listUniqueTags
from player_tag_lib import deleteTheseTags
from player_tag_lib import deleteOtherTags

worldDir = "/home/rock/tmp/BETA/region_1/Project_Epic-region_1/"
tagsToDelete = [
    "delMe",
    "delMe2",
]
tagsToKeep = [
    "keepMe",
    "keepMe2",
]

print "*** Current tags:"
listUniqueTags(worldDir)
'''
print "*** Deleting " + str(tagsToDelete)
deleteTheseTags(worldDir,tagsToDelete)
print "*** Current tags:"
listUniqueTags(worldDir)
print "*** Deleting tags not matching " + str(tagsToKeep)
deleteOtherTags(worldDir,tagsToKeep)
print "*** Current tags:"
listUniqueTags(worldDir)
print "*** Done."
'''

