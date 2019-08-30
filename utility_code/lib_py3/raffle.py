#!/usr/bin/env python3
"""
Raffle library - first used for weekly voting raffle
"""

from math import ceil
from collections import OrderedDict
import pprint

def normalized( a_list ):
    """
    Normalize a list of numbers to add up to 1.0
    """
    total = 1.0 * sum( a_list )
    new_list = []
    for a_val in a_list:
        new_list.append( a_val / total )
    return new_list

def vote_raffle( seed, scoreboard, log_path, num_winners ):
    logfp = open( log_path, "w" )

    raffle_cache = scoreboard.get_cache( Objective=[ "VotesWeekly", "VotesSinceWin", "VoteRaffle" ] )
    weekly_scores = scoreboard.search_scores( Objective="VotesWeekly", Score={ "min": 1 }, Cache=raffle_cache )
    since_win_scores = scoreboard.search_scores( Objective="VotesSinceWin", Score={ "min": 1 }, Cache=raffle_cache )

    # Get the votes from this week
    # Format: { "voter": (since_win, this_week) }
    votes = OrderedDict()
    names_that_voted_this_week = []
    total_votes_weekly = 0
    for a_score in weekly_scores:
        voter = a_score.at_path( "Name" ).value
        votes_weekly = a_score.at_path( "Score" ).value

        votes[voter] = (votes_weekly, votes_weekly)
        names_that_voted_this_week.append(voter)

        total_votes_weekly += votes_weekly

    # Get the votes since win
    total_votes_since_win = total_votes_weekly
    for a_score in since_win_scores:
        voter = a_score.at_path( "Name" ).value
        votes_since_win = a_score.at_path( "Score" ).value

        if voter in votes:
            # This player also voted this week - add those
            votes[voter] = (votes[voter][0] + votes_since_win, votes[voter][1])

        else:
            # This player did not vote this week but did since winning
            votes[voter] = (votes_since_win, 0)

        total_votes_since_win += votes_since_win

    # Sort this week's votes
    votes = OrderedDict(sorted(votes.items(), key=lambda kv: kv[1], reverse=True))

    logfp.write( " Votes Since Win | Votes This Week | Name\n" )
    logfp.write( "-----------------------------------------------------\n" )
    for voter in votes:
        logfp.write( " {} | {} | {}\n".format( str( votes[voter][0] ).rjust( 15 ), str( votes[voter][1] ).rjust( 15 ), voter ) )
    logfp.write( "-----------------------------------------------------\n" )
    logfp.write( " {} | {} | Total\n\n".format( str( total_votes_since_win ).rjust( 15 ), str( total_votes_weekly ).rjust( 15 )) )

    if total_votes_since_win == 0:
        logfp.close
        return

    # Reduce votes down to just the current list of votes
    simple_votes = OrderedDict()
    for voter in votes:
        if voter in names_that_voted_this_week:
            simple_votes[voter] = votes[voter][0]
    votes = simple_votes
    logfp.write('''
Run this code with python 3 (requires python3-numpy) to verify the results of the raffle:
################################################################################

from numpy import random
import hashlib
from collections import OrderedDict

seed = \'\'\'{}\'\'\'
num_winners = {}
votes = {}

# Split up into lists, count number of votes
vote_names = []
vote_scores = []
total_votes = 0
for voter in votes:
    vote_names.append(voter)
    vote_scores.append(votes[voter])
    total_votes += votes[voter]

# Convert string seed into a number, set the random number generator to start with that
random.seed(int(hashlib.sha1(seed.encode('utf-8')).hexdigest()[:8], 16))

# Pick winners
winners = list(random.choice(vote_names, replace=False, size=num_winners, p=[vote/total_votes for vote in vote_scores]))
print("This week's winners: " + ", ".join(sorted(winners)))

################################################################################

'''.format(seed, num_winners, pprint.pformat(votes)))

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
    for voter in votes:
        vote_names.append(voter)
        vote_scores.append(votes[voter])
        total_votes += votes[voter]

    # Convert string seed into a number, set the random number generator to start with that
    random.seed(int(hashlib.sha1(seed.encode('utf-8')).hexdigest()[:8], 16))

    # Pick winners
    winners = list(random.choice(vote_names, replace=False, size=num_winners, p=[vote/total_votes for vote in vote_scores]))
    logfp.write("This week's winners: " + ", ".join(sorted(winners)))

    #
    #####################################################################################################

    # Set the winner's raffle scores, set their votes since win to 0
    for winner in winners:
        scoreboard.add_score( winner, "VoteRaffle", 1, Cache=raffle_cache )
        votes[winner] = 0
    for voter in votes:
        scoreboard.set_score( voter, "VotesSinceWin", votes[voter], Cache=raffle_cache )

    scoreboard.save()

    logfp.close()
