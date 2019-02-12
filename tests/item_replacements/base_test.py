#!/usr/bin/env python3

# For interactive shell
import readline
import code

import os
import sys
import traceback

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../utility_code"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))

from quarry.types import nbt

from lib_py3.common import get_item_name_from_nbt
from lib_py3.item_replacement_manager import ItemReplacementManager

class ReplacementTest(object):
    def __init__(self, test_name, template_item, item_under_test, expected_result_item, interact_on_fail=True):
        self.test_name = test_name
        self.template_item = nbt.TagCompound.from_mojangson(template_item)
        self.item_under_test = nbt.TagCompound.from_mojangson(item_under_test)
        self.expected_result_item = nbt.TagCompound.from_mojangson(expected_result_item)
        self.interact_on_fail = interact_on_fail

        self.item_map = None
        self.replacement_manager = None

        self.result = None
        self.error = None

    def _test_try_block(self):
        # Abort replacement if the item has no ID (empty/invalid item) or no name (no valid replacement)
        if not self.template_item.has_path('id'):
            raise KeyError("Template item has no id; did you supply just the item tag?")

        if not self.template_item.has_path('tag.display.Name'):
            raise KeyError("Template item has no name; replacement will not occur.")

        # Get the correct replacement info; abort if none exists
        item_id = self.template_item.at_path('id').value
        item_name = get_item_name_from_nbt(self.template_item.at_path('tag'))

        self.item_map = {
            item_id: {
                item_name: {
                    'nbt': self.template_item.at_path('tag')
                }
            }
        }
        self.replacement_manager = ItemReplacementManager(self.item_map)

        self.result = self.item_under_test.deep_copy()
        self.replacement_manager.replace_item(self.result)

        if self.result.to_bytes() == self.item_under_test.to_bytes():
            raise ValueError("Item did not change")

        if self.result != self.expected_result_item:
            raise ValueError("Item does not match expected result")

        if self.result.to_bytes() != self.expected_result_item.to_bytes():
            raise ValueError("Item matches expected result, but in the wrong order")

    def test(self):
        self.test_failed = False
        try:
            self._test_try_block()
        except:
            self.error = traceback.format_exc()

        if self.error is not None:
            print("f: {}".format(self.test_name))
            if self.interact_on_fail:
                print("self is item under test, other is expected result:")
                self.result.diff(self.expected_result_item)
                self.interact()
        else:
            print("p: {}".format(self.test_name))

    def interact(self):
        print(self.error)
        print("╶"+"─"*78+"╴")
        print("self is the test case object.")
        variables = globals().copy()
        variables.update(locals())
        shell = code.InteractiveConsole(variables)
        shell.interact()

