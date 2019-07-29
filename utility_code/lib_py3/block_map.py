#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.block import LookupBlockMap

_server_jar_path = os.path.join(os.getenv('HOME'), '4_SHARED/vanilla_jars/1.13.1.jar')
block_map = LookupBlockMap.from_jar(_server_jar_path)

