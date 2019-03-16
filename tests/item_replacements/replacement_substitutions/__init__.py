#!/usr/bin/env python3
"""
Used to Load all scripts in this folder
"""

import importlib
import os
import sys

sys.path.append(os.path.dirname(__file__))

__all__ = []
for _module in os.listdir(os.path.dirname(__file__)):
    if _module == '__init__.py':
        continue
    if not _module.endswith('.py'):
        continue
    importlib.import_module(_module[:-3])

