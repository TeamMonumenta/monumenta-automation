#!/usr/bin/env python3
"""
Raffle library - first used for weekly voting raffle
"""

from math import ceil
from numpy import random

def normalized( a_list ):
    """
    Normalize a list of numbers to add up to 1.0
    """
    total = 1.0 * sum( a_list )
    new_list = []
    for a_val in a_list:
        new_list.append( a_val / total )
    return new_list

def vote_raffle( scoreboard, log_path, num_winners ):
    logfp = open( log_path, "w" )

    raffle_cache = scoreboard.get_cache( Objective=[ "VotesWeekly", "VoteRaffle" ] )
    weekly_scores = scoreboard.search_scores( Objective="VotesWeekly", Score={ "min": 1 }, Cache=raffle_cache )

    vote_names = []
    vote_counts = []
    vote_names_by_counts = {}
    total_votes = 0
    for a_score in weekly_scores:
        voter = a_score.at_path( "Name" ).value
        num_votes = a_score.at_path( "Score" ).value

        vote_names.append( voter )
        vote_counts.append( num_votes )

        if num_votes not in vote_names_by_counts.keys():
            vote_names_by_counts[ num_votes ] = []
        vote_names_by_counts[ num_votes ].append( voter )

        total_votes += num_votes

    logfp.write( "Total votes this week: {}\n".format( total_votes ) )

    if total_votes == 0:
        logfp.close
        return

    for num_votes in sorted( vote_names_by_counts.keys(), reverse=True ):
        vote_s = "s"
        if num_votes == 1:
            vote_s = ""
        logfp.write( "{} vote{}:{}\n\n".format(
            num_votes,
            vote_s,
            ", ".join( sorted( vote_names_by_counts[num_votes] ) )
        ) )

    winners = list( random.choice( vote_names, replace=False, size=num_winners, p=normalized( vote_counts ) ) )
    winner_s = "s"
    if len( winners ) == 1:
        winner_s = ""
    for winner in winners:
        scoreboard.add_score( winner, "VoteRaffle", 1, Cache=raffle_cache )
    scoreboard.save()
    logfp.write( "This week's winner{}: ".format( winner_s ) + ", ".join( sorted( winners ) ) )

    logfp.close()

