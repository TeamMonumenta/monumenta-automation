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
        self.restore_conditions = {"Name": "Combustible"}
        self.control_name = "NickNackGus"
        self.control_objective_change = "Class"
        self.control_objective_same = "TotalLevel"


        # Make an "old" copy of the scoreboard (the scores to restore are good here)
        self.old_scoreboard = Scoreboard(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../test_files/Project_Epic-region_1/data/scoreboard.dat"))
        self.cache_damage_old = self.old_scoreboard.get_cache(Conditions=self.restore_conditions)
        self.cache_control_old = self.old_scoreboard.get_cache(Name=self.control_name)

        self.control_score_change_old = self.old_scoreboard.get_score(
            Name=self.control_name,
            Objective=self.control_objective_change,
            Cache=self.cache_control_old
        )

        self.control_score_same_old = self.old_scoreboard.get_score(
            Name=self.control_name,
            Objective=self.control_objective_same,
            Cache=self.cache_control_old
        )

        self.len_old = len(self.old_scoreboard.all_scores)
        self.len_control_old = len(self.cache_control_old)
        self.len_damage_old = len(self.cache_damage_old)

        if self.len_control_old == 0:
            raise ValueError('Test invalid: Simulation "new" control conditions not satisfied.')

        if self.len_damage_old == 0:
            raise ValueError('Test invalid: Simulation "new" damage conditions not satisfied.')

        self.old_scores = {}
        for score in self.cache_damage_old:
            Objective = score.at_path("Objective").value
            self.old_scores[Objective] = score.at_path("Score").value


        # Make a new copy of the scoreboard (the scores to not restore are good here)
        self.new_scoreboard = Scoreboard(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../test_files/Project_Epic-region_1_respec/data/scoreboard.dat"))
        self.cache_damage_new = self.new_scoreboard.get_cache(Conditions=self.restore_conditions)
        self.cache_control_new = self.new_scoreboard.get_cache(Name=self.control_name)

        self.control_score_change_new = self.new_scoreboard.get_score(
            Name=self.control_name,
            Objective=self.control_objective_change,
            Cache=self.cache_control_new
        )

        self.control_score_same_new = self.new_scoreboard.get_score(
            Name=self.control_name,
            Objective=self.control_objective_same,
            Cache=self.cache_control_new
        )

        self.len_new = len(self.new_scoreboard.all_scores)
        self.len_control_new = len(self.cache_control_new)
        self.len_damage_new = len(self.cache_damage_new)

        if self.len_control_new == 0:
            raise ValueError('Test invalid: Simulation "new" control conditions not satisfied.')

        if self.len_damage_new == 0:
            raise ValueError('Test invalid: Simulation "new" damage conditions not satisfied.')


        # Final checks before applying damage
        if self.control_score_change_new == self.control_score_change_old:
            raise ValueError('Test invalid: "Changed" control score is identical in old/new scoreboards.')

        if self.control_score_same_new != self.control_score_same_old:
            raise ValueError('Test invalid: "Same" control score is different in old/new scoreboards.')


        # Damage the new copy of the scoreboard
        self.new_scores = {}
        for score in self.cache_damage_new:
            Objective = score.at_path("Objective").value
            score.at_path("Score").value = 0xdeadbeef
            self.new_scores[Objective] = 0xdeadbeef

        # Ensure damaged scores are different from old scores
        if self.new_scores == self.old_scores:
            raise ValueError('Test invalid: No difference between old and new "damaged" scores.')


        # Apply fix
        self.new_scoreboard.restore_scores(self.old_scoreboard, Conditions=self.restore_conditions)


        # Confirm fix worked
        self.len_fixed = len(self.new_scoreboard.all_scores)
        self.len_control_fixed = len(self.cache_control_new)
        self.len_damage_fixed = len(self.cache_damage_new)

        self.control_score_change_fix = self.new_scoreboard.get_score(
            Name=self.control_name,
            Objective=self.control_objective_change,
            Cache=self.cache_control_new
        )

        self.control_score_same_fix = self.new_scoreboard.get_score(
            Name=self.control_name,
            Objective=self.control_objective_same,
            Cache=self.cache_control_new
        )

        if self.control_score_change_new != self.control_score_change_fix:
            raise ValueError('"Changed" control score does not match "new" control score; may be copied from "old" instead.')

        if self.control_score_same_new != self.control_score_same_fix:
            raise ValueError('"Same" control score not preserved from "new" scoreboard.')

        self.fixed_scores = {}
        for score in self.cache_damage_old:
            Objective = score.at_path("Objective").value
            self.fixed_scores[Objective] = score.at_path("Score").value

        if self.fixed_scores != self.old_scores:
            raise ValueError('"Fixed" scores do not match "old" scores, failed to revert.')

        if self.len_fixed < self.len_new - self.len_damage_new + self.len_damage_old:
            raise ValueError('Fewer "fixed" scores than expected.')

        if self.len_fixed > self.len_new - self.len_damage_new + self.len_damage_old:
            raise ValueError('More "fixed" scores than expected.')

    def debug(self):
        """
        Provide extra debug info on failure
        """
        pass

reset_test = ScoreboardTest("Scoreboard: Restore scores")
reset_test.run()

