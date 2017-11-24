#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).

This does so as directly as possible while providing many features.

Fair warning, some of the optimization is done by removing error handling.
Python will tell you if/when the script crashes.
If it's going to crash, it won't damage the original worlds.
Just fix what broke, and run again.
"""

import os
import sys
import shutil

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
import pymclevel

from lib_monumenta.common import fillBoxes, copyBoxes, copyFolder, copyFolders
from lib_monumenta.common import resetRegionalDifficulty, movePlayers, replaceGlobally

def terrainReset(configlist):
    for config in configlist:
        print "Starting reset for server {0}...".format(config["server"])

        ################################################################################
        # Check for impossible config values
        if "localMainFolder" in config:
            if not os.path.isdir(config["localMainFolder"]):
                sys.exit("localMainFolder world folder does not exist.")
        else:
            sys.exit("localMainFolder not specified.")

        if "localDstFolder" not in config:
            sys.exit("localDstFolder not specified.")

        if "localBuildFolder" in config:
            if not os.path.isdir(config["localBuildFolder"]):
                sys.exit("localBuildFolder world folder does not exist.")

        if ("coordinatesToCopy" in config) and ("localBuildFolder" not in config):
            sys.exit("coordinatesToCopy requires localBuildFolder")

        if ("blockReplacements" in config) ^ ("blockReplaceLocations" in config):
            sys.exit("blockReplacements and blockReplaceLocations must be used together")

        if ("itemReplacements" in config) ^ ("itemReplaceLocations" in config):
            sys.exit("itemReplacements and itemReplaceLocations must be used together")

        ################################################################################
        # Assign variables

        localMainFolder = config["localMainFolder"]
        localDstFolder = config["localDstFolder"]

        blockReplacements = config["blockReplacements"] if ("blockReplacements" in config) else None
        itemReplacements = config["itemReplacements"] if ("itemReplacements" in config) else None
        shouldResetDifficulty = config["resetRegionalDifficulty"] if ("resetRegionalDifficulty" in config) else False

        ################################################################################
        # Copy folders

        # Copy build or main as base world, depending on config
        if "copyBaseFrom" in config:
            if config["copyBaseFrom"] == "build":
                print "  Copying build world as base..."
                copyFolder(config["localBuildFolder"], localDstFolder)
            elif config["copyBaseFrom"] == "main":
                print "  Copying main world as base..."
                copyFolder(localMainFolder, localDstFolder)
            else:
                sys.exit("Illegal value '" + config["copyBaseFrom"] + "' for key 'copyBaseFrom'")

        # Copy various bits of player data from the main world
        if "copyMainFolders" in config:
            print "  Copying folders from main world..."
            copyFolders(localMainFolder, localDstFolder, config["copyMainFolders"])


        ################################################################################
        # Perform world manipulations if required
        if (("coordinatesToFill" in config)
                or ("coordinatesToCopy" in config)
                or (blockReplacements is not None)
                or ((itemReplacements is not None) and "world" in config["itemReplaceLocations"])
                or (shouldResetDifficulty == True)):

            print "  Opening old play World..."
            srcWorld = pymclevel.loadWorld(localMainFolder)

            print "  Opening Destination World..."
            dstWorld = pymclevel.loadWorld(localDstFolder)

            if "coordinatesToFill" in config:
                print "  Filling selected regions with specified blocks..."
                fillBoxes(dstWorld, config["coordinatesToFill"])

            if "coordinatesToCopy" in config:
                if ("coordinatesDebug" in config) and (config["coordinatesDebug"] == True):
                    print "  DEBUG: Filling regions instead of copying them!"
                    fillBoxes(dstWorld, config["coordinatesToCopy"])
                else:
                    # Only pass in replacement lists if specifically requested for schematics
                    tmpBlockReplacements = blockReplacements if (blockReplacements is not None and "schematics" in config["blockReplaceLocations"]) else None
                    tmpItemReplacements = itemReplacements if (itemReplacements is not None and "schematics" in config["itemReplaceLocations"]) else None

                    print "  Copying needed terrain from the main world..."
                    copyBoxes(srcWorld, dstWorld, config["coordinatesToCopy"], tmpBlockReplacements, tmpItemReplacements)

            if (blockReplacements is not None) and ("world" in config["blockReplaceLocations"]):
                print "  Replacing specified blocks worldwide..."
                replaceGlobally(dstWorld, blockReplacements)

            if (itemReplacements is not None) and ("world" in config["itemReplaceLocations"]):
                print "  Replacing specified items worldwide..."
                itemReplacements.InWorld(dstWorld)

            if (shouldResetDifficulty == True):
                print "  Resetting difficulty..."
                resetRegionalDifficulty(dstWorld)

            print "  Generating lights (should only happen on block changes!)...."
            dstWorld.generateLights()
            print "  Saving...."
            dstWorld.saveInPlace()

        if "players" in config["itemReplaceLocations"]:
            itemReplacements.OnPlayers(localDstFolder)

        if "safetyTpLocation" in config:
            print "  Moving players..."
            movePlayers(localDstFolder, config["safetyTpLocation"])

        try:
            shutil.rmtree(localDstFolder+"##MCEDIT.TEMP##", ignore_errors=True)
            os.remove(localDstFolder+"mcedit_waypoints.dat")
        except Exception as e:
            pass

    print "Done!"

