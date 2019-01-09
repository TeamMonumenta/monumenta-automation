#!/usr/bin/env python3

import os
import sys

import shutil

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def remove_formatting(formattedString):
    nameNoFormat = formattedString
    while '§' in nameNoFormat:
        i = nameNoFormat.find('§')
        nameNoFormat = nameNoFormat[:i]+nameNoFormat[i+2:]
    return nameNoFormat

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

def bounded_range(min_in, max_in, range_start, range_length, divide=1):
    """
    Clip the input so the start and end don't exceed some other range.
    range_start is multiplied by range_length before use
    The output is relative to the start of the range.
    divide allows the range to be scaled to ( range // divide )
    """
    range_length //= divide
    range_start *= range_length

    min_out = min_in//divide - range_start
    max_out = max_in//divide - range_start + 1

    min_out = max( 0, min( min_out, range_length ) )
    max_out = max( 0, min( max_out, range_length ) )

    return range( min_out, max_out )
