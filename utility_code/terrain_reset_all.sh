#!/bin/sh
# Using a shell script because I'm not sure how to run a python script from
# within python instead of including it. I could import it or do a system call
# to run a command, but let's not get too weird. -NickNackGus

echo "Running terrain reset for region_1..."
./terrain_reset_region_1.py
echo "Running terrain reset for beta plots..."
./terrain_reset_beta_plots.py
echo "Running terrain reset for r1plots..."
./terrain_reset_r1plots.py
echo "Terrain reset Done. Dungeons and unlisted worlds untouched, however."

