#!/usr/bin/env python3

import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from lib.base_test import BaseTest

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../utility_code"))
from lib_py3.common import uuid_to_mc_uuid_tag_int_array, get_entity_uuid

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt
from quarry.types.chunk import PackedArray

class UUIDParseEntityTest(BaseTest):
    def __init__(self, test_name, interact_on_fail=True):
        super().__init__(test_name, interact_on_fail)

    def test(self):
        """
        Run the test, raising an exception on error
        """
        # Make sure parsing actually matches what happens to a real entity
        array = nbt.TagIntArray(PackedArray.from_int_list([-1438811803, 2031437540, -1579701167, 1748458783], 32))
        fake_entity = nbt.TagCompound({"UUID": array})
        parsed_uuid = get_entity_uuid(fake_entity)
        if uuid.UUID("aa3d7965-7915-46e4-a1d7-ac5168375d1f") != parsed_uuid:
            raise ValueError("Parsed UUID value doesn't match actual entity uuid")


    def debug(self):
        """
        Provide extra debug info on failure
        """
        pass

test = UUIDParseEntityTest("Libraries: Testing parsing a UUID gives the correct MC value")
test.run()

