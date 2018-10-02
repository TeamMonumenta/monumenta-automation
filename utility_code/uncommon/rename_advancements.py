#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from lib_monumenta.advancements import renameAdvancements

"""
To use this:
- shut down the server
- move advancements as needed
- run this
- continue
"""

renameAdvancements('/home/rock/tmp/POST_RESET/region_1/Project_Epic-region_1/',[
    ['dungeons:root','monumenta:dungeons'],
    ['dungeons:light_blue/find','monumenta:dungeons/light_blue/find'],
    ['dungeons:light_blue/complete','monumenta:dungeons/light_blue/complete'],
    ['dungeons:magenta/find','monumenta:dungeons/magenta/find'],
    ['dungeons:magenta/complete','monumenta:dungeons/magenta/complete'],
    ['dungeons:orange/find','monumenta:dungeons/orange/find'],
    ['dungeons:orange/complete','monumenta:dungeons/orange/complete'],
    ['dungeons:r1bonus/find','monumenta:dungeons/r1bonus/find'],
    ['dungeons:r1bonus/complete','monumenta:dungeons/r1bonus/complete'],
    ['dungeons:white/find','monumenta:dungeons/white/find'],
    ['dungeons:white/complete','monumenta:dungeons/white/complete'],
    ['dungeons:yellow/find','monumenta:dungeons/yellow/find'],
    ['dungeons:yellow/complete','monumenta:dungeons/yellow/complete'],
])

