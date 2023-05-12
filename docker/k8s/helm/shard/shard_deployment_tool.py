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
    "dev4"               : { "build": { "node": "m12", "memMB": 1536, }, },
    "mobs"               : { "build": { "node": "m12", "memMB": 1536, }, },
    "dungeon"            : { "build": { "node": "m12", "memGB": 8   , }, },
    "futurama"           : { "build": { "node": "m12", "memGB": 3   , }, },
    "test"               : { "build": { "node": "m12", "memGB": 3   , }, },
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
        "stage": { "node": "m12", "memGB": 3, },
    },
    "valley-3": {
        "play" : { "node": "m8" , "memGB": 6, },
    },

    # R2
    "isles": {
        "play" : { "node": "m11", "memGB": 5, },
        "build": { "node": "m12", "memGB": 3, },
        "stage": { "node": "m12", "memGB": 4, },
        "clash": { "node": "m12", "memGB": 4, },
    },
    "isles-2": {
        "play" : { "node": "m14", "memGB": 5, },
    },
    "isles-3": {
        "play" : { "node": "m15", "memGB": 5, },
    },

    # R3
    "ring": {
        "play":  { "node": "m13", "memGB": 7   , },
        "build": { "node": "m12", "memGB": 3   , },
        "stage": { "node": "m12", "memGB": 3   , },
    },
    "ring-2":  { "play" : { "node": "m15", "memGB": 7, }, },
    "ring-3":  { "play" : { "node": "m11", "memGB": 7, }, },
    "ring-4":  { "play" : { "node": "m11", "memGB": 7, }, },
    "ring-5":  { "play" : { "node": "m8" , "memGB": 7, }, },
    "ring-6":  { "play" : { "node": "m8" , "memGB": 7, }, },
    "ring-7":  { "play" : { "node": "m14", "memGB": 7, }, },
    "ring-8":  { "play" : { "node": "m15", "memGB": 7, }, },
    "ring-9":  { "play" : { "node": "m15", "memGB": 7, }, },
    "ring-10":  { "play" : { "node": "m13", "memGB": 7, }, },

    # Plots
    "plots": {
        "play" : { "node": "m14", "memGB": 8, },
        "stage": { "node": "m12", "memGB": 6, },
    },

    "playerplots": {
        "play":  { "node": "m13", "memGB": 8, },
        "build": { "node": "m12", "memMB": 1536, },
        "stage": { "node": "m12", "memGB": 4, },
    },

    # Player build shard
    "build": {
        "play" : { "node": "m8" , "memGB": 3   , "gsheetCredentials": "false" },
        "stage": { "node": "m12", "memMB": 1536, "gsheetCredentials": "false" },
    },

    # Dungeons
    "cyan": {
        "play" : { "node": "m15", "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "depths": {
        "play" : { "node": "m11", "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
        "clash": { "node": "m12", "memMB": 1536, },
    },
    "forum": {
        "play" : { "node": "m15", "memGB": 4   , },
        "stage": { "node": "m12", "memMB": 2048, },
    },
    "gray": {
        "play" : { "node": "m8" , "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "labs": {
        "play" : { "node": "m11", "memGB": 6   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "lightblue": {
        "play" : { "node": "m13", "memGB": 5   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "lightblue-2": {
        "play" : { "node": "m14", "memGB": 5   , },
    },
    "lightblue-3": {
        "play" : { "node": "m15", "memGB": 5   , },
    },
    "lightgray": {
        "play" : { "node": "m14" , "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "lime": {
        "play" : { "node": "m14", "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "magenta": {
        "play" : { "node": "m13", "memGB": 5   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "magenta-2": {
        "play" : { "node": "m14", "memGB": 5   , },
    },
    "magenta-3": {
        "play" : { "node": "m14", "memGB": 5   , },
    },
    "orange": {
        "play" : { "node": "m13", "memGB": 3, },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "pink": {
        "play" : { "node": "m14", "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "purple": {
        "play" : { "node": "m8" , "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "reverie": {
        "play" : { "node": "m13", "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "corridors": {
        "play" : { "node": "m14", "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "rush": {
        "play" : { "node": "m15", "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "shiftingcity": {
        "play" : { "node": "m11", "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "teal": {
        "play" : { "node": "m15" , "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "tutorial": {
        "play" : { "node": "m11", "memGB": 5   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "white": {
        "play" : { "node": "m13", "memGB": 3, },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "willows": {
        "play" : { "node": "m13", "memMB": 4608, },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "yellow": {
        "play" : { "node": "m14", "memGB": 3   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },

    "gallery": {
        "play" : { "node": "m8", "memGB": 4   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "gallery-2": { "play" : { "node": "m8", "memGB": 4, }, },

    "blue": {
        "play" : { "node": "m14", "memGB": 5   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "blue-2": { "play" : { "node": "m8" , "memGB": 5, }, },
    "blue-3": { "play" : { "node": "m15", "memGB": 5, }, },
    "blue-4": { "play" : { "node": "m11", "memGB": 5, }, },

    "brown": {
        "play" : { "node": "m15", "memGB": 5   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "brown-2":  { "play" : { "node": "m15", "memGB": 5, }, },
    "brown-3":  { "play" : { "node": "m11", "memGB": 5, }, },

    "portal": {
        "play" : { "node": "m11", "memGB": 6   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },

    "ruin": {
        "play" : { "node": "m8", "memGB": 4   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },

    "skt": {
        "play" : { "node": "m13", "memGB": 4   , },
        "stage": { "node": "m12", "memMB": 1536, },
    },
    "skt-2": { "play" : { "node": "m13", "memGB": 4, }, },
    "skt-3": { "play" : { "node": "m13", "memGB": 4, }, },
}

# Defaults for each namespace
namespace_defaults = {
    "play" : { "gsheetCredentials": "true" , "fastMetrics": "false", "maps": "true" },
    "build": { "gsheetCredentials": "false", "fastMetrics": "false", "maps": "true" },
    "stage": { "gsheetCredentials": "true", "fastMetrics": "false", "maps": "true" },
    "clash": { "gsheetCredentials": "false", "fastMetrics": "false", "maps": "false" },
}

# "node" uses abbreviated node names. This is the map back to full names:
abbrev_node_to_full = {
    "m8": "monumenta-8",
    "m11": "monumenta-11",
    "m12": "monumenta-12",
    "m13": "monumenta-13",
    "m14": "monumenta-14",
    "m15": "monumenta-15",
}


RE_NUMBER = re.compile('''[0-9]+''')
RE_NOT_NUMBER = re.compile('''[^0-9]+''')


def usage():
    sys.exit(f'''Usage: {sys.argv[0]} <action> <namespace> <shard>
<action> can be one of these:
    print - Generates the YAML deployment and prints it out
    memoryusage - Displays the memory usage on each node
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


def natural_sort(key):
    if not isinstance(key, str):
        return key

    result = []
    while len(key) > 0:
        match = RE_NUMBER.match(key)
        if match:
            result.append(int(key[:match.end()]))
            key = key[match.end():]
            continue

        match = RE_NOT_NUMBER.match(key)
        if match:
            part = key[:match.end()]
            if part.startswith('.'):
                result.append('.')
                part = part[1:]
            result.append(part.lower())
            result.append(part)
            key = key[match.end():]
            continue

        print('Somehow not a number nor a non-number?')
        print(repr(key))
        result.append(key)
        break

    return result


def print_memory_usage():
    node_memory_usages = {}
    namespace_memory_usages = {}
    namespaces = set()
    for shard in shard_config.values():
        for namespace, namespace_info in shard.items():
            if "node" not in namespace_info:
                continue
            if "memMB" not in namespace_info and "memGB" not in namespace_info:
                continue

            namespaces.add(namespace)

            node = namespace_info["node"]
            memGB = 0
            if "memMB" in namespace_info:
                memGB = namespace_info["memMB"] / 1024.0
            else:
                memGB = float(namespace_info["memGB"])

            if node not in node_memory_usages:
                node_memory_usages[node] = 0.0
            node_memory_usages[node] += memGB

            if namespace not in namespace_memory_usages:
                namespace_memory_usages[namespace] = {}
            if node not in namespace_memory_usages[namespace]:
                namespace_memory_usages[namespace][node] = 0.0
            namespace_memory_usages[namespace][node] += memGB

    header_width = max(len('Total:'), *[len(namespace) for namespace in namespaces])
    column_width = max(len(' '*7 + ' GB'), *[len(node) for node in node_memory_usages.keys()])

    print(' ' * header_width, end='')
    for node in sorted(node_memory_usages.keys(), key=natural_sort):
        print(f' │ {node:<{column_width}}', end='')
    print('')

    print('─' * header_width, end='')
    for node in sorted(node_memory_usages.keys(), key=natural_sort):
        print('─┼─' + '─'*column_width, end='')
    print('')

    for namespace in sorted(namespaces, key=natural_sort):
        namespace_info = namespace_memory_usages[namespace]
        print(f'{namespace:<{header_width}}', end='')
        for node in sorted(node_memory_usages.keys(), key=natural_sort):
            memGB = namespace_info.get(node, 0.0)
            preformatted_entry = f'{memGB:7.2f} GB'
            print(f' │ {preformatted_entry:>{column_width}}', end='')
        print('')

    print('─' * header_width, end='')
    for node in sorted(node_memory_usages.keys(), key=natural_sort):
        print('─┼─' + '─'*column_width, end='')
    print('')

    header = 'Total:'
    print(f'{header:<{header_width}}', end='')
    for node in sorted(node_memory_usages.keys(), key=natural_sort):
        memGB = node_memory_usages[node]
        preformatted_entry = f'{memGB:7.2f} GB'
        print(f' │ {preformatted_entry:>{column_width}}', end='')
    print('')


if len(sys.argv) != 4:
    usage()

action = sys.argv[1]
namespace = sys.argv[2]
shard = sys.argv[3]

if action in ["print", "apply", "delete", "memoryusage"]:
    if action == "memoryusage":
        print_memory_usage()
    else:
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
