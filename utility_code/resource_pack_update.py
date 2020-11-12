#!/usr/bin/env python3

import os
import re
from pprint import pprint
from lib_py3.common import parse_name_possibly_json

to_remove=re.compile('[^\r\n -~]')

def upgrade_line(line: str) -> str:
    if line.startswith("nbt.display"):
        split = line.split("=", 1)
        if len(split) != 2:
            raise Exception(f"Split contains {len(split)} elements")
        split[0] = split[0].replace("nbt.display", "nbt.plain.display")
        split[1] = parse_name_possibly_json(split[1], remove_color=True)

        newval = ''
        i = 0
        while i < len(split[1]):
            c = split[1][i]
            nxt = None
            if i < len(split[1]) - 1:
                nxt = split[1][i+1]
            if c == '\\':
                if nxt == 'u':
                    i += 5
            else:
                newval += c

            i += 1

        newval = to_remove.sub('', newval).strip()
        retval = f"{split[0]}={newval}"
    else:
        retval = line

    return retval.rstrip().strip() + "\n"


'''
nbt.display.Name=\\u00a76\\u00a7lBug in Amber
'''

for root, subdirs, files in os.walk('../tmp'):
    for fname in files:
        path = os.path.join(root, fname)
        if fname.endswith(".properties"):
            lines = []
            with open(path, 'r') as fp:
                lines = fp.readlines()
            newlines = []
            for line in lines:
                newlines.append(upgrade_line(line))
            with open(path, 'w') as fp:
                fp.writelines(newlines)

