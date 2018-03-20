#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ????????-????-M???-N???-????????????
# M = 0x4
# N = 0b10??

import random

class mcUUID(object):
    def __init__(self):
        maxVal = 2**128-1

        self.uuid = random.randint(0,maxVal)

        self.uuid &= 0xffffffffffff4fffbfffffffffffffff
        self.uuid |= 0x00000000000040008000000000000000

        self.uuid

    def __str__(self):
        unformattedStr=str(self.uuid)
        return '{0:8x}-{1:4x}-{2:4x}-{3:4x}-{4:12x}'.format(
            unformattedStr[0:8],
            unformattedStr[8:12],
            unformattedStr[12:16],
            unformattedStr[16:20],
            unformattedStr[20:32]
        )

    def asTuple(self):
        uuidMost  = ( self.uuid >> 64 ) & 0xffffffffffffffff
        uuidLeast = self.uuid & 0xffffffffffffffff
        return ( uuidMost, uuidLeast )

