#!/usr/bin/env python
# -*- coding: utf-8 -*-

import list_lootless_tile_entities_lib

################################################################################
# Config section

# Dst is the destination world, which gets overwritten by the build world.
# Then, data from the main world replaces the relevant parts of the dst world.
# Please note that no special care need be taken with whitespace in filenames.
worldFolder = "/home/rock/tmp/BUILD_Project_Epic"

coordinatesToScan = (
    # ("region name",        (lowerCoordinate),  (upperCoordinate),  ( id, dmg), "block name (comment)"),
    ("light blue",      (-2480, 0, 704),   (-2193, 255, 975),   (7, 0), "bedrock"),
    ("white",           (-2032, 0, 704),   (-1873, 255, 1055),  (7, 0), "bedrock"),
    ("magenta",         (-1616, 0, 704),   (-1361, 255, 959),   (7, 0), "bedrock"),
    ("orange",          (-1360, 0, 704),   (-1041, 120, 1055),  (7, 0), "bedrock"),
    ("bonus",           (-1040, 0, 704),   (-753,  93,  1071),  (7, 0), "bedrock"),
    ("masters1",        (-2400, 0, -769),  (-1000, 255, -1377), (7, 0), "bedrock"),
    ("masters2",        (-2400, 0, -1664), (-1569, 255, -1377), (7, 0), "bedrock"),
)

contentsLoreToIgnore = ("Monument Block", "Quest Item",)
#contentsLoreToIgnore = ("Monument Block", "Quest Item", "King's Valley : Uncommon",)

chestWhitelist = (
                  # Master copies
                  (-2081, 121, -950 ),
                  (-2081, 121, -951 ),
                  (-2081, 121, -954 ),
                  (-2081, 121, -953 ),
                  (-1863, 95,  -981 ),
                  (-1848, 178, -1354),
                  (-1831, 163, -1361),
                  (-1832, 171, -1354),
                  (-1830, 190, -1351),
                  (-1738, 87,  -858 ),
                  (-2088, 115, -1532),
                  (-2088, 115, -1531),
                  (-2094, 115, -1534),
                  (-2095, 115, -1534),
                  (-2036, 123, -1571),
                  (-1772, 78,  -1561),
                  (-1771, 78,  -1561),
                  (-2070, 48,  -1048),
                  (-2044, 53,  -1039),

                  # White
                  (-2025, 120, 753),
                  (-2013, 32,  946),
                  (-1983, 71,  808),
                  (-1954, 47,  802),
                  (-1954, 30,  912),
                  (-1938, 42,  900),
                  (-1939, 42,  900),
                  (-1929, 16,  917),
                  (-1916, 42,  851),
                  (-1905, 37,  953),
                  (-1905, 37,  952),
                  (-1883, 24,  972),

                  # Orange
                  # None!

                  # Magenta
                  # None!

                  # Light blue
                  (-2452, 130, 902  ),
                  (-2439, 181, 743  ),
                  (-2334, 210, 789  ),
                  (-2325, 180, 837  ),
                  (-2315, 175, 790  ),
                  (-2280, 168, 900  ),
                  (-2209, 181, 790  ),
                  (-2400, 170, 886  ),

                  # Bonus
                  # None!
                 )

tileEntitiesToCheck = ("chest",)
# If using only one item, ALWAYS use a trailing comma.
# Possible values: "chest" (trapped chest shares ID), "dispenser", "dropper", "shulker_box", "hopper"
# These are actually namespaced; default is "minecraft:*" in this code.

################################################################################
# Main Code

# This scans for tile entities that don't have a loot table
list_lootless_tile_entities_lib.run(worldFolder, coordinatesToScan, tileEntitiesToCheck, chestWhitelist)

