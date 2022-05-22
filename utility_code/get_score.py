#!/usr/bin/env pypy3
"""get score Name Objective"""

import argparse
from lib_py3.redis_scoreboard import RedisScoreboard

def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('name', type=str)
    arg_parser.add_argument('objective', type=str)
    args = arg_parser.parse_args()

    name = args.name
    objective = args.objective

    scoreboard = RedisScoreboard("play", redis_host="redis")
    score = scoreboard.get_score(name, objective, None)

    if score is None:
        print(f'Score for {name} in {objective}: not set (automation bot cannot see non-player scores)')
    else:
        print(f'Score for {name} in {objective}: {score}')

if __name__ == '__main__':
    main()
