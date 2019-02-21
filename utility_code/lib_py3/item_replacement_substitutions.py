#!/usr/bin/env python3

import os
import sys

import json
import traceback

from lib_py3.common import always_equal, eprint
from lib_py3.common import get_item_name_from_nbt, parse_name_possibly_json

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt
from quarry.types.text_format import unformat_text

class substitution_rule(object):
    """
    Base pre/post processing rule for item replacements, used to preserve and edit data.
    """
    # Edit this for all new objects:
    name = "Undefined global rule"

    def __init__(self):
        """
        Local data storage
        """
        pass

    def process(self, item, item_map):
        """
        Read the item details.
        Return True to abort replacement and changes.
        Edit item name and ID here, and it will change
        which item NBT is used for replacements.
        """
        pass

substitution_rules = []

class fix_broken_section_symbols(substitution_rule):
    name = "Fix broken section symbols"

    def process(self, item, item_map):
        name = item.at_path('tag.display.Name').value
        new_name = name.replace(ord(0xfffd), ord(0xa7))
        item.at_path('tag.display.Name').value = new_name

substitution_rules.append(fix_broken_section_symbols())

class fix_double_json_names(substitution_rule):
    name = "Fixed json in json names"

    def process(self, item, item_map):
        try:
            item_id = item.at_path('id').value
            name = item.at_path('tag.display.Name').value
            name_json = parse_name_possibly_json(name)
            name_json_json = parse_name_possibly_json(name_json)
            if name_json != name_json_json and name_json_json in item_map[item_id].keys():
                item.at_path('tag.display.Name').value = name_json
        except:
            pass

substitution_rules.append(fix_double_json_names())

class subtitute_items(substitution_rule):
    name = "Substitute the ID and name of items, ignoring other NBT"

    def __init__(self):
        self.replacements = {
            "minecraft:example_item_id": {
                '''{"text":"Example Name"}''': ("minecraft:new_id", '''{"text":"Example New Name"}'''),
            },
            "minecraft:example_banned_item": {
                always_equal: ("minecraft:new_id", '''{"text":"Example New Name"}'''),
            },
        }

    def process(self, item, item_map):
        item_id = item.at_path('id').value
        item_name = item.at_path('tag.display.Name').value

        if any(replaceable_id == item_id for replaceable_id in self.replacements.keys()):
            print(replaceable_id)
            if any(replaceable_name == item_name for replaceable_name in self.replacements[replaceable_id].keys()):
                print(replaceable_name)
                new_id_name_pair = self.replacements[replaceable_id][replaceable_name]

                new_id = new_id_name_pair[0]
                new_name = new_id_name_pair[1]

                item.at_path('id').value = new_id
                item.at_path('tag.display.Name').value = new_name

substitution_rules.append(subtitute_items())

