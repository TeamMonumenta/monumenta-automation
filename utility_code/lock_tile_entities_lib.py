#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This lists the tile entities that lack
a loot table within a box, filtering by type.
"""
# Required libraries have links where not part of a standard Python install.
import os
import shutil

# These are expected in your site-packages folder, see:
# https://stackoverflow.com/questions/31384639/what-is-pythons-site-packages-directory
import mclevel # from https://github.com/mcedit/pymclevel
from mclevel import mclevelbase
from mclevel import materials
from mclevel.box import BoundingBox, Vector
from mclevel import nbt

from monumenta_common import getBoxName
from monumenta_common import getBoxSize
from monumenta_common import getBoxPos
from monumenta_common import getBox
from monumenta_common import getBoxMaterial
from monumenta_common import getBoxMaterialName

################################################################################
# Function definitions

################################################################################
# Functions that display stuff while they work

def run(worldFolder, coordinatesToScan, tileEntitiesToCheck):
    print "Beginning scan..."
    world = mclevel.loadWorld(worldFolder)

    # Build tile ID list, adding default namespace if needed
    tileIDList = []
    for tileID in tileEntitiesToCheck:
        if ":" in tileID:
            tileIDList.append(tileID)
        else:
            tileIDList.append("minecraft:"+tileID)

    scanNum = 1
    scanMax = len(coordinatesToScan)

    allChunks = set(world.allChunks)

    # This is fine. The warning is known and can be ignored.
    # warnings.filterwarnings("ignore", category=numpy.VisibleDeprecationWarning)

    for aScanBox in coordinatesToScan:
        boxName = getBoxName(aScanBox)
        print "[{0}/{1}] Scaning {2}...".format(scanNum,scanMax,boxName)
        scanNum+=1

        scanBox = getBox(aScanBox)

        # The function world.getTileEntitiesInBox() does not work.
        # Working around it, since it works for chunks but not worlds.
        selectedChunks = set(scanBox.chunkPositions)
        chunksToScan = list(selectedChunks.intersection(allChunks))
        for cx,cz in chunksToScan:
            # Get and loop through entities within chunk and box
            aChunk = world.getChunk(cx,cz)
            chunkDirty = False
            newTileEntities = aChunk.getTileEntitiesInBox(scanBox)
            for aTileEntity in newTileEntities:

                # Check if tileEntity is being scanned
                if aTileEntity["id"].value in tileIDList:

                    chunkDirty = True
                    
                    # Detect missing lock tag
                    if ("Lock" not in aTileEntity):
                        # Add and set a lock tag
                        # String selection reasoning:
                        # - generated randomly
                        # - exceeds 32 character limit for anvil renaming
                        # - has a formatting code (obfuscate)
                        aTileEntity["Lock"] = nbt.Tag_STRING(u'''§kl{sC7v@6i-3g!% 22kTw?jhu.MML95,x?''')
                    else:
                        # Set the lock tag
                        aTileEntity["Lock"].value = u'''§kl{sC7v@6i-3g!% 22kTw?jhu.MML95,x?'''
            
            if chunkDirty:
                aChunk.chunkChanged(False) # needsLighting=False

    print "Saving..."
    world.saveInPlace()
    print "Done."

