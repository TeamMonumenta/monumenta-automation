#!/usr/bin/env python3

import os
import sys
import subprocess
import tempfile
import re
from pprint import pprint

# Required arguments:
#   node
#   memGB OR memMB
# Optional arguments:
#   gsheetCredentials
#   fastMetrics
#   useSocketForProbes
#   useHTTPForProbes
#   nodePort
shard_config = {
    # Shards that only exist on build
    "dev1"               : { "build": { "node": "m12", "memMB": 1536, }, },
    "dev2"               : { "build": { "node": "m12", "memMB": 1536, }, },
    "dev3"               : { "build": { "node": "m12", "memMB": 1536, }, },
    "mobs"               : { "build": { "node": "m12", "memMB": 1536, }, },
    "dungeon"            : { "build": { "node": "m12", "memGB": 3   , }, },
    "ring"               : { "build": { "node": "m12", "memGB": 3   , }, },
    "test"               : { "build": { "node": "m12", "memGB": 3   , }, },
    "test2"              : { "build": { "node": "m12", "memGB": 3   , }, },
    "event"              : { "build": { "node": "m12", "memGB": 3   , }, },
    "monumenta-sdk"      : { "build": { "node": "m12", "memGB": 3   , "nodePort": 22221, }, },

    # Purgatory
    "purgatory": {
        "play" : { "node": "m8" , "memGB": 1, "useSocketForProbes": "true", "useHTTPForProbes": "false" },
        "build": { "node": "m12", "memGB": 1, "useSocketForProbes": "true", "useHTTPForProbes": "false" },
        "stage": { "node": "m12", "memGB": 1, "useSocketForProbes": "true", "useHTTPForProbes": "false" },
    },

    # R1
    "valley": {
        "play" : { "node": "m8" , "memGB": 6, },
        "build": { "node": "m12", "memGB": 3, },
        "stage": { "node": "m12", "memGB": 3, },
    },
    "valley-2": {
        "play" : { "node": "m8" , "memGB": 6, },
    },
    "valley-3": {
        "play" : { "node": "m8" , "memGB": 6, },
    },
    "valley-4": {
        "play" : { "node": "m11", "memGB": 6, },
    },

    # R2
    "isles": {
        "play" : { "node": "m11", "memGB": 5, },
        "build": { "node": "m12", "memGB": 3, },
        "stage": { "node": "m12", "memGB": 4, },
    },
    "isles-2": {
        "play" : { "node": "m11", "memGB": 5, },
    },

    # Plots
    "plots": {
        "play" : { "node": "m11", "memGB": 8, },
        "stage": { "node": "m12", "memGB": 4, },
    },

    # Player build shard
    "build": {
        "play" : { "node": "m8" , "memGB": 2   , "gsheetCredentials": "false" },
        "stage": { "node": "m12", "memMB": 1536, "gsheetCredentials": "false" },
    },

    # Dungeons
    "cyan": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "depths": {
        "play" : { "node": "m11", "memGB": 3   , },
        "build": { "node": "m12", "memMB": 1536, },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "depths-2": {
        "play" : { "node": "m11", "memGB": 3   , },
    },
    "depths-3": {
        "play" : { "node": "m11", "memGB": 3   , },
    },
    "forum": {
        "play" : { "node": "m11", "memGB": 4   , },
        "stage": { "node": "m12", "memMB": 2048, },
    },
    "gray": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "labs": {
        "play" : { "node": "m11", "memGB": 6   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "lightblue": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "lightgray": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "lime": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "magenta": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "mist": {
        "play" : { "node": "m11", "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "orange": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "pink": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "purple": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "remorse": {
        "play" : { "node": "m11", "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "reverie": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "roguelike": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "rush": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "sanctum": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "shiftingcity": {
        "play" : { "node": "m8" , "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "teal": {
        "play" : { "node": "m8" , "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "tutorial": {
        "play" : { "node": "m8" , "memGB": 5   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "white": {
        "play" : { "node": "m8" , "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "willows": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "yellow": {
        "play" : { "node": "m8" , "memGB": 2   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
}

# Defaults for each namespace
namespace_defaults = {
    "play" : { "gsheetCredentials": "true" , "fastMetrics": "false" },
    "build": { "gsheetCredentials": "false", "fastMetrics": "false" },
    "stage": { "gsheetCredentials": "false", "fastMetrics": "false" },
}

# "node" uses abbreviated node names. This is the map back to full names:
abbrev_node_to_full = {
    "m8": "monumenta-8",
    "m11": "monumenta-11",
    "m12": "monumenta-12",
}

def usage():
    sys.exit(f'''Usage: {sys.argv[0]} <action> <namespace> <shard>
<action> can be one of these:
    print - Generates the YAML deployment and prints it out
    apply - Generates and applies the deployment, possibly creating or restarting the existing shard
    applyall - Generates and applies all deployments for this namespace with names matching the regex given by <shard>. Use '.' to match all.
    delete - Generates and then deletes the deployment, stopping shard if it is running
    deleteall - Generates and deletes all deployments for this namespace with names matching the regex given by <shard>. Use '.' to match all.
    testall - Prints out what shards match the arguments supplied which would be executed by applyall/deleteall (without actually running)
''')

def perform_shard_action(action, namespace, shard):
    if shard not in shard_config:
        sys.exit(f"Unable to find shard {shard} in shard_config, must be one of [{','.join(shard_config.keys())}]")

    shard_conf = shard_config[shard]
    if namespace not in shard_conf:
        sys.exit(f"Shard {shard} does not have config for namespace {namespace}")

    # Get the values just for this namespace
    shard_namespaced = shard_conf[namespace]

    # Start with the defaults for this namespace
    output_conf = namespace_defaults[namespace].copy()

    # Copy over all the values set for this shard/namespace
    for key in shard_namespaced:
        output_conf[key] = shard_namespaced[key]

    # Set additional required values from the context
    output_conf["name"] = shard
    output_conf["namespace"] = namespace
    output_conf["nodeFull"] = abbrev_node_to_full[shard_namespaced["node"]]
    if "memGB" in output_conf:
        output_conf["memMB"] = output_conf["memGB"] * 1024

    # Create a list of all the key=value pairs
    vals = []
    for key in output_conf:
        vals.append(f"{key}={output_conf[key]}")

    # Run helm to generate the new shard template
    proc = subprocess.run(["helm", "template", ".", "--set", ",".join(vals)], stdout=subprocess.PIPE)

    # Handle whatever action the user specified
    if action == "print":
        print(proc.stdout.decode('utf-8'))
    elif action == "apply":
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(proc.stdout)
            fp.flush()
            kubectl = subprocess.run(["kubectl", "apply", "-f", fp.name])
    elif action == "delete":
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(proc.stdout)
            fp.flush()
            kubectl = subprocess.run(["kubectl", "delete", "-f", fp.name])

if len(sys.argv) != 4:
    usage()

action = sys.argv[1]
namespace = sys.argv[2]
shard = sys.argv[3]

if action in ["print", "apply", "delete"]:
    perform_shard_action(action, namespace, shard)
elif action in ["applyall", "deleteall", "testall"]:
    # Shard is a regex for "all" operations
    shards = [s for s in shard_config if ((namespace in shard_config[s]) and re.match(shard, s))]
    for s in shards:
        if action == "applyall":
            perform_shard_action("apply", namespace, s)
        elif action == "deleteall":
            perform_shard_action("delete", namespace, s)
        else:
            print(s)

else:
    usage()
