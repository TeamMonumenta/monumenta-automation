#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ????????-????-M???-N???-????????????
# M = 0x4
# N = 0b10??

import random

class mcUUID(object):
    def __init__(self,value=None):
        type_value = type(value)
        if type_value is int:
            self.uuid = value
        elif (
            (
                type_value is tuple or
                type_value is list
            ) and
            len(value) == 2
        ):
            self.uuid = value[0] << 64 | value[1]
        elif type_value is dict:
            self.uuid = value["UUIDMost"] << 64 | value["UUIDLeast"]
        elif type_value is type(self):
            self.uuid = value.uuid
        else:
            maxVal = 2**128-1
            self.uuid = random.randint(0,maxVal)

        self.uuid &= 0xffffffffffff4fffbfffffffffffffff
        self.uuid |= 0x00000000000040008000000000000000

    def __eq__(self,other):
        return self.uuid == other.uuid

    def __ne__(self,other):
        return self.uuid != other.uuid

    def __lt__(self,other):
        return self.uuid < other.uuid

    def __le__(self,other):
        return self.uuid <= other.uuid

    def __gt__(self,other):
        return self.uuid > other.uuid

    def __ge__(self,other):
        return self.uuid >= other.uuid

    def __cmp__(self,other):
        return self.uuid - other.uuid

    def __hash__(self):
        return hash(self.uuid)

    def __repr__(self):
        return "mcUUID({:#32x})".format(self.uuid)

    def __str__(self):
        unformattedStr = '{:32x}'.format(self.uuid)
        return '{}-{}-{}-{}-{}'.format(
            unformattedStr[0:8],
            unformattedStr[8:12],
            unformattedStr[12:16],
            unformattedStr[16:20],
            unformattedStr[20:32]
        )

    def __unicode__(self):
        unformattedStr = u'{:32x}'.format(self.uuid)
        return u'{}-{}-{}-{}-{}'.format(
            unformattedStr[0:8],
            unformattedStr[8:12],
            unformattedStr[12:16],
            unformattedStr[16:20],
            unformattedStr[20:32]
        )

    def asTuple(self):
        UUIDMost  = ( self.uuid >> 64 ) & 0xffffffffffffffff
        UUIDLeast = self.uuid & 0xffffffffffffffff
        return ( UUIDMost, UUIDLeast )

