#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Raffle library - first used for weekly voting raffle
"""

from math import ceil
from numpy import random

def normalized(aList):
    """
    Normalize a list of numbers to add up to 1.0
    """
    total = 1.0 * sum(aList)
    newList = []
    for aVal in aList:
        newList.append(aVal/total)
    return newList

def voteRaffle(scoreboard,logPath):
    logfp = open(logPath,"w")

    raffleCache = scoreboard.searchScores( Objective=[ "VotesWeekly", "VoteRaffle" ] )
    weeklyScores = scoreboard.searchScores( Objective="VotesWeekly", Score={"min":1}, Cache=raffleCache )

    voteNames = []
    voteCounts = []
    voteNamesByCounts = {}
    totalVotes = 0
    for aScore in weeklyScores:
        voter = aScore["Name"].value
        numVotes = aScore["Score"].value

        voteNames.append(voter)
        voteCounts.append(numVotes)

        if numVotes not in voteNamesByCounts.keys():
            voteNamesByCounts[numVotes] = []
        voteNamesByCounts[numVotes].append(voter)

        totalVotes += numVotes

    logfp.write("Total votes this week: {}\n".format(totalVotes))

    if totalVotes == 0:
        logfp.close
        return

    numWinners = 1
    #numWinners = int( ceil( len(voteNames) / 10.0 ) )
    #logfp.write( "Since there are {} voters this week, there will be {} winners.\n\n".format( len(voteNames), numWinners ) )

    for numVotes in sorted( voteNamesByCounts.keys(), reverse=True ):
        logfp.write("{} votes:{}\n\n".format(
            numVotes,
            ", ".join( sorted( voteNamesByCounts[numVotes] ) )
        ))

    winners = list( random.choice( voteNames, replace=False, size=numWinners, p=normalized(voteCounts) ) )
    for winner in winners:
        scoreboard.addScore( winner, "VoteRaffle", 1, Cache=raffleCache )
    logfp.write( "This week's winners: " + ", ".join( sorted( winners ) ) )

    logfp.close()

