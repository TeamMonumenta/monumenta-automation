import os
import sys

import traceback

from lib_py3.common import eprint
from lib_py3.common import get_item_name_from_nbt
from lib_py3.common import get_masterwork_level_from_nbt
from lib_py3.item_replacement_rules import global_rules
from lib_py3.item_replacement_substitutions import substitution_rules

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

class ItemReplacementManager():
    """
    A tool to replace items while preserving certain data.
    """
    def __init__(self, item_map):
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
        # Abort replacement if the item has no ID (empty/invalid item)
        if not item.id:
            return False

        # Parse the item ID and name for later use.
        item_meta = {
            'id': item.id,
            'name': None,
            'masterwork_level': None,
        }

        # Note that include_masterwork_level=False here - we do
        # substitutions/etc without including the masterwork level
        item_meta['name'] = get_item_name_from_nbt(item.tag, include_masterwork_level=False)
        item_meta['masterwork_level'] = get_masterwork_level_from_nbt(item.tag)

        # Note that even if a name isn't found, it can still be replaced with a named item

        # Substitute name/id values in case an item changed ID.
        orig_id = item_meta['id']
        for rule in self.substitution_rules:
            rule.process(item_meta, item)

        # Abort replacement if the item has no name (no valid replacement)
        if not item_meta['name']:
            return False

        # Get the correct replacement info; abort if none exists
        item_id = item_meta['id']
        item_name = item_meta['name']

        # Transform the item name by the masterwork level. This is done only
        # after substitutions have run, because the substitutions may change
        # the item's name that will be used for replacements
        if item_meta['masterwork_level'] is not None:
            item_name = f"{item_name}_m{item_meta['masterwork_level']}"

        new_item_tag = self.item_map.get(item_id, {}).get(item_name, None)
        if not new_item_tag:
            if item_meta["masterwork_level"] is not None:
                eprint(f"WARNING: Failed to find masterwork item '{item_name}' in loot tables")
            return False

        # If the id changed, update the base item
        if orig_id != item_meta['id']:
            item.id = item_meta['id']

        # Remember the original tag (without damage)
        if not item.has_tag():
            item.tag = nbt.TagCompound({})

        orig_tag_copy = item.tag.deep_copy()

        # Run preprocess rules; if one returns True, abort replacements on this item!
        for rule in self.global_rules:
            try:
                if rule.preprocess(new_item_tag['nbt'], item):
                    return False
            except Exception:
                eprint("Error preprocessing " + repr(rule.name) + ":")
                eprint("Item being preprocessed: " + item.nbt.to_mojangson(highlight=True))
                eprint(str(traceback.format_exc()))

        # Replace the item tag
        item.tag = new_item_tag['nbt'].deep_copy()

        # Run postprocess rules
        for rule in self.global_rules:
            try:
                rule.postprocess(item)
            except Exception:
                eprint("Error postprocessing " + repr(rule.name) + ":")
                eprint("Item being postprocessed: " + item.nbt.to_mojangson(highlight=True))
                eprint("This may be a CRITICAL ERROR!")
                eprint(str(traceback.format_exc()))

        if item.has_tag() and len(item.tag.value) == 0:
            item.tag = None

        # Check if the tag exactly equals the original tag, including ordering
        if orig_tag_copy.equals_exact(item.tag):
            # Item is exactly the same, no logging or changes needed
            return False

        if orig_tag_copy == item.tag:
            # The items are functionally the same but the ordering has changed
            # This isn't worth logging - but it is a change that requires saving the chunks
            # So still return True to indicate something changed
            return True

        # To reduce the number of log entries, pop the Damage value off both the original and destination logged items
        out_item_no_damage_copy = item.tag.deep_copy()
        if "Damage" in out_item_no_damage_copy.value:
            out_item_no_damage_copy.value.pop("Damage")
        if "Damage" in orig_tag_copy.value:
            orig_tag_copy.value.pop("Damage")

        # Item has changed meaningfully, need to log it
        if log_dict is not None:
            item_log_key = item_name + " | " + item_id

            # This is the block that's common for all items of this type that were nontrivially replaced
            log_block = log_dict.setdefault(item_log_key, {})

            # This is the block for this specific NBT of an item, containing all items that replaced to it
            specific_output = log_block.setdefault(out_item_no_damage_copy.to_mojangson(), {})

            # This is the list of specific locations where this item was located and replaced
            # Note we use sort=[] to sort all keys here because the input key order really doesn't matter, and this combines entries
            locations = specific_output.setdefault(orig_tag_copy.to_mojangson(sort=[]), [])

            locations.append(debug_path)

        return True

    @classmethod
    def merge_log_tuples(cls, log_dicts_to_merge, out_log_dict={}):
        """Merges item replacements log tuples. out_log_dict can be specified to merge multiple different result generators into the same output

        Returns a tuple(num_replacements, {dict})"""
        num_replacements = 0
        for replacements, log_dict in log_dicts_to_merge:
            num_replacements += replacements
            for new_item_log_key in log_dict:
                existing_log_block = out_log_dict.setdefault(new_item_log_key, {})
                new_item_log_block = log_dict[new_item_log_key]

                for new_specific_output_key in new_item_log_block:
                    existing_specific_output = existing_log_block.setdefault(new_specific_output_key, {})
                    new_specific_output = new_item_log_block[new_specific_output_key]

                    for new_location_key in new_specific_output:
                        existing_locations = existing_specific_output.setdefault(new_location_key, [])
                        existing_locations += new_specific_output[new_location_key]

        return num_replacements, out_log_dict
