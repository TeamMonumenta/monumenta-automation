#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from lib.base_test import BaseTest

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../utility_code"))
loadedWorldClass = False
try:
    from lib_py3.world import World
    loadedWorldClass = True
except Exception:
    print("Skipping: Scoreboard: Prune")
    print("Could not import world, missing required files")

if loadedWorldClass:
    class ScoreboardTest(BaseTest):
        def __init__(self, test_name, interact_on_fail=True):
            super().__init__(test_name, interact_on_fail)

        def test(self):
            """
            Run the test, raising an exception on error
            """
            self.world = World(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../test_files/Project_Epic-valley"))
            self.living_uuids = self.world.entity_uuids()
            self.scoreboard = self.world.scoreboard

            # Player names cannot exceed 16 characters; UUID's are
            # always 36 characters (4 hyphens and 32 hexadecimal digits).

            self.old_score_count = len(self.scoreboard.all_scores)
            self.can_prune = 0
            self.keepable_entity_scores = 0
            for score in self.scoreboard.all_scores:
                owner = score.at_path("Name").value
                if len(owner) == 36:
                    if owner not in self.living_uuids:
                        self.can_prune += 1
                    else:
                        self.keepable_entity_scores += 1

            if self.can_prune == 0:
                raise ValueError("Test invalid: No scores to prune.")

            if self.keepable_entity_scores == 0:
                raise ValueError("Test invalid: No entity scores would be kept.")

            self.scoreboard.prune_missing_entities(self.living_uuids)

            self.new_score_count = len(self.scoreboard.all_scores)

            self.not_pruned = 0
            for score in self.scoreboard.all_scores:
                owner = score.at_path("Name").value
                if (
                    len(owner) == 36 and
                    owner not in self.living_uuids
                ):
                    self.not_pruned += 1

            if self.not_pruned > 0:
                raise ValueError("{} scores not pruned.".format(self.not_pruned))

            if self.new_score_count + self.can_prune > self.old_score_count:
                raise ValueError("Not enough scores were pruned.")

            if self.new_score_count + self.can_prune < self.old_score_count:
                raise ValueError("Too many scores were pruned.")

        def debug(self):
            """
            Provide extra debug info on failure
            """
            pass

    reset_test = ScoreboardTest("Scoreboard: Prune entities")
    reset_test.run()

