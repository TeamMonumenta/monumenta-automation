#!/usr/bin/env python3

import importlib
import os
import sys

sys.path.append(os.path.dirname(__file__))

for _package in os.listdir(os.path.dirname(__file__)):
    if not os.path.isdir(_package):
        continue
    if not os.path.isfile(os.path.join(_package,'__init__.py')):
        continue
    importlib.import_module(_package)

