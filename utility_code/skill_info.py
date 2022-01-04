#!/usr/bin/env python3
"""skill info <exported_skills.json>"""

import json
import sys
from collections import Counter, defaultdict, namedtuple
from datetime import datetime, timezone

from lib_py3.redis_scoreboard import RedisScoreboard
from lib_py3.timing import Timings

sys.argv.pop(0)
if len(sys.argv) == 0:
    print(__doc__)
    exit()
exported_skills_path = sys.argv.pop(0)


PlayerSkill = namedtuple('PlayerSkill', ('name', 'level'))
PlayerSpec = namedtuple('PlayerSpec', ('name', 'total_level', 'skills'))
PlayerClass = namedtuple('PlayerClass', ('name', 'total_level', 'skills', 'spec'))


def shorthand(class_manager, loadout):
    """Display a player's loadout in minimal aligned characters.

    Accepts a skill, spec, or class loadout.
    Not used for the final spreadsheet, but useful for debugging.
    """
    if isinstance(loadout, PlayerSkill):
        skill = class_manager.skills_by_name[loadout.name]
        return f'{skill.shorthand}{loadout.level}'

    elif isinstance(loadout, PlayerSpec):
        return f'{loadout.name}{loadout.total_level} ' + " ".join([shorthand(class_manager, skill) for skill in loadout.skills])

    elif isinstance(loadout, PlayerClass):
        return f'{loadout.name}{loadout.total_level:>02} '\
            + " ".join([shorthand(class_manager, skill) for skill in loadout.skills])\
            + " "\
            + shorthand(class_manager, loadout.spec)

    else:
        return str(loadout)


class Skill():
    """A Monumenta class skill"""
    def __init__(self, skill_data):
        self.objective = skill_data["scoreboardId"]
        self.name = skill_data["displayName"]
        self.shorthand = skill_data.get("shortName", "???")
        if self.shorthand == "???":
            print(f'{self.name} has no shorthand name and will display as ???')
        self.descriptions = skill_data["descriptions"]
        self.trigger = skill_data.get("trigger", None)
        self.cooldown = skill_data["cooldown"]


    def get_player_loadout(self, scoreboard, player_name):
        level = scoreboard.get_score(player_name, self.objective, Fallback=0)
        return PlayerSkill(self.name, level)


class Spec():
    """A Monumenta ability class specialization"""
    def __init__(self, spec_data):
        self.index = spec_data["specId"]
        self.name = spec_data["specName"]
        self.quest_objective = spec_data["specQuestScore"]

        self.skills = {}
        for skill_data in spec_data["specSkills"]:
            skill = Skill(skill_data)
            self.skills[skill.name] = skill


    def get_player_loadout(self, scoreboard, player_name):
        total_level = scoreboard.get_score(player_name, "TotalSpec", Fallback=0)

        skill_loadouts = []
        for skill_name in sorted(self.skills.keys()):
            skill = self.skills[skill_name]
            skill_loadouts.append(skill.get_player_loadout(scoreboard, player_name))

        return PlayerSpec(self.name, total_level, tuple(skill_loadouts))


class Class():
    """A Monumenta ability class"""
    def __init__(self, class_data):
        self.index = class_data["classId"]
        self.name = class_data["className"]

        self.skills = {}
        for skill_data in class_data["skills"]:
            skill = Skill(skill_data)
            self.skills[skill.name] = skill

        self.specs = {}
        self.specs_by_name = {}
        for spec_data in class_data["specs"]:
            spec = Spec(spec_data)
            self.specs[spec.index] = spec
            self.specs_by_name[spec.name] = spec


    def get_player_loadout(self, scoreboard, player_name):
        total_level = scoreboard.get_score(player_name, "TotalLevel", Fallback=0)

        skill_loadouts = []
        for skill_name in sorted(self.skills.keys()):
            skill = self.skills[skill_name]
            skill_loadouts.append(skill.get_player_loadout(scoreboard, player_name))

        spec_id = scoreboard.get_score(player_name, "Specialization", Fallback=0)
        spec_loadout = None
        if spec_id in self.specs:
            spec = self.specs[spec_id]
            spec_loadout = spec.get_player_loadout(scoreboard, player_name)

        return PlayerClass(self.name, total_level, tuple(skill_loadouts), spec_loadout)


class ClassManager():
    def __init__(self, exported_skills):
        self.classes = {}
        self.classes_by_name = {}
        self.specs_by_name = {}
        self.skills_by_name = {}
        self.max_chars = defaultdict(int)
        for class_data in exported_skills["classes"]:
            ability_class = Class(class_data)
            self.classes[ability_class.index] = ability_class
            self.classes_by_name[ability_class.name] = ability_class
            self.max_chars["class_name"] = max(self.max_chars["class_name"], len(ability_class.name))

            for skill_name, skill in ability_class.skills.items():
                self.skills_by_name[skill_name] = skill
                self.max_chars["skill_name"] = max(self.max_chars["skill_name"], len(skill_name))
                self.max_chars["skill_shorthand"] = max(self.max_chars["skill_shorthand"], len(skill.shorthand))

            for spec_name, spec in ability_class.specs_by_name.items():
                self.specs_by_name[spec_name] = spec
                self.max_chars["spec_name"] = max(self.max_chars["spec_name"], len(spec_name))
                for skill_name, skill in spec.skills.items():
                    self.skills_by_name[skill_name] = skill
                    self.max_chars["skill_name"] = max(self.max_chars["skill_name"], len(skill_name))
                    self.max_chars["skill_shorthand"] = max(self.max_chars["skill_shorthand"], len(skill.shorthand))


    def get_player_loadout(self, scoreboard, player_name):
        class_id = scoreboard.get_score(player_name, "Class", Fallback=0)
        class_loadout = None
        if class_id in self.classes:
            ability_class = self.classes[class_id]
            class_loadout = ability_class.get_player_loadout(scoreboard, player_name)

        return class_loadout


def main():
    mainTiming = Timings(enabled=True)
    nextStep = mainTiming.nextStep
    nextStep("Init")

    now = datetime.now(timezone.utc)
    now_timestamp = now.timestamp()
    days_since_epoch = int(now_timestamp/60/60/24)

    with open(exported_skills_path, "r") as fp:
        exported_skills = json.load(fp)
    class_manager = ClassManager(exported_skills)

    for class_id, ability_class in sorted(class_manager.classes.items()):
        print("="*80)
        print(f'{class_id} {ability_class.name}:')
        for skill_name, skill in sorted(ability_class.skills.items()):
            print(f'- {skill.shorthand:{class_manager.max_chars["skill_shorthand"]}} {skill_name}')
        for spec in ability_class.specs.values():
            print('-'*40)
            print(f'- {spec.index:2} {spec.name}:')
            for skill_name, skill in sorted(spec.skills.items()):
                print(f'    - {skill.shorthand:{class_manager.max_chars["skill_shorthand"]}} {skill_name}')
    print("="*80)

    # Play 10.217.0.65
    scoreboard = RedisScoreboard("play", redis_host="10.217.1.171")


    nextStep("Getting list of players who played in the last week")

    players = []
    for score in scoreboard.search_scores(Objective="DailyVersion", Score={"min": days_since_epoch - 7}):
        players.append(score.at_path("Name").value)


    nextStep("Reading player loadouts")

    all_loadouts_histogram = Counter()
    class_loadouts_histograms = defaultdict(Counter)
    spec_loadouts_histograms = defaultdict(Counter)

    for player_name in players:
        loadout = class_manager.get_player_loadout(scoreboard, player_name)
        all_loadouts_histogram[loadout] += 1

        if loadout is None:
            continue
        class_name = loadout.name
        class_loadouts_histograms[class_name][loadout] += 1

        if loadout.spec is None:
            continue
        spec = loadout.spec
        spec_name = spec.name
        spec_loadouts_histograms[spec_name][spec] += 1


    # TEMP
    COLUMNS = 230

    print("all_loadouts_histogram:")
    for key, value in all_loadouts_histogram.most_common(5):
        abridged_key = shorthand(class_manager, key)
        if len(abridged_key) > COLUMNS:
            abridged_key = abridged_key[:COLUMNS-3] + "..."
        print(f'{value:2d}x {abridged_key}')
    if len(all_loadouts_histogram) > 5:
        print(f'...and {len(all_loadouts_histogram)-5} more.')

    print("class_loadouts_histograms:")
    for class_name, class_loadout in class_loadouts_histograms.items():
        print(f'{class_name}:')
        for key, value in class_loadout.most_common(5):
            abridged_key = shorthand(class_manager, key)
            if len(abridged_key) > COLUMNS:
                abridged_key = abridged_key[:COLUMNS-3] + "..."
            print(f'{value:2d}x {abridged_key}')
        if len(class_loadout) > 5:
            print(f'...and {len(class_loadout)-5} more.')

    print("spec_loadouts_histograms:")
    for spec_name, spec_loadout in spec_loadouts_histograms.items():
        print(f'{spec_name}:')
        for key, value in spec_loadout.most_common(5):
            abridged_key = shorthand(class_manager, key)
            if len(abridged_key) > COLUMNS:
                abridged_key = abridged_key[:COLUMNS-3] + "..."
            print(f'{value:2d}x {abridged_key}')
        if len(spec_loadout) > 5:
            print(f'...and {len(spec_loadout)-5} more.')
    # TEMP

    nextStep("Done")

if __name__ == '__main__':
    main()
