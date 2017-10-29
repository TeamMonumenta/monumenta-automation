#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tools useful for modifying scoreboard values
"""
from scoreboard_tools_lib import getUniqueValues
from scoreboard_tools_lib import updateIGNs

################################################################################
# Config section

# The world folder to edit the scoreboard values for
#worldFolder = "/home/rock/tmp/Project Epic"
worldFolder = "/home/rock/tmp/project_epic/region_1/Project_Epic/"

# Dictionary of name changes to move scoreboard
# values from one IGN to another (case sensitive)
# Verify name changes with:
# https://api.mojang.com/users/profiles/minecraft/<Current_IGN>
# https://api.mojang.com/user/profiles/<UUID>/names
# Another bad example:
# https://api.mojang.com/users/profiles/minecraft/NickNackGus
# https://api.mojang.com/user/profiles/25c8b7fadd4a4bbb8cf9d534cf66d6f9/names
IGNReplacements = {
    "dinnerbone":"NickNackGus", # Normally, an index is in [], but a string is a list!
    # There, proof dinnerbone played in my singleplayer world...sorta.
}

################################################################################
# Main Code

# Get unique values for a given objective, ie for plots or apartments.
getObjectiveValues(worldFolder,objective="Plot")

# updateIGNs within the scoreboard
#updateIGNs(worldFolder,IGNReplacements)


