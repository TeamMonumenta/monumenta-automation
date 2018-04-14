#!/bin/bash

# Synchronizes whitelist from R1 to all other shards

source_dir="$1"
target_project_epic_dir="$2"

for x in betaplots lightblue magenta orange r1bonus r1plots region_1 roguelike tutorial white yellow; do
	cp "$source_dir/whitelist.json" "$target_project_epic_dir/$x/"
	cp "$source_dir/banned-players.json" "$target_project_epic_dir/$x/"
	cp "$source_dir/banned-ips.json" "$target_project_epic_dir/$x/"
	cp "$source_dir/ops.json" "$target_project_epic_dir/$x/"
done
