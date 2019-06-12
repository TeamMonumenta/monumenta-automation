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
        self.week_is_plus = 1000

        self.name_instance_last  = "$last"

        self.name_no_instance     = "NickNackGus"
        self.name_new_instance    = "Noxavis"
        self.name_old_instance    = "TheMonarchAwaken"
        self.name_done_instance   = "Noxavis"

        self.objective_access   = "D1Access"
        self.objective_finished = "D1Finished"

        self.batch_rules = [
            {"condition": {"Objective": "D1Access", "Score": {"min": 1}},
                "actions": {"add": [
                    {"Objective": "D1Access", "Score": self.week_is_plus}]}},
            {"condition": {"Objective": "D1Access", "Score": {"min": 2 * self.week_is_plus}},
                "actions": {"set": [
                    {"Objective": "D1Access", "Score": 0},
                    {"Objective": "D1Finished", "Score": 0}]}},
            {"condition": {"Name": "$last", "Objective": "D1Access"},
                "actions": {"set": [
                    {"Objective": "D1Access", "Score": 0}]}},
        ]


        self.scoreboard = Scoreboard(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../test_files/Project_Epic-region_1/data/scoreboard.dat"))
        self.cache = self.scoreboard.get_cache(
            Name=[
                self.name_instance_last,
                self.name_no_instance,
                self.name_new_instance,
                self.name_old_instance,
                self.name_done_instance,
            ],
            Objective=[
                self.objective_access,
                self.objective_finished
            ]
        )


        self.last_week = {}

        self.last_week["instance_last"] = self.scoreboard.get_score(self.name_instance_last, self.objective_access, Cache=self.cache)

        self.last_week["no_instance"] = self.scoreboard.get_score(self.name_no_instance, self.objective_access, Cache=self.cache)
        self.last_week["no_instance_finished"] = self.scoreboard.get_score(self.name_no_instance, self.objective_finished, Cache=self.cache)

        self.last_week["new_instance"] = self.scoreboard.get_score(self.name_new_instance, self.objective_access, Cache=self.cache)
        self.last_week["new_instance_finished"] = self.scoreboard.get_score(self.name_new_instance, self.objective_finished, Cache=self.cache)

        self.last_week["old_instance"] = self.scoreboard.get_score(self.name_old_instance, self.objective_access, Cache=self.cache)
        self.last_week["old_instance_finished"] = self.scoreboard.get_score(self.name_old_instance, self.objective_finished, Cache=self.cache)

        self.last_week["done_instance"] = self.scoreboard.get_score(self.name_done_instance, self.objective_access, Cache=self.cache)
        self.last_week["done_instance_finished"] = self.scoreboard.get_score(self.name_done_instance, self.objective_finished, Cache=self.cache)


        if self.last_week["instance_last"] == 0:
            raise ValueError("Test invalid: No instances used last week.")

        if self.last_week["no_instance"] != 0:
            raise ValueError("Test invalid: Last week's No Instance score is not 0.")

        if self.last_week["no_instance_finished"] != 0:
            raise ValueError("Test invalid: Last week's No Instance Finished score is not 0.")

        if 0 >= self.last_week["new_instance"] or self.last_week["new_instance"] >= self.week_is_plus:
            raise ValueError("Test invalid: Last week's New Instance score isn't in the New Instance range.")

        if self.week_is_plus >= self.last_week["old_instance"] or self.last_week["old_instance"] >= 2 * self.week_is_plus:
            raise ValueError("Test invalid: Last week's Old Instance score isn't in the Old Instance range.")

        if self.last_week["done_instance"] == 0:
            raise ValueError("Test invalid: Last week's Done Instance score is 0 (not accessible).")

        if self.last_week["done_instance_finished"] == 0:
            raise ValueError("Test invalid: Last week's Done Instance Finished score is 0 (not done).")


        self.scoreboard.batch_score_changes(self.batch_rules)


        self.this_week = {}

        self.this_week["instance_last"] = self.scoreboard.get_score(self.name_instance_last, self.objective_access, Cache=self.cache)

        self.this_week["no_instance"] = self.scoreboard.get_score(self.name_no_instance, self.objective_access, Cache=self.cache)
        self.this_week["no_instance_finished"] = self.scoreboard.get_score(self.name_no_instance, self.objective_finished, Cache=self.cache)

        self.this_week["new_instance"] = self.scoreboard.get_score(self.name_new_instance, self.objective_access, Cache=self.cache)
        self.this_week["new_instance_finished"] = self.scoreboard.get_score(self.name_new_instance, self.objective_finished, Cache=self.cache)

        self.this_week["old_instance"] = self.scoreboard.get_score(self.name_old_instance, self.objective_access, Cache=self.cache)
        self.this_week["old_instance_finished"] = self.scoreboard.get_score(self.name_old_instance, self.objective_finished, Cache=self.cache)

        self.this_week["done_instance"] = self.scoreboard.get_score(self.name_done_instance, self.objective_access, Cache=self.cache)
        self.this_week["done_instance_finished"] = self.scoreboard.get_score(self.name_done_instance, self.objective_finished, Cache=self.cache)


        if self.this_week["instance_last"] != 0:
            raise ValueError("Instances used this week not reset.")

        if self.this_week["no_instance"] != 0:
            raise ValueError("This week's No Instance score is not 0.")

        if self.this_week["no_instance_finished"] != 0:
            raise ValueError("This week's No Instance Finished score is not 0.")

        if self.week_is_plus >= self.this_week["new_instance"] or self.this_week["new_instance"] >= 2 * self.week_is_plus:
            raise ValueError("This week's New Instance score isn't in the Old Instance range.")

        if self.this_week["old_instance"] != 0:
            raise ValueError("This week's Old Instance score is not 0.")

        if self.this_week["done_instance"] == 0 and self.this_week["done_instance_finished"] != 0:
            raise ValueError("This week's Done Instance Finished score is not 0 (>= 1 means done) despite the instance expiring.")


        self.scoreboard.batch_score_changes(self.batch_rules)


        self.next_week = {}

        self.next_week["instance_last"] = self.scoreboard.get_score(self.name_instance_last, self.objective_access, Cache=self.cache)

        self.next_week["no_instance"] = self.scoreboard.get_score(self.name_no_instance, self.objective_access, Cache=self.cache)
        self.next_week["no_instance_finished"] = self.scoreboard.get_score(self.name_no_instance, self.objective_finished, Cache=self.cache)

        self.next_week["new_instance"] = self.scoreboard.get_score(self.name_new_instance, self.objective_access, Cache=self.cache)
        self.next_week["new_instance_finished"] = self.scoreboard.get_score(self.name_new_instance, self.objective_finished, Cache=self.cache)

        self.next_week["old_instance"] = self.scoreboard.get_score(self.name_old_instance, self.objective_access, Cache=self.cache)
        self.next_week["old_instance_finished"] = self.scoreboard.get_score(self.name_old_instance, self.objective_finished, Cache=self.cache)

        self.next_week["done_instance"] = self.scoreboard.get_score(self.name_done_instance, self.objective_access, Cache=self.cache)
        self.next_week["done_instance_finished"] = self.scoreboard.get_score(self.name_done_instance, self.objective_finished, Cache=self.cache)


        if self.next_week["instance_last"] != 0:
            raise ValueError("Instances used next week not reset.")

        if self.next_week["no_instance"] != 0:
            raise ValueError("Next week's No Instance score is not 0.")

        if self.next_week["no_instance_finished"] != 0:
            raise ValueError("Next week's No Instance Finished score is not 0.")

        if self.next_week["new_instance"] != 0:
            raise ValueError("Next week's New Instance score is not 0.")

        if self.next_week["old_instance"] != 0:
            raise ValueError("Next week's Old Instance score is not 0.")

        if self.next_week["done_instance"] != 0:
            raise ValueError("Next week's Done Instance score is not 0")

        if self.next_week["done_instance_finished"] != 0:
            raise ValueError("Next week's Done Instance Finished score is not 0 (>= 1 means done) despite the instance expiring.")

    def debug(self):
        """
        Provide extra debug info on failure
        """
        pass

reset_test = ScoreboardTest("Scoreboard: Batch score changes")
reset_test.run()

