#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.registry import LookupRegistry

_reports_path = os.path.join(os.getenv('HOME'), '4_SHARED/vanilla_jars/1.15.2/generated/reports')

if os.path.isdir(_reports_path):
    block_map = LookupRegistry.from_json(_reports_path)
else:
    print("Unable to load LookupRegistry from '{}': block operations will fail".format(_reports_path), file=sys.stderr)
    block_map = None
