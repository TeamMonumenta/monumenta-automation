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
    Match stone and its variants (NYI):
    {"id":"stone"}
    
    Same, but specify namespace (good for modded, NYI):
    {"id":"minecraft:stone"}
    
    Match stone and its variants by ID (NYI):
    {"id":1}
    
    Match smooth andesite by damage (NYI):
    {"id":"stone","damage":6}
    
    Match colored beds with NBT (NYI):
    {"id":"bed","nbt":{"color":"red"}}
    This will not check if the NBT matches perfectly,
    only if the specified NBT matches. Other tags are
    ignored.
    
    To specify strict NBT (NYI):
    {"id":"bed","nbt":{"color":"red"},"nbtStrict":True}
    This matches NBT exactly as specified.

    To specify no NBT:
    {"id":"log","nbt":None}
    This matches NBT exactly as specified.
    
    To specify an item count:
    {"id":"stick","count":5}
    
    To specify an item count range:
    {"id":"stick","count":[12,24]}

Action lists appear like so (NYI):
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
        
        nbt - alter an item's damage
            replace - replace an item's NBT data entirely
            set - set specified NBT without altering other NBT
                    existing lists and compounds will not have items removed
            clear - remove all NBT from the item
        
        scoreboard - if on a player, in an ender chest, or in a shulker box
                    in one of those places, affect that player's scoreboard
                    
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
    # Remove any diamonds that are present
    [
        {"id":264},
        [
            "scoreboard", "operation", "@s", "illegal_diamonds", "+=", "@i", "count"
        ]
    ],
    # Remove any iron nuggets that are present
    [
        {"id":452},
        [
            "scoreboard", "operation", "@s", "illegal_iron", "+=", "@i", "count"
        ]
    ],
    # Remove any iron ingots that are present
    [
        {"id":265},
        [
            
            "count","*","9",
            "scoreboard", "operation", "@s", "illegal_iron", "+=", "@i", "count"
        ]
    ],
    # Remove any iron blocks that are present
    [
        {"id":42},
        [
            
            "count","*","81",
            "scoreboard", "operation", "@s", "illegal_iron", "+=", "@i", "count"
        ]
    ],
    # Remove any gold nuggets that are present
    [
        {"id":371},
        [
            "scoreboard", "operation", "@s", "illegal_gold", "+=", "@i", "count"
        ]
    ],
    # Remove any gold ingots that are present
    [
        {"id":266},
        [
            
            "count","*","9",
            "scoreboard", "operation", "@s", "illegal_gold", "+=", "@i", "count"
        ]
    ],
    # Remove any gold blocks that are present
    [
        {"id":41},
        [
            
            "count","*","81",
            "scoreboard", "operation", "@s", "illegal_gold", "+=", "@i", "count"
        ]
    ],
]

