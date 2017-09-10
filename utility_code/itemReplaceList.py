#!/usr/bin/python
# -*- coding: utf-8 -*-

# This is in development; suggestions are more than welcome!
# Looking for:
#   additional item matching pattens
#   additional actions
#   better notation
#   whatever else

"""
Item replacement list - this MUST be mutable!

This is an ordered list of replacement definitions
Each replacement definition is a list that contains a
    pattern matching list and a list of actions to perform

Pattern matching lists appear like so:
    Match stone and its variants:
    {"id":"minecraft:stone"}
    
    Match smooth andesite by damage:
    {"id":"minecraft:stone","damage":6}
    
    Match certain damage values:
    {"id":"minecraft:wool","damage":[4,7,12,13]}
    
    Match colored beds with NBT (NYI):
    {"id":"bed","nbt":"{color:14}"}
    This will not check if the NBT matches perfectly,
    only if the specified NBT matches. Other tags are
    ignored.
    
    To specify strict NBT (NYI):
    {"id":"bed","nbt":"{color:14}","nbtStrict":True}
    This matches NBT exactly as specified.

    To specify no NBT:
    {"id":"minecraft:log","nbt":None}
    This matches NBT exactly as specified.
    
    To specify an item count:
    {"id":"minecraft:stick","count":5}
    
    To specify an item count range:
    {"id":"minecraft:stick","count":range(12,24+1)}

Action lists appear like so:
    Action lists are lists that contain actions, and
    are run from top to bottom. They look like this:
    [
    ["damage", "-", 7, "min", 2],
    ["nbt", "update", "{display:{CustomName:"§o§6Resurrected Pheonix"}}"],
    ]
    
    Valid actions include:
        id - change the item's ID to a new value
        
        count - alter an item stack's count
            = - set count
            + - increase count
            - - decrease count
            * - multiplies count (integer)
            / - divides count (integer)
            % - set count to ( oldCount % arg ) - always positive
            max - set count to max if max is exceeded
            min - set count to min if min is exceeded
        
        damage - alter an item's damage
            = - set damage
            + - increase damage
            - - decrease damage
            * - multiplies damage (integer)
            / - divides damage (integer)
            % - set damage to ( oldDamage % arg ) - always positive
            max - set damage to max if max is exceeded
            min - set damage to min if min is exceeded
        
        nbt - alter an item's damage (NYI) - only clear is implemented
            replace - replace an item's NBT data entirely
            set - set specified NBT without altering other NBT
                    existing lists and compounds will not have items removed
            clear - remove all NBT from the item
        
        scoreboard - if on a player, in an ender chest, or in a shulker box
                    in one of those places, affect that player's scoreboard
                    (NYI)
                    
                    @s - the player to target
                    @i - item's details
                    
                    @i's scores:
                        count
                        damage
            accepted arguments:
                set, add, remove, reset, enable, operation
            example:
                "scoreboard", "operation", "@s", "iron_confiscated", "+=", "@i", "count"
            
        
        remove - delete the item

So, for example:
itemReplacements = [
    # Replace light gray wool with five cyan stained terracotta blocks
    [
        {"id":"wool","damage":8},
        [
            "id","stained_hardened_clay",
            "count","=",5,
            "damage","+",1,
        ]
    ],
    # Replace Pheonix Armor Ash (gunpowder) with a Pheonix Chestplate
    [
        {
            "id":289,
            "damage":0,
            "count":8,
            "nbt":"{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}",
        },
        [
            "id","leather_chestplate",
            "count","=","1",
            "nbt","replace","{display:{Name:"§6Pheonix Chestplate",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}",
        ]
    ],
]
"""
itemReplacements = [
    # Remove any iron ore that is present
    [
        {"id":"minecraft:iron_ore"},
        [
            "remove",
        ]
    ],
    # Remove any iron nuggets that are present
    [
        {"id":"minecraft:iron_nugget"},
        [
            "remove",
        ]
    ],
    # Remove any iron ingots that are present
    [
        {"id":"minecraft:iron_ingot"},
        [
            
            "remove",
        ]
    ],
    # Remove any iron blocks that are present
    [
        {"id":"minecraft:iron_block"},
        [
            "remove",
        ]
    ],
    # Remove any gold ore that is present
    [
        {"id":"minecraft:gold_ore"},
        [
            "remove",
        ]
    ],
    # Remove any gold nuggets that are present
    [
        {"id":"minecraft:gold_nugget"},
        [
            "remove",
        ]
    ],
    # Remove any gold ingots that are present
    [
        {"id":"minecraft:gold_ingot"},
        [
            "remove",
        ]
    ],
    # Remove any gold blocks that are present
    [
        {"id":"minecraft:gold_block"},
        [
            "remove",
        ]
    ],
    # Remove any diamond ore that is present
    [
        {"id":"minecraft:diamond_ore"},
        [
            "remove",
        ]
    ],
    # Remove any diamonds that are present
    [
        {"id":"minecraft:diamond"},
        [
            "remove",
        ]
    ],
    # Remove any diamond blocks that are present
    [
        {"id":"minecraft:diamond_block"},
        [
            "remove",
        ]
    ],
    # Remove any emerald ore that is present
    [
        {"id":"minecraft:emerald_ore"},
        [
            "remove",
        ]
    ],
    # Remove any emeralds that are present
    [
        {"id":"minecraft:emerald"},
        [
            "remove",
        ]
    ],
    # Remove any emerald blocks that are present
    [
        {"id":"minecraft:emerald_block"},
        [
            "remove",
        ]
    ],
    # Remove any lapis ore that is present
    [
        {"id":"minecraft:lapis_ore"},
        [
            "remove",
        ]
    ],
    # Remove any lapis that is present
    [
        {"id":"minecraft:dye","damage":4},
        [
            "remove",
        ]
    ],
    # Remove any lapis blocks that are present
    [
        {"id":"minecraft:lapis_block"},
        [
            "remove",
        ]
    ],
    # Remove any anvils that are present
    [
        {"id":"minecraft:anvil"},
        [
            "remove",
        ]
    ],
]

