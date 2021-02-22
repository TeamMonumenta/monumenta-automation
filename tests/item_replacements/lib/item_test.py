#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".."))
from lib.base_test import BaseTest

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../utility_code"))
from lib_py3.common import get_item_name_from_nbt
from lib_py3.item_replacement_manager import ItemReplacementManager
from minecraft.player_dat_format.item import Item

class ItemTest(BaseTest):
    def __init__(self, test_name, template_item, item_under_test, expected_result_item, interact_on_fail=True):
        super().__init__(test_name, interact_on_fail)

        self.template_item = Item(nbt.TagCompound.from_mojangson(template_item))
        self.item_under_test = Item(nbt.TagCompound.from_mojangson(item_under_test))
        self.expected_result_item = Item(nbt.TagCompound.from_mojangson(expected_result_item))

        self.item_map = None
        self.replacement_manager = None

        self.result = None

    def test(self):
        """Run the test, raising an exception on error"""
        # Abort replacement if the item has no ID (empty/invalid item) or no name (no valid replacement)
        if not self.template_item.id:
            raise KeyError("Template item has no id; did you supply just the item tag?")

        if not self.template_item.nbt.has_path('tag.display.Name'):
            raise KeyError("Template item has no name; replacement will not occur.")

        # Get the correct replacement info; abort if none exists
        item_id = self.template_item.id
        item_name = get_item_name_from_nbt(self.template_item.tag)

        self.item_map = {
            item_id: {
                item_name: {
                    'nbt': self.template_item.tag
                }
            }
        }
        self.replacement_manager = ItemReplacementManager(self.item_map)

        self.result = Item(self.item_under_test.nbt.deep_copy())
        self.replacement_manager.replace_item(self.result)

        if self.result.nbt != self.expected_result_item.nbt:
            raise ValueError("Item does not match expected result")

        if not self.result.nbt.equals_exact(self.expected_result_item.nbt):
            raise ValueError("Item matches expected result, but in the wrong order")

    def debug(self):
        """Provide extra debug info on failure"""
        print(self.spacer)
        print("self is item under test, other is expected result:")
        try:
            self.result.nbt.diff(self.expected_result_item.nbt)
        except Exception:
            print("Additionally, a diff could not be generated.")
        except KeyboardInterrupt:
            sys.exit()

