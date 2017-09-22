#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This takes a build world (terrain), a main world (play area), and
merges them into a new world, dstWorld (destination).

This does so as directly as possible while providing many features.

Fair warning, some of the optimization is done by removing error handling.
Python will tell you if/when the script crashes.
If it's going to crash, it won't damage the original worlds.
Just fix what broke, and run again.
"""
import mclevel
import terrain_reset_lib
import item_replace_lib
# import item_replace_list # This is where the item replacements are kept

################################################################################
# Config section

config = {
    # Dst is the destination world, which gets overwritten by the build world.
    # Then, data from the main world replaces the relevant parts of the dst world.
    # Please note that no special care need be taken with whitespace in filenames.
    "localMainFolder":"/home/rock/tmp/Project Epic Source/",
    "localBuildFolder":"/home/rock/tmp/Project Epic/",
    "localDstFolder":"/home/rock/tmp/Project Epic Updated/",
    
    # No 0.5 offset here, add it yourself if you like.
    # (x,y,z,ry,rx)
    "SafetyTpLocation":(-734.0, 105.5, 50.0, 0.0, 0.0),

    "coordinatesToCopy":(
        # ("a unique name",        (lowerCoordinate),  (upperCoordinate), ( id, dmg), "block name (comment)"),
        ("Apartments_buying_room", ( -809,  99,   47), (-874,  96,    4), (  41, 0 ), "gold"),
        ("Apartments_units",       ( -817, 113,   87), (-859, 164,   16), (  41, 0 ), "gold"),
        ("Plot_Pressure_Plates",   ( -719, 106, -118), (-665, 106,  -74), (  41, 0 ), "gold"),
        ("Guild_Room",             ( -800, 109,  -75), (-758, 104, -102), (  41, 0 ), "gold"),
        ("Section_1",              (-1130,   0, -267), (-897, 255,  318), (  41, 0 ), "gold"),
        ("Section_2",              ( -896,   0,  208), (-512, 255,  318), (  57, 0 ), "diamond"),
        ("Section_3",              ( -896,   0,  207), (-788, 255,  119), (  42, 0 ), "iron"),
        ("Section_4",              ( -896,   0, -267), (-825, 255,  -28), (  22, 0 ), "lapis"),
        ("Section_5",              ( -512,   0,  207), (-640, 255, -273), (  24, 0 ), "sandstone"),
        ("Section_6",              ( -824,   0, -169), (-641, 255, -272), ( 152, 0 ), "redstone"),
        ("Section_7",              ( -641,   0, -168), (-677, 255, -132), ( 155, 0 ), "quartz"),
        ("Section_8",              ( -774,   0, -168), (-813, 255, -150), (  17, 14), "birch wood"),
        ("Section_9",              ( -641,   0,  -25), (-655, 255,  -52), (  17, 15), "jungle wood"),
        ("Section_10",             ( -680,   0,  183), (-641, 255,  207), (  19, 0 ), "sponge"),
        ("Section_11",             ( -668,   0,  -14), (-641, 255,   25), (   1, 1 ), "granite"),
    )
}

testConfig = {
    "localMainFolder":"/home/tim/.minecraft/saves/main/",
    "localBuildFolder":"/home/tim/.minecraft/saves/build/",
    "localDstFolder":"/home/tim/.minecraft/saves/dst/",
    "SafetyTpLocation":(149.0, 76.0, 133.0, 0.0, 0.0),
    "coordinatesToCopy":(
        ("hut1",           (      153, 68,      104), (      156, 73,      108), (0,0), "air"),
        ("hut2fence",      (      159, 64,      112), (      163, 69,      116), (0,0), "air"),
        ("hut3",           (      150, 70,      112), (      154, 75,      115), (0,0), "air"),
        ("church",         (      138, 73,      113), (      146, 84,      117), (0,0), "air"),
        ("hut4",           (      113, 62,      126), (      116, 68,      130), (0,0), "air"),
        ("farm1s",         (      120, 62,      122), (      126, 64,      130), (0,0), "air"),
        ("hut5",           (      133, 70,      126), (      136, 74,      130), (0,0), "air"),
        ("hut6",           (      155, 70,      126), (      158, 74,      130), (0,0), "air"),
        ("farm2l",         (      164, 67,      122), (      176, 69,      130), (0,0), "air"),
        ("well",           (      146, 58,      130), (      151, 73,      135), (0,0), "air"),
        ("hut7",           (      111, 61,      134), (      115, 67,      138), (0,0), "air"),
        ("farm3l",         (      118, 62,      134), (      130, 64,      142), (0,0), "air"),
        ("hut8TShape",     (      136, 63,      136), (      147, 73,      144), (0,0), "air"),
        ("hut9fence",      (      153, 68,      134), (      157, 74,      138), (0,0), "air"),
        ("hut10fence",     (      150, 64,      139), (      154, 70,      143), (0,0), "air"),
        ("farm4l",         (      164, 68,      134), (      176, 70,      142), (0,0), "air"),
        ("farm5s",         (      150, 63,      146), (      158, 65,      152), (0,0), "air"),
        ("farm6l",         (      138, 62,      153), (      146, 64,      165), (0,0), "air"),
    )
}


"""
List of blocks to not copy over for the regions above
"""
blocksToReplace = (
    ("minecraft:iron_block", "air"),
    ("minecraft:iron_ore", "air"),
    ("minecraft:gold_block", "air"),
    ("minecraft:gold_ore", "air"),
    ("minecraft:lapis_block", "air"),
    ("minecraft:lapis_ore", "air"),
    ("minecraft:diamond_block", "air"),
    ("minecraft:diamond_ore", "air"),
    ("minecraft:emerald_block", "air"),
    ("minecraft:emerald_ore", "air"),
    
    ("minecraft:beacon", "air"),
    
    # Not sure about this section
    #("enchanting_Table", "air"),
    #("quartz_ore", "air"),
    #("hopper", "air"),
    
    # anvils
    ((145,0), "air"),
    ((145,1), "air"),
    ((145,2), "air"),
    ((145,3), "air"),
    ((145,4), "air"),
    ((145,5), "air"),
    ((145,6), "air"),
    ((145,7), "air"),
    ((145,8), "air"),
    ((145,9), "air"),
    ((145,10), "air"),
    ((145,11), "air"),
)


################################################################################
# Testing sandbox

world = mclevel.loadWorld("/home/tim/.minecraft/saves/dst/")

testReplacementList = [
    [
        {
            "id":"minecraft:gunpowder",
            "damage":0,
            "count":5,
            "nbt":'{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}',
        },
        [
            "id","leather_helmet",
            "count","=","1",
            "nbt","replace",ur'{ench:[{lvl:2s,id:1s},{lvl:1s,id:10s}],display:{color:16381908,Name:"§6Pheonix Cap",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}',
        ]
    ],
    [
        {
            "id":"minecraft:gunpowder",
            "damage":0,
            "count":8,
            "nbt":'{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}',
        },
        [
            "id","leather_chestplate",
            "count","=","1",
            "nbt","replace",ur'{ench:[{lvl:2s,id:1s},{lvl:1s,id:10s}],display:{color:16314131,Name:"§6Pheonix Tunic",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}',
        ]
    ],
    [
        {
            "id":"minecraft:gunpowder",
            "damage":0,
            "count":7,
            "nbt":'{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}',
        },
        [
            "id","leather_leggings",
            "count","=","1",
            "nbt","replace",ur'{ench:[{lvl:2s,id:1s},{lvl:1s,id:10s}],display:{color:16747314,Name:"§6Pheonix Pants",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}',
        ]
    ],
    [
        {
            "id":"minecraft:gunpowder",
            "damage":0,
            "count":4,
            "nbt":'{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}',
        },
        [
            "id","leather_boots",
            "count","=","1",
            "nbt","replace",ur'{ench:[{lvl:2s,id:1s},{lvl:1s,id:10s}],display:{color:12189696,Name:"§6Pheonix Boots",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}',
        ]
    ],
]

print "Parsing item replace list..."
testReplace = item_replace_lib.allReplacements(testReplacementList)
print "Replacing items in the world..."
item_replace_lib.replaceItemsInWorld(world,testReplace)
print "Saving in place..."
world.saveInPlace()


#terrain_reset_lib.replaceBlocksInBoxList(config,coordinatesToCopy,"main")
#terrain_reset_lib.replaceBlocksGlobally(config,blocksToReplaceB,"build")

#terrain_reset_lib.terrainReset(testConfig,blocksToReplace)

################################################################################
# Main Code

# This shows where the selected regions are, as your old script does.
#terrain_reset_lib.fillRegions(config)

# This does the move itself - copy areas, entities, scoreboard, etc.
#terrain_reset_lib.terrainReset(config,blocksToReplace)


