#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# This file is needed for this folder to be considered a library
# This folder is for per-shard build server updates

import dungeon, mobs, region_1, region_2

allConfigDict = {
    "region_1": region_1.config,
    "region_2": region_2.config,
    "dungeon": dungeon.config,
    "mobs": mobs.config,

    # These are valid shards but no terrain reset action exists for them
    "bungee": None,
    "purgatory": None,
}

