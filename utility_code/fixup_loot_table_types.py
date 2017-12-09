#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

replacements = [
        ("UUIDLeast", "l"),
        ("UUIDMost", "l"),
        ("Amount", "d"),
        ("lvl", "s"),
        ("id", "s"),
        ("Operation", ""),
        ("color", ""),
    ]

if not os.path.isdir("loot_tables"):
    sys.exit("This script must be run from the minecraft 'data' directory containing a loot_tables folder")

for repl in replacements:
    print "Fixing: " + repl[0]
    command = r"find loot_tables -name '*.json' | xargs perl -p -i -e 's|(" + repl[0] + r":)([-\.0-9]*)[lLsSbBfFdD]*|\1\2" + repl[1] + r"|g'"
    os.system(command)
