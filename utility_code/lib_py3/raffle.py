"""
Raffle library - first used for weekly voting raffle
"""

import sys
from collections import OrderedDict
from pprint import pformat
import redis

def normalized(a_list):
    """
    Normalize a list of numbers to add up to 1.0
    """
    total = 1.0 * sum(a_list)
    new_list = []
    for a_val in a_list:
        new_list.append(a_val / total)
    return new_list

def vote_raffle(seed, redis_host, log_path, dry_run=False):
    if log_path is sys.stdout or log_path is sys.stderr:
        logfp = log_path
    else:
        logfp = open(log_path, "w")

    winner_every_n_points = 300
    no_vote_penalty = 3

    # Votes relevant to this raffle. Format: { 'uuid': (raffleEntries, votesThisWeek) }
    votes = {}
    # List of uuids that had at least one vote & raffle entry this week
    uuids_that_voted_this_week = []
    total_votes_this_week = 0
    total_raffle_entries = 0

    r = redis.StrictRedis(host=redis_host, port=6379, charset="utf-8", decode_responses=True)

    cur = None
    while cur is None or cur != 0:
        cur, keys = r.scan(cursor=(0 if cur is None else cur), match="play:playerdata:*:remotedata", count=20000)
        pipe = r.pipeline()
        for key in keys:
            pipe.hgetall(key)
        bulkdata = pipe.execute()

        if len(bulkdata) != len(keys):
            raise Exception(f"len(bulkdata)={len(bulkdata)} != len(keys)={len(keys)}")

        for i in range(len(bulkdata)):
            key = keys[i]
            data = bulkdata[i]

            split = key.split(":")
            uuid = split[2]

            if "votesThisWeek" in data and "raffleEntries" in data:
                if int(data["votesThisWeek"]) > 0 or int(data["raffleEntries"]) > 0:
                    votes[uuid] = (int(data["raffleEntries"]), int(data["votesThisWeek"]))

                    total_votes_this_week += int(data["votesThisWeek"])
                    total_raffle_entries += int(data["raffleEntries"])
                    if int(data["votesThisWeek"]) > 0:
                        uuids_that_voted_this_week.append(uuid)

    uuid2name = r.hgetall("uuid2name")
    name2uuid = r.hgetall("name2uuid")

    def get_name(uuid):
        if uuid in uuid2name:
            return uuid2name[uuid]
        return uuid

    def get_uuid(name):
        if name in name2uuid:
            return name2uuid[name]
        return name

    # Sort this week's votes
    orig_votes = votes
    votes = OrderedDict(sorted(votes.items(), key=lambda kv: kv[1], reverse=True))

    logfp.write(" Raffle Entries | Votes This Week | Name\n")
    logfp.write("-----------------------------------------------------\n")
    for voter in votes:
        logfp.write(" {} | {} | {}\n".format(str(votes[voter][0]).rjust(15), str(votes[voter][1]).rjust(15), get_name(voter)))
    logfp.write("-----------------------------------------------------\n")
    logfp.write(" {} | {} | Total\n\n".format(str(total_raffle_entries).rjust(15), str(total_votes_this_week).rjust(15)))

    if total_raffle_entries == 0:
        if logfp is not sys.stdout and logfp is not sys.stderr:
            logfp.close()
        return

    # Reduce votes down to just the current list of votes
    simple_votes = []
    for voter in votes:
        if voter in uuids_that_voted_this_week:
            simple_votes.append((get_name(voter), votes[voter][0], votes[voter][1]))

    votes = simple_votes
    logfp.write(f'''
Run this code with python 3 (requires python3-numpy) to verify the results of the raffle:
################################################################################

from numpy import random
import hashlib

seed = {seed!r}
winner_every_n_points = {winner_every_n_points}
votes = {pformat(votes)}

# Split up into lists, count number of votes
vote_names = []
vote_scores = []
total_votes = 0
total_weekly_votes = 0
for voter, raffle_entries, weekly_votes in votes:
    vote_names.append(voter)
    vote_scores.append(raffle_entries)
    total_votes += raffle_entries
    total_weekly_votes += weekly_votes

# Require at least one vote to proceed
if total_weekly_votes >= 1:
    num_winners = total_weekly_votes // winner_every_n_points + 1

    # Convert string seed into a number, set the random number generator to start with that
    random.seed(int(hashlib.sha1(seed.encode('utf-8')).hexdigest()[:8], 16))

    # Pick winners
    winners = list(random.choice(vote_names, replace=False, size=num_winners, p=[vote/total_votes for vote in vote_scores]))
    if num_winners == 1:
        print("This week's winner: " + winners[0])
    else:
        print("This week's winners: " + ", ".join(sorted(winners)))

else:
    print("No winners this week")

################################################################################

''')

    # Run exactly the same code in the printed snippet (print -> logfp.write)
    #####################################################################################################
    #
    from numpy import random
    import hashlib

    #### Variables already defined

    # Split up into lists, count number of votes
    vote_names = []
    vote_scores = []
    total_votes = 0
    total_weekly_votes = 0
    for voter, raffle_entries, weekly_votes in votes:
        vote_names.append(voter)
        vote_scores.append(raffle_entries)
        total_votes += raffle_entries
        total_weekly_votes += weekly_votes

    logfp.write(f"Players who did not vote this week lost {no_vote_penalty} raffle entries. Vote every week to keep all your raffle entries!\n\n")

    # Require at least one vote to proceed
    if total_weekly_votes >= 1:
        num_winners = total_weekly_votes // winner_every_n_points + 1

        # Convert string seed into a number, set the random number generator to start with that
        random.seed(int(hashlib.sha1(seed.encode('utf-8')).hexdigest()[:8], 16))

        # Pick winners
        winners = list(random.choice(vote_names, replace=False, size=num_winners, p=[vote/total_votes for vote in vote_scores]))
        if num_winners == 1:
            logfp.write(f"This week's winner: {winners[0]}\n")
        else:
            logfp.write(f"This week's winners: {', '.join(sorted(winners))}\n")

    else:
        winners = []
        logfp.write("No winners this week\n")

    #
    #####################################################################################################

    # Set the winner's raffle scores, set their votes since win to 0
    if not dry_run:
        pipe = r.pipeline()

        for winner in winners:
            winner_uuid = get_uuid(winner)
            pipe.hincrby(f"play:playerdata:{winner_uuid}:remotedata", "raffleWinsTotal", 1)
            pipe.hincrby(f"play:playerdata:{winner_uuid}:remotedata", "raffleWinsUnclaimed", 1)
            pipe.hset(f"play:playerdata:{winner_uuid}:remotedata", "raffleEntries", 0)

        for uuid in orig_votes:
            pipe.hset(f"play:playerdata:{uuid}:remotedata", "votesThisWeek", 0)

            # Decrement votes for anyone who hasn't voted this week, minimum of 0.
            raffle_entries, votes_this_week = orig_votes[uuid]
            if votes_this_week == 0 and raffle_entries > 0:
                pipe.hset(f"play:playerdata:{uuid}:remotedata", "raffleEntries", max(0, raffle_entries - no_vote_penalty))

        pipe.execute()

    if logfp is not sys.stdout and logfp is not sys.stderr:
        logfp.close()
