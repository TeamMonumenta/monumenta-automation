#!/usr/bin/env pypy3

"""A tool to export/import chests to/from json for bulk editing"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

dimension = nbt.NBTFile.load(sys.argv[1]).root_tag.tree()

