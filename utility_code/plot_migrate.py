#!/usr/bin/python3
import sys
import math

from collections import OrderedDict
from lib_py3.redis_scoreboard import RedisScoreboard
from r1plot_lookup import lut
from pprint import pprint
import json

scoreboard = RedisScoreboard("play", redis_host="localhost")

# Get the plot command blocks and their orientations
with open("plots.json", "r") as fp:
    plot_commands = json.load(fp)

plot_commands_index = {}
for command in plot_commands:
    if "function plot:plot/enter" in command["command"]:
        x, y, z = command["pos"]
        pos = f"{x} {y} {z}"
        plot_commands_index[pos] = command["facing"]

# pprint(plot_commands_index)

plot_scores = {}
num_players_with_plots = 0;
for uuid in scoreboard._players:
    name = scoreboard.get_name(uuid)
    scores = scoreboard._players[uuid]
    ploty = scores.get("ploty", 0)
    if ploty != 0:
        if ploty < 0:
            ploty = ploty * -1
        plotx = scores.get('plotx', 0)
        plotz = scores.get('plotz', 0)
        pos = f"{plotx} {ploty} {plotz}"
        plotID = scores.get("R1Plot", 0)
        if plotID > 0:
            if plotID > 10000:
                plotID -= 10000
        else:
            plotID = 10000 + math.sqrt(((-2458 - plotx) ** 2) + ((1103 - plotz) ** 2))

        slot = plot_scores.get(pos, {})
        if plotID < slot.get("id", 999999999):
            slot["id"] = plotID;

        members = slot.get("members", {})
        members[uuid] = name
        slot["members"] = members

        # Have to try all four offset directions to find the plot door command block
        facing = None
        skip = False
        for offsetfacing, dx, dy, dz in [("north", 0, -2, 3), ("east", -3, -2, 0), ("south", 0, -2, -3), ("west", 3, -2, 0)]:
            checkfacing = plot_commands_index.get(f"{plotx + dx} {ploty + dy} {plotz + dz}", None)
            if checkfacing is not None:
                if checkfacing != offsetfacing:
                    print(f"Serious problem, plot facing direction '{offsetfacing}' doesn't match command block '{checkfacing}' at {pos}")
                    skip = True
                facing = offsetfacing
                break

        if skip:
            continue
        if facing is None:
            print(f"Serious problem, got plot at {pos} but couldn't find matching command block")
            sys.exit(1)

        if facing == "north":
            slot["min"] = (plotx - 8, ploty - 17, plotz - 23)
            slot["max"] = (plotx + 8, ploty + 32, plotz - 1)
        elif facing == "east":
            slot["min"] = (plotx + 1, ploty - 17, plotz - 8)
            slot["max"] = (plotx + 23, ploty + 32, plotz + 8)
        elif facing == "south":
            slot["min"] = (plotx - 8, ploty - 17, plotz + 1)
            slot["max"] = (plotx + 8, ploty + 32, plotz + 23)
        elif facing == "west":
            slot["min"] = (plotx - 23, ploty - 17, plotz - 8)
            slot["max"] = (plotx - 1, ploty + 32, plotz + 8)
        slot["facing"] = facing

        plot_scores[pos] = slot
        num_players_with_plots += 1


plot_scores = OrderedDict(sorted(plot_scores.items(), key=lambda item: item[1]["id"]))
world_id = 1
for item in plot_scores:
    plot_scores[item]["world_id"] = world_id
    world_id += 1

with open("all_plot_records.json", "w") as fp:
    json.dump(plot_scores, fp, indent=2)

# pprint(plot_scores)

print(f"Total number of plots: {len(plot_scores)}")
print(f"Total number of players owning a plot: {num_players_with_plots}")
