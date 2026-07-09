#!/usr/bin/env pypy3
"""View market bans"""


import argparse
from datetime import datetime, timedelta, timezone
from lib_py3.redis_scoreboard import RedisScoreboard


def format_score(score):
    """Converts a score to a human readable format"""

    if score < -3:
        return f"permanent (not sure what a score of {score} means in particular, though)"

    if score == -2:
        return "permanent (no ping on Discord)"

    if score == -1:
        return "permanent"

    if score == 0:
        return "not banned"

    if score <= 10000:
        return f"{score} days after they next enter the player market"

    utc_offset = timedelta(hours=-17)
    tz = timezone(utc_offset)
    now_monumenta = datetime.now(tz)
    epoch_monumenta = datetime(1970, 1, 1, tzinfo=tz)
    daily_version_today = (now_monumenta - epoch_monumenta) // timedelta(days=1)

    days_remaining = score - daily_version_today

    if days_remaining <= 0:
        return "not banned (MarketBanned score will reset when entering market)"

    return f"banned for {days_remaining} more days"


def mb_list_sort_key(score_entry):
    """A sort key to use for a given player's market banned status"""

    name = score_entry.value["Name"].value
    score = score_entry.value["Score"].value

    # Return value may change between versions; currently (assuming lowest comes first):
    # (priority, negative of score, player name)

    if score <= -3:
        # Permanent (unknown); show third to last
        return (3, 1, name)

    if score == -2:
        # Permanent (no ping); show second to last
        return (4, 1, name)

    if score == -1:
        # Permanent; show last
        return (5, 1, name)

    if score == 0:
        # Not banned; show first (likely not included unless this is used to check individual bans)
        return (0, 0, name)

    if score <= 10000:
        # Banned on next market entry; show before temp bans
        return (1, -score, name)

    # Temp ban with a fixed date
    return (2, -score, name)


def mb_list(args):
    """Lists active market bans"""

    PAGE_SIZE = 10

    page = args.page if args.page is not None else 1
    if page < 1:
        print("Page number must be at least 1")
        return

    scores = RedisScoreboard("play", redis_host="redis")
    matches = sorted(scores.search_scores(Objective='MarketBanned', Score={"not_in": [0]}), key=mb_list_sort_key)
    max_page = 1 + (len(matches) // PAGE_SIZE)
    min_entry = PAGE_SIZE * (page - 1)
    shown_entries = matches[min_entry:min_entry + PAGE_SIZE]

    print(f"Page {page}/{max_page} ({len(matches)} entries)")
    for score_entry in shown_entries:
        name = score_entry.value["Name"].value
        score = score_entry.value["Score"].value
        formatted_score = format_score(score)
        print(f"{name}: {formatted_score}")


def mb_check(args):
    """Checks the market ban status of specified players"""

    names = args.name

    scores = RedisScoreboard("play", redis_host="redis")
    matches = sorted(scores.search_scores(Name=names, Objective='MarketBanned'), key=mb_list_sort_key)

    for score_entry in matches:
        name = score_entry.value["Name"].value
        score = score_entry.value["Score"].value
        formatted_score = format_score(score)
        print(f"{name}: {formatted_score}")


def main():
    """Argument parsing for viewing market bans"""
    arg_parser = argparse.ArgumentParser(description=__doc__)
    subparsers = arg_parser.add_subparsers(required=True)

    list_parser = subparsers.add_parser('list', help="List active market bans")
    list_parser.add_argument('page', type=int, nargs='?', help="Skip to a specific page number")
    list_parser.set_defaults(func=mb_list)

    check_parser = subparsers.add_parser('check', help="Checks the market ban status of specified players")
    check_parser.add_argument('name', type=str, nargs='+', help="A player name whose market banned status you wish to check")
    check_parser.set_defaults(func=mb_check)

    args = arg_parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
