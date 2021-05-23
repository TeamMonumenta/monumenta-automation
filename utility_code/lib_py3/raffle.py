#!/usr/bin/env python3
"""
Raffle library - first used for weekly voting raffle
"""

import os
import json
import yaml
from collections import OrderedDict
from pprint import pformat

def normalized( a_list ):
    """
    Normalize a list of numbers to add up to 1.0
    """
    total = 1.0 * sum( a_list )
    new_list = []
    for a_val in a_list:
        new_list.append( a_val / total )
    return new_list

def vote_raffle(seed, uuid2name_path, votes_dir_path, log_path, dry_run=False):
    logfp = open( log_path, "w" )
    winner_every_n_points = 300
    no_vote_penalty = 3

    # All the raw JSON data gets dumped here. key = 'uuid' val = { vote data }
    raw_data = {}
    # The original file paths containing the data. key = 'uuid' val = '/path/to/uuid.json'
    file_paths = {}
    # Votes relevant to this raffle. Format: { 'uuid': (since_win, this_week) }
    votes = {}
    # List of uuids that had at least one vote & raffle entry this week
    uuids_that_voted_this_week = []
    total_votes_this_week = 0
    total_raffle_entries = 0

    # Get the votes from this week
    for root, dirs, files in os.walk(votes_dir_path):
        for aFile in files:
            if aFile.endswith(".json"):
                uuid = aFile[:-5]
                full_file_path = os.path.join(root, aFile)
                with open(full_file_path, "r") as fp:
                    data = json.load(fp)
                    if "votesThisWeek" in data and "raffleEntries" in data:
                        if data["votesThisWeek"] > 0 or data["raffleEntries"] > 0:
                            raw_data[uuid] = data
                            file_paths[uuid] = full_file_path

                            votes[uuid] = (data["raffleEntries"], data["votesThisWeek"])

                            total_votes_this_week += data["votesThisWeek"]
                            total_raffle_entries += data["raffleEntries"]
                            if data["votesThisWeek"] > 0:
                                uuids_that_voted_this_week.append(uuid)

    with open(uuid2name_path, "r") as fp:
        uuid2name = yaml.load(fp, Loader=yaml.FullLoader)
        name2uuid = {value: key for key, value in uuid2name.items()}

    def get_name(uuid):
        if uuid in uuid2name:
            return uuid2name[uuid]
        return uuid

    def get_uuid(name):
        if name in name2uuid:
            return name2uuid[name]
        return name

    # Sort this week's votes
    votes = OrderedDict(sorted(votes.items(), key=lambda kv: kv[1], reverse=True))

    logfp.write( " Raffle Entries | Votes This Week | Name\n" )
    logfp.write( "-----------------------------------------------------\n" )
    for voter in votes:
        logfp.write( " {} | {} | {}\n".format( str( votes[voter][0] ).rjust( 15 ), str( votes[voter][1] ).rjust( 15 ), get_name(voter) ) )
    logfp.write( "-----------------------------------------------------\n" )
    logfp.write( " {} | {} | Total\n\n".format( str( total_raffle_entries ).rjust( 15 ), str( total_votes_this_week ).rjust( 15 )) )

    # Decrement votes for anyone who hasn't voted this week, minimum of 0.
    someone_lost_raffle_entries = False
    for uuid, voter_data in raw_data.items():
        if voter_data["votesThisWeek"] != 0:
            continue
        if voter_data["raffleEntries"] > 0:
            someone_lost_raffle_entries = True
            voter_data["raffleEntries"] = max(0, voter_data["raffleEntries"] - no_vote_penalty)
    if someone_lost_raffle_entries:
        logfp.write(f"Players who did not vote this week lost {no_vote_penalty} raffle entries. Vote every week to keep all your raffle entries!\n\n")

    if total_raffle_entries == 0:
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

    # Require at least one vote to proceed
    if total_weekly_votes >= 1:
        num_winners = total_weekly_votes // winner_every_n_points + 1

        # Convert string seed into a number, set the random number generator to start with that
        random.seed(int(hashlib.sha1(seed.encode('utf-8')).hexdigest()[:8], 16))

        # Pick winners
        winners = list(random.choice(vote_names, replace=False, size=num_winners, p=[vote/total_votes for vote in vote_scores]))
        if num_winners == 1:
            logfp.write("This week's winner: " + winners[0])
        else:
            logfp.write("This week's winners: " + ", ".join(sorted(winners)))

    else:
        logfp.write("No winners this week")

    #
    #####################################################################################################

    # Set the winner's raffle scores, set their votes since win to 0
    for winner in winners:
        winner_uuid = get_uuid(winner)
        raw_data[winner_uuid]["raffleWinsTotal"] += 1
        raw_data[winner_uuid]["raffleWinsUnclaimed"] += 1
        raw_data[winner_uuid]["raffleEntries"] = 0

    for uuid in raw_data:
        raw_data[uuid]["votesThisWeek"] = 0

    if not dry_run:
        for uuid in raw_data:
            with open(file_paths[uuid], 'w') as fp:
                json.dump(raw_data[uuid], fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

    logfp.close()
