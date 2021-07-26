#!/usr/bin/env python3

import os
import sys
import subprocess
import tempfile
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
    "depths"             : { "build": { "node": "m12", "memMB": 1536, }, },
    "purgatory"          : { "build": { "node": "m12", "memGB": 1   , "useSocketForProbes": "true", "useHTTPForProbes": "false" }, },
    "test"               : { "build": { "node": "m12", "memGB": 3   , }, },
    "test2"              : { "build": { "node": "m12", "memGB": 3   , }, },
    "event"              : { "build": { "node": "m12", "memGB": 3   , }, },
    "monumenta-sdk"      : { "build": { "node": "m12", "memGB": 3   , "nodePort": 22221, }, },

    # R1
    "valley": {
        "play" : { "node": "m8" , "memGB": 6, },
        "build": { "node": "m12", "memGB": 3, },
        "stage": { "node": "m12", "memGB": 4, },
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
    delete - Generates and then deletes the deployment, stopping shard if it is running
''')

if len(sys.argv) != 4:
    usage()

action = sys.argv[1]
namespace = sys.argv[2]
shard = sys.argv[3]

# Check arguments & get shard config
if action not in ["print", "apply", "delete"]:
    usage()
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
