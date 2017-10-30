#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Player scoreboard tag utility
"""

from player_tag_lib import listUniqueTags
from player_tag_lib import deleteTheseTags
from player_tag_lib import deleteOtherTags

folders = (
    "/home/rock/tmp/POST_RESET/betaplots/Project_Epic-betaplots/",
    "/home/rock/tmp/POST_RESET/lightblue/Project_Epic-lightblue/",
    "/home/rock/tmp/POST_RESET/magenta/Project_Epic-magenta/",
    "/home/rock/tmp/POST_RESET/orange/Project_Epic-orange/",
    "/home/rock/tmp/POST_RESET/purgatory/Project_Epic-purgatory/",
    "/home/rock/tmp/POST_RESET/region_1/Project_Epic-region_1/",
    "/home/rock/tmp/POST_RESET/r1bonus/Project_Epic-r1bonus/",
    "/home/rock/tmp/POST_RESET/r1plots/Project_Epic-r1plots/",
    "/home/rock/tmp/POST_RESET/tutorial/Project_Epic-tutorial/",
    "/home/rock/tmp/POST_RESET/white/Project_Epic-white/",
    "/home/rock/tmp/POST_RESET/yellow/Project_Epic-yellow/",
)
tagsToDelete = [
    "Quest13Done",
    "Q15",
]
tagsToKeep = [
    "keepMe",
    "keepMe2",
]

for worldDir in folders:
    print "*** Current tags:"
    listUniqueTags(worldDir)

    deleteTheseTags(worldDir,tagsToDelete)

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

