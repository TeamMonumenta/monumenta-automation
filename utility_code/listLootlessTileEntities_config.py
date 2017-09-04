#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
# Config section

# Dst is the destination world, which gets overwritten by the build world.
# Then, data from the main world replaces the relevant parts of the dst world.
# Please note that no special care need be taken with whitespace in filenames.
worldFolder = "/home/rock/tmp/Project Epic"

coordinatesToScan = (
    # ("region name",        (lowerCoordinate),  (upperCoordinate),  ( id, dmg), "block name (comment)"),
    ("main template region", (-30000000, 0, -30000000), (30000000, 255,30000000), (   7, 0 ), "bedrock"),
)

tileEntitiesToCheck = ("chest",)
# If using only one item, ALWAYS use a trailing comma.
# Possible values: "chest" (trapped chest shares ID), "dispenser", "dropper", "shulker_box", "hopper"
# These are actually namespaced; default is "minecraft:*" in this code.

