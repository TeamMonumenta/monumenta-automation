#!/usr/bin/env python3

import json
import os
import sys
import re
from pprint import pprint

# Pseudocode for what this does
#
# Parse each file line by line
# for each line
#  for each subcomponent matching 'Lore:\["[^]]*"\]' not already containing "text"
#     extract relevant substring ["stuff","morestuff",...]
#     parse as JSON
#     for each element in the array:
#       update element to '"text":"stuff"'
#       re-serialize to json string
#
#       replace non-escaped " with '
#       Un-escape one level of quotes (replace \" with just "

textpattern = re.compile(r'''\\*"text\\*"''')
lorepattern = re.compile(r'''Lore:\["[^]]*"\]''')
unescapedpattern = re.compile(r'''(?<!\\)"''')
escapedpattern = re.compile(r'''\\"''')

def process_one_command(line):
    '''
    Called on a line of text.

    Returns None if no changes are needed, or a new replacement line of text if Lore format was updated
    '''
    end=0
    newline=''
    for m in re.finditer(lorepattern, line):
        if not textpattern.search(m.group(0)):
            loreblock = m.group(0)[5:]
            js = json.loads(loreblock)
            newjs = []
            for loreentry in js:
                newjs.append("""{"text":""" + '"' + loreentry + '"' + """}""")
            newloreblock = json.dumps(newjs, ensure_ascii=False, sort_keys=False, separators=(',', ':'))
            newloreblock = re.sub(unescapedpattern, "'", newloreblock)
            newloreblock = re.sub(escapedpattern, '"', newloreblock)

            # Add whatever came before the match
            newline += line[end:m.start(0)]

            # Add the newly updated lore block
            newline += "Lore:" + newloreblock

            end = m.end(0)

    if end > 0:
        return newline + line[end:]
    else:
        return None


def process_one_function_file(filepath):
    changed = False
    with open(filepath, "r") as fp:
        data = fp.readlines()

    for idx in range(len(data)):
        line = data[idx]

        newline = process_one_command(line)
        if newline is not None:
            changed = True
            data[idx] = newline

            print("")
            print("FILE: " + filepath.rstrip())
            print("ORIG: " + line.rstrip())
            print("NEW : " + newline.rstrip())

    if changed:
        with open(filepath, "w") as fp:
            fp.writelines(data)

def process_json_file_element(data):
    """
    Recursively processes one json element. Returns a modified element if something changed, None otherwise
    """
    changed = False

    if type(data) is str:
        data = process_one_command(data)
        if data is not None:
            changed = True
    elif type(data) is dict:
        for key in data:
            newval = process_json_file_element(data[key])
            if newval is not None:
                changed = True
                data[key] = newval
    elif type(data) is list:
        for idx in range(len(data)):
            list_element = data[idx]

            new_list_element = process_json_file_element(list_element)
            if new_list_element is not None:
                changed = True
                data[idx] = new_list_element

                # print("")
                # print("FILE: " + filepath.rstrip())
                # print("ORIG: " + list_element.rstrip())
                # print("NEW : " + new_list_element.rstrip())

    if changed:
        return data

    return None

def process_one_json_file(filepath):

    with open(filepath, "r") as fp:
        data = json.load(fp)

    try:
        newdata = process_json_file_element(data)

        if newdata is not None:
            with open(filepath, "w") as fp:
                json.dump(newdata, fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))
                fp.write('\n')
    except Exception as e:
        print("Failed to process '{}': {}".format(filepath, e))


for subdir, dirs, files in os.walk("data"):
    for fname in files:
        filepath = os.path.join(subdir, fname)
        if filepath.lower().endswith(".mcfunction"):
            process_one_function_file(filepath)
            pass
        elif filepath.lower().endswith(".json"):
            # process_one_json_file(filepath)
            pass
