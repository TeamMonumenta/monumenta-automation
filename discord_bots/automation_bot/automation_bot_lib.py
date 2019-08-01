#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import datetime
import asyncio
#import traceback
import subprocess
import os
import sys

################################################################################
# Utility Functions

def get_list_match(item, lst):
    tmpitem = item.lower()

    match = None
    for x in lst:
        if x.lower().startswith(tmpitem):
            if x.lower() == tmpitem:
                # Exact match - return it
                return x
            elif match is None:
                # Partial match - keep track of it
                match = x
            else:
                # Multiple matches - don't want to return the wrong one!
                return None
    return match

def datestr():
    return datetime.datetime.now().strftime("%Y_%m_%d")

def split_string(text):
    # Maximum number of characters in a single line
    n = 1950

    splits = text.splitlines()
    result = []
    cur = None
    for i in splits:
        while True:
            if cur is None and len(i) <= n:
                cur = i;
                break # Done with i
            elif cur is None and len(i) > n:
                # Annoying case - one uber long line. Have to split into chunks
                result = result + [i[:n]]
                i = i[n:]
                pass # Repeat this iteration
            elif len(cur) + len(i) < n:
                cur = cur + "\n" + i
                break # Done with i
            else:
                result = result + [cur]
                cur = None
                pass # Repeat this iteration

    if cur is not None:
        result = result + [cur]
        cur = None

    return result
