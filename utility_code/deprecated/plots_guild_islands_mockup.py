#!/usr/bin/env python3

import random
from pprint import pprint
import numpy as np

grid = 64
# Derp, I transposed this. So it's type, Z, X
plot_offsets = [
    (0, 2, 2),   # a
    (1, 3, 6),   # b
    (2, 1, 10),  # c
    (1, 2, 15),  # d
    (2, 7, 16),  # e
    (0, 5, 11),  # f
    (2, 8, 7),   # g
    (2, 7, 2),   # h
    (0, 12, 2),  # i
    (1, 13, 6),  # j
    (0, 13, 10), # k
    (1, 11, 15), # l
    (0, 15, 14), # m
    (1, 19, 14), # n
    (2, 23, 15), # o
    (1, 28, 15), # p
    (0, 33, 15), # q
    (2, 32, 11), # r
    (1, 34, 7),  # s
    (0, 33, 3),  # t
    (2, 29, 3),  # u
    (0, 30, 7),  # v
    (0, 27, 11), # w
    (1, 26, 7),  # x
    (2, 25, 2),  # y
    (1, 21, 2),  # z
    (0, 22, 6),  # {
    (2, 22, 10), # |
    (2, 17, 2),  # }
    (1, 9, 11),  # ~
]
random.shuffle(plot_offsets)
min_corner = (-2111, -64)
size = [1024 + 128, 2048 + 256]
render_resolution = 16

coords = []
index = "a"
orientation = 0
for plot in plot_offsets:
    orientation += 1
    coords.append((plot[0], plot[2] * grid + grid//2 + min_corner[0] + random.randint(-12, 12), plot[1] * grid + grid//2 + min_corner[1] + random.randint(-12, 12), orientation))
    #coords.append((plot[0], plot[2] * grid + grid//2 + min_corner[0] + random.randint(-12, 12), plot[1] * grid + grid//2 + min_corner[1] + random.randint(-12, 12), ord(index)))
    orientation = orientation % 4
    index = chr(ord(index) + 1)

tile_radius = (176//2, 176//2)
render = np.zeros([i // render_resolution for i in size]);
for plot_type, x, z, orientation in coords:
    relx = x - min_corner[0]
    relz = z - min_corner[1]
    for xstep in range((relx - tile_radius[0] + 1) // render_resolution, (relx + tile_radius[0] - 1) // render_resolution):
        for zstep in range((relz - tile_radius[1] + 1) // render_resolution, (relz + tile_radius[1] - 1) // render_resolution):
            render[xstep][zstep] = orientation

step = 0;
coords.sort(reverse=True|False, key= lambda i: (i[0], i[3]))
for plot_type, x, z, orientation in coords:
    print("execute if score @s temp matches {} run tp @s {} 100 {}".format(step, x, z))
    print("msg @s type={} orientation={}".format(plot_type, (orientation - 1) * 90))
    step = step + 1
print("scoreboard players add @s temp 1")


for row in render:
    for y in row:
        if y == 0:
            print(".", end ="")
        elif y == 1:
            print("-", end ="")
        elif y == 2:
            print("/", end ="")
        elif y == 3:
            print("O", end ="")
        elif y == 4:
            print("|", end ="")
        else:
            print(chr(int(y)), end ="")

    print("")
