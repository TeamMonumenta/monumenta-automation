#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

args = sys.argv

if len(args) != 3:
    print("Usage: diff_nbt <file1> <file2>")
else:
    file1 = nbt.NBTFile.load(args[1]).root_tag.body.at_path("Data")
    file2 = nbt.NBTFile.load(args[2]).root_tag.body.at_path("Data")

    file1.diff(file2, order_matters=False, show_values=True)
