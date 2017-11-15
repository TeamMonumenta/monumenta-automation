#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import uuid

x = uuid.uuid4().hex
# First 14 bytes, last 14 bytes
sys.stdout.write("UUIDMost:" + str(int(x[:14], 16)) + "L,UUIDLeast:" + str(int(x[18:], 16)) + "L")


# UUIDMost:230886,UUIDLeast:58454
#qx:let @a=system("uuidgen.py")<enter>c7w^ra<escape>q
