#!/usr/bin/python3

import os

allowedTypes = (
    ".mcfunction",
    ".json",
)

foldersToWalk = [
    "/home/rock/project_epic/region_1/Project_Epic-region_1/advancements/",
]

allRenamed = (
    ("monumenta:acrewtoremember","monumenta:quests/r1/acrewtoremember"),
    ("monumenta:acrownofmajesty","monumenta:quests/r1/acrownofmajesty"),
    ("monumenta:acrownoftopaz","monumenta:quests/r1/acrownoftopaz"),
    ("monumenta:avaultofglass","monumenta:quests/r1/avaultofglass"),
    ("monumenta:bandittroubles","monumenta:quests/r1/bandittroubles"),
    ("monumenta:baneofthebakers","monumenta:quests/r1/baneofthebakers"),
    ("monumenta:buriedblade","monumenta:quests/r1/buriedblade"),
    ("monumenta:castingforhelp","monumenta:quests/r1/castingforhelp"),
    ("monumenta:clearasglass","monumenta:quests/r1/clearasglass"),
    ("monumenta:crownofmadness","monumenta:quests/r1/crownofmadness"),
    ("monumenta:dishtodiefor","monumenta:quests/r1/dishtodiefor"),
    ("monumenta:farr","monumenta:quests/r1/farr"),
    ("monumenta:flashinthepan","monumenta:quests/r1/flashinthepan"),
    ("monumenta:fountainofmiracles","monumenta:quests/r1/fountainofmiracles"),
    ("monumenta:heroreturn","monumenta:quests/r1/heroreturn"),
    ("monumenta:highwatch","monumenta:quests/r1/highwatch"),
    ("monumenta:lostinmymind","monumenta:quests/r1/lostinmymind"),
    ("monumenta:lowtide","monumenta:quests/r1/lowtide"),
    ("monumenta:mageslegacy","monumenta:quests/r1/mageslegacy"),
    ("monumenta:missingpet","monumenta:quests/r1/missingpet"),
    ("monumenta:missingsoldiers","monumenta:quests/r1/missingsoldiers"),
    ("monumenta:nelfinescurse","monumenta:quests/r1/nelfinescurse"),
    ("monumenta:nyr","monumenta:quests/r1/nyr"),
    ("monumenta:ofmonksandmagic","monumenta:quests/r1/ofmonksandmagic"),
    ("monumenta:quests/oldlabs","monumenta:quests/r1/oldlabs"),
    ("monumenta:pirateslife","monumenta:quests/r1/pirateslife"),
    ("monumenta:pyromania","monumenta:quests/r1/pyromania"),
    ("monumenta:root","monumenta:quests/r1/root"),
    ("monumenta:siegeofhighwatch","monumenta:quests/r1/siegeofhighwatch"),
    ("monumenta:sierhaven","monumenta:quests/r1/sierhaven"),
    ("monumenta:sonsoftheforest","monumenta:quests/r1/sonsoftheforest"),
    ("monumenta:starriernight","monumenta:quests/r1/starriernight"),
    ("monumenta:starrynight","monumenta:quests/r1/starrynight"),
    ("monumenta:supplyanddemand","monumenta:quests/r1/supplyanddemand"),
    ("monumenta:taeldim","monumenta:quests/r1/taeldim"),
    ("monumenta:theplague","monumenta:quests/r1/theplague"),
    ("monumenta:thesalmon","monumenta:quests/r1/thesalmon"),
    ("monumenta:thestaff","monumenta:quests/r1/thestaff"),
    ("monumenta:timetoreflect","monumenta:quests/r1/timetoreflect"),
    ("monumenta:tlaxantroubles","monumenta:quests/r1/tlaxantroubles"),
    ("monumenta:unveiled","monumenta:quests/r1/unveiled"),
    ("monumenta:WUHL","monumenta:quests/r1/WUHL"),
)

def fix_file(filePath,allRenamed):
    try:
        test = open(filePath, "r")
        test.close()
        os.rename( filePath, filePath + ".old" )
        with open(filePath + ".old", "r") as fin:
            with open(filePath, "w") as fout:
                for line in fin:
                    for renamed in allRenamed:
                        line = line.replace( '"' + renamed[0] + '"', '"' + renamed[1] + '"' )
                    fout.write(line)
                fout.close()
            fin.close()
        os.remove(filePath + ".old")
    except:
        pass

for aFolderToWalk in foldersToWalk:
    for folderInfo in os.walk(aFolderToWalk):
        folder=folderInfo[0]
        files =folderInfo[2]
        for fileName in files:
            for aType in allowedTypes:
                if fileName[-len(aType):] == aType:
                    filePath = folder+'/'+fileName
                    print(filePath)
                    fix_file( filePath, allRenamed )

