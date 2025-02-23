#!/usr/bin/env python3
"""Detects when a player's scores have changed"""

import argparse
import csv
import json
import sys
import redis


class ScoreTrainer():
    """A class to identify changes to player scores"""

    def __init__(self, domain, log_fp, objectives, redis_host='redis', redis_port=6379):
        self._domain = domain
        self._objectives = objectives
        self._values = []
        self._show_decreased = False
        self._show_increased = False
        self._show_defined = False
        self._show_undefined = False

        self._r = redis.Redis(host=redis_host, port=redis_port)
        self._csvwriter = csv.writer(log_fp)

        self._current_player_name = None
        self._current_history_description = None


    def values(self, values):
        self._values = set(values)
        return self


    def show_decreased(self, value):
        self._show_decreased = bool(value)
        return self


    def show_increased(self, value):
        self._show_increased = bool(value)
        return self


    def show_defined(self, value):
        self._show_defined = bool(value)
        return self


    def show_undefined(self, value):
        self._show_undefined = bool(value)
        return self


    def get_player_name(self, player_uuid):
        """Gets a player's name, optionally using a previous value"""
        if self._current_player_name is not None:
            return self._current_player_name
        self._current_player_name = self._r.hget('uuid2name', player_uuid).decode('utf-8')
        return self._current_player_name


    def get_history_description(self, player_uuid, history_index):
        """Gets a player's name, optionally using a previous value"""
        if self._current_history_description is not None:
            return self._current_history_description
        self._current_history_description = self._r.lindex(f'{self._domain}:playerdata:{player_uuid}:history', history_index).decode('utf-8')
        return self._current_history_description


    def run(self):
        self._csvwriter.writerow(['Player UUID', 'Player Name', 'Objective', 'Old Value', 'New Value', 'History Index', 'History Description', 'Change Description'])

        for key in self._r.scan_iter(f'{self._domain}:playerdata:*:scores'):
            split = key.decode('utf-8').split(':')
            uuid = split[2]

            self._current_player_name = None # Lazily fetch this
            previous_scores = 'no previous history' # If 'no previous history', treat current as initial values; None might be used for reset values

            # All history elements; 0 is most recent, so reverse this
            for history_index, scores_json_str in reversed(list(enumerate(self._r.lrange(key, 0, -1)))):
                self._current_history_description = None # Lazily fetch this
                scores = json.loads(scores_json_str)

                for objective in self._objectives:
                    value = scores.get(objective, 'undefined')

                    previous_value = 'no previous history'
                    if previous_scores is None:
                        previous_value = 'wiped' # In case wiping scores stores null instead of an empty map
                    elif isinstance(previous_scores, dict):
                        previous_value = previous_scores.get(objective, 'undefined')

                    if value in self._values and previous_value not in self._values:
                        self._csvwriter.writerow([
                            uuid,
                            self.get_player_name(uuid),
                            objective,
                            previous_value,
                            value,
                            history_index,
                            self.get_history_description(uuid, history_index),
                            'Important Value'
                        ])
                    if self._show_defined and previous_value == 'undefined' and isinstance(value, int):
                        self._csvwriter.writerow([
                            uuid,
                            self.get_player_name(uuid),
                            objective,
                            previous_value,
                            value,
                            history_index,
                            self.get_history_description(uuid, history_index),
                            'Value Defined'
                        ])
                    if self._show_undefined and value == 'undefined' and isinstance(previous_value, int):
                        self._csvwriter.writerow([
                            uuid,
                            self.get_player_name(uuid),
                            objective,
                            previous_value,
                            value,
                            history_index,
                            self.get_history_description(uuid, history_index),
                            'Value Undefined'
                        ])
                    if isinstance(value, int) and isinstance(previous_value, int):
                        if self._show_decreased and value < previous_value:
                            self._csvwriter.writerow([
                                uuid,
                                self.get_player_name(uuid),
                                objective,
                                previous_value,
                                value,
                                history_index,
                                self.get_history_description(uuid, history_index),
                                'Value Decreased'
                            ])
                        if self._show_increased and value > previous_value:
                            self._csvwriter.writerow([
                                uuid,
                                self.get_player_name(uuid),
                                objective,
                                previous_value,
                                value,
                                history_index,
                                self.get_history_description(uuid, history_index),
                                'Value Increased'
                            ])

                previous_scores = scores


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('domain', type=str)
    arg_parser.add_argument('--redis_host', type=str, default='redis')
    arg_parser.add_argument('--redis_port', type=int, default=6379)
    arg_parser.add_argument('--objective', type=str, nargs='+',
                            help='Search for these objectives')
    arg_parser.add_argument('--value', type=int, nargs='*',
                            help='Search for objectives that changed to this value')
    arg_parser.add_argument('--decreased', action='store_true',
                            help='Search for objectives that decreased in value')
    arg_parser.add_argument('--increased', action='store_true',
                            help='Search for objectives that increased in value')
    arg_parser.add_argument('--defined', action='store_true',
                            help='Search for objectives were undefined, and are now set; does not include initialization')
    arg_parser.add_argument('--undefined', action='store_true',
                            help='Search for objectives were defined, and are now undefined')
    args = arg_parser.parse_args()

    objectives = args.objective
    important_values = args.value
    show_decreased = args.decreased
    show_increased = args.increased
    show_defined = args.defined
    show_undefined = args.undefined

    trainer = (
        ScoreTrainer(args.domain, sys.stdout, objectives, args.redis_host, args.redis_port)
        .values(important_values)
        .show_decreased(show_decreased)
        .show_increased(show_increased)
        .show_defined(show_defined)
        .show_undefined(show_undefined)
    )
    trainer.run()


if __name__ == '__main__':
    main()
