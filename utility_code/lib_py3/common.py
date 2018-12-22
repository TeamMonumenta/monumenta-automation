#!/usr/bin/env python3

import os
import sys

import shutil

class AlwaysEqual(object):
    def __init__(self):
        pass
    def __eq__(self,other):
        return True
always_equal = AlwaysEqual()

class NeverEqual(object):
    def __init__(self):
        pass
    def __eq__(self,other):
        return False
never_equal = NeverEqual()

def move_file(old, new):
    if not os.path.exists(old):
        print("*** '{}' does not exist, preserving original.".format(old))
        return False
    if os.path.exists(new):
        os.remove(new)
    if os.path.islink(old):
        linkto = os.readlink(old)
        os.symlink(linkto, new)
        os.remove(old)
    else:
        shutil.move(old, new)
    return True

def copy_file(old, new):
    if not os.path.exists(old):
        print("*** '{}' does not exist, preserving original.".format(old))
        return False
    if not os.path.exists(os.path.dirname(new)):
        os.makedirs(os.path.dirname(new))
    if os.path.exists(new):
        os.remove(new)
    if os.path.islink(old):
        linkto = os.readlink(old)
        os.symlink(linkto, new)
    else:
        shutil.copy2(old, new)
    return True

def copy_folder(old, new):
    # This does not check if it's a path or a file, but there's another function for that case.
    if not os.path.exists(old):
        print("*** '{}' does not exist, preserving original.".format(old))
        return
    if not os.path.exists(os.path.dirname(new)):
        os.makedirs(os.path.dirname(new))
    shutil.rmtree(new, ignore_errors=True)
    shutil.copytree(old, new, symlinks=True)

def copy_path(old, new, path):
    if os.path.isdir(os.path.join(old, path)):
        copy_folder(os.path.join(old, path), os.path.join(new, path))
    else:
        copy_file(os.path.join(old, path), os.path.join(new, path))

def copy_paths(old, new, paths):
    for path in paths:
        try:
            copy_path(old, new, path);
        except:
            print("*** " + path + " could not be copied, may not exist.")
