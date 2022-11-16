#!/usr/bin/env python3

import os
import sys
from glob import glob
from pprint import pprint
from lib_py3.common import eprint

if len(sys.argv) < 5:
    sys.exit(f"Usage: {sys.argv[0]} <num_orig_instances> <num_new_instances> <path_to_instance1> <path_to_instance2> [...]")

sys.argv.pop(0)
num_orig_instances = int(sys.argv.pop(0))
num_new_instances = int(sys.argv.pop(0))

folders = []
for folder in sys.argv:
    folders.append(folder)


# pprint(folders)

# Gather data about the folders

match_shard_name = None

data = {}
for folder in folders:
    if not os.path.isdir(folder):
        sys.exit(f"ERROR: Shard folder '{folder}' doesn't exist")

    shard_name = os.path.basename(folder)
    dash_idx = shard_name.rfind("-")
    shard_index = 1
    if dash_idx > 0:
        shard_index = int(shard_name[dash_idx + 1:])
        shard_name = shard_name[:dash_idx]

    if match_shard_name is None:
        match_shard_name = shard_name

    if shard_name != match_shard_name:
        sys.exit(f"ERROR: Shard name '{shard_name}' for folder '{folder}' doesn't match prior shard name '{match_shard_name}'")

    this_shard_instances = []
    for subfolder in glob(f"{folder}/{shard_name}*"):
        basename = os.path.basename(subfolder)
        subfolder_idx = basename[len(shard_name):]
        if len(subfolder_idx) <= 0:
            continue
        subfolder_idx = int(subfolder_idx)
        this_shard_instances.append(subfolder_idx)

    this_shard_instances.sort()

    data[shard_index] = {
        "path": folder,
        "index": shard_index,
        "instances": this_shard_instances,
    }

#pprint(data)

# Figure out what to do with that information

num_shard_folders = len(data)

if num_orig_instances > num_shard_folders:
    sys.exit(f"ERROR: Missing folder? Number of original instances {num_orig_instances} is greater than the number of provided folders {num_shard_folders}")

if num_new_instances > num_shard_folders:
    sys.exit(f"ERROR: Missing folder? Number of new instances {num_new_instances} is greater than the number of provided folders {num_shard_folders}")

for shard_idx in range(num_shard_folders):
    if shard_idx + 1 not in data:
        sys.exit(f"ERROR: All shard folders must be provided, missing {shard_idx + 1}")

# Print instance removal commands
delete_list = []
for shard_idx in data:
    shard_data = data[shard_idx]
    shard_instances = shard_data["instances"]

    for instance in shard_instances:
        if instance % num_orig_instances != shard_idx - 1:
            correct_shard_idx = (instance % num_orig_instances) + 1
            correct_shard_name = match_shard_name
            if correct_shard_idx > 1:
                correct_shard_name = f"{match_shard_name}-{correct_shard_idx}"

            correct_path = f"{data[correct_shard_idx]['path']}/{match_shard_name}{instance}"
            if os.path.isdir(correct_path):
                eprint(f"WARNING: Found instance {instance} in {shard_data['path']} which should be on {correct_shard_name}")
            else:
                eprint(f"SEVERE WARNING: Found instance {instance} in {shard_data['path']} which should be on {correct_shard_name} but the {correct_path} doesn't exist")

            delete_list.append(f"rm -rf {shard_data['path']}/{match_shard_name}{instance}")

for d in delete_list:
    print(d)

# Print instance removal commands
for shard_idx in data:
    shard_data = data[shard_idx]
    shard_instances = shard_data["instances"]

    for instance in shard_instances:
        if instance % num_orig_instances != shard_idx - 1:
            continue # This would be handled / deleted by the above block

        new_shard_idx = (instance % num_new_instances) + 1

        old_path = f"{shard_data['path']}/{match_shard_name}{instance}"
        new_shard_data = data[new_shard_idx]
        new_path = f"{new_shard_data['path']}/{match_shard_name}{instance}"

        if old_path == new_path:
            continue # No reason to move something to itself. This could happen in some configurations, such as going from 4 -> 2 instances

        print(f"mv {old_path} {new_path}")

