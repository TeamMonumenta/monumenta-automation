#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
WARNING!
This is very unoptimized. A cache would speed this up significantly.
I'm glad this pointed out that problem for terrain reset, though.
"""

from lib_monumenta import scoreboard
from lib_monumenta.timing import timings

mainTiming = timings(enabled=True)
nextStep = mainTiming.nextStep
nextStep("Init")

classList = [
    "Mage",
    "Warrior",
    "Cleric",
    "Rogue",
    "Alchemist",
    "Scout",
    "Warlock",
]

maxSkillPoints = 6
maxSkillLevel = 2

classSkills = [
    [ # Mage
        {"Shorthand":"AS", "Objective":"ArcaneStrike","Name":"Arcane Strike"},
        {"Shorthand":"FN", "Objective":"FrostNova",   "Name":"Frost Nova"},
        {"Shorthand":"PS", "Objective":"Prismatic",   "Name":"Prismatic Shield"},
        {"Shorthand":"MS", "Objective":"Magma",       "Name":"Magma Shield",},
        {"Shorthand":"ML", "Objective":"ManaLance",   "Name":"Mana Lance"},
        {"Shorthand":"EA", "Objective":"Elemental",   "Name":"Elemental Arrows"},
        {"Shorthand":"Int","Objective":"Intellect",   "Name":"Intellect",},
    ],
    [ # Warrior
        {"Shorthand":"CS", "Objective":"CounterStrike","Name":"Counter Strike"},
        {"Shorthand":"WM", "Objective":"WeaponMastery","Name":"Weapon Mastery"},
        {"Shorthand":"Tgh","Objective":"Toughness",    "Name":"Toughness"},
        {"Shorthand":"Fnz","Objective":"Frenzy",       "Name":"Frenzy"},
        {"Shorthand":"Rip","Objective":"Obliteration", "Name":"Riposte"},
        {"Shorthand":"DL", "Objective":"DefensiveLine","Name":"Defensive Line"},
        {"Shorthand":"BF", "Objective":"BruteForce",   "Name":"Brute Force"},
    ],
    [ # Cleric
        {"Shorthand":"Rjv","Objective":"Rejuvenation", "Name":"Rejuvenation"},
        {"Shorthand":"SA", "Objective":"Sanctified",   "Name":"Sanctified Armor"},
        {"Shorthand":"HB", "Objective":"HeavenlyBoon", "Name":"Heavenly Boon"},
        {"Shorthand":"CB", "Objective":"Celestial",    "Name":"Celestial Blessing"},
        {"Shorthand":"CR", "Objective":"Cleansing",    "Name":"Cleansing Rain"},
        {"Shorthand":"HoL","Objective":"Healing",      "Name":"Hand of Light"},
        {"Shorthand":"DJ", "Objective":"DivineJustice","Name":"Divine Justice"},
    ],
    [ # Rogue
        #{"Shorthand":"As", "Objective":"Assassination","Name":"Assassination"},
        {"Shorthand":"BmB","Objective":"ByMyBlade","Name":"By My Blade"},
        {"Shorthand":"VC", "Objective":"ViciousCombos","Name":"Vicious Combos"},
        {"Shorthand":"AS", "Objective":"AdvancingShadows","Name":"Advancing Shadows"},
        {"Shorthand":"Smk","Objective":"SmokeScreen","Name":"Smokescreen"},
        {"Shorthand":"Dg", "Objective":"Dodging","Name":"Dodging"},
        {"Shorthand":"ED", "Objective":"EscapeDeath","Name":"Escape Death"},
    ],
    [ # Alchemist
        {"Shorthand":"GA", "Objective":"GruesomeAlchemy","Name":"Gruesome Alchemy"},
        {"Shorthand":"PF", "Objective":"PutridFumes","Name":"Putrid Fumes"},
        {"Shorthand":"CM", "Objective":"CausticMixture","Name":"Caustic Mixture"},
        {"Shorthand":"BP", "Objective":"BasiliskPoison","Name":"Basilisk Poison"},
        {"Shorthand":"PI", "Objective":"PowerInjection","Name":"Power Injection"},
        {"Shorthand":"IO", "Objective":"InvigoratingOdor","Name":"Invigorating Odor"},
        #{"Shorthand":"PT", "Objective":"PoisonTrail","Name":"Poison Trail"},
    ],
    [ # Scout
        {"Shorthand":"Agl","Objective":"Agility","Name":"Agility"},
        {"Shorthand":"Swf","Objective":"Swiftness","Name":"Swiftness"},
        #{"Shorthand":"Fb", "Objective":"Exploration","Name":"Flashbang"},
        {"Shorthand":"BM", "Objective":"BowMastery","Name":"Bow Mastery"},
        {"Shorthand":"EE", "Objective":"Tinkering","Name":"Eagle Eye"},
        {"Shorthand":"Vly","Objective":"Volley","Name":"Volley"},
        {"Shorthand":"SB", "Objective":"StandardBearer","Name":"Standard Bearer"},
    ],
    [ # Warlock
        {"Shorthand":"AH", "Objective":"AmplifyingHex","Name":"Amplifying Hex"},
        {"Shorthand":"BA", "Objective":"BlasphemousAura","Name":"Blasphemous Aura"},
        {"Shorthand":"CW", "Objective":"CursedWound","Name":"Cursed Wound"},
        {"Shorthand":"GC", "Objective":"GraspingClaws","Name":"Grasping Claws"},
        {"Shorthand":"SR", "Objective":"SoulRend","Name":"Soul Rend"},
        #{"Shorthand":"VM", "Objective":"VersatileMagic","Name":"Versatile Magic"},
        {"Shorthand":"CF", "Objective":"ConsumingFlames","Name":"Consuming Flames"},
    ],
]

Objectives = ["Class","Skill","TotalLevel"]
for skills in classSkills:
    for skill in skills:
        Objectives.append(skill["Objective"])

worldScores = scoreboard.scoreboard("/home/rock/project_epic/region_1/Project_Epic-region_1")
Cache = worldScores.searchScores(Objective=Objectives)
searchResults = worldScores.searchScores(Objective="Class",Score={"min":1,"max":len(classList)},Cache=Cache)

playersByClass = {}
# 0th item is total regardless of skill points
totalWithClass = [0]
for skillPoints in range(1,maxSkillPoints+1):
    totalWithClass.append(0)
    for classNum in range(1,len(classList)+1):
        playersByClass[(classNum,skillPoints)] = []

for aScoreEntry in searchResults:
    player = aScoreEntry["Name"].value
    playerClass = aScoreEntry["Score"].value

    playerTotalLevel = worldScores.getScore(Name=player,Objective="TotalLevel",Fallback=0,Cache=Cache)
    playerSkillPointsLeft = worldScores.getScore(Name=player,Objective="Skill",Fallback=0,Cache=Cache)
    playerSkillCount = playerTotalLevel - playerSkillPointsLeft
    try:
        playersByClass[(playerClass,playerSkillCount)].append(player)
        totalWithClass[playerSkillCount] += 1
        totalWithClass[0] += 1
    except:
        pass

print "Percentage of players with X skill points spent:"
for skillPoints in range(1,maxSkillPoints+1):
    percent = 100.0 * totalWithClass[skillPoints] / totalWithClass[0]
    print "{0:>2} points, {1:6.2f}%".format(skillPoints,percent)

print "Class by skill points"
line = "         ,"
for skillPoints in range(1,maxSkillPoints+1):
    line += "{0:>7},".format(skillPoints)
print line
for classNum in range(len(classList)):
    className = classList[classNum]
    line = "{0:<9},".format(className)
    for skillPoints in range(1,maxSkillPoints+1):
        totalMembers = len(playersByClass[(classNum+1,skillPoints)])
        percentUsage = 100.0 * totalMembers / totalWithClass[skillPoints]
        line += "{0:6.2f}%,".format(percentUsage)
    print line

for skillPoints in range(1,maxSkillPoints+1):
    print "=--="*20
    print "Players with {} skill points selected:".format(skillPoints)
    for classNum in range(len(classList)):
        className = classList[classNum]

        print "="*80
        print className

        skillList = classSkills[classNum]
        
        classMembers = playersByClass[(classNum+1,skillPoints)]
        totalMembers = len(classMembers)

        percentUsage = 100.0 * totalMembers / totalWithClass[skillPoints]

        print "-"*80
        print "{} Members".format(totalMembers)
        print "{0:6.2f}% of players play this class".format(percentUsage)

        if totalMembers == 0:
            continue

        playersUsingSkill = {}
        specSheet = {}
        for skillId in range(len(skillList)):
            for level in range(1,maxSkillLevel+1):
                playersUsingSkill[(skillId,level)] = 0

                specSheet[(skillId,level)] = {}
                for specSkillId in range(len(skillList)):
                    for specLevel in range(1,maxSkillLevel+1):
                        specSheet[(skillId,level)][(specSkillId,specLevel)] = 0

        for player in classMembers:
            for skillId in range(len(skillList)):
                skill = skillList[skillId]
                skillObjective = skill["Objective"]

                level = worldScores.getScore(Name=player,Objective=skillObjective,Fallback=0,Cache=Cache)
                if level == 0:
                    continue
                if level > maxSkillLevel:
                    continue
                playersUsingSkill[(skillId,level)] += 1

                for specSkillId in range(len(skillList)):
                    specSkill = skillList[specSkillId]
                    specSkillObjective = specSkill["Objective"]

                    specLevel = worldScores.getScore(Name=player,Objective=specSkillObjective,Fallback=0,Cache=Cache)
                    if specLevel == 0:
                        continue
                    if specLevel > maxSkillLevel:
                        continue
                    specSheet[(skillId,level)][(specSkillId,specLevel)] += 1

        print "-"*80
        for skillId in range(len(skillList)):
            skill = skillList[skillId]
            skillName = skill["Name"]

            for level in range(1,maxSkillLevel+1):
                percentThisSkill = 100.0 * playersUsingSkill[(skillId,level)] / totalMembers
                print "{0:6.2f}% of {1} players use {2} {3}".format(percentThisSkill,className,skillName,level)

        print "-"*80
        print "For players using skill A, this percent use skill B:"
        header = "       ,"
        toPrint = []
        for skillId in range(len(skillList)):
            skill = skillList[skillId]
            skillShorthand = skill["Shorthand"]

            for level in range(1,maxSkillLevel+1):
                header += "  {0:>3} {1},".format(skillShorthand,level)
                thisLine = "  {0:>3} {1},".format(skillShorthand,level)
                playersThisSkill = playersUsingSkill[(skillId,level)]

                for specSkillId in range(len(skillList)):
                    for specLevel in range(1,maxSkillLevel+1):
                        if playersThisSkill == 0:
                            percentThisSpec = 0.0
                        else:
                            percentThisSpec = 100.0 * specSheet[(skillId,level)][(specSkillId,specLevel)] / playersThisSkill
                        thisLine += "{0:6.2f}%,".format(percentThisSpec)
                toPrint.append(thisLine)

        print header
        for thisLine in toPrint:
            print thisLine
        print "-"*80

nextStep("Done")

