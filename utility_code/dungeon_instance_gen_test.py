#!/usr/bin/env python3

import os

from lib_py3.copy_region import copy_region

config = {
    "dungeonRefFolder":"/home/rock/5_SCRATCH/tmpreset/Project_Epic-dungeon/",
    "outFolder":"/home/rock/5_SCRATCH/tmpreset/dungeons-out/",

    # Dungeons are placed one per MC region file (32x32 chunks)
    # Each dungeon starts in the most-negative corner of the region
    # Regions with dungeons form a line of consecutive regions in +z
    #
    # Each region containing a dungeon is full of void biome
    # There is a padding layer of void biome in the -x and -z directions as specified below
    #
    # All dungeons fit in a region file; even corrupted sierhaven is only 30x24 chunks

    "dungeons":(
        {
            "name":"white",
            "region":{"x":-3, "z":-2},
            "numDungeons":50,
        },{
            "name":"orange",
            "region":{"x":-3, "z":-1},
            "numDungeons":50,
        },{
            "name":"magenta",
            "region":{"x":-3, "z":0},
            "numDungeons":50,
        },{
            "name":"lightblue",
            "region":{"x":-3, "z":1},
            "numDungeons":50,
        },{
            "name":"yellow",
            "region":{"x":-3, "z":2},
            "numDungeons":50,
        },{
            "name":"r1bonus",
            "region":{"x":-3, "z":3},
            "numDungeons":50,
        },{
            "name":"roguelike",
            "region":{"x":-2, "z":-1},
            "numDungeons":1,
        },{
            "name":"nightmare",
            "region":{"x":-3, "z":4},
            "numDungeons":50,
        },{
            "name":"tutorial",
            "region":{"x":-2, "z":0},
            "numDungeons":200,
        },
    ),
    "spawnRegion":{"x":-3, "z":-3},
    # Dungeons placed in region -3,-2 - a region is 32x32 chunks
    "targetRegion":{"x":-3, "z":-2},
}

dungeons = config["dungeons"]

for dungeon in dungeons:
    dungeonName = dungeon["name"]

    dungeonRefFolder = config["dungeonRefFolder"]
    outFolder = config["outFolder"]
    targetRegion = config["targetRegion"]
    dungeonRegion = dungeon["region"]
    numDungeons = dungeon["numDungeons"]
    dstFolder = os.path.join(outFolder,dungeonName,'Project_Epic-'+dungeonName)
    
    oldRegionDir = os.path.join(dungeonRefFolder,"region")
    newRegionDir = os.path.join(       dstFolder,"region")

    # New!
    print("Working on {}...0/{}".format(dungeonName,numDungeons),end="")

    os.makedirs(os.path.join(dstFolder,"region"),mode=0o775,exist_ok=True)

    spawnRegion = config["spawnRegion"]
    copy_region(
        oldRegionDir,
        newRegionDir,
        spawnRegion["x"],spawnRegion["z"],
        spawnRegion["x"],spawnRegion["z"]
    )

    rx=targetRegion["x"]
    rzInit=targetRegion["z"]
    for i in range(numDungeons):
        print("\rWorking on {}...{}/{}".format(dungeonName,i+1,numDungeons),end="")
        rz = rzInit + i
        copy_region(
            oldRegionDir,
            newRegionDir,
            dungeonRegion["x"],dungeonRegion["z"],
            rx,rz
        )
    print("")

