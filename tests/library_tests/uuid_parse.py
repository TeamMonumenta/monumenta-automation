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

class UUIDParseTest(BaseTest):
    def __init__(self, test_name, interact_on_fail=True):
        super().__init__(test_name, interact_on_fail)

    def test(self):
        """
        Run the test, raising an exception on error
        """
        # Generate a bunch of UUIDs and make sure encoding / decoding matches
        for test in range(0, 1000):
            self.orig_uuid = uuid.uuid4()
            self.result_uuid = uuid_to_mc_uuid_tag_int_array(self.orig_uuid)
            fake_entity = nbt.TagCompound({"UUID": self.result_uuid})
            self.parsed_uuid = get_entity_uuid(fake_entity)
            self.reparsed_tagint = uuid_to_mc_uuid_tag_int_array(self.parsed_uuid)
            fake_entity = nbt.TagCompound({"UUID": self.reparsed_tagint})
            self.reparsed_uuid = get_entity_uuid(fake_entity)

            if (self.orig_uuid != self.parsed_uuid):
                raise ValueError("Original and re-parsed UUIDs don't match")
            if (self.parsed_uuid != self.reparsed_uuid):
                raise ValueError("Parsed and re-parsed UUIDs don't match")

    def debug(self):
        """
        Provide extra debug info on failure
        """
        print("orig:    {0:#0{1}x} {2}".format(int(self.orig_uuid), 32, self.orig_uuid))
        print("parse:   {0:#0{1}x} {2}".format(int(self.parsed_uuid), 32, self.parsed_uuid))
        print("reparse: {0:#0{1}x} {2}".format(int(self.reparsed_uuid), 32, self.reparsed_uuid))
        self.result_uuid.tree()
        self.reparsed_tagint.tree()

test = UUIDParseTest("Libraries: Testing UUID parsing/encoding")
test.run()

