import os
import warnings
import shutil

from mclevel.box import BoundingBox, Vector

def getBoxSize(box):
    # Get the size of a box from
    # an element of coordinatesToScan
    sizeFix = Vector(*(1,1,1))
    min_pos = Vector(*map(min, zip(box[1], box[2])))
    max_pos = Vector(*map(max, zip(box[1], box[2])))
    return max_pos - min_pos + sizeFix

def getBoxPos(box):
    # Get the origin of a box from
    # an element of coordinatesToScan
    return Vector(*map(min, zip(box[1], box[2])))

def getBox(box):
    # Returns a box around from
    # an element of coordinatesToScan
    origin = getBoxPos(box)
    size   = getBoxSize(box)

    return BoundingBox(origin,size)

def filesInBox(aBox):
    # returns a list of (x,z) pairs in terms of .mca files
    # Useful for reducing the number of files being transfered.
    # Untested, but should work.

    return itertools.product( xrange(self.minx >> 9, self.maxx >> 9),
                              xrange(self.minz >> 9, self.maxz >> 9))

def copyFile(old, new):
    os.remove(new)
    if os.path.islink(old):
        linkto = os.readlink(old)
        os.symlink(linkto, new)
    else:
        shutil.copy2(old, new)

def copyFolder(old, new):
    shutil.rmtree(new, ignore_errors=True)
    shutil.copytree(old, new, symlinks=True)

def copyFolders(old, new, subfolders):
    for folder in subfolders:
        print "Copying " + folder + "..."
        copyFolder(old+folder, new+folder)
