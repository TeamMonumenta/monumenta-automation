#!/usr/bin/env python3

import os
import sys
import getopt
import yaml
import multiprocessing
import traceback
import json
from pprint import pprint

def path_to_namespacedkey(path: str) -> str:
    adv_found = False
    key = None
    for item in reversed(path.split('/')):
        if item == "advancements":
            adv_found = True
            continue
        elif adv_found:
            return item + ':' + key
        else:
            if key is None:
                key = item
            else: 
                key = item + '/' + key

advancements_path = sys.argv[1]
out_path = sys.argv[2]

adv_files = []
root_node = None
advs = {}

for root, subdirs, files in os.walk(advancements_path):
    for fname in files:
        if fname.endswith(".json"):
            path = os.path.abspath(os.path.join(root, fname))
            with open(path) as fp:
                adv_files.append(path)
                adv = json.load(fp)

                node = {
                    "id": path_to_namespacedkey(path[:-5]),
                    "path": path,
                    "parent": None,
                    "item": None,
                    "title": adv["display"]["title"]["text"],
                    "location_tag": fname[:-5]
                }

                display = adv["display"]
                if "icon" in display and "item" in display["icon"]: 
                    item_id = display["icon"]["item"]
                    if "minecraft" not in item_id: 
                        item_id = "minecraft:" + item_id
                    if "nbt" in display["icon"]:
                        node["item"] = '{id:"' + item_id + '",' + display["icon"]["nbt"][1:]
                    else: 
                        node["item"] = '{id:"' + item_id + '"}'

                if "parent" not in adv:
                    root_node = node
                else:
                    node["parent"] = adv["parent"]
                advs[node["id"]] = node

# Create a tree structure linking the nodes
for key in advs: 
    node = advs[key]
    if node["parent"] is not None: 
        parent = advs[node["parent"]]
        if "children" not in parent: 
            parent["children"] = {}
        parent["children"][node["id"]] = node

def recurse_flatten(node, root_link): 
    print(node["id"] + "   " + node["title"] )
    if node is not root_link:
        node["parent"] = root_link["id"]
    if node["location_tag"] == "root":
        root_link = node
    if "children" in node:
        for child in node["children"]:
            recurse_flatten(node["children"][child], root_link)
        node.pop("children")

recurse_flatten(root_node, root_node)

# Rebuild the flattened tree structure, minus discover nodes
for key in advs: 
    node = advs[key]
    if node["parent"] is not None: 
        parent = advs[node["parent"]]
        if node["location_tag"] == "discover":
            continue
        if "children" not in parent: 
            parent["children"] = {}
        parent["children"][node["title"]] = node

def recurse_print(node, recurse_indent=''): 
    print(recurse_indent + node["id"] + "   " + node["title"] )
    if "children" in node:
        for child in node["children"]:
            recurse_print(node["children"][child], recurse_indent + '  ')

recurse_print(root_node)

def recurse_cleanup(node): 
    node["required_advancement"] = node["id"]
    node.pop("id")
    node.pop("parent")
    node.pop("path")
    node.pop("title")
    if "children" in node:
        node.pop("location_tag")
        for child in node["children"]:
            recurse_cleanup(node["children"][child])

recurse_cleanup(root_node)

with open(out_path, "w") as fp: 
     yaml.dump(root_node["children"], fp, width=2147483647, allow_unicode=True)

