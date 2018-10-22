#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))

from quarry.types.block import LookupBlockMap
block_map = LookupBlockMap.from_jar(jar_path)


