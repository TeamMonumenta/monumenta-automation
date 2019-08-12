#!/usr/bin/env python3

import os
import sys
import codecs
import multiprocessing as mp
import tempfile
import traceback

from lib_py3.copy_region import copy_region
from lib_py3.common import copy_paths
from lib_py3.world import World

config = {
    "dungeonRefFolder":"/home/epic/5_SCRATCH/tmpreset/Project_Epic-dungeon/",
    "outFolder":"/home/epic/5_SCRATCH/tmpreset/dungeons-out/",

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
            "numDungeons":40,
        },{
            "name":"orange",
            "region":{"x":-3, "z":-1},
            "numDungeons":40,
        },{
            "name":"magenta",
            "region":{"x":-3, "z":0},
            "numDungeons":40,
        },{
            "name":"lightblue",
            "region":{"x":-3, "z":1},
            "numDungeons":40,
        },{
            "name":"yellow",
            "region":{"x":-3, "z":2},
            "numDungeons":40,
        },{
            "name":"r1bonus",
            "region":{"x":-3, "z":3},
            "numDungeons":40,
        },{
            "name":"roguelike",
            "region":{"x":-2, "z":-1},
            "numDungeons":200,
        },{
            "name":"nightmare",
            "region":{"x":-3, "z":4},
            "numDungeons":40,
        },{
            "name":"tutorial",
            "region":{"x":-2, "z":0},
            "numDungeons":200,
        },{
            "name":"sanctum",
            "region":{"x":-3, "z":12},
            "numDungeons":40,
        },{
            "name":"labs",
            "region":{"x":-2, "z":1},
            "numDungeons":75,
        },{
            "name":"lime",
            "region":{"x":-3, "z":5},
            "numDungeons":40,
        },{
            "name":"pink",
            "region":{"x":-3, "z":7},
            "numDungeons":40,
        },{
            "name":"gray",
            "region":{"x":-3, "z":6},
            "numDungeons":40,
        },{
            "name":"cyan",
            "region":{"x":-3, "z":9},
            "numDungeons":40,
        },{
            "name":"lightgray",
            "region":{"x":-3, "z":8},
            "numDungeons":40,
        },{
            "name":"fred",
            "region":{"x":-2, "z":9},
            "numDungeons":20,
        },
    ),

    # Chunk to copy directly from the reference folder
    "spawnRegion":{"x":-3, "z":-3},

    # Dungeon instances start nn region -3,-2 and move in +z - a region is 32x32 chunks
    "targetRegion":{"x":-3, "z":-2},

    # Files/directories to copy from reference
    "copyPaths":[
        "level.dat",
    ],

    # Blocks to set
    "setBlocks":[
        {'pos': [-1441, 2, -1441], 'block': {'name': 'minecraft:air'} },
    ],
}

# Generate instances for a single dungeon
def generateDungeonInstances(config, dungeon, outputFile, statusQueue):
    dungeonName = dungeon["name"]

    try:
        # Redirect output to specified file
        sys.stdout = codecs.getwriter('utf8')(open(outputFile, "wb"))

        ##################################################################################
        dungeonRefFolder = config["dungeonRefFolder"]
        targetRegion = config["targetRegion"]
        dungeonRegion = dungeon["region"]
        numDungeons = dungeon["numDungeons"]
        dstFolder = os.path.join(config["outFolder"],dungeonName,'Project_Epic-'+dungeonName)

        oldRegionDir = os.path.join(dungeonRefFolder,"region")
        newRegionDir = os.path.join(       dstFolder,"region")

        # New!
        print("Working on {}...0/{}".format(dungeonName,numDungeons))

        # Create target directories
        os.makedirs(os.path.join(dstFolder,"region"),mode=0o775,exist_ok=True)

        # Copy files/directories
        copy_paths(dungeonRefFolder, dstFolder, config["copyPaths"])

        # Copy spawn chunks
        spawnRegion = config["spawnRegion"]
        copy_region(
            oldRegionDir,
            newRegionDir,
            spawnRegion["x"],spawnRegion["z"],
            spawnRegion["x"],spawnRegion["z"]
        )

        # Instance the dungeons
        rx=targetRegion["x"]
        rzInit=targetRegion["z"]
        for i in range(numDungeons):
            print("\rWorking on {}...{}/{}".format(dungeonName,i+1,numDungeons))
            rz = rzInit + i
            copy_region(
                oldRegionDir,
                newRegionDir,
                dungeonRegion["x"],dungeonRegion["z"],
                rx,rz
            )

        # Set blocks
        if "setBlocks" in config:
            world = World(dstFolder)
            for block in config["setBlocks"]:
                world.set_block(block["pos"], block)

        print("")
        ##################################################################################

        statusQueue.put({"server":dungeonName, "done":True})

    except:
        e = traceback.format_exc()
        statusQueue.put({"server":dungeonName, "done":True, "error":e})



# Multiprocessing implementation based on:
# http://sebastianraschka.com/Articles/2014_multiprocessing.html

# Run each config item in parallel
print("Generating instances. There will be no output here until finished.")

processes = {}
statusQueue = mp.Queue()
for dungeon in config["dungeons"]:
    dungeonName = dungeon["name"]
    outputFile = tempfile.mktemp()
    processes[dungeonName] = {
        "process":mp.Process(target=generateDungeonInstances, args=(config, dungeon, outputFile, statusQueue)),
        "outputFile":outputFile,
    }

# Decrease the priority for this work so it doesn't slow down other things
os.nice(20)

for p in processes.values():
    p["process"].start()


while len(processes.keys()) > 0:
    statusUpdate = statusQueue.get()
    statusFrom = statusUpdate["server"]
    p = processes[statusFrom]

    if "done" in statusUpdate:
        p["process"].join()

        if "error" not in statusUpdate:
            print(statusFrom + " completed successfully")

        try:
            logFile = codecs.open(p["outputFile"],'rb',encoding='utf8')
            print(logFile.read())
            logFile.close()
        except:
            print("Log file could not be read!")

        processes.pop(statusFrom)

    if "error" in statusUpdate:
        print("\n!!! " + statusFrom + " has crashed.\n")

        # stop all other subprocesses
        for p in processes.values():
            p["process"].terminate()

        raise RuntimeError(str(statusUpdate["error"]))

print("Done!")
