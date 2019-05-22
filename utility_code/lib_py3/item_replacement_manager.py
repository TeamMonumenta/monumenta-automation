#!/usr/bin/env python3

import os
import sys

import traceback

from lib_py3.common import eprint
from lib_py3.common import get_item_name_from_nbt
from lib_py3.item_replacement_rules import global_rules
from lib_py3.item_replacement_substitutions import substitution_rules

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

class ItemReplacementManager(object):
    """
    A tool to replace items while preserving certain data.
    """
    def __init__(self,item_map):
        # Master copies
        self.item_map = item_map

        # Item substitutions
        self.substitution_rules = substitution_rules

        # Item pre/post-processing
        self.global_rules = global_rules

    # Returns True if the item was updated, False otherwise
    def replace_item(self, item, log_dict=None, debug_path=""):
        """
        Replace an item per provided rules and master copy
        """
        # Abort replacement if the item has no ID (empty/invalid item) or no name (no valid replacement)
        if not ( item.has_path('id') and item.has_path('tag.display.Name') ):
            return False

        # Substitute name/id values in case an item changed ID.
        for rule in self.substitution_rules:
            rule.process(item, self.item_map)

        # Get the correct replacement info; abort if none exists
        item_id = item.at_path('id').value
        item_name = get_item_name_from_nbt(item.at_path('tag'))

        new_item_tag = self.item_map.get(item_id,{}).get(item_name,None)
        if not new_item_tag:
            return False

        # Remember the original tag (without damage)
        orig_tag_copy = item.at_path('tag').deep_copy()
        if "Damage" in orig_tag_copy.value:
            orig_tag_copy.value.pop("Damage")

        # Run preprocess rules; if one returns True, abort replacements on this item!
        for rule in self.global_rules:
            try:
                if rule.preprocess(new_item_tag['nbt'], item):
                    return False
            except:
                eprint("Error preprocessing '" + rule.name + "':")
                eprint("Item being preprocessed: " + item.to_mojangson(highlight=True))
                eprint(str(traceback.format_exc()))

        # Replace the item tag
        item.at_path('tag').value = new_item_tag['nbt'].deep_copy().value

        # Run postprocess rules
        for rule in self.global_rules:
            try:
                rule.postprocess(item)
            except:
                eprint("Error postprocessing '" + rule.name + "':")
                eprint("Item being postprocessed: " + item.to_mojangson(highlight=True))
                eprint("This may be a CRITICAL ERROR!")
                eprint(str(traceback.format_exc()))

        # Get a copy of the newly updated item to compare with (without damage)
        updated_tag_copy = item.at_path('tag').deep_copy()
        if "Damage" in updated_tag_copy.value:
            updated_tag_copy.value.pop("Damage")

        if not orig_tag_copy.equals_exact(updated_tag_copy):
            # Item changed
            if log_dict is not None:
                log_key = item_name + "  " + item_id
                if log_key not in log_dict:
                    log_dict[log_key] = {}

                    log_dict[log_key]["NAME"] = item_name
                    log_dict[log_key]["ID"] = item_id
                    log_dict[log_key]["TO"] = updated_tag_copy.to_mojangson()
                    log_dict[log_key]["FROM"] = {}

                orig_tag_mojangson = orig_tag_copy.to_mojangson()

                if orig_tag_mojangson not in log_dict[log_key]["FROM"]:
                    log_dict[log_key]["FROM"][orig_tag_mojangson] = []

                log_dict[log_key]["FROM"][orig_tag_mojangson].append(debug_path)
            return True
        else:
            # Nothing actually changed
            return False


