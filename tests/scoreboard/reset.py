#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from lib.base_test import BaseTest

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../utility_code"))
from lib_py3.scoreboard import Scoreboard

class ScoreboardTest(BaseTest):
    def __init__(self, test_name, interact_on_fail=True):
        super().__init__(test_name, interact_on_fail)

    def test(self):
        """
        Run the test, raising an exception on error
        """
        self.deletion_conditions = {"Name": "NickNackGus"}
        self.scoreboard = Scoreboard(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../test_files/Project_Epic-region_1/data/scoreboard.dat"))

        self.cache_to_delete = self.scoreboard.get_cache(Conditions=self.deletion_conditions)
        self.scores_to_delete = self.scoreboard.search_scores(Conditions=self.deletion_conditions)

        self.len_old_scores = len(self.scoreboard.all_scores)
        self.len_scores_to_delete = len(self.scores_to_delete)
        self.len_expected_scores = self.len_old_scores - self.len_scores_to_delete

        if self.len_scores_to_delete == 0:
            raise ValueError("Test invalid: No scores to delete.")

        self.scoreboard.reset_scores(Conditions=self.deletion_conditions)

        self.len_new_scores = len(self.scoreboard.all_scores)

        if self.len_new_scores < self.len_expected_scores:
            raise ValueError("More scores were deleted than expected.")

        if self.len_new_scores > self.len_expected_scores:
            raise ValueError("Less scores were deleted than expected.")

        if len(self.cache_to_delete) != 0:
            raise ValueError("Not all scores were removed from the cache. Wrong scores may have been deleted.")

        self.scores_not_deleted = self.scoreboard.search_scores(Conditions=self.deletion_conditions)

        if len(self.scores_not_deleted) != 0:
            raise ValueError("Not all scores were deleted from the complete list of scores. Wrong scores may have been deleted.")

    def debug(self):
        """
        Provide extra debug info on failure
        """
        pass

reset_test = ScoreboardTest("Scoreboard: Reset scores")
reset_test.run()

