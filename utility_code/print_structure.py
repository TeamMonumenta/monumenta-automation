#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from minecraft.chunk_format.structure import Structure

args = sys.argv

if len(args) != 2:
    print("Usage: print_schematic </path/to/schematic>")
else:
    structure = Structure(args[1])

    structure.root_tag.body.tree()
