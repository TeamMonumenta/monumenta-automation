#!/usr/bin/env python3

# For interactive shell
import readline
import code

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

if __name__ == '__main__':
    print("Starting interactive mode")
    print("Try nbt.NBTFile.load(path)")
    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.interact()
