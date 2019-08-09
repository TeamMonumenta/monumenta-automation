#!/usr/bin/env python3

from lib_py3.scoreboard import Scoreboard
from lib_py3.timing import Timings

mainTiming = Timings(enabled=True)
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

maxSkillPoints = 9
maxSkillLevel = 2

classSkills = [
    [ # Mage
        {"Shorthand":"AS", "Objective":"ArcaneStrike","Name":"Arcane Strike"},
        {"Shorthand":"FN", "Objective":"FrostNova",   "Name":"Frost Nova"},
        {"Shorthand":"PS", "Objective":"Prismatic",   "Name":"Prismatic Shield"},
        {"Shorthand":"MS", "Objective":"Magma",       "Name":"Magma Shield",},
        {"Shorthand":"ML", "Objective":"ManaLance",   "Name":"Mana Lance"},
        {"Shorthand":"EA", "Objective":"Elemental",   "Name":"Elemental Arrows"},
        {"Shorthand":"SS", "Objective":"SpellShock",  "Name":"SpellShock",},
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
        {"Shorthand":"DT", "Objective":"DaggerThrow",     "Name":"Dagger Throw"},
        {"Shorthand":"BmB","Objective":"ByMyBlade",       "Name":"By My Blade"},
        {"Shorthand":"VC", "Objective":"ViciousCombos",   "Name":"Vicious Combos"},
        {"Shorthand":"AS", "Objective":"AdvancingShadows","Name":"Advancing Shadows"},
        {"Shorthand":"Smk","Objective":"SmokeScreen",     "Name":"Smokescreen"},
        {"Shorthand":"Dg", "Objective":"Dodging",         "Name":"Dodging"},
        {"Shorthand":"ED", "Objective":"EscapeDeath",     "Name":"Escape Death"},
    ],
    [ # Alchemist
        {"Shorthand":"GA", "Objective":"GruesomeAlchemy", "Name":"Gruesome Alchemy"},
        {"Shorthand":"BA", "Objective":"BrutalAlchemy",   "Name":"Brutal Alchemy"},
        {"Shorthand":"IT", "Objective":"IronTincture",    "Name":"Iron Tincture"},
        {"Shorthand":"BP", "Objective":"BasiliskPoison",  "Name":"Basilisk Poison"},
        {"Shorthand":"PI", "Objective":"PowerInjection",  "Name":"Power Injection"},
        {"Shorthand":"UA", "Objective":"BombArrow",       "Name":"Unstable Arrows"},
        {"Shorthand":"EE", "Objective":"EnfeeblingElixir","Name":"Enfeebling Elixer"},
    ],
    [ # Scout
        {"Shorthand":"Agl","Objective":"Agility",     "Name":"Agility"},
        {"Shorthand":"Swf","Objective":"Swiftness",   "Name":"Swiftness"},
        {"Shorthand":"SC", "Objective":"SwiftCuts",   "Name":"Swift Cuts"},
        {"Shorthand":"BM", "Objective":"BowMastery",  "Name":"Bow Mastery"},
        {"Shorthand":"EE", "Objective":"Tinkering",   "Name":"Eagle Eye"},
        {"Shorthand":"Vly","Objective":"Volley",      "Name":"Volley"},
        {"Shorthand":"ShS","Objective":"Sharpshooter","Name":"Sharpshooter"},
    ],
    [ # Warlock
        {"Shorthand":"AH", "Objective":"AmplifyingHex",  "Name":"Amplifying Hex"},
        {"Shorthand":"BA", "Objective":"BlasphemousAura","Name":"Blasphemous Aura"},
        {"Shorthand":"CW", "Objective":"CursedWound",    "Name":"Cursed Wound"},
        {"Shorthand":"GC", "Objective":"GraspingClaws",  "Name":"Grasping Claws"},
        {"Shorthand":"SR", "Objective":"SoulRend",       "Name":"Soul Rend"},
        {"Shorthand":"VM", "Objective":"Harvester",      "Name":"Harvester of the Damned"},
        {"Shorthand":"CF", "Objective":"ConsumingFlames","Name":"Consuming Flames"},
    ],
]

Objectives = ["Class","Skill","TotalLevel"]
for skills in classSkills:
    for skill in skills:
        Objectives.append(skill["Objective"])

worldScores = Scoreboard("/home/epic/project_epic/region_1/Project_Epic-region_1")

nextStep("Building caches")

GlobalCache = worldScores.get_cache(Objective=Objectives)
TotalLevelCache = worldScores.get_cache(Objective="TotalLevel",Cache=GlobalCache)
SkillCache = worldScores.get_cache(Objective="Skill",Cache=GlobalCache)

for skills in classSkills:
    for skill in skills:
        skill["Cache"] = worldScores.get_cache(Objective=skill["Objective"],Score={"min":1,"max":maxSkillLevel},Cache=GlobalCache)

nextStep("Caches complete")

searchResults = worldScores.search_scores(Objective="Class",Score={"min":1,"max":len(classList)},Cache=GlobalCache)

playersByClass = {}
# 0th item is total regardless of skill points
totalWithClass = [0]
for skillPoints in range(1,maxSkillPoints+1):
    totalWithClass.append(0)
    for classNum in range(1,len(classList)+1):
        playersByClass[(classNum,skillPoints)] = []

for aScoreEntry in searchResults:
    player = aScoreEntry.at_path("Name").value
    playerClass = aScoreEntry.at_path("Score").value

    playerTotalLevel = worldScores.get_score(Name=player,Objective="TotalLevel",Fallback=0,Cache=TotalLevelCache)
    playerSkillPointsLeft = worldScores.get_score(Name=player,Objective="Skill",Fallback=0,Cache=SkillCache)
    playerSkillCount = playerTotalLevel - playerSkillPointsLeft
    try:
        playersByClass[(playerClass,playerSkillCount)].append(player)
        totalWithClass[playerSkillCount] += 1
        totalWithClass[0] += 1
    except:
        pass

print("Percentage of players with X skill points spent:")
for skillPoints in range(1,maxSkillPoints+1):
    percent = 100.0 * totalWithClass[skillPoints] / totalWithClass[0]
    print("{0:>2} points, {1:6.2f}%".format(skillPoints,percent))

print("Class by skill points")
line = "         ,"
for skillPoints in range(1,maxSkillPoints+1):
    line += "{0:>7},".format(skillPoints)
print(line)
for classNum in range(len(classList)):
    className = classList[classNum]
    line = "{0:<9},".format(className)
    for skillPoints in range(1,maxSkillPoints+1):
        totalMembers = len(playersByClass[(classNum+1,skillPoints)])
        percentUsage = 100.0 * totalMembers / totalWithClass[skillPoints]
        line += "{0:6.2f}%,".format(percentUsage)
    print(line)

for skillPoints in range(1,maxSkillPoints+1):
    print("=--="*20)
    print("Players with {} skill points selected:".format(skillPoints))
    for classNum in range(len(classList)):
        className = classList[classNum]

        print("="*80)
        print(className)

        skillList = classSkills[classNum]
        
        classMembers = playersByClass[(classNum+1,skillPoints)]
        totalMembers = len(classMembers)

        percentUsage = 100.0 * totalMembers / totalWithClass[skillPoints]

        print("-"*80)
        print("{} Members".format(totalMembers))
        print("{0:6.2f}% of players play this class".format(percentUsage))

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
                skillCache = skill["Cache"]

                level = worldScores.get_score(Name=player,Objective=skillObjective,Fallback=0,Cache=skillCache)
                if level == 0:
                    continue
                if level > maxSkillLevel:
                    continue
                playersUsingSkill[(skillId,level)] += 1

                for specSkillId in range(len(skillList)):
                    specSkill = skillList[specSkillId]
                    specSkillObjective = specSkill["Objective"]
                    specSkillCache = specSkill["Cache"]

                    specLevel = worldScores.get_score(Name=player,Objective=specSkillObjective,Fallback=0,Cache=specSkillCache)
                    if specLevel == 0:
                        continue
                    if specLevel > maxSkillLevel:
                        continue
                    specSheet[(skillId,level)][(specSkillId,specLevel)] += 1

        print("-"*80)
        for skillId in range(len(skillList)):
            skill = skillList[skillId]
            skillName = skill["Name"]

            for level in range(1,maxSkillLevel+1):
                percentThisSkill = 100.0 * playersUsingSkill[(skillId,level)] / totalMembers
                print("{0:6.2f}% of {1} players use {2} {3}".format(percentThisSkill,className,skillName,level))

        print("-"*80)
        print("For players using skill A, this percent use skill B:")
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

        print(header)
        for thisLine in toPrint:
            print(thisLine)
        print("-"*80)

nextStep("Done")

