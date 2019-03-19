#!/usr/bin/env python3
"""
Used to Load all scripts in this folder
"""

import importlib
import os
import sys

this_folder = os.path.dirname(__file__)

sys.path.append(this_folder)

__all__ = []
for _module in sorted(os.listdir(this_folder)):
    if _module == '__init__.py':
        continue
    if not _module.endswith('.py'):
        continue
    importlib.import_module(_module[:-3])

for _package in sorted(os.listdir(this_folder)):
    if not os.path.isdir(os.path.join(this_folder, _package)):
        continue
    if not os.path.isfile(os.path.join(this_folder, _package, '__init__.py')):
        continue
    importlib.import_module(_package)

