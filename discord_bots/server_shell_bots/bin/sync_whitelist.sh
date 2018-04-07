#!/bin/bash

# Synchronizes whitelist from R1 to all other shards

for x in betaplots lightblue magenta orange r1bonus r1plots region_1 roguelike tutorial white yellow; do
	cp ~/project_epic/region_1/whitelist.json ~/project_epic/$x/
	cp ~/project_epic/region_1/banned-players.json ~/project_epic/$x/
	cp ~/project_epic/region_1/banned-ips.json ~/project_epic/$x/
	cp ~/project_epic/region_1/ops.json ~/project_epic/$x/
done
