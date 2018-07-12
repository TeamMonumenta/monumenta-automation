#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''view scores [-d] Conditions [Order]

  -d shows duplicate scores only (ie, same apartment)

  Conditions can be mixed and matched, so long as none of them are used twice in
one command (ie, you can't show multiple score ranges at once). They must never
contain spaces. Conditions can be in one of the following formats:
{"Name":"Fred"}: Show Fred's scores (incompatible with @ selectors)
{"Objective":"Guild"}: Shows all Guild scores (including where 0!)
{"Objective":["Guild","Apartment"]}: Shows all guild and apartment scores
{"Objective":"Guild","Score":{"min":1}}: Show all Guild scores that are at least 1
{"Objective":"Guild","Score":10}: Show all Guild scores that are exactly 10
{"Objective":"Quest01","Locked":False}: Show only unlocked scores; this is legacy
{}: Shows everything. You almost certainly want to avoid this one.

  Order specifies the order to display the fields. It determines sort order, and
is case sensitive. Can leave out any of the following, but if missing they will
be added in this order:
Objective Name Score Locked

Examples:

  Show duplicate apartment scores:
view scores -d {"Objective":"Apartment","Score":{"min":1}} Objective Score Name
'''

import sys
import ast
from lib_monumenta.scoreboard import scoreboard

sys.argv.pop(0)

if len(sys.argv) == 0:
    print __doc__
    exit()

duplicatesOnly = False
if sys.argv[0] == '-d':
    duplicatesOnly = True
    sys.argv.pop(0)

if len(sys.argv) == 0:
    print __doc__
    exit()

Conditions = ast.literal_eval(sys.argv[0])
sys.argv.pop(0)

components = ("Objective","Name","Score","Locked")

# Order will contain all fields in the end
Order = []
if len(sys.argv) > 0:
    Order = list(sys.argv[:4])

for i in range(len(Order)-1,-1,-1):
    if Order[i] not in components:
        Order.pop(i)

for i in components:
    if i not in Order:
        Order.append(i)
# Order is finalized

scores = scoreboard('/home/rock/project_epic/region_1/Project_Epic-region_1/')
unsorted = scores.searchScores(Conditions=Conditions)

scoreMap = {}
maxCharCounts = []
alignment = ""
for i in Order:
    maxCharCounts.append(len(i))
    if i in ("Score","Locked"):
        alignment += ">"
    else:
        alignment += "<"

if duplicatesOnly:
    dupes = {}
    for score in unsorted:
        key = (
            score["Objective"].value,
            score["Score"].value
        )
        if key not in dupes:
            dupes[key] = 1
        else:
            dupes[key] += 1

    onlyDupes = []

    for score in unsorted:
        key = (
            score["Objective"].value,
            score["Score"].value
        )
        if dupes[key] > 1:
            onlyDupes.append(score)

    unsorted = onlyDupes

for score in unsorted:
    pointer = scoreMap
    for i in range(2):
        key = Order[i]
        val = score[key].value
        maxCharCounts[i] = max(maxCharCounts[i],len(str(val)))
        if val not in pointer:
            pointer[val] = {}
        pointer = pointer[val]
    key = score[Order[2]].value
    maxCharCounts[2] = max(maxCharCounts[2],len(str(key)))
    val = score[Order[3]].value
    maxCharCounts[3] = max(maxCharCounts[3],len(str(val)))
    pointer[key] = val

# Header
result = ""
for i in range(4):
    strFormat = '{:^' + str( maxCharCounts[i] ) + '},'
    result += strFormat.format(Order[i])

result += '\n'

# Table contents
score = ['','','','']
for keyA in sorted(scoreMap.keys()):
    strFormat = '{:' + alignment[0] + str( maxCharCounts[0] ) + '},'
    score[0] = strFormat.format(keyA)
    mapA = scoreMap[keyA]
    for keyB in sorted(mapA.keys()):
        strFormat = '{:' + alignment[1] + str( maxCharCounts[1] ) + '},'
        score[1] = strFormat.format(keyB)
        mapB = mapA[keyB]
        for keyC in sorted(mapB.keys()):
            strFormat = '{:' + alignment[2] + str( maxCharCounts[2] ) + '},'
            score[2] = strFormat.format(keyC)
            keyD = mapB[keyC]

            strFormat = '{:' + alignment[3] + str( maxCharCounts[3] ) + '},'
            score[3] = strFormat.format(keyD)

            result += ''.join(score) + '\n'

print result

