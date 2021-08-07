#!/usr/bin/env python3

import os
import sys
import subprocess
import tempfile
import re
from pprint import pprint

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../../utility_code/"))
from lib_py3.config_manager import shards_config

# Required arguments:
#   node
#   memGB OR memMB
# Optional arguments:
#   gsheetCredentials
#   fastMetrics
#   useSocketForProbes
#   useHTTPForProbes
#   nodePort
shard_config = shards_config["shard_config"]

# Defaults for each namespace
namespace_defaults = shards_config["namespace_defaults"]

# "node" uses abbreviated node names. This is the map back to full names:
abbrev_node_to_full = shards_config["abbrev_node_to_full"]

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

    shard_conf = shard_config[shard]["k8"]
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
    shards = [s for s in shard_config if ((namespace in shard_config[s]["k8"]) and re.match(shard, s))]
    for s in shards:
        if action == "applyall":
            perform_shard_action("apply", namespace, s)
        elif action == "deleteall":
            perform_shard_action("delete", namespace, s)
        else:
            print(s)

else:
    usage()
