#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
#from quarry.types.block import LookupBlockMap

_pregenerated_blocks_json = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../reports/blocks.json")
_pregenerated_items_json = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../reports/items.json")
_pregenerated_commands_json = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../reports/commands.json")

#if os.path.exists(_pregenerated_blocks_json) and os.path.exists(_pregenerated_items_json):
#    block_map = LookupBlockMap.from_json(_pregenerated_blocks_json, _pregenerated_items_json)
#else:
#    _server_jar_path = os.path.join(os.getenv('HOME'), '4_SHARED/vanilla_jars/1.13.1.jar')
#    block_map = LookupBlockMap.from_jar(_server_jar_path)

block_map = None

