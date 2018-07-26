#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# This file is needed for this folder to be considered a library
# This folder is for per-shard terrain reset configs.
# Hopefully it will make it easier to move shards between host servers.

import region_1, r1plots, betaplots, white, orange, magenta, lightblue, yellow, nightmare, r1bonus, roguelike

allConfigDict = {
    "region_1": region_1.config,
    "r1plots": r1plots.config,
    "betaplots": betaplots.config,
    "white": white.config,
    "orange": orange.config,
    "magenta": magenta.config,
    "lightblue": lightblue.config,
    "yellow": yellow.config,
    "nightmare": nightmare.config,
    "r1bonus": r1bonus.config,
    "roguelike": roguelike.config,

    # These are valid shards but no terrain reset action exists for them
    "bungee": None,
    "build": None,
    "tutorial": None,
    "purgatory": None,
}

