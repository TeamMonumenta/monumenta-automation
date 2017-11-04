#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is in development; suggestions are more than welcome!
# Looking for:
#   additional item matching pattens
#   additional actions
#   better notation
#   whatever else

blockReplacements = (
    ("minecraft:iron_block", "air"),
    ("minecraft:iron_ore", "air"),
    ("minecraft:hopper", "air"),
    #("minecraft:gold_block", "air"), # probably fine
    #("minecraft:gold_ore", "air"),
    ("minecraft:diamond_block", "air"),
    ("minecraft:diamond_ore", "air"),
    #("minecraft:emerald_block", "air"), # probably fine
    #("minecraft:emerald_ore", "air"),

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
    
    Match colored beds with NBT:
    {"id":"bed","nbt":"{color:14}"}
    This will not check if the NBT matches perfectly,
    only if the specified NBT matches. Other tags are
    ignored.
    
    To specify strict NBT:
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
    ["nbt", "update", "{display:{Name:"§o§6Resurrected Pheonix"}}"],
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
        
        nbt - alter an item's nbt - only clear is implemented
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
    # Replace Pheonix Armor Ash (gunpowder) with Pheonix Armor
    [
        {
            "id":"minecraft:gunpowder",
            "damage":0,
            "count":5,
            "nbt":ur'''{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}''',
        },
        [
            "id","leather_helmet",
            "count","=","1",
            "nbt","replace",ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:10s}],display:{color:16381908,Name:"§6Pheonix Cap",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}''',
        ]
    ],
    [
        {
            "id":"minecraft:gunpowder",
            "damage":0,
            "count":8,
            "nbt":ur'''{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}''',
        },
        [
            "id","leather_chestplate",
            "count","=","1",
            "nbt","replace",ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:10s}],display:{color:16314131,Name:"§6Pheonix Tunic",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}''',
        ]
    ],
    [
        {
            "id":"minecraft:gunpowder",
            "damage":0,
            "count":7,
            "nbt":ur'''{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}''',
        },
        [
            "id","leather_leggings",
            "count","=","1",
            "nbt","replace",ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:10s}],display:{color:16747314,Name:"§6Pheonix Pants",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}''',
        ]
    ],
    [
        {
            "id":"minecraft:gunpowder",
            "damage":0,
            "count":4,
            "nbt":ur'''{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}''',
        },
        [
            "id","leather_boots",
            "count","=","1",
            "nbt","replace",ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:10s}],display:{color:12189696,Name:"§6Pheonix Boots",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}''',
        ]
    ],
]
"""

""" Items that aren't going in this list (for now at least)
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
"""

itemReplacements = [
    ############################################################################
    # Remove dungeon key items on weekly terrain resets:
    # (key items within dungeons, not keys to enter dungeons)
    ############################################################################
    
    # Simbelmynë
    [
        {
            "id":"minecraft:red_flower",
            "nbt":ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§fSimbelmynë is a rare flower, and it is said to","§fonly grow on the burial mounds of Royalty...","§e§lTaking this item outside of the dungeon","§e§lwill result in its destruction.","* D4 Key 1 *"],Name:"§9§lSimbelmynë"}}''',
        },
        [
            "remove"
        ]
    ],
    
    # Ancient Mortar
    [
        {
            "id":"minecraft:bowl",
            "nbt":ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§fA Mortar perfect for mashing ingredients...","§e§lTaking this item outside of the dungeon","§e§lwill result in its destruction.","* D4 Key 2 *"],Name:"§9§lAncient Mortar"}}''',
        },
        [
            "remove"
        ]
    ],
    
    # Aquanis Lily
    [
        {
            "id":"minecraft:red_flower",
            "nbt":ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§fAn uncommon flower generally found near Hot Springs...","§e§lTaking this item outside of the dungeon","§e§lwill result in its destruction.","* D4 Key 3 *"],Name:"§9§lAquanis Lily"}}''',
        },
        [
            "remove"
        ]
    ],
    
    ############################################################################
    # Update items that have changed:
    ############################################################################
    
    # Topaz Cap
    [
        {
            "id":"minecraft:leather_helmet",
            "nbt":ur'''{display:{Name:"§6§lTopaz Cap"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","* Unique Item *","§6The luck has decayed into health"],color:16776960,Name:"§6§lTopaz Cap"},AttributeModifiers:[{UUIDMost:-4372966254504623356L,UUIDLeast:-5757139819161180185L,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-6920208193525167582L,UUIDLeast:-9012692505744652313L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],
    
    # Old Amber Cap -> Topaz Cap
    [
        {
            "id":"minecraft:leather_helmet",
            "nbt":ur'''{display:{Name:"§6§lAmber Cap"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","* Unique Item *","§6The luck has decayed into health"],color:16776960,Name:"§6§lTopaz Cap"},AttributeModifiers:[{UUIDMost:-4372966254504623356L,UUIDLeast:-5757139819161180185L,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-6920208193525167582L,UUIDLeast:-9012692505744652313L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],
    
    # Jeweled Tiara
    [
        {
            "id":"minecraft:golden_helmet",
            "nbt":ur'''{display:{Name:"§d§lJeweled Tiara"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["* Unique Item *","§6The luck has decayed into health"],Name:"§d§lJeweled Tiara"},AttributeModifiers:[{UUIDMost:992743L,UUIDLeast:9295615L,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:2252054273775257919L,UUIDLeast:-6258579311022731853L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],
    
    # Kismet's Blessing
    [
        {
            "id":"minecraft:leather_helmet",
            "nbt":ur'''{display:{Name:"§b§lKismet's Blessing"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§6The luck has decayed into health"],color:65493,Name:"§b§lKismet's Blessing"},AttributeModifiers:[{UUIDMost:-6900745281224160306L,UUIDLeast:-4828553848378685989L,Amount:3.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:1116995255491055008L,UUIDLeast:-6766107056483247837L,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
        ]
    ],
    
    ############################################################################
    # Stuff that players shouldn't have had:
    ############################################################################
    
    ############################################################################
    # Iron:

    [
        {"id":"minecraft:iron_ore"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:iron_nugget"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:iron_ingot"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:iron_block"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:iron_helmet"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:iron_chestplate"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:iron_leggings"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:iron_boots"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:iron_axe"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:iron_hoe"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:iron_pickaxe"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:iron_shovel"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:iron_sword"},
        [
            "remove"
        ]
    ],
    
    ############################################################################
    # Diamond:

    [
        {"id":"minecraft:diamond_ore"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:diamond"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:diamond_block"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:diamond_helmet"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:diamond_chestplate"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:diamond_leggings"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:diamond_boots"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:diamond_axe"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:diamond_hoe"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:diamond_pickaxe"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:diamond_shovel"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:diamond_sword"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:anvil"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:hopper"},
        [
            "remove"
        ]
    ],
    [
        {"id":"minecraft:beacon"},
        [
            "remove"
        ]
    ],
    # Wither skeleton skulls
    [
        {
            "id":"minecraft:skull",
            "damage":1
        },
        [
            "remove"
        ]
    ],
    
    ############################################################################
    # Other:
    
    # Luck items
    [
        {"nbt":ur'''{tag:{AttributeModifiers:[{AttributeName:"generic.luck"}]}}'''},
        [
            "remove"
        ]
    ],

    ############################################################################
    # Replace removed items with a notice:
    ############################################################################
    [
        {
            "count":"0",
        },
        [
            "id","minecraft:rotten_flesh",
            "count","=","1",
            "damage","=","0",
            "nbt","replace",ur'''{ench:[{lvl:1s,id:71s}],display:{Name:"§cDecayed Item",Lore:["You had something","you shouldn't have,","didn't you?"]}}''',
        ]
    ],
]

