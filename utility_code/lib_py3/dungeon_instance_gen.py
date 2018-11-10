#!/usr/bin/env python3

import multiprocessing as mp
import os
import psutil
import shutil
import sys

from lib_py3.common import copy_folder #, tempdir
from lib_py3.copy_region import copy_region
from lib_py3.timing import Timings
from lib_py3.world import World

def gen_dungeon_instance(config, dungeon, outputFile):
    mainTiming = Timings(enabled=True)
    nextStep = mainTiming.nextStep

    # Per-dungeon config
    dungeonName = dungeon["name"]

    nextStep(dungeonName + ": Thread started")

    # Global config
    dungeonRefFolder = config["dungeonRefFolder"]
    templateFolder = config["templateFolder"]
    outFolder = config["outFolder"]
    voidPadding = config["voidPadding"]
    targetRegion = config["targetRegion"]
    tileEntitiesToCheck = config["tileEntitiesToCheck"]

    # Per-dungeon config
    dungeonName = dungeon["name"]
    dungeonRegion = dungeon["region"]
    dungeonSize = dungeon["size"]
    dungeonContentsLoreToIgnore = dungeon.get("chestContentsLoreToIgnore",None)
    dungeonChestWhitelist = dungeon.get("chestWhitelist",None)
    numDungeons = dungeon["numDungeons"]
    dstFolder = os.path.join( outFolder, dungeonName, 'Project_Epic-' + dungeonName )

    nextStep(dungeonName + ": Config read")

    # Compute dungeon parameters
    dungeonPos = ( dungeonRegion["x"] * 512, 0, dungeonRegion["z"] * 512 )

    nextStep(dungeonName + ": pre-calc done")

