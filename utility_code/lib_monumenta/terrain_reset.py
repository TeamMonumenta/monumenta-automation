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

        # Check for impossible config values
        if "localMainFolder" in config:
            if not os.path.isdir(config["localMainFolder"]):
                sys.exit("localMainFolder world folder does not exist.")
        else:
            sys.exit("localMainFolder not specified.")
        if "localBuildFolder" in config:
            if not os.path.isdir(config["localBuildFolder"]):
                sys.exit("localBuildFolder world folder does not exist.")
        if "localDstFolder" not in config:
            sys.exit("localDstFolder not specified.")
        if ("coordinatesToCopy" in config) and ("localBuildFolder" not in config):
            sys.exit("coordinatesToCopy requires localBuildFolder")

        # Assign required variables
        localMainFolder = config["localMainFolder"]
        localDstFolder = config["localDstFolder"]

        # Copy the build world as a base if it was provided
        if "localBuildFolder" in config:
            print "  Copying build world as base..."
            copyFolder(config["localBuildFolder"], localDstFolder)

        # Copy the main world if the destination world doesn't exist
        # TODO: This path is a little weird, because it copies the base then copies the playerdata again
        if ("localBuildFolder" not in config) and (not os.path.isdir(config["localDstFolder"])):
            print "  Copying main world as base..."
            copyFolder(config["localMainFolder"], localDstFolder)

        replaceItems = config["itemReplacements"]

        # If block replacements were specified, assign a variable
        if "blockReplacements" in config:
            blockReplacements = config["blockReplacements"]
        else:
            blockReplacements = None

        # Copy various bits of player data from the main world
        # Note updating advancements, functions, and loot_tables is now done via gen_server_config
        print "  Copying player data files from main world..."
        copyFolders(localMainFolder, localDstFolder, ["advancements/", "playerdata/", "stats/",])
        print "  Copying player maps and scoreboard from main world..."
        copyFolders(localMainFolder, localDstFolder, ["data/",])

        replaceItems.OnPlayers(localDstFolder)

        # Only load the world and manipulate it if we need to
        # TODO - This is a little weird, since we skip doing item replacements worldwide if we don't also do something else involving the world
        #        This is desired behavior, but it's unintuitive
        if (("coordinatesToFill" in config) or ("coordinatesToCopy" in config) or (blockReplacements is not None) or
            (("resetRegionalDifficulty" in config) and (config["resetRegionalDifficulty"] == True))):

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
                    print "  Copying needed terrain from the main world..."
                    copyBoxes(srcWorld, dstWorld, config["coordinatesToCopy"], blockReplacements, replaceItems)
            else:
                # No coordinates to copy, but still want to replace blocks - do the block replacement worldwide
                if blockReplacements is not None:
                    print "  Replacing specified blocks worldwide..."
                    replaceGlobally(dstWorld, blockReplacements)
                # No coordinates to copy, but still want to replace items - do the item replacement worldwide
                print "  Replacing specified items worldwide..."
                replaceItems.InWorld(dstWorld)

            if ("resetRegionalDifficulty" in config) and (config["resetRegionalDifficulty"] == True):
                print "  Resetting difficulty..."
                resetRegionalDifficulty(dstWorld)

            print "  Generating lights (should only happen on block changes!)...."
            dstWorld.generateLights()
            print "  Saving...."
            dstWorld.saveInPlace()

        if "safetyTpLocation" in config:
            print "  Moving players..."
            movePlayers(localDstFolder, config["safetyTpLocation"])

        try:
            shutil.rmtree(localDstFolder+"##MCEDIT.TEMP##", ignore_errors=True)
            os.remove(localDstFolder+"mcedit_waypoints.dat")
        except Exception as e:
            pass

    print "Done!"

