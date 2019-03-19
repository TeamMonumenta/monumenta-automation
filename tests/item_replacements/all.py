#!/usr/bin/env python3

import importlib
import os
import sys

this_folder = os.path.dirname(__file__)

sys.path.append(this_folder)

for _package in sorted(os.listdir(this_folder)):
    if not os.path.isdir(_package):
        continue
    if not os.path.isfile(os.path.join(_package,'__init__.py')):
        continue
    importlib.import_module(_package)

